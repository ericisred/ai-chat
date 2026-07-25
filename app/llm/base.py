from abc import ABC, abstractmethod
from typing import Generator, List, Dict
from config import SUMMARY_TRIGGER_TURNS, RECENT_KEEP_TURNS


class BaseChatProvider(ABC):
    """所有大语言模型 Provider 的抽象基类 (接口规范)"""

    def __init__(
        self,
        provider_name: str,
        model_name: str,
        summary_trigger_turns: int = SUMMARY_TRIGGER_TURNS,
        recent_keep_turns: int = RECENT_KEEP_TURNS,
    ):
        self.provider_name = provider_name
        self.model_name = model_name
        self.summary_trigger_turns = summary_trigger_turns
        self.recent_keep_turns = recent_keep_turns
        self.summary: str = ""

    @abstractmethod
    def ask_stream(self, question: str) -> Generator[str, None, None]:
        """
        流式对话核心方法 (子类必须实现)

        :param question: 用户输入的问题
        :return: 生成器，逐 Token 产出文本 chunk
        """
        pass

    @abstractmethod
    def load_history(self, history_messages: List[Dict], summary: str = ""):
        """
        加载历史对话消息及记忆摘要到当前 Provider 内部 (子类必须实现)

        :param history_messages: 从数据库查询出的标准消息列表 [{"role": "user"/"assistant", "content": "..."}, ...]
        :param summary: 历史对话总结摘要
        """
        pass
