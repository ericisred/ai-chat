import uuid
from typing import List, Dict
from memory.storage import SQLiteStorage
from logger import logger


class MemoryManager:
    """会话内存与持久化业务管理器 (支持 Lazy 创建会话)"""

    def __init__(self, storage: SQLiteStorage = None):
        self.storage = storage or SQLiteStorage()
        self.current_session_id: str = ""

    def prepare_new_session(self):
        """准备新会话（仅清空当前 session_id 标记，不写入数据库）"""
        self.current_session_id = ""

    def list_history_sessions(self, limit: int = 5) -> List[Dict]:
        """获取最近的历史会话列表"""
        return self.storage.get_recent_sessions(limit=limit)

    def load_session(self, session_id: str) -> List[Dict]:
        """激活并加载指定 Session 的所有历史消息"""
        self.current_session_id = session_id
        messages = self.storage.get_session_messages(session_id)
        logger.info(f"加载会话: {session_id} | 读取历史消息: {len(messages)} 条")
        return messages

    def save_turn(
        self, question: str, answer: str, provider_name: str, model_name: str
    ):
        """持久化保存一轮完整的对话（问 + 答）"""
        # 1. 延迟创建：如果是全新的对话且首次成功回答，此时才延迟创建会话记录
        if not self.current_session_id:
            session_id = f"sess_{uuid.uuid4().hex[:8]}"
            short_title = (question[:15] + "...") if len(question) > 15 else question

            self.storage.create_session(
                session_id, short_title, provider_name, model_name
            )
            self.current_session_id = session_id
            logger.info(
                f"首轮对话成功，延迟创建会话落盘: {session_id} [{provider_name}/{model_name}]"
            )

        # 2. 写入问答消息
        self.storage.save_message(self.current_session_id, "user", question)
        self.storage.save_message(self.current_session_id, "assistant", answer)
        logger.info(f"会话 [{self.current_session_id}] 成功持久化保存 1 轮对话")
