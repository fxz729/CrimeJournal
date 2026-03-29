"""
MiniMax AI服务实现

使用OpenAI兼容API格式
文档: https://www.minimaxi.com/document/Chinese
"""
import time
import json
import re
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
            timeout=httpx.Timeout(180.0, connect=10.0)  # 180s for large texts with think mode
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
            # MiniMax M2.x 模型默认开启 thinking，返回内容含<think>...</think> 标签
            # 去掉标签只保留最终回答内容
            result = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL).strip()
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
                max_tokens=5000  # increased for M2.x think mode
            )
            # 去掉 markdown 代码块包装
            response = re.sub(r'```(?:json)?\s*', '', response.strip())
            response = re.sub(r'\s*```', '', response)
            entities = json.loads(response)
            logger.info(f"成功提取{sum(len(v) for v in entities.values())}个实体")
            return entities

        except json.JSONDecodeError as e:
            logger.error(f"实体提取JSON解析失败: {str(e)}")
            raise RuntimeError(f"AI返回了无效的JSON格式: {str(e)}")
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
                max_tokens=max_length * 8  # 8x to accommodate think tags + answer
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
                max_tokens=2000
            )
            # 去掉 markdown 代码块包装
            response = re.sub(r'```(?:json)?\s*', '', response.strip())
            response = re.sub(r'\s*```', '', response)
            keywords = json.loads(response)
            logger.info(f"成功提取{len(keywords)}个关键词")
            return keywords[:top_n]

        except json.JSONDecodeError as e:
            logger.error(f"关键词提取JSON解析失败: {str(e)}")
            raise RuntimeError(f"AI返回了无效的JSON格式: {str(e)}")
        except Exception as e:
            logger.error(f"关键词提取失败: {str(e)}")
            raise

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
                max_tokens=1000  # increased for M2.x think mode
            )
            result = category.strip()
            logger.info(f"案例分类结果: {result}")
            return result

        except Exception as e:
            logger.error(f"案例分类失败: {str(e)}")
            raise

    async def format_text(
        self,
        text: str,
    ) -> str:
        """
        使用MiniMax整理优化法律案例文本

        保持原文结构，只做格式整理：修正换行、清理乱码、统一标点、
        标注段落、识别章节结构等。不改写内容，只优化可读性。

        Args:
            text: 待整理的原始文本

        Returns:
            整理优化后的文本
        """
        system_prompt = self._build_system_prompt(
            task="整理优化法律案例文本的格式与可读性",
            context="请仅整理格式，不要改写内容或添加解释"
        )

        user_prompt = f"""请对以下法律案例文本进行格式整理与优化。要求：

1. 保持原文所有内容不变，不删改任何文字
2. 统一换行符，每段之间空一行
3. 清除原文中明显的乱码、无效字符、异常空格
4. 统一标点符号格式（全角/半角保持原样，标点后统一加一个空格）
5. 如果原文有明显的大写标题或章节标记（如 "I.", "II.", "A.", "B." 或全大写短语），保留并适当强调
6. 如果段落过长（超过500字），在自然语义处拆分
7. 在文件开头保留原始案号、当事人、法院等基本信息行（如果存在）
8. 开头加一行分隔线：{'='*60}

只返回整理后的文本，不要添加任何说明。

原始文本：
{text}

整理后的文本："""

        try:
            formatted = await self.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.2,  # 低温度保证格式一致性
                max_tokens=8000,
            )
            logger.info(f"成功整理文本，长度: {len(formatted)}（原始: {len(text)}）")
            return formatted.strip()

        except Exception as e:
            logger.error(f"文本整理失败: {str(e)}")
            raise

    async def health_check(self) -> bool:
        """健康检查"""
        try:
            response = await self.generate(
                prompt="Respond with OK",
                max_tokens=50
            )
            return len(response) > 0
        except Exception as e:
            logger.error(f"MiniMax健康检查失败: {str(e)}")
            return False

    async def translate(
        self,
        text: str,
        target_language: str = "English",
        source_language: str = "auto",
    ) -> str:
        """
        使用MiniMax翻译文本

        Args:
            text: 待翻译文本
            target_language: 目标语言
            source_language: 源语言，auto表示自动检测

        Returns:
            翻译后的文本
        """
        system_prompt = self._build_system_prompt(
            task="翻译法律文本",
            context="请准确翻译法律案例文本，保持专业术语和含义"
        )

        source_hint = f"源语言: {source_language}，" if source_language != "auto" else ""

        user_prompt = f"""请将以下法律案例文本翻译成{source_hint}目标语言: {target_language}。

要求：
1. 保持原文的专业法律术语
2. 保持判决要点和关键信息的准确性
3. 只返回翻译结果，不要添加任何说明

案例文本：
{text}

翻译结果："""

        try:
            translated = await self.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=16000,  # increased for M2.x think mode
            )
            logger.info(f"成功翻译文本至 {target_language}，长度: {len(translated)}")
            return translated.strip()
        except Exception as e:
            logger.error(f"翻译失败: {str(e)}")
            raise
