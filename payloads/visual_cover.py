"""实验 D：视觉覆盖欺骗。

先打印"安全命令"，再用光标上移 + 擦除把视觉替换成"危险命令"。
屏幕上用户看到的是 rm -rf ~/，scrollback 里第一行还是 echo safe command。
"""
import sys

payload = (
    b"echo safe command\n"
    b"\x1b[2A"      # 光标上移 2 行
    b"\x1b[2K"      # 擦除当前行
    b"rm -rf ~/\n"
)
sys.stdout.buffer.write(payload)
