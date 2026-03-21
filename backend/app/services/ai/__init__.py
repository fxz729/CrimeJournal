"""AI服务模块 - 统一使用MiniMax"""
from .base import AIServiceBase
from .minimax import MiniMaxService
from .router import AIRouter, TaskType

# 向后兼容保留
from .deepseek import DeepSeekService
from .claude import ClaudeService

__all__ = [
    "AIServiceBase",
    "MiniMaxService",   # 主要服务
    "DeepSeekService",   # 保留但不再使用
    "ClaudeService",    # 保留但不再使用
    "AIRouter",
    "TaskType",         # 任务类型枚举
]
