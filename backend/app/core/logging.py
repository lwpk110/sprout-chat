"""
日志配置模块

提供结构化日志配置，支持开发和生产环境
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

from app.core.config import settings


def setup_logging() -> logging.Logger:
    """
    配置应用日志系统

    功能：
    - 控制台输出（彩色日志）
    - 文件输出（可选，带轮转）
    - 结构化格式
    - 环境感知配置
    """
    # 创建根日志记录器
    logger = logging.getLogger("sprout_chat")
    logger.setLevel(getattr(logging, settings.log_level))

    # 清除现有处理器
    logger.handlers.clear()

    # 日志格式
    log_format = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 开发环境：彩色控制台输出
    if settings.is_development:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(log_format)
        logger.addHandler(console_handler)

    # 生产环境：文件输出 + 控制台
    if settings.is_production:
        # 控制台（仅 INFO 及以上）
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(log_format)
        logger.addHandler(console_handler)

        # 文件输出（带轮转）
        if settings.log_file:
            log_path = Path(settings.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = RotatingFileHandler(
                settings.log_file,
                maxBytes=settings.log_max_bytes,
                backupCount=settings.log_backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(getattr(logging, settings.log_level))
            file_handler.setFormatter(log_format)
            logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    获取命名日志记录器

    Args:
        name: 日志记录器名称（通常为 __name__）

    Returns:
        配置好的日志记录器
    """
    return logging.getLogger(f"sprout_chat.{name}")


class LoggerMixin:
    """
    日志记录器混入类

    使用示例：
    ```python
    class MyService(LoggerMixin):
        def do_something(self):
            self.logger.info("Doing something...")
    ```
    """
    @property
    def logger(self) -> logging.Logger:
        """获取当前类的日志记录器"""
        return get_logger(self.__class__.__name__)


# 初始化应用日志
app_logger = setup_logging()
