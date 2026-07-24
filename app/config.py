import os
from dotenv import load_dotenv

load_dotenv()

# 当前使用的 LLM 提供商 (默认: deepseek，可选: "deepseek" / "gemini")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "deepseek").lower()

# DeepSeek 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")

# Gemini 配置
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

def validate_config():
    """根据当前激活的 LLM_PROVIDER，检查必填的 API Key"""
    if LLM_PROVIDER == "deepseek" and not DEEPSEEK_API_KEY:
        raise ValueError("❌ 错误: 当前配置为 deepseek，但未在 .env 中找到 DEEPSEEK_API_KEY")
    elif LLM_PROVIDER == "gemini" and not GEMINI_API_KEY:
        raise ValueError("❌ 错误: 当前配置为 gemini，但未在 .env 中找到 GEMINI_API_KEY")

# 加载配置时自动进行合法性校验
validate_config()


