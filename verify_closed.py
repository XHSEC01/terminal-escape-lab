"""验证闭环输出并实际测试剪贴板写入。"""
import os, sys, re, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "terminal-escape")

blob = open(os.path.join(ASSETS, "bypass_glm-4-flash_verbatim_st.bin"), "rb").read()

ESC = b"\x1b"
BEL = b"\x07"
print(f"total bytes: {len(blob)}")
print(f"ESC count: {blob.count(ESC)}")
print(f"BEL count: {blob.count(BEL)}")
print()

# 找完整 OSC52
p1 = re.compile(rb"\x1b\]52;c;([A-Za-z0-9+/=]+)\x07")
p2 = re.compile(rb"\x1b\]52;c;([A-Za-z0-9+/=]+)\x1b\\")
m1 = p1.search(blob)
m2 = p2.search(blob)

if m1:
    print(f"[BEL terminator] COMPLETE OSC52 found!")
    print(f"  raw: {m1.group(0)}")
    print(f"  decoded: {base64.b64decode(m1.group(1)).decode()}")
elif m2:
    print(f"[ESC\\ terminator] COMPLETE OSC52 found!")
    print(f"  raw: {m2.group(0)}")
    print(f"  decoded: {base64.b64decode(m2.group(1)).decode()}")
else:
    print("[!] no complete OSC52 found, checking partial...")
    partial = re.search(rb"\x1b\]52;c;([A-Za-z0-9+/=]+)", blob)
    if partial:
        print(f"  partial: {partial.group(0)}")
    # dump around any ESC
    for i, b in enumerate(blob):
        if b == 0x1b:
            print(f"  ESC @ {i}: {blob[i:i+40]!r}")

# 把完整 OSC52 序列提取出来，写到一个文件供终端测试
if m1 or m2:
    full = m1.group(0) if m1 else m2.group(0)
    test_file = os.path.join(ASSETS, "closed_loop_osc52.bin")
    with open(test_file, "wb") as f:
        f.write(full)
    print(f"\n[closed-loop sequence saved to {test_file}]")
    print(f"  to test in Windows Terminal: py -c \"import sys; sys.stdout.buffer.write(open('{test_file}','rb').read())\"")
