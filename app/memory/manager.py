import uuid
from typing import List, Dict, Optional
from memory.storage import SQLiteStorage
from logger import logger


class MemoryManager:
    """会话内存与持久化业务管理器 (无状态纯函数服务，100% 并发安全)"""

    def __init__(self, storage: SQLiteStorage = None):
        self.storage = storage or SQLiteStorage()

    def list_history_sessions(self, limit: int = 5) -> List[Dict]:
        """获取最近的历史会话列表"""
        return self.storage.get_recent_sessions(limit=limit)

    def load_session(self, session_id: str) -> tuple[List[Dict], str, Dict]:
        """加载指定 Session 的所有历史消息、摘要及元数据"""
        messages = self.storage.get_session_messages(session_id)
        summary = self.storage.get_session_summary(session_id)
        session_meta = self.storage.get_session(session_id) or {}
        logger.info(f"加载会话: {session_id} | 读取历史消息: {len(messages)} 条 | 摘要长度: {len(summary)} 字符")
        return messages, summary, session_meta

    def save_turn(
        self,
        session_id: Optional[str],
        question: str,
        answer: str,
        provider_name: str,
        model_name: str,
        summary: str = "",
    ) -> str:
        """
        无状态持久化保存一轮完整的对话（问 + 答），并更新摘要
        
        :param session_id: 当前会话ID，若为 None 或空字符串，则表示开启全新会话
        :return: 最终保存生效的 session_id
        """
        target_session_id = session_id

        # 1. 延迟创建：如果是全新的对话且首次成功回答，此时才延迟创建会话记录
        if not target_session_id:
            target_session_id = f"sess_{uuid.uuid4().hex[:8]}"
            short_title = (question[:15] + "...") if len(question) > 15 else question

            self.storage.create_session(
                target_session_id, short_title, provider_name, model_name
            )
            logger.info(
                f"首轮对话成功，延迟创建会话落盘: {target_session_id} [{provider_name}/{model_name}]"
            )

        # 2. 写入问答消息
        self.storage.save_message(target_session_id, "user", question)
        self.storage.save_message(target_session_id, "assistant", answer)

        # 3. 若产生/更新了摘要，更新到数据库
        if summary:
            self.storage.update_session_summary(target_session_id, summary)

        logger.info(f"会话 [{target_session_id}] 成功持久化保存 1 轮对话")
        return target_session_id

    def delete_session(self, session_id: str) -> bool:
        """删除指定会话及其持久化数据"""
        return self.storage.delete_session(session_id)
