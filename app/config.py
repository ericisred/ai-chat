import os
from dotenv import load_dotenv

load_dotenv()


DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-v4-flash")

if not DEEPSEEK_API_KEY:
    raise ValueError("❌ 错误: 未配置 DEEPSEEK_API_KEY，请在 .env 文件中设置")


