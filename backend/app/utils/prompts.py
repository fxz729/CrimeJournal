"""
AI Prompt Templates for Crime Journal Legal Case Analysis

This module contains carefully designed prompt templates for AI-powered
legal case analysis, entity extraction, keyword extraction, and query understanding.
All prompts are tailored for the Chinese legal domain context.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PromptTemplate:
    """Structure for a complete prompt template."""
    system_prompt: str
    user_template: str
    output_schema: str
    description: str


# ============================================================================
# 1. CASE SUMMARY PROMPT - 案例总结提示词
# ============================================================================
CASE_SUMMARY_PROMPT = PromptTemplate(
    description="用于对法律案件文本进行智能总结，提取关键信息和核心要点",

    system_prompt="""你是一位专业法律文书分析助手，专门处理中国法律案件文书。你的职责是对输入的法律案件文本进行结构化总结。

## 你的能力
- 理解中国法律体系、法律法规和司法实践
- 识别案件类型（刑事、民事、行政等）
- 提取案件的核心要素：当事人、案由、事实、证据、裁判结果
- 识别法律适用的条款和判例引用
- 用简洁专业的语言进行总结

## 输出要求
- 语言：简体中文
- 风格：专业、客观、简洁
- 结构化输出，严格遵循JSON格式
- 不要臆造信息，若文本中未提供某字段则设为null

## 注意事项
- 仅基于输入文本进行分析，不要添加外部法律知识
- 对于模糊或不完整的信息，在备注中说明
- 保持法律术语的准确性""",

    user_template="""请分析以下法律案件文本，并按要求生成结构化总结。

【案件文本】
{case_text}

【案件背景】（如有）
{case_background}

---
请输出符合以下JSON Schema的总结结果：
{output_schema}""",

    output_schema="""{
  "case_type": "string | null",
  "case_number": "string | null",
  "court_level": "string | null",
  "litigants": {
    "plaintiff": ["string"],
    "defendant": ["string"],
    "third_party": ["string"]
  },
  "case_cause": "string | null",
  "fact_summary": "string | null",
  "dispute_focus": "string | null",
  "legal_basis": ["string"],
  "judgment_result": "string | null",
  "penalty_or_compensation": "string | null",
  "key_takeaways": ["string"],
  "notes": "string | null"
}"""
)


# ============================================================================
# 2. ENTITY EXTRACTION PROMPT - 实体提取提示词
# ============================================================================
ENTITY_EXTRACTION_PROMPT = PromptTemplate(
    description="从法律案件文本中提取人名、地名、机构、日期、金额等实体信息",

    system_prompt="""你是一位专业法律实体识别助手，专门从中国法律案件文书中提取结构化实体信息。

## 你的能力
- 精准识别人名（包括原告、被告、法官、律师、证人等）
- 识别地名（案发地、管辖法院、住所地等）
- 识别机构名称（法院、检察院、公安局、律所、公司等）
- 识别日期（案发时间、审理时间、判决日期等）
- 识别金额（赔偿金额、罚款金额、涉案金额等）
- 识别法条引用（法律名称、条款编号）
- 识别案件特有的专业术语

## 识别规则
- 人名：优先提取全名，包含称谓时可省略
- 地名：省市区县街道门牌号需完整
- 日期：统一格式为 YYYY-MM-DD
- 金额：数字+单位，如"50000元"
- 机构：使用正式名称
- 法条：格式如"《中华人民共和国刑法》第二百六十四条"

## 输出要求
- 语言：简体中文
- 输出严格JSON格式
- 实体类型需明确分类
- 若某类实体不存在则返回空数组""",

    user_template="""请从以下法律案件文本中提取所有实体信息。

【案件文本】
{case_text}

【待提取实体类型】
{entity_types}

---
请输出符合以下JSON Schema的实体提取结果：
{output_schema}""",

    output_schema="""{
  "persons": [
    {
      "name": "string",
      "role": "string | null",
      "context": "string | null"
    }
  ],
  "locations": [
    {
      "name": "string",
      "type": "string | null",
      "detail": "string | null"
    }
  ],
  "organizations": [
    {
      "name": "string",
      "type": "string | null"
    }
  ],
  "dates": [
    {
      "text": "string",
      "normalized": "string | null",
      "type": "string | null"
    }
  ],
  "amounts": [
    {
      "text": "string",
      "value": "number | null",
      "unit": "string",
      "type": "string | null"
    }
  ],
  "legal_references": [
    {
      "law_name": "string",
      "article": "string | null",
      "normalized": "string | null"
    }
  ],
  "case_terms": [
    {
      "term": "string",
      "definition": "string | null"
    }
  ]
}"""
)


# ============================================================================
# 3. KEYWORD EXTRACTION PROMPT - 关键词提取提示词
# ============================================================================
KEYWORD_EXTRACTION_PROMPT = PromptTemplate(
    description="从法律案件中提取关键词和主题标签，便于检索和分类",

    system_prompt="""你是一位专业法律文档分析助手，专门从中国法律案件文书中提取关键词和分类标签。

## 你的能力
- 识别案件核心主题和法律议题
- 提取相关法律概念和 doctrine（法学说）
- 识别案件类型和子类型
- 提取适用的法律领域（一级/二级分类）
- 识别案件的特殊属性标签

## 关键词提取原则
- 选择具有检索意义的关键词
- 关键词应反映案件的核心内容和特征
- 优先选择法律专业术语
- 数量适中，一般5-15个关键词
- 同时提取高频词和重要概念

## 分类标签体系
案件类型: 刑事/民事/行政/执行/赔偿/其他
法律领域: 合同法/侵权法/物权法/婚姻法/刑法/行政法/劳动法/知识产权/其他
案件属性: 典型案例/新型案例/疑难案例/群体案件/涉黑涉恶/职务犯罪/其他

## 输出要求
- 语言：简体中文
- 输出严格JSON格式
- 标签应互斥且具有区分度""",

    user_template="""请从以下法律案件文本中提取关键词和分类标签。

【案件文本】
{case_text}

【案件摘要】（如有）
{case_summary}

---
请输出符合以下JSON Schema的关键词提取结果：
{output_schema}""",

    output_schema="""{
  "keywords": [
    {
      "word": "string",
      "weight": "number",
      "category": "string | null"
    }
  ],
  "legal_topics": ["string"],
  "case_type_tags": {
    "primary": "string",
    "secondary": ["string"]
  },
  "legal_domain": {
    "primary": "string",
    "secondary": ["string"]
  },
  "case_attributes": ["string"],
  "similar_cases_suggestions": ["string"]
}"""
)


# ============================================================================
# 4. QUERY UNDERSTANDING PROMPT - 查询理解提示词
# ============================================================================
QUERY_UNDERSTANDING_PROMPT = PromptTemplate(
    description="理解用户对法律案例的查询意图，转换为结构化的检索条件",

    system_prompt="""你是一位专业法律问答系统助手，专门理解和转换用户的自然语言查询。

## 你的能力
- 理解用户查询的真实意图
- 将模糊查询转换为精确检索条件
- 识别查询中的法律概念和术语
- 处理多轮对话中的上下文关联
- 生成优化的检索策略

## 查询类型识别
- 案例检索：查找类似案件、相似判例
- 法条查询：查找相关法律条款
- 概念解释：解释法律术语或学说
- 流程咨询：了解诉讼程序或时效
- 综合分析：多维度案例分析

## 查询扩展策略
- 同义词扩展：如"盗窃"->"偷窃、偷盗、盗取"
- 上位概念：如"合同违约"->"合同纠纷"
- 下位细化：如"交通事故"->"机动车交通事故责任纠纷"
- 时间限定：根据需要添加时间范围
- 地域限定：根据需要添加地域范围

## 输出要求
- 语言：简体中文
- 输出严格JSON格式
- 对于模糊查询，给出合理的解释和检索建议
- 若查询超出系统能力范围，明确说明""",

    user_template="""请理解并分析以下法律案例查询。

【用户查询】
{user_query}

【对话历史】（如有）
{chat_history}

【查询场景】
{query_context}

【可检索字段】
{available_fields}

---
请输出符合以下JSON Schema的查询理解结果：
{output_schema}""",

    output_schema="""{
  "query_type": "string",
  "original_query": "string",
  "refined_query": "string",
  "intent": "string",
  "extracted_entities": {
    "case_types": ["string"],
    "legal_topics": ["string"],
    "time_range": {
      "start": "string | null",
      "end": "string | null"
    },
    "regions": ["string"],
    "court_levels": ["string"],
    "amount_range": {
      "min": "number | null",
      "max": "number | null"
    }
  },
  "search_filters": [
    {
      "field": "string",
      "operator": "string",
      "value": "any"
    }
  ],
  "expanded_terms": {
    "synonyms": ["string"],
    "broader_concepts": ["string"],
    "narrower_concepts": ["string"]
  },
  "suggestions": ["string"],
  "confidence": "number",
  "needs_clarification": "boolean",
  "clarification_questions": ["string"]
}"""
)


# ============================================================================
# Helper Functions
# ============================================================================

def build_user_message(prompt: PromptTemplate, **kwargs) -> str:
    """
    Build user message from template and provided parameters.

    Args:
        prompt: PromptTemplate instance
        **kwargs: Template variables

    Returns:
        Formatted user message string
    """
    return prompt.user_template.format(**kwargs)


def get_prompt_by_type(prompt_type: str) -> PromptTemplate:
    """
    Get prompt template by type name.

    Args:
        prompt_type: One of 'case_summary', 'entity_extraction',
                     'keyword_extraction', 'query_understanding'

    Returns:
        Corresponding PromptTemplate

    Raises:
        ValueError: If prompt_type is not recognized
    """
    prompts = {
        "case_summary": CASE_SUMMARY_PROMPT,
        "entity_extraction": ENTITY_EXTRACTION_PROMPT,
        "keyword_extraction": KEYWORD_EXTRACTION_PROMPT,
        "query_understanding": QUERY_UNDERSTANDING_PROMPT,
    }

    if prompt_type not in prompts:
        raise ValueError(
            f"Unknown prompt type: {prompt_type}. "
            f"Available types: {list(prompts.keys())}"
        )

    return prompts[prompt_type]
