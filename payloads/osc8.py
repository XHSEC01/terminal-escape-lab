"""实验 C：OSC 8 钓鱼链接 payload 生成。

输出一段 OSC 8 序列，终端会把指定文本渲染成指向 URL 的可点击超链接，
URL 本身不在可见区域显示。
"""
import sys

def osc8(text: str, url: str) -> bytes:
    return f"\x1b]8;;{url}\x1b\\{text}\x1b]8;;\x1b\\".encode("utf-8")

if __name__ == "__main__":
    payload = osc8("查看官方文档", "https://evil.tld/docs")
    cover = b"[INFO] build succeeded, see report: "
    sys.stdout.buffer.write(cover + payload + b"\n")
