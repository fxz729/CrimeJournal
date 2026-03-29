"""AI服务模块 - MiniMax（总结/实体提取等）+ DeepSeek（翻译/格式整理）"""
from .base import AIServiceBase
from .minimax import MiniMaxService
from .deepseek import DeepSeekService
from .router import AIRouter, TaskType

__all__ = [
    "AIServiceBase",
    "MiniMaxService",   # 总结、实体提取、关键词、分类等
    "DeepSeekService",  # 翻译、格式整理
    "AIRouter",
    "TaskType",         # 任务类型枚举
]
