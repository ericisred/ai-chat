from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """问答请求数据模型"""

    question: str = Field(..., description="用户输入的问题", example="你好，请介绍一下你自己")
    session_id: Optional[str] = Field(
        None, description="会话ID，如果不传则自动开启/延迟创建新会话", example="sess_a1b2c3d4"
    )
    provider: Optional[str] = Field(
        None, description="指定LLM提供商 (deepseek / gemini)，不传则使用默认配置", example="gemini"
    )


class ChatResponse(BaseModel):
    """非流式问答响应数据模型"""

    session_id: str = Field(..., description="当前对话所属的会话ID")
    answer: str = Field(..., description="模型回答的完整文本")
    provider: str = Field(..., description="使用的模型提供商")
    model: str = Field(..., description="使用的具体模型名称")


class SessionItem(BaseModel):
    """会话列表项数据模型"""

    id: str
    title: str
    provider_name: str
    model_name: str
    updated_at: str
    created_at: Optional[str] = None
    summary: Optional[str] = ""


class SessionDetailResponse(BaseModel):
    """会话详情响应数据模型"""

    session_id: str
    provider_name: Optional[str] = ""
    model_name: Optional[str] = ""
    summary: str = ""
    messages: List[Dict[str, str]] = []


class CommonResponse(BaseModel):
    """通用操作响应模型"""

    success: bool
    message: str
