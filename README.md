# AI Chat

> 一个基于 DeepSeek API (OpenAI 协议) 的终端命令行 AI 对话助手。

这是我 AI 工程学习路线中的项目，用于学习大语言模型（LLM）API 调用、OpenAI 标准协议接入、System Prompt 设置、上下文管理以及流式打字输出（Streaming）。

---

## ✨ Features

- 🤖 **DeepSeek API 接入**：基于官方推荐的 OpenAI SDK，兼容性强、稳定高质。
- ⚡ **流式打字响应（Streaming）**：回答按 Token 实时打字输出，提升终端交互体验。
- 🎯 **System Prompt 定制**：独立封装系统提示词，支持设定 AI 角色定位（如乐叔 AI 助手）。
- 💬 **标准多轮对话（Conversation Memory）**：基于 OpenAI 标准 `messages` 数组高效维系多轮上下文。
- 🛡 **健壮的交互与异常处理**：支持 `Ctrl+C` / `Ctrl+D` 优雅退出与极佳的异常反馈。
- 🔐 **环境配置解耦**：使用 `python-dotenv` 管理 `API_KEY` 与模型参数。
- 🏗 **模块化设计**：入口、配置、提示词与 API 调用彻底解耦，结构清晰。

---

## 🛠 Tech Stack

- Python 3.9+
- DeepSeek API / OpenAI SDK (`openai>=1.0.0`)
- `python-dotenv`
- Git

---

## 📂 Project Structure

```text
ai-chat
│
├── app
│   ├── main.py          # 终端交互与程序入口
│   ├── chat.py          # DeepSeek / OpenAI 调用与会话管理
│   ├── config.py        # 环境变量与 API 配置加载
│   └── prompts.py       # 系统提示词 (System Prompt)
│
├── .env                 # 本地 API Key 与配置文件 (Git 忽略)
├── .gitignore
├── requirements.txt     # 项目依赖包列表
└── README.md
```

---

# 🚀 Quick Start

## 1. Clone Project

```bash
git clone https://github.com/yourname/ai-chat.git
cd ai-chat
```

---

## 2. Create & Activate Virtual Environment

创建虚拟环境：

```bash
python3 -m venv .venv
```

激活虚拟环境：
- **Mac / Linux**：
  ```bash
  source .venv/bin/activate
  ```
- **Windows**：
  ```bash
  .venv\Scripts\activate
  ```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

在项目根目录下创建 `.env` 文件，内容如下：

```text
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
MODEL_NAME=deepseek-v4-flash
```

> ⚠️ **注意**：请务必将 `.env` 添加到 `.gitignore`，切勿提交真实的 API Key 到 GitHub。

---

## 5. Run App

```bash
python app/main.py
```

终端运行效果：

```text
🤖 DeepSeek Chat 已启动
💡 输入 'exit' 退出

你: 你好
DeepSeek: 你好！我是乐叔 AI 助手。很高兴认识你，今天有什么我可以帮你的吗？
--------------------------------------------------
```

---

# 💬 Conversation Example

```text
你: 我叫 Eric，我正在学习 Python 开发 AI 应用。
DeepSeek: 你好，Eric！欢迎来到 Python 与 AI 开发的世界...

你: 记不记得我是谁？
DeepSeek: 当然记得，你是 Eric！刚才你告诉我你正在学习 Python 开发 AI 应用呢。
```

---

# 📖 Architecture Flow

```text
           用户输入 (Terminal)
                  │
                  ▼
             app/main.py
                  │
                  ▼
             app/chat.py  <─── app/prompts.py & app/config.py
                  │
                  ▼
       DeepSeek API (OpenAI SDK)
                  │
                  ▼
      Streaming Tokens Output
                  │
                  ▼
           终端打字机实时显示
```

---

# 🔑 Environment Variables

| 变量名 | 说明 | 默认值 |
|------|-------------|-------|
| `DEEPSEEK_API_KEY` | DeepSeek 开放平台 API Key | 无 (必需) |
| `DEEPSEEK_BASE_URL` | DeepSeek 服务 Base URL | `https://api.deepseek.com` |
| `MODEL_NAME` | 调用的模型名称 (`deepseek-v4-flash` / `deepseek-v4-pro`) | `deepseek-v4-flash` |

---

# 📚 Learning Goals

本项目涵盖的核心工程技能：

- [x] Python 虚拟环境与标准包管理
- [x] OpenAI 兼容协议接入与调试
- [x] DeepSeek 大模型流式输出 (Streaming)
- [x] System Prompt 设计与注入
- [x] 多轮上下文 Memory 管理
- [x] 配置解耦与敏感信息保护 (`.env`)
- [x] 交互终端健壮性与异常捕获

---

# 🗺 Roadmap

当前版本：
- ✅ DeepSeek API (OpenAI SDK) 接入
- ✅ 多轮上下文记忆
- ✅ Streaming 打字机实时流式响应
- ✅ System Prompt 定制（乐叔 AI 助手）
- ✅ `Ctrl+C` / `Ctrl+D` 优雅中断与退出处理

下一步计划：
- ⏳ Logging 日志模块
- ⏳ 聊天历史记录本地持久化（SQLite / JSON）
- ⏳ 支持 R1 思考链 (Reasoning Content) 显示
- ⏳ Web UI 界面（Streamlit / Gradio）
- ⏳ FastAPI 后端接口封装

---

# 📝 Version History

## v0.3 (Current)
- 从 Google Gemini 迁移至 DeepSeek API (OpenAI 协议)。
- 新增独立的 `app/prompts.py` 管理 System Prompt。
- 增加控制台打字机流式输出 (Streaming)。
- 修复流式传输下的上下文记忆 Bug。

## v0.2
- 增加多轮上下文交互。
- 配置模块解耦 (`app/config.py`)。

## v0.1
- 项目创建与初始结构规划。

---

# 🤝 License

MIT License

---

# 👨‍💻 Author

**Eric**  
AI Learning Journey (2026)