import os
from dotenv import load_dotenv

load_dotenv()

# 当前使用的 LLM 提供商 (默认: deepseek，可选: "deepseek" / "gemini")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "deepseek").lower()

# 读取最大历史保留轮数，默认为 10 轮
MAX_HISTORY_TURNS = int(os.getenv("MAX_HISTORY_TURNS", "10"))

# 滚动摘要参数配置
# 触发摘要压缩的轮数阈值（默认 10 轮对话 / 20 条消息）
SUMMARY_TRIGGER_TURNS = int(os.getenv("SUMMARY_TRIGGER_TURNS", "10"))
# 触发摘要压缩后，原对话明细中保留最近的轮数（默认保留最近 5 轮对话 / 10 条消息）
RECENT_KEEP_TURNS = int(os.getenv("RECENT_KEEP_TURNS", "5"))


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

# 数据库存储目录与文件路径
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "ai-chat.db")

