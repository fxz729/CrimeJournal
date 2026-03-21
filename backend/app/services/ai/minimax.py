"""
MiniMax AI服务实现

使用OpenAI兼容API格式
文档: https://www.minimaxi.com/document/Chinese
"""
import time
import json
from typing import Dict, List, Optional
import logging
import httpx
from .base import AIServiceBase

logger = logging.getLogger(__name__)


class MiniMaxService(AIServiceBase):
    """MiniMax AI服务，用于案例总结和实体提取"""

    def __init__(
        self,
        api_key: str,
        model: str = "MiniMax-Text-01",
        base_url: str = "https://api.minimax.chat/v1",
        **kwargs
    ):
        super().__init__(api_key, model, **kwargs)
        self.base_url = base_url.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None

    async def initialize(self) -> None:
        """初始化MiniMax客户端"""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=60.0
        )
        logger.info(f"MiniMax客户端初始化成功，base_url: {self.base_url}")

    async def close(self) -> None:
        """关闭MiniMax客户端"""
        if self._client:
            await self._client.aclose()
            logger.info("MiniMax客户端已关闭")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        使用MiniMax生成文本

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

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self._client.post(
                "/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    **kwargs
                }
            )
            response.raise_for_status()
            data = response.json()

            result = data["choices"][0]["message"]["content"]
            duration = time.time() - start_time
            self._log_response(result, duration)

            return result

        except httpx.HTTPStatusError as e:
            logger.error(f"MiniMax API错误: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"MiniMax生成失败: {str(e)}")
            raise

    async def extract_entities(
        self,
        text: str,
        entity_types: Optional[List[str]] = None
    ) -> Dict[str, List[str]]:
        """
        使用MiniMax提取实体

        Args:
            text: 待提取文本
            entity_types: 实体类型列表

        Returns:
            实体字典
        """
        if entity_types is None:
            entity_types = [
                "案件编号", "当事人", "法院", "法官",
                "律师", "日期", "地点", "罪名", "判决结果"
            ]

        system_prompt = self._build_system_prompt(
            task="从法律案例文本中提取关键实体信息",
            context="请以JSON格式返回提取的实体"
        )

        user_prompt = f"""请从以下法律案例文本中提取实体信息：

{text}

请提取以下类型的实体：{', '.join(entity_types)}

请以JSON格式返回，格式如下：
{{
    "案件编号": ["..."],
    "当事人": ["..."],
    "法院": ["..."],
    ...
}}

只返回JSON，不要其他说明文字。"""

        try:
            response = await self.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=1500
            )
            entities = json.loads(response)
            logger.info(f"成功提取{sum(len(v) for v in entities.values())}个实体")
            return entities

        except json.JSONDecodeError as e:
            logger.error(f"实体提取JSON解析失败: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"实体提取失败: {str(e)}")
            raise

    async def summarize(
        self,
        text: str,
        max_length: int = 500
    ) -> str:
        """
        使用MiniMax总结案例

        Args:
            text: 待总结文本
            max_length: 最大长度

        Returns:
            案例总结
        """
        system_prompt = self._build_system_prompt(
            task="总结法律案例的关键信息和判决要点",
            context="总结应简明扼要，突出重点"
        )

        user_prompt = f"""请总结以下法律案例，要求：
1. 字数不超过{max_length}字
2. 包含案件基本情况、争议焦点、法院观点、判决结果
3. 语言简洁，专业

案例文本：
{text}

请直接输出总结内容："""

        try:
            summary = await self.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.5,
                max_tokens=max_length * 2
            )
            logger.info(f"成功生成案例总结，长度: {len(summary)}")
            return summary.strip()

        except Exception as e:
            logger.error(f"案例总结失败: {str(e)}")
            raise

    async def extract_keywords(
        self,
        text: str,
        top_n: int = 10
    ) -> List[str]:
        """MiniMax关键词提取"""
        system_prompt = self._build_system_prompt(
            task="从法律案例中提取关键词"
        )

        user_prompt = f"""请从以下文本中提取最重要的{top_n}个关键词：

{text}

要求：
1. 关键词应体现案例的核心要点
2. 按重要性排序
3. 以JSON数组格式返回

格式：["关键词1", "关键词2", ...]"""

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

        except Exception as e:
            logger.error(f"关键词提取失败: {str(e)}")
            return []

    async def classify(
        self,
        text: str,
        categories: List[str]
    ) -> str:
        """MiniMax文本分类"""
        system_prompt = self._build_system_prompt(
            task="对法律案例进行分类"
        )

        user_prompt = f"""请将以下案例分类到最合适的类别中：

案例文本：
{text[:500]}

可选类别：{', '.join(categories)}

只返回类别名称，不要其他说明。"""

        try:
            category = await self.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=100
            )
            result = category.strip()
            logger.info(f"案例分类结果: {result}")
            return result

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
            logger.error(f"MiniMax健康检查失败: {str(e)}")
            return False
