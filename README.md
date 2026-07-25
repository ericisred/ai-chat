# AI Chat

> 一个基于 Python + 多 LLM Provider 架构与 SQLite 对话持久化的终端命令行 AI 助手。

本项目采用**策略模式（Strategy Pattern）与工厂模式（Factory Pattern）**设计，实现业务层与 LLM SDK 的彻底解耦；同时引入全新的 **`memory/` 内存与持久化模块**，基于 SQLite 实现了优雅的对话持久化落盘与会话恢复。

---

## ✨ Features

- 🧠 **滚动摘要记忆系统 (Rolling Summary Memory)**：引入“长期摘要 + 短期明细”双层记忆架构。当对话超长时自动生成增量摘要并注入 System Instruction，既控制 Token 成本，又使早期重要记忆永不遗忘。
- ⚡ **历史会话 0 秒秒开加载**：恢复历史会话时直接复用已落盘的 `summary` 并加载近期明细，跳过耗时的重复 API 摘要计算，瞬间响应。
- 🛡 **应用层网络超时与防 Crash 保护**：配置 60 秒 API 连接超时，并在 CLI 对话循环中优雅捕获网络异常（`APITimeoutError`），消除网络波动导致的程序崩溃。
- 🔧 **Gemini SDK 内部流式历史修复**：修补 `google-genai` SDK 在 `send_message_stream` 时因尾部 Chunk 校验导致历史未落盘的官方 Bug。
- 💾 **SQLite 对话与摘要持久化**：基于 `sqlite3` 实现 `sessions` (含 `summary` 记忆摘要) 和 `messages` 落盘，支持会话恢复与记忆断点续聊。
- 🛡 **Lazy Session 惰性会话创建**：避免首次请求异常产生垃圾数据，只有首轮问答成功才延迟落地数据库。
- 🏗 **多 LLM Provider 插件化架构**：面向接口编程（`BaseChatProvider`），通过 `LLMProviderFactory` 实现无缝切换模型（Provider 完全与数据库解耦）。
- 🤖 **多大模型支持**：
  - **DeepSeek**（基于 OpenAI 规范协议 + 增量摘要生成）
  - **Google Gemini**（基于官方 `google-genai` SDK + 增量摘要生成）
- ⚡ **打字机流式输出 (Streaming)**：统一封装生成器，Token 实时打字显示。
- 📜 **工业级 Logging 日志管理**：监控 API 耗时、首包延迟 (TTFT)、字符数与错误堆栈，支持 `RotatingFileHandler` 自动滚动归档。
- 🎯 **结构化 System Prompt**：遵照 Role + Task + Constraints + Output Format 四要素工程规范重构提示词，支持动态拼接 Memory Summary。
- 🛡 **交互与配置解耦**：快捷键 `Ctrl+C` / `Ctrl+D` 优雅退出，按需校验 `.env` 配置。

---

## 🛠 Tech Stack

- Python 3.9+
- SQLite3 (Python 内置)
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
│   ├── main.py              # CLI 入口（网络异常防护、防 Crash 捕获与选单交互）
│   ├── config.py            # 环境变量、防错校验与数据库路径
│   ├── logger.py            # 工业级 Logging 日志模块
│   ├── prompts.py           # 结构化 System Prompt 及动态 Summary 构建
│   │
│   ├── memory/              # 对话内存与 SQLite 持久化模块
│   │   ├── __init__.py      # 包导出与模块初始化
│   │   ├── storage.py       # SQLite 底层 DAO (支持 summary 读写)
│   │   └── manager.py       # 会话与内存管理业务服务 (MemoryManager)
│   │
│   └── llm/                 # 多 LLM Provider 策略封装包
│       ├── __init__.py      # 包导出与模块初始化
│       ├── base.py          # LLM 抽象基类 (BaseChatProvider 接口)
│       ├── deepseek.py      # DeepSeek Provider (超时配置 + 滚动摘要 + 0秒秒开)
│       ├── gemini.py        # Gemini Provider (google-genai SDK 修复 + 0秒秒开)
│       └── factory.py       # LLM 提供者工厂类 (LLMProviderFactory)
│
├── data/                    # [NEW] SQLite 数据库目录 (ai-chat.db，Git 忽略)
├── logs/                    # 自动日志目录 (ai-chat.log，Git 忽略)
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

# 安装依赖
pip install -r requirements.txt
```

---

## 2. Configure Environment Variables

在根目录下创建 `.env` 文件：

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

终端选单与运行效果：

```text
🤖 DeepSeek Chat (deepseek-v4-flash) 已启动
💡 输入 'exit' 退出

==================================================
📋 会话选单：
  [0] 开启新对话 (默认)
  [1] 恢复历史: 我叫 Eric (2026-07-24 16:30) [DeepSeek]
  [2] 恢复历史: 什么是 RAG (2026-07-24 15:10) [DeepSeek]
==================================================
请选择 [0-5] (直接回车默认开启新对话): 1

🔄 已成功恢复历史会话: [我叫 Eric] (共 4 条历史记录)

你: 记不记得我是谁？
DeepSeek: 当然记得，你是 Eric！
--------------------------------------------------
```

---

# 📖 Architecture Flow

```text
                               app/main.py (业务层)
                                     │
           ┌─────────────────────────┴─────────────────────────┐
           ▼                                                   ▼
 LLMProviderFactory (工厂)                           MemoryManager (内存服务)
           │                                                   │
 ┌─────────┴─────────┐                                ┌────────┴────────┐
 ▼                   ▼                                ▼                 ▼
DeepSeekProvider  GeminiProvider                 load_history     SQLiteStorage
 (OpenAI 协议)  (google-genai)                       │             (data/ai-chat.db)
 │                   │                               ▼                 │
 └─────────┬─────────┘                       滑动窗口裁剪 (Context Window)
           ▼                                                           │
 BaseChatProvider (抽象基类) ◄─────────────────────────────────────────┘
```

---

# 🔑 Environment Variables

| 变量名 | 说明 | 可选值 / 默认值 |
|------|-------------|-------|
| `LLM_PROVIDER` | 当前激活的大模型提供商 | `deepseek` (默认) / `gemini` |
| `SUMMARY_TRIGGER_TURNS` | 触发滚动摘要压缩的对话轮数阈值 | `10` (默认) |
| `RECENT_KEEP_TURNS` | 滚动摘要压缩后保留的最近对话明细轮数 | `5` (默认) |
| `DEEPSEEK_API_KEY` | DeepSeek 开放平台 Key | 无 (当激活 deepseek 时必需) |
| `DEEPSEEK_BASE_URL` | DeepSeek API 地址 | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | DeepSeek 模型名称 | `deepseek-v4-flash` |
| `GEMINI_API_KEY` | Google Gemini API Key | 无 (当激活 gemini 时必需) |
| `GEMINI_MODEL` | Gemini 模型名称 | `gemini-2.5-flash` |

---

# 📚 Learning Goals

本项目涵盖的核心工程技能：

- [x] 滚动摘要双层记忆架构设计与增量 Summarization Prompt 工程
- [x] 历史会话 0 秒秒开恢复与缓冲步长防重复计算机制
- [x] 应用层网络超时防护 (`timeout=60.0`) 与防 Crash 捕获
- [x] 修复 `google-genai` SDK 官方流式历史未落盘 Bug
- [x] SQLite3 关系型数据库 schema 动态升级与 CRUD 封装
- [x] 解耦的 Memory / Storage 架构设计与 Lazy Session 防僵尸数据策略
- [x] 抽象工厂与策略模式在 AI 多模型架构中的落地
- [x] 面向接口编程，实现业务层与底层 LLM SDK 彻底解耦
- [x] 工业级 Logging 日志模块（TTFT 首包耗时监控、滚动日志）
- [x] 结构化 System Prompt 设计 (Role+Task+Constraints+Output) 及记忆融合

---

# 🗺 Roadmap

当前版本：
- ✅ 应用层网络超时防护与防 Crash 捕获异常处理
- ✅ 历史会话 0 秒秒开恢复与缓冲步长机制
- ✅ 滚动摘要记忆系统 (Rolling Summary Memory) 实现与动态 System Instruction 拼接
- ✅ Gemini Provider 底层 `google-genai` SDK 流式历史 BUG 修复
- ✅ SQLite 数据库 `sessions` 表支持 `summary` 字段持久化与载入
- ✅ 聊天历史记录本地持久化（SQLite3 / MemoryManager / Lazy Session）
- ✅ 多 LLM Provider 架构重构（支持 DeepSeek / Gemini 一键切换）
- ✅ LLMProviderFactory 工厂模式与 BaseChatProvider 接口规范
- ✅ 多轮上下文记忆与流式打字响应
- ✅ Logging 日志模块（TTFT 监控、耗时统计、滚动文件日志）

下一步计划：
- ⏳ 支持 R1 思考链 (Reasoning Content) 显示
- ⏳ Web UI 界面（Streamlit / Gradio）
- ⏳ FastAPI 后端接口封装

---

# 📝 Version History

## v0.8 (Current)
- **滚动摘要记忆系统 (Rolling Summary Memory)**：实现“长期摘要 + 短期明细”双层记忆架构，彻底解决多轮长对话 Token 暴涨与硬裁剪丢记忆的困境。
- ** Gemini SDK 流式 Bug 修复**：修补 `google-genai` SDK 在 `send_message_stream` 下由于尾部 Chunk 校验导致 `_curated_history` 缺失的官方 BUG。
- **⚡ 历史会话 0 秒秒开加载与缓冲防护**：恢复带 `summary` 的历史会话时直接继承摘要实现秒开；配置防御性校验与 5 轮缓冲步长，消除频繁重复触发摘要。
- **🛡 网络超时与防 Crash 保护**：配置 `timeout=60.0` 秒连接超时，并在对话循环中捕获网络异常 (`APITimeoutError`)，消除网络波动导致的程序崩溃。

## v0.7
- 引入全新的 `app/memory/` 持久化模块，基于 SQLite3 实现 `sessions` 和 `messages` 数据落盘。
- 支持启动时通过选单恢复历史会话，恢复时自动结合 `MAX_HISTORY_TURNS` 实施滑动窗口裁切。
- 引入 Lazy Session 机制，防止首轮提问异常在数据库产生僵尸垃圾数据。
- 在 `BaseChatProvider` 中增加 `load_history` 契约，维持 Provider 的完全解耦。

## v0.6
- 引入滑动窗口上下文裁剪机制 (Context Truncation)，支持通过 `MAX_HISTORY_TURNS` 控制记忆上限。

## v0.5 / v0.4 / v0.3 / v0.2 / v0.1
- 多 LLM Provider 架构重构、Logging 模块、DeepSeek/Gemini 接入与基础迭代。

---

# 🤝 License

MIT License

---

# 👨‍💻 Author

**Eric**  
AI Learning Journey (2026)