"""实验C：OSC 8 钓鱼链接 - 生成 payload 截图。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render.render_ansi import render_bytes

LAB = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(LAB, "assets", "terminal-escape")
os.makedirs(ASSETS, exist_ok=True)

def osc8(text, url):
    return f"\x1b]8;;{url}\x1b\\{text}\x1b]8;;\x1b\\".encode("utf-8")

def run():
    print("[C] OSC 8 phishing link")
    payload = (b"[INFO] build succeeded, see report: "
               + osc8("查看官方文档", "https://evil.tld/docs")
               + b"\n")
    with open(os.path.join(ASSETS, "05-osc8-payload.bin"), "wb") as f:
        f.write(payload)
    render_bytes(payload, "实验C：OSC 8 钓鱼链接（下划线=可点击）",
                 os.path.join(ASSETS, "05-osc8-payload.png"),
                 cols=72, rows=6)
    print("  [shot] 05-osc8-payload.png")
    print()

if __name__ == "__main__":
    run()
