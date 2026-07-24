# AI Chat

> 一个基于 Python + 多 LLM Provider 架构的终端命令行 AI 对话助手。

本项目采用**策略模式（Strategy Pattern）与工厂模式（Factory Pattern）**设计，使业务逻辑与底层模型 API 彻底解耦。支持一键无缝切换 DeepSeek、Google Gemini 等多个大语言模型，并内建滑动窗口上下文裁剪与日志监控。

---

## ✨ Features

- 🏗 **多 LLM Provider 插件化架构**：面向接口编程（`BaseChatProvider`），通过 `LLMProviderFactory` 实现无缝切换模型。
- 🤖 **多大模型支持**：
  - **DeepSeek**（基于 OpenAI 规范协议）
  - **Google Gemini**（基于官方 `google-genai` SDK，内建流式 Chunk 格式修补）
- ✂️ **滑动窗口上下文裁剪 (Context Truncation)**：支持配置 `MAX_HISTORY_TURNS`，自动裁剪过旧对话，防止 Token 溢出并大幅节省 API 成本，同时永久锁定首位 System Prompt。
- ⚡ **打字机流式输出 (Streaming)**：统一封装生成器，Token 实时打字显示。
- 📜 **工业级 Logging 日志管理**：监控 API 耗时、首包延迟 (TTFT)、字符数与错误堆栈，支持 `RotatingFileHandler` 自动滚动归档。
- 🎯 **结构化 System Prompt**：遵照 Role + Task + Constraints + Output Format 四要素工程规范重构提示词。
- 💬 **标准多轮对话 (Conversation Memory)**：支持各模型下的完整上下文记忆。
- 🛡 **交互与配置解耦**：快捷键 `Ctrl+C` / `Ctrl+D` 优雅退出，按需校验 `.env` 配置。

---

## 🛠 Tech Stack

- Python 3.9+
- OpenAI SDK (`openai>=1.0.0`)
- Google GenAI SDK (`google-genai>=1.0.0`)
- `python-dotenv`
- Git

---

## 📂 Project Structure

```text
ai-chat
│
├── app
│   ├── main.py              # CLI 入口（面向接口编程，彻底解耦具体 SDK）
│   ├── config.py            # 多 Provider 环境变量、裁剪轮数与配置校验中心
│   ├── logger.py            # 工业级 Logging 日志模块
│   ├── prompts.py           # 结构化 System Prompt 配置
│   │
│   └── llm/                 # 多 LLM Provider 策略封装包
│       ├── __init__.py      # 包导出与模块初始化
│       ├── base.py          # LLM 抽象基类 (BaseChatProvider)
│       ├── deepseek.py      # DeepSeek Provider (OpenAI 协议 + 消息裁剪)
│       ├── gemini.py        # Gemini Provider (google-genai SDK + 历史裁剪)
│       └── factory.py       # LLM 提供者工厂类 (LLMProviderFactory)
│
├── logs/                    # 自动日志目录 (Git 忽略)
│   └── ai-chat.log
├── .env                     # 本地 API Key 与模型配置文件 (Git 忽略)
├── .gitignore
├── requirements.txt         # 依赖包列表
└── README.md
```

---

# 🚀 Quick Start

## 1. Clone Project & Install Dependencies

```bash
git clone https://github.com/yourname/ai-chat.git
cd ai-chat

# 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装全套 Provider 依赖
pip install -r requirements.txt
```

---

## 2. Configure Environment Variables

在根目录下创建 `.env` 文件，根据需求配置要使用的 LLM 与最大保留对话轮数：

```env
# 选择激活的模型提供商: "deepseek" 或 "gemini"
LLM_PROVIDER=deepseek

# 最大保留历史对话轮数 (1 轮 = 1 问 + 1 答，默认 10 轮)
MAX_HISTORY_TURNS=10

# DeepSeek 配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash

# Gemini 配置
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

---

## 3. Run App

```bash
python app/main.py
```

终端运行效果：

```text
🤖 DeepSeek Chat (deepseek-v4-flash) 已启动
💡 输入 'exit' 退出

你: 什么是 RAG？
DeepSeek: 💡 直观理解
...
--------------------------------------------------
```

---

# 📖 Architecture Flow

```text
                               app/main.py (业务层)
                                     │
                                     ▼
                          LLMProviderFactory (工厂)
                                     │
               ┌─────────────────────┴─────────────────────┐
               ▼                                           ▼
       DeepSeekProvider                            GeminiProvider
   (滑动窗口裁剪 Context)                    (滑动窗口裁剪 History)
               │                                           │
               └─────────────────────┬─────────────────────┘
                                     ▼
                           BaseChatProvider (抽象基类)
                                     │
                         ┌───────────┴───────────┐
                         ▼                       ▼
                   logger.py (性能/错误日志)  Terminal (流式打字输出)
```

---

# 🔑 Environment Variables

| 变量名 | 说明 | 可选值 / 默认值 |
|------|-------------|-------|
| `LLM_PROVIDER` | 当前激活的大模型提供商 | `deepseek` (默认) / `gemini` |
| `MAX_HISTORY_TURNS` | 最长历史记忆保留轮数 | `10` (默认) |
| `DEEPSEEK_API_KEY` | DeepSeek 开放平台 Key | 无 (当激活 deepseek 时必需) |
| `DEEPSEEK_BASE_URL` | DeepSeek API 地址 | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | DeepSeek 模型名称 | `deepseek-v4-flash` |
| `GEMINI_API_KEY` | Google Gemini API Key | 无 (当激活 gemini 时必需) |
| `GEMINI_MODEL` | Gemini 模型名称 | `gemini-2.5-flash` |

---

# 📚 Learning Goals

本项目涵盖的核心工程技能：

- [x] 抽象工厂与策略模式在 AI 多模型架构中的落地
- [x] 上下文历史滑动窗口裁剪算法 (Context Truncation)
- [x] 面向接口编程，实现业务层与底层 LLM SDK 彻底解耦
- [x] OpenAI 兼容协议与 Google GenAI 双 SDK 接入
- [x] 工业级 Logging 日志模块（TTFT 首包耗时监控、滚动日志）
- [x] 结构化 System Prompt 设计 (Role+Task+Constraints+Output)
- [x] 多模型流式输出 (Streaming) 与历史 Chunk 合并修复

---

# 🗺 Roadmap

当前版本：
- ✅ 多 LLM Provider 架构重构（支持 DeepSeek / Gemini 一键切换）
- ✅ 上下文历史滑动窗口裁剪 (`MAX_HISTORY_TURNS`)
- ✅ LLMProviderFactory 工厂模式与 BaseChatProvider 接口规范
- ✅ 多轮上下文记忆与流式打字响应
- ✅ 结构化 System Prompt 定制
- ✅ Logging 日志模块（TTFT 监控、耗时统计、滚动文件日志）

下一步计划：
- ⏳ 聊天历史记录本地持久化（SQLite / JSON）
- ⏳ 支持 R1 思考链 (Reasoning Content) 显示
- ⏳ Web UI 界面（Streamlit / Gradio）
- ⏳ FastAPI 后端接口封装

---

# 📝 Version History

## v0.6 (Current)
- 引入滑动窗口上下文裁剪机制 (Context Truncation)，支持通过 `MAX_HISTORY_TURNS` 控制记忆上限。
- 保护首位 System Prompt 不受裁剪影响，自动切片过期历史，防止 Token 溢出并大幅节省 API 费用。

## v0.5
- 重构为多 LLM Provider 架构，新增 `app/llm/` 模块包。
- 实现 `BaseChatProvider` 抽象基类与 `LLMProviderFactory` 工厂类。
- 拆分 `DeepSeekProvider` 与 `GeminiProvider` 独立策略实现。

## v0.4
- 引入 Logging 日志模块，支持自动记录请求耗时、首包延迟 (TTFT) 与错误堆栈。
- 重构 `app/prompts.py` 结构化提示词。

## v0.3 / v0.2 / v0.1
- 基础功能迭代与架构优化。

---

# 🤝 License

MIT License

---

# 👨‍💻 Author

**Eric**  
AI Learning Journey (2026)