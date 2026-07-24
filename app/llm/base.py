from abc import ABC, abstractmethod
from typing import Generator, List, Dict
from config import MAX_HISTORY_TURNS


class BaseChatProvider(ABC):
    """所有大语言模型 Provider 的抽象基类 (接口规范)"""

    def __init__(
        self,
        provider_name: str,
        model_name: str,
        max_history_turns: int = MAX_HISTORY_TURNS,
    ):
        self.provider_name = provider_name
        self.model_name = model_name
        self.max_history_turns = max_history_turns

    @abstractmethod
    def ask_stream(self, question: str) -> Generator[str, None, None]:
        """
        流式对话核心方法 (子类必须实现)

        :param question: 用户输入的问题
        :return: 生成器，逐 Token 产出文本 chunk
        """
        pass

    @abstractmethod
    def load_history(self, history_messages: List[Dict]):
        """
        加载历史对话消息到当前 Provider 内部 (子类必须实现)

        :param history_messages: 从数据库查询出的标准消息列表 [{"role": "user"/"assistant", "content": "..."}, ...]
        """
        pass
