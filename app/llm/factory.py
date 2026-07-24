from config import LLM_PROVIDER
from llm.base import BaseChatProvider
from llm.deepseek import DeepSeekProvider
from llm.gemini import GeminiProvider


class LLMProviderFactory:
    """LLM Provider 简单工厂类，负责根据配置实例化对应的 Provider"""

    _PROVIDERS = {
        "deepseek": DeepSeekProvider,
        "gemini": GeminiProvider,
    }

    @classmethod
    def get_provider(cls, provider_type: str = None) -> BaseChatProvider:
        """
        获取当前指定的 Provider 实例

        :param provider_type: 显式指定的提供商名称（若为 None 则默认读取 config.LLM_PROVIDER）
        :return: 继承自 BaseChatProvider 的 Provider 实例
        """
        target_provider = (provider_type or LLM_PROVIDER).lower()

        provider_cls = cls._PROVIDERS.get(target_provider)

        if not provider_cls:
            supported = ", ".join(cls._PROVIDERS.keys())
            raise ValueError(
                f"❌ 错误: 不支持的 LLM Provider '{target_provider}'。当前仅支持: [{supported}]"
            )

        return provider_cls()
