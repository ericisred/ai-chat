import sqlite3
from typing import List, Dict, Optional
from config import DB_PATH
from logger import logger


class SQLiteStorage:
    """SQLite 数据库底层数据访问对象 (DAO)"""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接，设置 row_factory 以字典形式返回结果"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """自动创建 sessions 与 messages 表结构"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 创建 sessions 会话元数据表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    provider_name TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
            )

            # 创建 messages 消息明细表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                );
            """
            )
            conn.commit()
            logger.info(f"数据库初始化成功，位置: {self.db_path}")

    def create_session(
        self, session_id: str, title: str, provider_name: str, model_name: str
    ):
        """保存新创建的会话元数据"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO sessions (id, title, provider_name, model_name)
                VALUES (?, ?, ?, ?)
            """,
                (session_id, title, provider_name, model_name),
            )
            conn.commit()

    def get_recent_sessions(self, limit: int = 5) -> List[Dict]:
        """获取最近更新的会话列表"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, title, provider_name, model_name, updated_at
                FROM sessions
                ORDER BY updated_at DESC
                LIMIT ?
            """,
                (limit,),
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def save_message(self, session_id: str, role: str, content: str):
        """保存单条消息，并同步更新会话的 updated_at 时间"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO messages (session_id, role, content)
                VALUES (?, ?, ?)
            """,
                (session_id, role, content),
            )
            cursor.execute(
                """
                UPDATE sessions
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (session_id,),
            )
            conn.commit()

    def get_session_messages(self, session_id: str) -> List[Dict]:
        """根据 session_id 获取属于该会话的所有历史消息"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT role, content
                FROM messages
                WHERE session_id = ?
                ORDER BY id ASC
            """,
                (session_id,),
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
