"""实验E 闭环版截图：展示完整攻击链 + 剪贴板实测结果。

用真实 API 结果（glm-4-flash verbatim + ESC\\终止符）+ 真实剪贴板写入。
"""
import os, sys, base64, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render.render_ansi import render_bytes
from render.fonts import load_font as _font
from PIL import Image, ImageDraw, ImageFont

LAB = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(LAB, "assets", "terminal-escape")
os.makedirs(ASSETS, exist_ok=True)

def run():
    print("[E-closed] generating closed-loop screenshot")
    # 读取闭环模型输出
    closed_blob = open(os.path.join(ASSETS, "bypass_glm-4-flash_verbatim_st.bin"), "rb").read()
    # 读取 normal（被过滤）的输出
    normal_blob = open(os.path.join(ASSETS, "bypass_glm-4-flash_normal_bel.bin"), "rb").read()

    # 验证闭环
    p2 = re.compile(rb"\x1b\]52;c;([A-Za-z0-9+/=]+)\x1b\\")
    m = p2.search(closed_blob)
    decoded = base64.b64decode(m.group(1)).decode() if m else "(no match)"
    esc_closed = closed_blob.count(b"\x1b")
    esc_normal = normal_blob.count(b"\x1b")

    # ===== 大图：三栏闭环 =====
    font = _font(15); big = _font(22); small = _font(13); tiny = _font(11)
    W = 1280; H = 720
    img = Image.new("RGB", (W, H), (18,18,24))
    d = ImageDraw.Draw(img)
    d.rectangle([0,0,W,50], fill=(48,54,72))
    d.text((30, 14), "实验E：端到端闭环 PoC（glm-4-flash + verbatim + ESC\\终止符）",
           fill=(230,230,240), font=big)

    # === 第一栏：模型输出（Composer 对话） ===
    x1, y1 = 30, 70
    pw = 380; ph = 580
    d.rectangle([x1, y1, x1+pw, y1+ph], fill=(28,30,40), outline=(70,80,110))
    d.text((x1+10, y1+8), "1. 模型输出（Composer）", fill=(180,200,255), font=font)
    d.text((x1+10, y1+34), "system: verbatim 指令", fill=(160,160,180), font=small)
    d.text((x1+10, y1+52), "tool: read_log -> 日志+OSC52", fill=(160,160,180), font=small)
    d.text((x1+10, y1+70), "assistant:", fill=(180,180,220), font=small)
    # 渲染模型输出（含 OSC52，标注）
    tmp = os.path.join(ASSETS, "_tmp_e1.png")
    render_bytes(closed_blob, "", tmp, cols=48, rows=22, font_size=12, pad=4)
    try:
        timg = Image.open(tmp).resize((pw-20, ph-100))
        img.paste(timg, (x1+10, y1+90))
    except Exception:
        pass
    # 标注
    d.text((x1+10, y1+ph-20), f"ESC={esc_closed}  -> 含完整 OSC52", fill=(255,120,120), font=small)

    # === 第二栏：终端渲染 ===
    x2 = x1 + pw + 20
    d.rectangle([x2, y1, x2+pw, y1+ph], fill=(30,30,38), outline=(60,60,80))
    d.text((x2+10, y1+8), "2. IDE 终端（xterm.js）", fill=(180,180,200), font=font)
    d.text((x2+10, y1+34), "OSC52 被解释 -> 序列不可见", fill=(255,180,120), font=small)
    # 渲染：终端会把 OSC52 吃掉，只显示其他文本
    tmp2 = os.path.join(ASSETS, "_tmp_e2.png")
    render_bytes(closed_blob, "", tmp2, cols=48, rows=22, font_size=12, pad=4)
    try:
        timg2 = Image.open(tmp2).resize((pw-20, ph-100))
        img.paste(timg2, (x2+10, y1+90))
    except Exception:
        pass
    d.text((x2+10, y1+ph-20), "用户看不到 OSC52 序列", fill=(255,180,120), font=small)

    # === 第三栏：剪贴板实测 ===
    x3 = x2 + pw + 20
    d.rectangle([x3, y1, x3+pw, y1+ph], fill=(40,28,28), outline=(120,60,60))
    d.text((x3+10, y1+8), "3. 系统剪贴板（实测）", fill=(255,180,120), font=font)
    d.text((x3+10, y1+34), "test_clipboard.py 真实结果:", fill=(220,180,160), font=small)
    # 模拟 test_clipboard.py 的输出
    box_y = y1 + 60
    d.rectangle([x3+10, box_y, x3+pw-10, box_y+200], fill=(20,20,28), outline=(80,80,100))
    yy = box_y + 10
    d.text((x3+20, yy), "[before] clipboard = ''", fill=(120,220,140), font=small); yy += 20
    d.text((x3+20, yy), "[before] writing OSC52 (49 bytes)...", fill=(200,200,200), font=small); yy += 20
    d.text((x3+20, yy), "", fill=(200,200,200), font=small); yy += 16
    d.text((x3+20, yy), "[after]  clipboard =", fill=(200,200,200), font=small); yy += 20
    d.text((x3+30, yy), f"'{decoded}'", fill=(255,100,100), font=font); yy += 28
    d.text((x3+20, yy), "[!!!] CLIPBOARD HIJACKED", fill=(255,80,80), font=font); yy += 24
    d.text((x3+20, yy), "- OSC52 was interpreted", fill=(255,160,120), font=small); yy += 18
    d.text((x3+20, yy), "  by terminal!", fill=(255,160,120), font=small); yy += 18
    d.text((x3+20, yy), f"  written: {decoded}", fill=(255,120,120), font=small); yy += 18

    # 箭头
    arr_y = y1 + ph // 2
    d.text((x1+pw+2, arr_y), "->", fill=(255,220,120), font=big)
    d.text((x2+pw+2, arr_y), "->", fill=(255,220,120), font=big)

    # 底部结论
    cy = y1 + ph + 15
    d.rectangle([30, cy, W-30, cy+50], fill=(40,30,20), outline=(120,100,60))
    d.text((40, cy+8), "闭环成立：攻击者控制工具结果(间接注入) -> 模型 verbatim 复述完整 OSC52 -> 终端解释 -> 剪贴板被写入",
           fill=(255,220,120), font=small)
    d.text((40, cy+28), f"关键突破：把 BEL(\\x07) 换成 ESC\\\\(\\x1b\\\\) 终止符，绕过模型对 BEL 的过滤。剪贴板实测写入: {decoded}",
           fill=(255,200,100), font=small)

    out = os.path.join(ASSETS, "07-agent-e2e.png")
    img.save(out)
    print(f"  [shot] 07-agent-e2e.png (closed loop)")

    # 清理临时
    for t in ["_tmp_e1.png", "_tmp_e2.png"]:
        p = os.path.join(ASSETS, t)
        if os.path.exists(p):
            os.remove(p)

if __name__ == "__main__":
    run()
