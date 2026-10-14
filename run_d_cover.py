"""实验D：视觉覆盖欺骗 - 生成两张截图（当前显示 + scrollback）。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render.render_ansi import render_bytes

LAB = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(LAB, "assets", "terminal-escape")
os.makedirs(ASSETS, exist_ok=True)

def run():
    print("[D] visual cover deception")
    # 当前屏幕：光标上移+擦除后，用户看到 rm -rf ~/
    payload = (b"echo safe command\n"
               b"\x1b[2A\x1b[2K"
               b"rm -rf ~/\n")
    with open(os.path.join(ASSETS, "06-visual-cover-after.bin"), "wb") as f:
        f.write(payload)
    render_bytes(payload, "实验D：视觉覆盖欺骗（终端当前显示 rm -rf ~/）",
                 os.path.join(ASSETS, "06-visual-cover-after.png"),
                 cols=60, rows=8)
    print("  [shot] 06-visual-cover-after.png")

    # scrollback 视角
    scrollback = (
        "# === tmux scrollback (上翻历史) ===\n"
        "echo safe command   <- 原始第一行仍在历史\n"
        "rm -rf ~/           <- 当前屏幕显示\n"
    ).encode("utf-8")
    render_bytes(scrollback, "实验D：scrollback 视角（原始 echo safe command 仍在历史）",
                 os.path.join(ASSETS, "06-visual-cover-scrollback.png"),
                 cols=70, rows=6)
    print("  [shot] 06-visual-cover-scrollback.png")
    print()

if __name__ == "__main__":
    run()
