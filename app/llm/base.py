from abc import ABC, abstractmethod
from typing import Generator


class BaseChatProvider(ABC):
    """所有大语言模型 Provider 的抽象基类 (接口规范)"""

    def __init__(self, provider_name: str, model_name: str):
        self.provider_name = provider_name
        self.model_name = model_name

    @abstractmethod
    def ask_stream(self, question: str) -> Generator[str, None, None]:
        """
        流式对话核心方法 (子类必须实现)

        :param question: 用户输入的问题
        :return: 生成器，逐 Token 产出文本 chunk
        """
        pass
