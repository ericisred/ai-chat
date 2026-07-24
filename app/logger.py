import os
import logging
from logging.handlers import RotatingFileHandler

# 1. 确保项目根目录下存在 logs/ 文件夹
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "ai-chat.log")

# 2. 定义统一的日志格式：[时间] [日志级别] [模块名] - 消息内容
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str = "ai-chat") -> logging.Logger:
    """获取配置好的 Logger 实例"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 避免重复添加 Handler（防止打印多条相同日志）
    if not logger.handlers:
        # 文件 Handler：日志写入文件，最大 5MB，最多保留 3 个历史备份文件
        file_handler = RotatingFileHandler(
            LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
        )
        file_handler.setLevel(logging.INFO)

        # 格式化输出
        formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

    return logger


# 导出全局默认 logger
logger = get_logger()
