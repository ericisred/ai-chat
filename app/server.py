import os
import sys
import json
import asyncio
from typing import List
from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

# 保证当前 app 目录在 sys.path 中
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import LLM_PROVIDER
from llm import LLMProviderFactory
from memory import MemoryManager
from logger import logger
from schemas import (
    ChatRequest,
    ChatResponse,
    SessionItem,
    SessionDetailResponse,
    CommonResponse,
)

# 1. 初始化 FastAPI 应用
app = FastAPI(
    title="💬 AI Chat API Service",
    description="基于 FastAPI + 多 Provider 架构与 SQLite 对话持久化的 Web API 服务",
    version="1.0.0",
)

# 2. 配置 CORS 跨域（方便后续 Web 前端界面调用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. 实例全局 MemoryManager
memory_manager = MemoryManager()


# --- 路由接口定义 ---


@app.get("/health", tags=["基础接口"])
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "app": "AI Chat API Service"}


@app.get("/api/providers", tags=["模型接口"])
async def list_providers():
    """获取当前可用的 LLM 提供商列表与默认配置"""
    return {
        "providers": ["deepseek", "gemini"],
        "default": LLM_PROVIDER,
    }


@app.get("/api/sessions", response_model=List[SessionItem], tags=["会话管理"])
async def get_sessions(limit: int = 20):
    """获取历史会话列表"""
    sessions = memory_manager.list_history_sessions(limit=limit)
    return sessions


@app.get("/api/sessions/{session_id}", response_model=SessionDetailResponse, tags=["会话管理"])
async def get_session_detail(session_id: str):
    """获取特定会话的详细消息历史与总结摘要"""
    messages, summary, session_meta = memory_manager.load_session(session_id)
    if not messages and not summary and not session_meta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到 Session ID 为 '{session_id}' 的会话",
        )
    return SessionDetailResponse(
        session_id=session_id,
        provider_name=session_meta.get("provider_name", ""),
        model_name=session_meta.get("model_name", ""),
        summary=summary,
        messages=messages,
    )


@app.delete("/api/sessions/{session_id}", response_model=CommonResponse, tags=["会话管理"])
async def delete_session(session_id: str):
    """删除指定的历史会话"""
    success = memory_manager.delete_session(session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"删除失败，未找到会话 '{session_id}'",
        )
    return CommonResponse(success=True, message=f"会话 '{session_id}' 已成功删除")


@app.post("/api/chat/completions", response_model=ChatResponse, tags=["问答接口"])
async def chat_completions(req: ChatRequest):
    """非流式同步问答接口（一次性返回完整回答）"""
    try:
        # 实例化 Provider
        chat_session = LLMProviderFactory.get_provider(req.provider)

        # 加载历史会话（如果指定了 session_id）
        if req.session_id:
            messages, summary, _ = memory_manager.load_session(req.session_id)
            chat_session.load_history(messages, summary)
        else:
            memory_manager.prepare_new_session()

        # 生成回答
        full_answer = ""
        for chunk in chat_session.ask_stream(req.question):
            full_answer += chunk

        # 保存持久化落盘
        memory_manager.save_turn(
            req.question,
            full_answer,
            chat_session.provider_name,
            chat_session.model_name,
            chat_session.summary,
        )

        return ChatResponse(
            session_id=memory_manager.current_session_id,
            answer=full_answer,
            provider=chat_session.provider_name,
            model=chat_session.model_name,
        )
    except Exception as e:
        logger.error(f"非流式对话异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"请求生成失败: {str(e)}",
        )


@app.post("/api/chat/stream", tags=["问答接口"])
async def chat_stream(req: ChatRequest):
    """SSE 流式打字机问答接口 (Server-Sent Events)"""

    async def event_generator():
        try:
            # 实例化 Provider
            chat_session = LLMProviderFactory.get_provider(req.provider)

            # 加载历史
            if req.session_id:
                messages, summary, _ = memory_manager.load_session(req.session_id)
                chat_session.load_history(messages, summary)
            else:
                memory_manager.prepare_new_session()

            full_answer = ""
            for chunk in chat_session.ask_stream(req.question):
                full_answer += chunk
                # 输出 SSE 数据包
                yield {
                    "data": json.dumps(
                        {
                            "content": chunk,
                            "session_id": memory_manager.current_session_id or "",
                        },
                        ensure_ascii=False,
                    )
                }
                await asyncio.sleep(0.01)  # 微小让步让事件循环及时推流

            # 问答结束，落盘保存
            memory_manager.save_turn(
                req.question,
                full_answer,
                chat_session.provider_name,
                chat_session.model_name,
                chat_session.summary,
            )

            # 推送完成标志 [DONE]
            yield {
                "data": json.dumps(
                    {
                        "content": "[DONE]",
                        "session_id": memory_manager.current_session_id,
                    },
                    ensure_ascii=False,
                )
            }

        except Exception as e:
            logger.error(f"SSE 流式对话异常: {str(e)}")
            yield {
                "data": json.dumps(
                    {"error": f"发生异常: {str(e)}"}, ensure_ascii=False
                )
            }

    return EventSourceResponse(event_generator())

# 4. 挂载静态文件服务 (将 app/static 映射到根路径 /)
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
