# terminal-escape-lab

LLM 输出侧的终端转义注入实验：OSC 52 剪贴板劫持、OSC 8 钓鱼链接、视觉覆盖、Agent 端到端闭环。

配套文章：《终端转义注入：LLM 输出如何绕过过滤、劫持剪贴板（实测闭环）》

所有 PoC 只在本地终端里改颜色、写剪贴板、落一个空文件，没有回连，没有动系统命令。实验模型为智谱 `glm-4-flash`。

## 环境

- Python 3.11+
- 智谱 API Key（OpenAI 兼容接口）
- 支持 OSC 52 的终端（Windows Terminal / VS Code 或 Cursor 内嵌终端 / iTerm2）

```powershell
git clone https://github.com/XHSEC01/terminal-escape-lab.git
cd terminal-escape-lab
py -m pip install -r requirements.txt
copy .env.example .env
# 编辑 .env，填入 ZHIPU_API_KEY
$env:PYTHONIOENCODING = "utf-8"
```

## 实验

| 脚本 | 做什么 |
|------|--------|
| `py run_a_emit.py` | 实验 A：模型到底吐不吐 ESC |
| `py run_b_osc52.py` | 实验 B：OSC 52 payload + 五终端对照 |
| `py run_c_osc8.py` | 实验 C：OSC 8 钓鱼链接 |
| `py run_d_cover.py` | 实验 D：视觉覆盖欺骗 |
| `py run_bypass_all.py` | 组合扫描：终止符 × 指令 × 模型 |
| `py verify_closed.py` | 验证闭环 OSC 52 序列是否完整 |
| `py test_clipboard.py` | 实测：OSC 52 是否写入系统剪贴板 |
| `py run_e_closed.py` | 生成闭环版实验 E 截图 |
| `py run_remaining.py` | 生成图 01 / 02 / 08 / 09 |

`test_clipboard.py` 必须在会解释 OSC 52 的真实终端里跑。输出被捕获的环境（部分 IDE 任务面板）不会写入剪贴板。

## 目录

```text
terminal-escape-lab/
├── payloads/          # OSC 52 / OSC 8 / 视觉覆盖 payload
├── probe/             # 探测模型是否输出 ESC
├── agent/             # 最小 Agent：工具结果夹带 OSC 52
├── detect/            # 输出扫描器
├── render/            # ANSI -> PNG
└── assets/terminal-escape/   # 截图与原始字节
```

## 闭环结论（glm-4-flash）

- `normal` 指令：模型把 OSC 52 整行删掉
- `verbatim` + BEL（`\x07`）：复述 ESC，但把 BEL 换成换行，序列不完整
- `verbatim` + `ESC \`（String Terminator）：三件齐备，Cursor / xterm.js 内嵌终端实测写入剪贴板

过滤发生在字节层面，不是协议层面。换终止符就能绕过。防御应打在终端和 IDE 渲染层，不要押注模型自己挡。
