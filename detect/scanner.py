"""LLM 输出扫描器。吃 stdin 字节流，报控制字符位置和类型。"""
import re, sys, base64

C0 = re.compile(rb"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
CSI = re.compile(rb"\x1b\[[0-9;?]*[ -/]*[@-~]")
OSC = re.compile(rb"\x1b\][0-9]+(?:;[^\x07\x1b]*)*(?:\x07|\x1b\\)")
OSC52 = re.compile(rb"\x1b\]52;([a-zA-Z0-9]*);([A-Za-z0-9+/=]+)(?:\x07|\x1b\\)")
OSC8 = re.compile(rb"\x1b\]8;;([^\x1b\x07]*)\x1b\\([^\x1b]*)\x1b\]8;;\x1b\\")
ZWB = re.compile(b"[\xe2\x80\x8b-\xe2\x80\x8f\xe2\x81\xa6-\xe2\x81\xa9]")

def scan(blob: bytes):
    findings = []
    for m in OSC52.finditer(blob):
        clip, b64 = m.group(1), m.group(2)
        try:
            decoded = base64.b64decode(b64)
            findings.append(("OSC52_CLIPBOARD", m.start(), decoded))
        except Exception:
            findings.append(("OSC52_MALFORMED", m.start(), b64))
    for m in OSC8.finditer(blob):
        findings.append(("OSC8_LINK", m.start(), m.group(1)))
    for m in CSI.finditer(blob):
        findings.append(("CSI", m.start(), m.group(0)))
    for m in OSC.finditer(blob):
        if not OSC52.match(m.group(0)) and not OSC8.match(m.group(0)):
            findings.append(("OSC_OTHER", m.start(), m.group(0)))
    for m in C0.finditer(blob):
        findings.append(("C0", m.start(), m.group(0)))
    for m in ZWB.finditer(blob):
        findings.append(("ZERO_WIDTH", m.start(), m.group(0)))
    return findings

if __name__ == "__main__":
    blob = sys.stdin.buffer.read()
    if not blob:
        print("[scanner] empty input")
        sys.exit(0)
    findings = scan(blob)
    if not findings:
        print("[scanner] clean - no control sequences found")
    for kind, pos, payload in findings:
        print(f"{kind}\t@{pos}\t{payload!r}")
