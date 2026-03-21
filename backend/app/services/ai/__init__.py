"""AI服务模块 - 统一使用MiniMax"""
from .base import AIServiceBase
from .minimax import MiniMaxService
from .router import AIRouter, TaskType

__all__ = [
    "AIServiceBase",
    "MiniMaxService",   # 主要服务（唯一）
    "AIRouter",
    "TaskType",         # 任务类型枚举
]
