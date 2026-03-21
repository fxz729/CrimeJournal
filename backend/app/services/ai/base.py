"""AI服务抽象基类"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AIServiceBase(ABC):
    """AI服务抽象基类，定义统一接口"""

    def __init__(self, api_key: str, model: str, **kwargs):
        """
        初始化AI服务

        Args:
            api_key: API密钥
            model: 模型名称
            **kwargs: 其他配置参数
        """
        self.api_key = api_key
        self.model = model
        self.config = kwargs
        self._client = None
        logger.info(f"初始化{self.__class__.__name__}，模型: {model}")

    @abstractmethod
    async def initialize(self) -> None:
        """初始化客户端连接"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """关闭客户端连接"""
        pass

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        生成文本

        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数

        Returns:
            生成的文本
        """
        pass

    @abstractmethod
    async def extract_entities(
        self,
        text: str,
        entity_types: Optional[List[str]] = None
    ) -> Dict[str, List[str]]:
        """
        提取实体

        Args:
            text: 待提取文本
            entity_types: 实体类型列表

        Returns:
            实体字典 {实体类型: [实体列表]}
        """
        pass

    @abstractmethod
    async def summarize(
        self,
        text: str,
        max_length: int = 500
    ) -> str:
        """
        总结文本

        Args:
            text: 待总结文本
            max_length: 最大长度

        Returns:
            总结文本
        """
        pass

    @abstractmethod
    async def extract_keywords(
        self,
        text: str,
        top_n: int = 10
    ) -> List[str]:
        """
        提取关键词

        Args:
            text: 待提取文本
            top_n: 返回前N个关键词

        Returns:
            关键词列表
        """
        pass

    @abstractmethod
    async def classify(
        self,
        text: str,
        categories: List[str]
    ) -> str:
        """
        分类文本

        Args:
            text: 待分类文本
            categories: 分类类别列表

        Returns:
            分类结果
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        健康检查

        Returns:
            服务是否正常
        """
        pass

    def _build_system_prompt(self, task: str, context: Optional[str] = None) -> str:
        """
        构建系统提示

        Args:
            task: 任务描述
            context: 上下文信息

        Returns:
            系统提示
        """
        base_prompt = f"你是一个专业的法律案例分析师。任务: {task}"
        if context:
            base_prompt += f"\n\n上下文: {context}"
        return base_prompt

    def _log_request(self, prompt: str, **kwargs) -> None:
        """记录请求日志"""
        logger.debug(
            f"AI请求 - 模型: {self.model}, "
            f"提示长度: {len(prompt)}, "
            f"参数: {kwargs}"
        )

    def _log_response(self, response: str, duration: float) -> None:
        """记录响应日志"""
        logger.debug(
            f"AI响应 - 长度: {len(response)}, "
            f"耗时: {duration:.2f}秒"
        )

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
