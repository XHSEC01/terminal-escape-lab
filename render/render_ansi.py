"""ANSI 终端渲染器：把含转义序列的字节流渲染成 PNG 截图。

支持：
- SGR 颜色 (ESC[...m)
- CSI 光标移动 (ESC[<n>A/B/C/D/H)
- CSI 擦除 (ESC[<n>J/K)
- OSC 52 剪贴板写入 (标注在右侧)
- OSC 8 超链接 (下划线 + URL 标注)
- 普通可打印字符 + 中文

用法：
    render.render_bytes(raw_bytes, title, out_path, cols, rows)
"""
import re, io, base64
from PIL import Image, ImageDraw, ImageFont

# 16 色 + 8 bit bright
PALETTE = [
    (24,24,24),(199,55,47),(38,205,58),(229,200,71),(57,119,224),
    (170,82,224),(33,182,182),(200,200,200),(80,80,80),(255,107,107),
    (38,205,58),(229,200,71),(57,119,224),(170,82,224),(33,182,182),
    (255,255,255),
]

BG = (30,30,38)
FG = (220,220,228)

def _font(size=18):
    for p in [
        r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\cour.ttf",
        r"C:\Windows\Fonts\msyh.ttc",
    ]:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()

# ---------- ANSI 解析 ----------
ESC, CSI_RE = b"\x1b", re.compile(rb"\x1b\[([0-9;?]*)([ -/]*)([@-~])")
OSC52_RE = re.compile(rb"\x1b\]52;([a-zA-Z0-9]*);([A-Za-z0-9+/=]+)(?:\x07|\x1b\\)")
OSC8_RE  = re.compile(rb"\x1b\]8;;([^\x1b\x07]*)\x1b\\([^\x1b]*)\x1b\]8;;\x1b\\")
OSC_OTHER = re.compile(rb"\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)")

class Cell:
    __slots__ = ("ch","fg","bg","bold","underline","link")
    def __init__(self, ch=" ", fg=FG, bg=BG, bold=False, underline=False, link=None):
        self.ch=ch; self.fg=fg; self.bg=bg
        self.bold=bold; self.underline=underline; self.link=link

class Screen:
    def __init__(self, cols, rows):
        self.cols, self.rows = cols, rows
        self.grid = [[Cell() for _ in range(cols)] for _ in range(rows)]
        self.cx, self.cy = 0, 0
        self.fg, self.bg = FG, BG
        self.bold = self.underline = False
        self.annotations = []   # (row, text)  右侧标注
        self.cur_link = None

    def _newline(self):
        self.cy += 1
        if self.cy >= self.rows: self.cy = self.rows - 1
        self.cx = 0

    def put(self, ch):
        if self.cx >= self.cols:
            self._newline()
        if 0 <= self.cy < self.rows and 0 <= self.cx < self.cols:
            c = self.grid[self.cy][self.cx]
            c.ch = ch; c.fg = self.fg; c.bg = self.bg
            c.bold = self.bold; c.underline = self.underline
            c.link = self.cur_link
        self.cx += 1

    def sgr(self, params):
        if not params or params == [0]:
            self.fg, self.bg = FG, BG
            self.bold = self.underline = False
            return
        for p in params:
            if p == 0: self.fg, self.bg = FG, BG; self.bold=self.underline=False
            elif p == 1: self.bold = True
            elif p == 4: self.underline = True
            elif p == 22: self.bold = False
            elif p == 24: self.underline = False
            elif 30 <= p <= 37: self.fg = PALETTE[p-30]
            elif p == 38: pass  # 256色/真彩色 简化跳过
            elif p == 39: self.fg = FG
            elif 40 <= p <= 47: self.bg = PALETTE[p-40]
            elif p == 49: self.bg = BG
            elif 90 <= p <= 97: self.fg = PALETTE[p-90+8]
            elif 100 <= p <= 107: self.bg = PALETTE[p-100+8]

    def csi(self, params, inter, final):
        n = params[0] if params else 0
        if final == ord("A"): self.cy = max(0, self.cy - (n or 1))
        elif final == ord("B"): self.cy = min(self.rows-1, self.cy + (n or 1))
        elif final == ord("C"): self.cx = min(self.cols-1, self.cx + (n or 1))
        elif final == ord("D"): self.cx = max(0, self.cx - (n or 1))
        elif final == ord("H"):
            r = (params[0] if len(params)>0 else 1) - 1
            c = (params[1] if len(params)>1 else 1) - 1
            self.cy = max(0, min(self.rows-1, r))
            self.cx = max(0, min(self.cols-1, c))
        elif final == ord("J"):
            mode = n or 0
            if mode in (0, 2):
                for r in range(self.cy, self.rows):
                    for c in range(self.cols):
                        self.grid[r][c] = Cell()
            if mode == 2:
                for r in range(0, self.cy):
                    for c in range(self.cols):
                        self.grid[r][c] = Cell()
        elif final == ord("K"):
            for c in range(self.cx, self.cols):
                self.grid[self.cy][c] = Cell()

def parse(raw: bytes, cols=80, rows=24):
    s = Screen(cols, rows)
    i = 0
    n = len(raw)
    while i < n:
        # OSC 52
        m = OSC52_RE.match(raw, i)
        if m:
            try:
                decoded = base64.b64decode(m.group(2)).decode("utf-8", errors="replace")
            except Exception:
                decoded = m.group(2).decode("ascii", errors="replace")
            s.annotations.append((s.cy, f"OSC52 -> clipboard: {decoded}"))
            i = m.end(); continue
        # OSC 8
        m = OSC8_RE.match(raw, i)
        if m:
            url = m.group(1).decode("utf-8", errors="replace")
            text = m.group(2).decode("utf-8", errors="replace")
            s.cur_link = url
            for ch in text:
                s.put(ch)
            s.cur_link = None
            i = m.end(); continue
        # 其他 OSC 吃掉
        m = OSC_OTHER.match(raw, i)
        if m:
            i = m.end(); continue
        # CSI
        m = CSI_RE.match(raw, i)
        if m:
            pstr = m.group(1).decode("ascii")
            params = [int(x) if x else 0 for x in pstr.split(";")] if pstr else []
            inter = m.group(2)
            final = m.group(3)[0]
            if final == ord("m"):
                s.sgr(params)
            else:
                s.csi(params, inter, final)
            i = m.end(); continue
        # ESC 单字符 (非 [)
        if raw[i:i+1] == ESC:
            if i+1 < n and raw[i+1:i+2] not in (b"[", b"]"):
                i += 2; continue
            i += 1; continue
        # 普通字符
        b = raw[i]
        if b in (0x0a, 0x0d):   # \n \r
            if b == 0x0a: s._newline()
            else: s.cx = 0
            i += 1; continue
        if b == 0x08:  # backspace
            s.cx = max(0, s.cx-1); i += 1; continue
        if b == 0x07:  # bell
            i += 1; continue
        if b < 0x20:
            i += 1; continue
        # UTF-8 解码
        if b < 0x80:
            s.put(chr(b)); i += 1
        else:
            # 多字节
            if b >> 5 == 0b110: w = 2
            elif b >> 4 == 0b1110: w = 3
            elif b >> 3 == 0b11110: w = 4
            else: w = 1
            try:
                ch = raw[i:i+w].decode("utf-8")
                for c in ch: s.put(c)
            except Exception:
                s.put("?")
            i += w
    return s

# ---------- 渲染 ----------
def render_bytes(raw: bytes, title: str, out_path: str,
                 cols=80, rows=24, font_size=18, pad=24):
    s = parse(raw, cols, rows)
    font = _font(font_size)
    # 量字宽
    bbox = font.getbbox("M")
    cw = bbox[2] - bbox[0] + 2
    ch = font_size + 8
    title_h = 36
    annot_w = 0
    ann_lines = []
    if s.annotations:
        max_ann = max(len(a[1]) for a in s.annotations)
        annot_w = min(max_ann * 9 + 40, 520)
    W = pad*2 + cols*cw + annot_w
    H = pad*2 + rows*ch + title_h
    img = Image.new("RGB", (W, H), (18,18,24))
    d = ImageDraw.Draw(img)
    # 标题栏
    d.rectangle([0,0,W,title_h], fill=(48,54,72))
    d.text((pad, 8), title, fill=(230,230,240), font=_font(20))
    # 终端区背景
    d.rectangle([pad, title_h+pad, pad+cols*cw, title_h+pad+rows*ch], fill=BG)
    # 画格子
    for r in range(rows):
        for c in range(cols):
            cell = s.grid[r][c]
            x = pad + c*cw
            y = title_h + pad + r*ch
            if cell.bg != BG:
                d.rectangle([x, y, x+cw, y+ch], fill=cell.bg)
            if cell.ch.strip():
                color = cell.fg
                if cell.bold:
                    color = tuple(min(255, v+30) for v in color)
                d.text((x+1, y+2), cell.ch, fill=color, font=font)
            if cell.underline or cell.link:
                uy = y + ch - 3
                d.line([x, uy, x+cw-2, uy], fill=(120,180,255))
    # 右侧标注
    if s.annotations:
        ax = pad + cols*cw + 20
        d.rectangle([ax, title_h+pad, ax+annot_w-20, title_h+pad+rows*ch],
                    fill=(40,30,30), outline=(120,60,60))
        d.text((ax+10, title_h+pad+6), "OSC52 注入", fill=(255,180,120), font=_font(16))
        yy = title_h + pad + 34
        for row, txt in s.annotations:
            # 截断
            t = txt if len(txt)*9 < annot_w-40 else txt[:annot_w//9-4]+"..."
            d.text((ax+10, yy), t, fill=(255,200,160), font=_font(15))
            yy += 22
    img.save(out_path)
    return out_path

if __name__ == "__main__":
    import sys
    raw = sys.stdin.buffer.read()
    out = sys.argv[1] if len(sys.argv) > 1 else "render_out.png"
    title = sys.argv[2] if len(sys.argv) > 2 else "terminal output"
    render_bytes(raw, title, out)
    print(f"saved -> {out}")
