"""
AI Router Tests

测试 AI 服务路由器
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.ai.router import AIRouter, TaskType


class TestTaskType:
    """任务类型枚举测试"""

    def test_task_types_exist(self):
        """所有任务类型都存在"""
        assert TaskType.CASE_SUMMARIZATION is not None
        assert TaskType.ENTITY_EXTRACTION is not None
        assert TaskType.KEYWORD_EXTRACTION is not None
        assert TaskType.CLASSIFICATION is not None
        assert TaskType.GENERAL_QA is not None

    def test_task_type_values(self):
        """任务类型值正确"""
        assert TaskType.CASE_SUMMARIZATION.value == "case_summarization"
        assert TaskType.ENTITY_EXTRACTION.value == "entity_extraction"
        assert TaskType.KEYWORD_EXTRACTION.value == "keyword_extraction"
        assert TaskType.CLASSIFICATION.value == "classification"
        assert TaskType.GENERAL_QA.value == "general_qa"


class TestAIRouterInit:
    """AI路由器初始化测试"""

    def test_init_without_services(self):
        """无服务初始化"""
        router = AIRouter()

        assert router.services == {}
        assert router.service_status == {}

    def test_init_with_minimax_service(self):
        """带MiniMax服务初始化"""
        mock_service = MagicMock()
        mock_service.health_check = AsyncMock(return_value=True)

        router = AIRouter(minimax_service=mock_service)

        assert "minimax" in router.services
        assert router.service_status["minimax"] is True


class TestAIRouterInitializeAll:
    """AI路由器服务初始化测试"""

    @pytest.mark.asyncio
    async def test_initialize_all_services(self):
        """初始化所有服务"""
        mock_service = MagicMock()
        mock_service.initialize = AsyncMock()

        router = AIRouter(minimax_service=mock_service)

        await router.initialize_all()

        mock_service.initialize.assert_called_once()
        assert router.service_status["minimax"] is True

    @pytest.mark.asyncio
    async def test_initialize_handles_errors(self):
        """初始化错误处理"""
        mock_service = MagicMock()
        mock_service.initialize = AsyncMock(side_effect=Exception("Init error"))

        router = AIRouter(minimax_service=mock_service)

        await router.initialize_all()

        assert router.service_status["minimax"] is False


class TestAIRouterCloseAll:
    """AI路由器服务关闭测试"""

    @pytest.mark.asyncio
    async def test_close_all_services(self):
        """关闭所有服务"""
        mock_service = MagicMock()
        mock_service.close = AsyncMock()

        router = AIRouter(minimax_service=mock_service)
        await router.initialize_all()

        await router.close_all()

        mock_service.close.assert_called_once()


class TestAIRouterSelectService:
    """AI路由器服务选择测试"""

    def test_select_service_with_prefer(self):
        """指定优先服务"""
        mock_minimax = MagicMock()
        router = AIRouter(minimax_service=mock_minimax)
        router.service_status["minimax"] = True

        service = router._select_service(
            task_type=TaskType.CASE_SUMMARIZATION,
            prefer_service="minimax"
        )

        assert service == mock_minimax

    def test_select_service_not_available(self):
        """服务不可用"""
        mock_service = MagicMock()
        router = AIRouter(minimax_service=mock_service)
        router.service_status["minimax"] = False

        service = router._select_service(
            task_type=TaskType.CASE_SUMMARIZATION,
            prefer_service="minimax"
        )

        assert service is None

    def test_select_service_auto_select(self):
        """自动选择服务"""
        mock_service = MagicMock()
        router = AIRouter(minimax_service=mock_service)
        router.service_status["minimax"] = True

        service = router._select_service(
            task_type=TaskType.CASE_SUMMARIZATION
        )

        assert service == mock_service

    def test_select_service_no_service(self):
        """无服务可用"""
        router = AIRouter()

        service = router._select_service(
            task_type=TaskType.CASE_SUMMARIZATION
        )

        assert service is None


class TestAIRouterRoute:
    """AI路由器路由测试"""

    @pytest.mark.asyncio
    async def test_route_success(self):
        """路由成功"""
        mock_service = MagicMock()
        mock_service.summarize = AsyncMock(return_value="Summary")
        router = AIRouter(minimax_service=mock_service)
        router.service_status["minimax"] = True

        result = await router.route(
            task_type=TaskType.CASE_SUMMARIZATION,
            method_name="summarize",
            text="Test text"
        )

        assert result == "Summary"

    @pytest.mark.asyncio
    async def test_route_no_service(self):
        """无可用服务"""
        router = AIRouter()

        with pytest.raises(RuntimeError) as exc_info:
            await router.route(
                task_type=TaskType.CASE_SUMMARIZATION,
                method_name="summarize"
            )

        assert "无可用服务" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_route_method_error(self):
        """方法调用错误"""
        mock_service = MagicMock()
        mock_service.summarize = AsyncMock(side_effect=Exception("Method error"))
        router = AIRouter(minimax_service=mock_service)
        router.service_status["minimax"] = True

        with pytest.raises(RuntimeError) as exc_info:
            await router.route(
                task_type=TaskType.CASE_SUMMARIZATION,
                method_name="summarize"
            )

        assert "MiniMax服务调用失败" in str(exc_info.value)


class TestAIRouterSummarizeCase:
    """AI路由器案例总结测试"""

    @pytest.mark.asyncio
    async def test_summarize_case(self):
        """案例总结"""
        mock_service = MagicMock()
        mock_service.summarize = AsyncMock(return_value="Case summary")
        router = AIRouter(minimax_service=mock_service)
        router.service_status["minimax"] = True

        result = await router.summarize_case(text="Test case", max_length=500)

        assert result == "Case summary"
        mock_service.summarize.assert_called_once_with(text="Test case", max_length=500)

    @pytest.mark.asyncio
    async def test_summarize_case_no_service(self):
        """无服务时总结失败"""
        router = AIRouter()

        with pytest.raises(RuntimeError):
            await router.summarize_case(text="Test")


class TestAIRouterExtractEntities:
    """AI路由器实体提取测试"""

    @pytest.mark.asyncio
    async def test_extract_entities(self):
        """实体提取"""
        mock_service = MagicMock()
        mock_service.extract_entities = AsyncMock(return_value={"defendants": ["John"]})
        router = AIRouter(minimax_service=mock_service)
        router.service_status["minimax"] = True

        result = await router.extract_entities(text="Test", entity_types=["defendants"])

        assert result == {"defendants": ["John"]}

    @pytest.mark.asyncio
    async def test_extract_entities_default_types(self):
        """默认实体类型"""
        mock_service = MagicMock()
        mock_service.extract_entities = AsyncMock(return_value={})
        router = AIRouter(minimax_service=mock_service)
        router.service_status["minimax"] = True

        await router.extract_entities(text="Test")

        mock_service.extract_entities.assert_called_once_with(
            text="Test",
            entity_types=None
        )


class TestAIRouterExtractKeywords:
    """AI路由器关键词提取测试"""

    @pytest.mark.asyncio
    async def test_extract_keywords(self):
        """关键词提取"""
        mock_service = MagicMock()
        mock_service.extract_keywords = AsyncMock(return_value=["kw1", "kw2"])
        router = AIRouter(minimax_service=mock_service)
        router.service_status["minimax"] = True

        result = await router.extract_keywords(text="Test", top_n=5)

        assert result == ["kw1", "kw2"]
        mock_service.extract_keywords.assert_called_once_with(text="Test", top_n=5)


class TestAIRouterClassifyCase:
    """AI路由器案例分类测试"""

    @pytest.mark.asyncio
    async def test_classify_case(self):
        """案例分类"""
        mock_service = MagicMock()
        mock_service.classify = AsyncMock(return_value="Criminal Law")
        router = AIRouter(minimax_service=mock_service)
        router.service_status["minimax"] = True

        result = await router.classify_case(
            text="Test case",
            categories=["Criminal Law", "Civil Law"]
        )

        assert result == "Criminal Law"


class TestAIRouterHealthCheckAll:
    """AI路由器健康检查测试"""

    @pytest.mark.asyncio
    async def test_health_check_all_success(self):
        """所有服务健康"""
        mock_service = MagicMock()
        mock_service.health_check = AsyncMock(return_value=True)
        router = AIRouter(minimax_service=mock_service)

        results = await router.health_check_all()

        assert results["minimax"] is True
        assert router.service_status["minimax"] is True

    @pytest.mark.asyncio
    async def test_health_check_all_failure(self):
        """服务不健康"""
        mock_service = MagicMock()
        mock_service.health_check = AsyncMock(return_value=False)
        router = AIRouter(minimax_service=mock_service)

        results = await router.health_check_all()

        assert results["minimax"] is False
        assert router.service_status["minimax"] is False

    @pytest.mark.asyncio
    async def test_health_check_all_exception(self):
        """健康检查异常"""
        mock_service = MagicMock()
        mock_service.health_check = AsyncMock(side_effect=Exception("Error"))
        router = AIRouter(minimax_service=mock_service)

        results = await router.health_check_all()

        assert results["minimax"] is False


class TestAIRouterGetServiceStatus:
    """AI路由器服务状态测试"""

    def test_get_service_status(self):
        """获取服务状态"""
        mock_service = MagicMock()
        router = AIRouter(minimax_service=mock_service)
        router.service_status["minimax"] = True

        status = router.get_service_status()

        assert status == {"minimax": True}

    def test_get_service_status_copy(self):
        """返回状态副本"""
        mock_service = MagicMock()
        router = AIRouter(minimax_service=mock_service)
        router.service_status["minimax"] = True

        status = router.get_service_status()
        status["minimax"] = False

        # 原始状态不变
        assert router.service_status["minimax"] is True


class TestAIRouterContextManager:
    """AI路由器上下文管理器测试"""

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """异步上下文管理器"""
        mock_service = MagicMock()
        mock_service.initialize = AsyncMock()
        mock_service.close = AsyncMock()

        async with AIRouter(minimax_service=mock_service) as router:
            mock_service.initialize.assert_called_once()

        mock_service.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager_init_error(self):
        """上下文管理器初始化错误"""
        mock_service = MagicMock()
        mock_service.initialize = AsyncMock(side_effect=Exception("Init error"))
        mock_service.close = AsyncMock()

        async with AIRouter(minimax_service=mock_service) as router:
            pass

        mock_service.close.assert_called_once()


class TestAIRouterTaskServiceMap:
    """AI路由器任务服务映射测试"""

    def test_task_service_map_exists(self):
        """任务服务映射存在"""
        assert TaskType.CASE_SUMMARIZATION in AIRouter.TASK_SERVICE_MAP
        assert TaskType.ENTITY_EXTRACTION in AIRouter.TASK_SERVICE_MAP
        assert TaskType.KEYWORD_EXTRACTION in AIRouter.TASK_SERVICE_MAP
        assert TaskType.CLASSIFICATION in AIRouter.TASK_SERVICE_MAP
        assert TaskType.GENERAL_QA in AIRouter.TASK_SERVICE_MAP

    def test_task_service_map_configuration(self):
        """任务服务映射配置正确"""
        # MiniMax 用于总结、实体提取、关键词、分类
        minimax_tasks = [
            TaskType.CASE_SUMMARIZATION,
            TaskType.ENTITY_EXTRACTION,
            TaskType.KEYWORD_EXTRACTION,
            TaskType.CLASSIFICATION,
            TaskType.GENERAL_QA,
        ]
        for task_type in minimax_tasks:
            services = AIRouter.TASK_SERVICE_MAP[task_type]
            assert len(services) > 0
            assert services[0][0] == "minimax"

        # DeepSeek 用于翻译、格式整理
        deepseek_tasks = [
            TaskType.TRANSLATION,
            TaskType.TEXT_FORMATTING,
        ]
        for task_type in deepseek_tasks:
            services = AIRouter.TASK_SERVICE_MAP[task_type]
            assert len(services) > 0
            assert services[0][0] == "deepseek"
