"""DeepSeek AI服务实现"""
import time
import json
from typing import Dict, List, Optional
import logging
import httpx

from .base import AIServiceBase

logger = logging.getLogger(__name__)


class DeepSeekService(AIServiceBase):
    """DeepSeek AI服务，专注于关键词提取和分类"""

    BASE_URL = "https://api.deepseek.com/v1"

    def __init__(self, api_key: str, model: str = "deepseek-chat", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def initialize(self) -> None:
        """初始化HTTP客户端"""
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers=self.headers,
            timeout=60.0
        )
        logger.info("DeepSeek客户端初始化成功")

    async def close(self) -> None:
        """关闭HTTP客户端"""
        if self._client:
            await self._client.aclose()
            logger.info("DeepSeek客户端已关闭")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        使用DeepSeek生成文本

        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            生成的文本
        """
        start_time = time.time()
        self._log_request(prompt, temperature=temperature, max_tokens=max_tokens)

        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs
            }

            response = await self._client.post(
                "/chat/completions",
                json=payload
            )
            response.raise_for_status()

            data = response.json()
            result = data["choices"][0]["message"]["content"]

            duration = time.time() - start_time
            self._log_response(result, duration)

            return result

        except httpx.HTTPStatusError as e:
            logger.error(f"DeepSeek API错误: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"DeepSeek生成失败: {str(e)}")
            raise

    async def extract_entities(
        self,
        text: str,
        entity_types: Optional[List[str]] = None
    ) -> Dict[str, List[str]]:
        """
        DeepSeek不擅长实体提取，建议使用Claude
        这里提供简单实现作为降级方案
        """
        logger.warning("DeepSeek不擅长实体提取，建议使用Claude服务")

        if entity_types is None:
            entity_types = ["案件编号", "当事人", "法院", "日期"]

        system_prompt = self._build_system_prompt(
            task="从法律案例中提取实体信息"
        )

        user_prompt = f"""
请从以下文本中提取实体：
{text}

提取类型：{', '.join(entity_types)}
以JSON格式返回：{{"实体类型": ["值"]}}
"""

        try:
            response = await self.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=1000
            )

            entities = json.loads(response)
            return entities

        except Exception as e:
            logger.error(f"实体提取失败: {str(e)}")
            return {}

    async def summarize(
        self,
        text: str,
        max_length: int = 500
    ) -> str:
        """
        DeepSeek可用于总结，但Claude效果更好
        """
        logger.warning("DeepSeek总结效果不如Claude，建议使用Claude服务")

        system_prompt = self._build_system_prompt(
            task="总结法律案例"
        )

        user_prompt = f"""
请用不超过{max_length}字总结以下案例：
{text}

要求简明扼要，突出重点。
"""

        try:
            summary = await self.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.5,
                max_tokens=max_length * 2
            )

            return summary.strip()

        except Exception as e:
            logger.error(f"案例总结失败: {str(e)}")
            raise

    async def extract_keywords(
        self,
        text: str,
        top_n: int = 10
    ) -> List[str]:
        """
        使用DeepSeek提取关键词（专长功能）

        Args:
            text: 待提取文本
            top_n: 返回前N个关键词

        Returns:
            关键词列表
        """
        system_prompt = self._build_system_prompt(
            task="从法律案例中提取关键词",
            context="关键词应体现案例的核心法律要点和争议焦点"
        )

        user_prompt = f"""
请从以下法律案例中提取最重要的{top_n}个关键词：

{text}

要求：
1. 关键词应体现案例的核心法律要点
2. 优先选择法律术语和争议焦点
3. 按重要性排序
4. 以JSON数组格式返回

格式：["关键词1", "关键词2", ...]
"""

        try:
            response = await self.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=500
            )

            keywords = json.loads(response)
            logger.info(f"成功提取{len(keywords)}个关键词")
            return keywords[:top_n]

        except json.JSONDecodeError as e:
            logger.error(f"关键词JSON解析失败: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"关键词提取失败: {str(e)}")
            raise

    async def classify(
        self,
        text: str,
        categories: List[str]
    ) -> str:
        """
        使用DeepSeek进行案例分类（专长功能）

        Args:
            text: 待分类文本
            categories: 分类类别列表

        Returns:
            分类结果
        """
        system_prompt = self._build_system_prompt(
            task="对法律案例进行分类",
            context="根据案例内容选择最匹配的类别"
        )

        user_prompt = f"""
请将以下案例分类到最合适的类别：

案例文本（前500字）：
{text[:500]}

可选类别：{', '.join(categories)}

要求：
1. 只返回类别名称，不要其他说明
2. 选择最匹配的类别
"""

        try:
            category = await self.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=50
            )

            result = category.strip()

            # 验证分类结果是否在候选列表中
            if result in categories:
                logger.info(f"案例分类结果: {result}")
                return result
            else:
                logger.warning(f"分类结果'{result}'不在候选列表中，使用第一个类别")
                return categories[0] if categories else ""

        except Exception as e:
            logger.error(f"案例分类失败: {str(e)}")
            return categories[0] if categories else ""

    async def health_check(self) -> bool:
        """健康检查"""
        try:
            response = await self.generate(
                prompt="Hello",
                max_tokens=10
            )
            return len(response) > 0
        except Exception as e:
            logger.error(f"DeepSeek健康检查失败: {str(e)}")
            return False
