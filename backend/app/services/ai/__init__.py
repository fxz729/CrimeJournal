"""AI服务模块"""
from .base import AIServiceBase
from .minimax import MiniMaxService
from .deepseek import DeepSeekService
from .router import AIRouter

# 保留ClaudeService以兼容旧代码
from .claude import ClaudeService

__all__ = [
    "AIServiceBase",
    "MiniMaxService",  # 主要服务（已替换Claude）
    "DeepSeekService",
    "ClaudeService",   # 保留但不再使用
    "AIRouter",
]
