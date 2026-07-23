# AI Chat

> 一个基于 Google Gemini API 的命令行 AI Chat 应用。

这是我 AI 工程学习路线中的第一个项目，用于学习大语言模型（LLM）API 调用、上下文管理以及 AI 应用工程化开发。

---

## ✨ Features

- 🤖 Google Gemini API 调用
- 💬 支持多轮对话（Conversation Memory）
- 🔐 API Key 环境变量管理
- 📦 Python 虚拟环境
- 🏗 模块化项目结构
- 🔄 Git 版本管理

---

## 🛠 Tech Stack

- Python 3
- Google Gemini API
- google-genai
- python-dotenv
- Git

---

## 📂 Project Structure

```text
ai-chat
│
├── app
│   ├── main.py          # 程序入口
│   ├── chat.py          # Gemini 调用逻辑
│   └── config.py        # 配置管理
│
├── .env                 # API Key（不会提交）
├── .gitignore
├── requirements.txt
└── README.md
```

---

# 🚀 Quick Start

## 1. Clone Project

```bash
git clone https://github.com/yourname/ai-chat.git
```

进入项目：

```bash
cd ai-chat
```

---

## 2. Create Virtual Environment

创建虚拟环境：

```bash
python3 -m venv .venv
```

Mac / Linux：

```bash
source .venv/bin/activate
```

Windows：

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

创建 `.env`

内容如下：

```text
GEMINI_API_KEY=your_api_key
MODEL_NAME=gemini-3.5-flash
```

> 请不要将 `.env` 上传到 GitHub。

---

## 5. Run

```bash
python app/main.py
```

运行效果：

```text
Gemini Chat 已启动
输入 'exit' 退出

你：
你好

Gemini：
你好！有什么可以帮助你的吗？
```

---

# 💬 Conversation Example

```text
你：
我叫 Eric

Gemini：
你好，Eric！

你：
我叫什么？

Gemini：
你叫 Eric。
```

说明：

当前项目通过维护聊天历史（History）实现多轮上下文，而不是模型本身拥有记忆。

---

# 📖 Project Architecture

```text
          用户输入
              │
              ▼
        app/main.py
              │
              ▼
        app/chat.py
              │
              ▼
      Google Gemini API
              │
              ▼
        Gemini Response
              │
              ▼
          Terminal
```

---

# 🔑 Environment Variables

| Name | Description |
|------|-------------|
| GEMINI_API_KEY | Gemini API Key |
| MODEL_NAME | 使用的模型名称 |

---

# 📚 Learning Goals

本项目主要学习：

- Python 项目结构
- Python 虚拟环境
- API Key 管理
- Google Gemini API
- Prompt 基础
- 多轮上下文管理
- Git 基础
- README 编写

---

# 🗺 Roadmap

当前版本：

- ✅ Gemini API 调用
- ✅ 多轮聊天
- ✅ 配置文件管理
- ✅ Git 管理
- ✅ Streaming 输出

下一步计划：

- ⏳ System Prompt
- ⏳ Logging
- ⏳ 聊天记录持久化（SQLite）
- ⏳ Web UI（Streamlit）
- ⏳ FastAPI 接口
- ⏳ Docker 部署
- ⏳ RAG 知识库
- ⏳ AI Agent

---

# 📝 Version History

## v0.1

- 创建项目
- 配置虚拟环境
- 接入 Gemini API
- 完成命令行聊天

---

## v0.2

- 增加多轮上下文
- 增加配置文件
- 优化项目结构

---

## v0.3（规划中）

- Streaming 输出
- Logging
- 更好的异常处理

---

# 🤝 License

MIT License

---

# 👨‍💻 Author

Eric

AI Learning Journey

2026