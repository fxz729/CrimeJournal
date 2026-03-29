"""AI服务智能路由器 - 使用 MiniMax 和 DeepSeek"""
import logging
from typing import Dict, List, Optional, Any
from enum import Enum
from .minimax import MiniMaxService
from .deepseek import DeepSeekService
from .base import AIServiceBase

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """任务类型枚举"""
    CASE_SUMMARIZATION = "case_summarization"  # 案例总结
    ENTITY_EXTRACTION = "entity_extraction"    # 实体提取
    KEYWORD_EXTRACTION = "keyword_extraction"  # 关键词提取
    CLASSIFICATION = "classification"          # 文本分类
    GENERAL_QA = "general_qa"                # 通用问答
    TRANSLATION = "translation"                # 文本翻译
    TEXT_FORMATTING = "text_formatting"       # 文本格式整理


class AIRouter:
    """
    AI服务智能路由器

    使用 MiniMax 提供总结、实体提取等能力
    使用 DeepSeek 提供翻译、格式整理能力
    """

    # 任务类型到服务的映射
    TASK_SERVICE_MAP = {
        TaskType.CASE_SUMMARIZATION: [
            ("minimax", 1.0),    # MiniMax 擅长总结
        ],
        TaskType.ENTITY_EXTRACTION: [
            ("minimax", 1.0),    # MiniMax 擅长实体提取
        ],
        TaskType.KEYWORD_EXTRACTION: [
            ("minimax", 1.0),    # MiniMax 擅长关键词提取
        ],
        TaskType.CLASSIFICATION: [
            ("minimax", 1.0),    # MiniMax 擅长分类
        ],
        TaskType.GENERAL_QA: [
            ("minimax", 1.0),    # MiniMax 通用能力强
        ],
        TaskType.TRANSLATION: [
            ("deepseek", 1.0),   # DeepSeek 翻译能力
        ],
        TaskType.TEXT_FORMATTING: [
            ("deepseek", 1.0),   # DeepSeek 文本格式整理
        ]
    }

    def __init__(
        self,
        minimax_service: Optional[MiniMaxService] = None,
        deepseek_service: Optional[DeepSeekService] = None,
    ):
        """
        初始化路由器

        Args:
            minimax_service: MiniMax服务实例
            deepseek_service: DeepSeek服务实例
        """
        self.services: Dict[str, AIServiceBase] = {}
        self.service_status: Dict[str, bool] = {}

        if minimax_service:
            self.services["minimax"] = minimax_service
            self.service_status["minimax"] = True
        if deepseek_service:
            self.services["deepseek"] = deepseek_service
            self.service_status["deepseek"] = True

        logger.info(f"路由器初始化完成，可用服务: {list(self.services.keys())}")

    async def initialize_all(self) -> None:
        """初始化所有服务"""
        for name, service in self.services.items():
            try:
                await service.initialize()
                self.service_status[name] = True
                logger.info(f"服务 {name} 初始化成功")
            except Exception as e:
                self.service_status[name] = False
                logger.error(f"服务 {name} 初始化失败: {str(e)}")

    async def close_all(self) -> None:
        """关闭所有服务"""
        for name, service in self.services.items():
            try:
                await service.close()
                logger.info(f"服务 {name} 已关闭")
            except Exception as e:
                logger.error(f"服务 {name} 关闭失败: {str(e)}")

    def _select_service(
        self,
        task_type: TaskType,
        prefer_service: Optional[str] = None
    ) -> Optional[AIServiceBase]:
        """
        选择最佳服务

        Args:
            task_type: 任务类型
            prefer_service: 指定优先使用的服务

        Returns:
            选中的服务实例
        """
        # 如果指定了服务且可用，直接使用
        if prefer_service and prefer_service in self.services:
            if self.service_status.get(prefer_service, False):
                logger.info(f"使用指定服务: {prefer_service}")
                return self.services[prefer_service]

        # 根据任务类型选择最佳服务
        service_candidates = self.TASK_SERVICE_MAP.get(task_type, [])

        for service_name, priority in service_candidates:
            if service_name in self.services and self.service_status.get(service_name, False):
                logger.info(f"任务 {task_type.value} 选择服务: {service_name} (优先级: {priority})")
                return self.services[service_name]

        logger.warning(f"任务 {task_type.value} 无可用服务")
        return None

    async def route(
        self,
        task_type: TaskType,
        method_name: str,
        prefer_service: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        智能路由请求到最佳服务

        Args:
            task_type: 任务类型
            method_name: 要调用的方法名
            prefer_service: 指定优先使用的服务
            **kwargs: 方法参数

        Returns:
            方法调用结果
        """
        service = self._select_service(task_type, prefer_service)

        if not service:
            raise RuntimeError(f"无可用服务处理任务: {task_type.value}")

        try:
            method = getattr(service, method_name)
            result = await method(**kwargs)
            return result

        except Exception as e:
            logger.error(f"服务 {service.__class__.__name__} 调用失败: {str(e)}")
            raise RuntimeError(f"MiniMax服务调用失败: {str(e)}")

    async def summarize_case(self, text: str, max_length: int = 500) -> str:
        """案例总结"""
        return await self.route(
            task_type=TaskType.CASE_SUMMARIZATION,
            method_name="summarize",
            text=text,
            max_length=max_length
        )

    async def extract_entities(
        self,
        text: str,
        entity_types: Optional[List[str]] = None
    ) -> Dict[str, List[str]]:
        """实体提取"""
        return await self.route(
            task_type=TaskType.ENTITY_EXTRACTION,
            method_name="extract_entities",
            text=text,
            entity_types=entity_types
        )

    async def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """关键词提取"""
        return await self.route(
            task_type=TaskType.KEYWORD_EXTRACTION,
            method_name="extract_keywords",
            text=text,
            top_n=top_n
        )

    async def classify_case(self, text: str, categories: List[str]) -> str:
        """案例分类"""
        return await self.route(
            task_type=TaskType.CLASSIFICATION,
            method_name="classify",
            text=text,
            categories=categories
        )

    async def translate_case(
        self,
        text: str,
        target_language: str = "English",
        source_language: str = "auto",
    ) -> str:
        """文本翻译"""
        return await self.route(
            task_type=TaskType.TRANSLATION,
            method_name="translate",
            text=text,
            target_language=target_language,
            source_language=source_language,
        )

    async def format_text_case(self, text: str) -> str:
        """文本格式整理"""
        return await self.route(
            task_type=TaskType.TEXT_FORMATTING,
            method_name="format_text",
            text=text,
        )

    async def health_check_all(self) -> Dict[str, bool]:
        """检查所有服务健康状态"""
        results = {}
        for name, service in self.services.items():
            try:
                is_healthy = await service.health_check()
                results[name] = is_healthy
                self.service_status[name] = is_healthy
                logger.info(f"服务 {name} 健康检查: {'正常' if is_healthy else '异常'}")
            except Exception as e:
                results[name] = False
                self.service_status[name] = False
                logger.error(f"服务 {name} 健康检查失败: {str(e)}")

        return results

    def get_service_status(self) -> Dict[str, bool]:
        """获取服务状态"""
        return self.service_status.copy()

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize_all()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close_all()
