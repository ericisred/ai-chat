# 💬 AI Chat

> 一个基于 Python + 多 LLM Provider 架构与 SQLite 对话持久化的终端命令行与 Web 现代化 UI 助手。

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

本项目采用**策略模式（Strategy Pattern）与工厂模式（Factory Pattern）**设计，实现业务层与底层 LLM SDK 的解耦；引入全新的 **`memory/` 双层架构**，支持长对话滚动摘要压缩与历史会话断点恢复；同时提供完整的 **FastAPI Web API 服务** 以及**高颜值毛玻璃深色模式 Web UI 界面**（包含 SSE 打字机流式推流、中文输入法体验优化与本地时区转换）。

---

## ✨ Features

- 🎨 **高颜值 Web UI 单页界面 (SPA)**：采用深色暗黑系 + 悬浮毛玻璃设计，包含侧边栏历史会话列表、模型切换菜单、响应式自适应输入框。
- ⚡ **RESTful & SSE 流式 API 服务**：基于 FastAPI 封装 `app/server.py`，支持 OpenAPI Swagger 交互文档、CORS 跨域、非流式 JSON 问答与 **SSE (Server-Sent Events) 打字机流式推流**。
- 🕒 **精确时区与对话时间戳**：历史消息与实时对话均附带时间戳展示，支持 UTC 到本地东八区 (+8h) 时间精准转换。
- ⌨️ **中文输入法选词优化**：防输入法选词/回车上字误触发送，支持 `Enter` 发送、`Shift+Enter` 换行。
- 🧠 **滚动摘要双层记忆 (Rolling Summary Memory)**：“长期摘要 + 短期明细”双层记忆架构，自动提炼超长对话上下文注入 System Prompt，突破 Token 限制且关键信息永不遗忘。
- ⚡ **历史会话 0 秒秒开**：恢复带摘要的历史会话时直接继承本地 `summary`，跳过重复 API 摘要计算；选会话自动联动切换顶部模型菜单。
- 💾 **SQLite 对话持久化**：基于 SQLite3 支持 `sessions` 与 `messages` 完整数据落盘、惰性会话创建 (Lazy Session)、会话全生命周期管理（列表查询、历史明细、彻底删除）。
- 🔌 **多模型一键切换**：封装 `LLMProviderFactory`，支持统一接口规范下 DeepSeek (OpenAI 协议) 与 Gemini (`google-genai` SDK) 无缝一键切换。

---

## 📖 Architecture

```text
                             客户端 (Web UI / Mobile / CLI)
                                        │
           ┌────────────────────────────┴────────────────────────────┐
           ▼                                                         ▼
     app/main.py (CLI 终端应用)                             app/server.py (FastAPI API 服务)
           │                                                         │
           └────────────────────────────┬────────────────────────────┘
                                        ▼
                                 MemoryManager & LLM
                                        │
           ┌────────────────────────────┴────────────────────────────┐
           ▼                                                         ▼
  LLMProviderFactory (工厂)                             MemoryManager (内存服务)
           │                                                         │
  ┌────────┴────────┐                                       ┌────────┴────────┐
  ▼                 ▼                                       ▼                 ▼
DeepSeekProvider GeminiProvider                         load_history    SQLiteStorage
 (OpenAI 协议)  (google-genai)                              │           (data/ai-chat.db)
  │                 │                                       ▼                 │
  └────────┬────────┘                               滑动窗口裁剪 / 摘要
           ▼                                                          │
 BaseChatProvider (抽象基类) ◄────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置文件
复制环境配置文件模板并配置您的 API Key：
```bash
cp .env.example .env
```
在 `.env` 中配置对应模型 API Key：
```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_deepseek_api_key
# 或开启 Gemini:
# LLM_PROVIDER=gemini
# GEMINI_API_KEY=your_gemini_api_key
```

### 3. 运行应用

#### 方式 A: 运行 Web UI 界面 (推荐)
```bash
python app/server.py
```
启动后在浏览器打开：
👉 **http://127.0.0.1:8000/** 查看高颜值 Web UI 对话界面。  
👉 **http://127.0.0.1:8000/docs** 查看并测试 Swagger 在线 API 文档。

#### 方式 B: 运行命令行 CLI 终端助手
```bash
python app/main.py
```

---

## 🔑 Environment Variables

| 变量名 | 说明 | 可选值 / 默认值 |
|------|-------------|-------|
| `LLM_PROVIDER` | 当前激活的大模型提供商 | `deepseek` (默认) / `gemini` |
| `SUMMARY_TRIGGER_TURNS` | 触发滚动摘要压缩的对话轮数阈值 | `10` (默认) |
| `RECENT_KEEP_TURNS` | 滚动摘要压缩后保留的近期对话明细轮数 | `5` (默认) |
| `DEEPSEEK_API_KEY` | DeepSeek API Key | 无 (激活 deepseek 时必需) |
| `DEEPSEEK_BASE_URL` | DeepSeek API Base URL | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | DeepSeek 模型名称 | `deepseek-v4-flash` |
| `GEMINI_API_KEY` | Google Gemini API Key | 无 (激活 gemini 时必需) |
| `GEMINI_MODEL` | Gemini 模型名称 | `gemini-2.5-flash` |

---

## 📚 Technical Highlights

- **面向接口编程**：定义 `BaseChatProvider` 抽象接口，彻底屏蔽底层 SDK (OpenAI / google-genai) 的交互差异。
- **双层记忆架构设计**：实现滚动摘要 + 短期明细结合的 Memory System，极大降低 Token 开销。
- **FastAPI SSE 流式解耦**：使用 `sse-starlette` 实现轻量级 SSE 打字机流式传输，解耦 Web 前端与底层 LLM 生成器。
- **输入法体验与时区优化**：解决 Web 端 IME `isComposing` 回车选词冲突与 SQLite UTC0 到本地时区精确转化。
- **SDK Bug 修复**：解决 `google-genai` SDK 在流式响应 (`send_message_stream`) 尾 Chunk 校验导致历史丢失的问题。

---

## 🗺 Roadmap & Changelog

### 🗺 Roadmap
- [x] 多 Provider 架构与工厂模式
- [x] SQLite3 会话持久化与 0 秒秒开恢复
- [x] 滚动摘要双层记忆机制
- [x] 网络超时防护与 SDK 官方流式历史 Bug 修复
- [x] FastAPI 后端 API 封装 (v0.9)
- [x] Web UI 前端界面与打字机流式推流 (v1.0)
- [ ] ⏳ 支持 R1 思考链 (Reasoning Content) 显示

<details>
<summary>📜 点击展开版本变更记录 (Changelog)</summary>

#### v1.0 (Current)
- **Web UI 界面发布**：基于 HTML5/CSS3/JS 实现高颜值深色毛玻璃单页应用 (SPA)，并集成静态托管。
- **实时与历史对话时间戳**：消息卡片与侧边栏列表支持 UTC 到本地东八区时间的精确转换展示。
- **中文输入法体验优化**：引入 `isComposing` 与 `compositionstart/end` 事件，防止输入法回车选词误触发发送。
- **历史模型联动匹配**：选择历史会话时，顶部模型下拉菜单自动切换匹配对应 Provider。

#### v0.9
- **FastAPI Web API 封装**：新增 `app/server.py` 与 `app/schemas.py`，完整支持 RESTful 接口与 SSE 流式问答 (`/api/chat/stream`)。
- **会话持久化擦除扩展**：在 `SQLiteStorage` 和 `MemoryManager` 中新增 `delete_session` 会话安全删除功能。
- **CORS 跨域与 Swagger 自动文档支持**：全量内置 Pydantic v2 Schema 数据校验与 CORS 支持。

#### v0.8
- **滚动摘要记忆系统**：引入“长期摘要 + 短期明细”双层记忆架构。
- **Gemini SDK 流式 Bug 修复**：修复 `send_message_stream` 尾部 Chunk 导致历史缺失的 BUG。
- **历史会话秒开恢复**：结合 `summary` 字段实现 0 秒开会话与 5 轮缓冲防护。
- **网络超时保护**：配置 60s 连接超时与 `APITimeoutError` 防 Crash 捕获。

#### v0.7 - v0.1
- 新增 `app/memory/` 模块，基于 SQLite3 实现 `sessions` 和 `messages` 落盘。
- 支持选单恢复历史会话与 Lazy Session 机制。
- 引入滑动窗口上下文裁剪机制 (Context Truncation)。
- 实现基础多 LLM Provider 重构、TTFT 耗时监控与日志系统。
</details>

---

## 🤝 License & Author

- **License**: MIT
- **Author**: Eric (AI Learning Journey 2026)
