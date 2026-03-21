"""
Helper utilities for Crime Journal backend services.

Provides common utility functions for AI response parsing,
text processing, date formatting, and cache key generation.
"""

import hashlib
import json
import re
from datetime import datetime, date
from typing import Any, Optional, Union


# ============================================================================
# JSON Response Parsing
# ============================================================================

def parse_json_response(
    response: Union[str, dict, Any],
    default: Optional[Any] = None,
    strict: bool = False
) -> Optional[dict]:
    """
    Parse AI response into JSON structure with robust error handling.

    Args:
        response: Raw response from AI service (string or dict)
        default: Default value to return on parse failure
        strict: If True, raise exception on parse failure

    Returns:
        Parsed JSON dict, or default value on failure

    Examples:
        >>> parse_json_response('{"key": "value"}')
        {'key': 'value'}
        >>> parse_json_response('{"key": "value"}', default={})
        {'key': 'value'}
        >>> parse_json_response('invalid json', strict=True)
        Traceback (most likely contains JSONDecodeError)
    """
    if isinstance(response, dict):
        return response

    if response is None or (isinstance(response, str) and not response.strip()):
        return default

    if not isinstance(response, str):
        response = str(response)

    try:
        return json.loads(response)
    except (json.JSONDecodeError, TypeError):
        pass

    # Extract JSON from markdown code blocks
    json_patterns = [
        r'```json\s*([\s\S]*?)\s*```',
        r'```\s*([\s\S]*?)\s*```',
        r'\{[\s\S]*\}',
    ]

    for pattern in json_patterns:
        match = re.search(pattern, response)
        if match:
            json_str = match.group(1) if '```' in pattern else match.group(0)
            try:
                return json.loads(json_str.strip())
            except (json.JSONDecodeError, TypeError):
                continue

    fixed = _fix_common_json_issues(response)
    if fixed != response:
        try:
            return json.loads(fixed)
        except (json.JSONDecodeError, TypeError):
            pass

    if strict:
        raise ValueError(f"Failed to parse JSON from response: {response[:200]}")

    return default


def _fix_common_json_issues(text: str) -> str:
    """
    Attempt to fix common JSON formatting issues.

    Args:
        text: Raw text that should be JSON

    Returns:
        Fixed text
    """
    if not text:
        return text

    text = text.lstrip('\ufeff')
    text = re.sub(r',(\s*[}\]])', r'\1', text)
    text = re.sub(r"(')([^']+)(')", lambda m: f'"{m.group(2)}"', text)
    text = re.sub(r'//.*', '', text)
    text = re.sub(r'/\*[\s\S]*?\*/', '', text)
    text = re.sub(r'(\s)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:)', r'\1"\2"\3', text)

    return text


# ============================================================================
# Text Truncation
# ============================================================================

def truncate_text(
    text: str,
    max_length: int = 1000,
    suffix: str = "...",
    word_boundary: bool = True
) -> str:
    """
    Truncate text to maximum length with proper handling.

    Args:
        text: Input text to truncate
        max_length: Maximum allowed length (including suffix)
        suffix: String to append when truncated
        word_boundary: If True, truncate at word boundary

    Returns:
        Truncated text

    Examples:
        >>> truncate_text("这是一个很长的文本", max_length=10)
        '这是一个...'
        >>> truncate_text("short text", max_length=100)
        'short text'
    """
    if not text:
        return text

    if len(text) <= max_length:
        return text

    if not word_boundary:
        return text[:max_length - len(suffix)] + suffix

    truncated = text[:max_length - len(suffix)]

    boundary_chars = re.compile(r'[\s,，.。;；!！?？\n\r\t]')
    match = boundary_chars.search(truncated[::-1])

    if match:
        cut_pos = len(truncated) - match.start()
        return text[:cut_pos].rstrip() + suffix

    return truncated.rstrip() + suffix


def truncate_text_by_tokens(
    text: str,
    max_tokens: int = 2000
) -> str:
    """
    Truncate text by approximate token count.
    Uses a simple character-based estimation (Chinese ~0.5 tokens per char,
    English ~0.25 tokens per char).

    Args:
        text: Input text
        max_tokens: Maximum token count

    Returns:
        Token-truncated text
    """
    if not text:
        return text

    def estimate_tokens(t: str) -> int:
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', t))
        other_chars = len(t) - chinese_chars
        return int(chinese_chars * 0.5 + other_chars * 0.25)

    if estimate_tokens(text) <= max_tokens:
        return text

    low, high = 0, len(text)
    while low < high:
        mid = (low + high + 1) // 2
        if estimate_tokens(text[:mid]) <= max_tokens:
            low = mid
        else:
            high = mid - 1

    return truncate_text(text, max_length=low)


# ============================================================================
# Date Formatting
# ============================================================================

def format_case_date(
    date_input: Union[str, datetime, date, int, float, None],
    output_format: str = "%Y年%m月%d日"
) -> Optional[str]:
    """
    Format legal case dates to standardized Chinese format.

    Args:
        date_input: Date as string, datetime, date, or timestamp
        output_format: Desired output format (Python strftime format)

    Returns:
        Formatted date string, or None if parsing fails

    Examples:
        >>> format_case_date("2023-12-15")
        '2023年12月15日'
        >>> format_case_date(datetime.now())
        '2026年03月21日'
        >>> format_case_date(1700000000, output_format="%Y-%m-%d")
        '2023-11-14'
    """
    if date_input is None:
        return None

    if isinstance(date_input, datetime):
        return date_input.strftime(output_format)
    if isinstance(date_input, date):
        return date_input.strftime(output_format)

    if isinstance(date_input, (int, float)):
        try:
            dt = datetime.fromtimestamp(float(date_input))
            return dt.strftime(output_format)
        except (ValueError, OSError):
            return None

    if isinstance(date_input, str):
        date_input = date_input.strip()
        if not date_input:
            return None

        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%Y年%m月%d日",
            "%Y.%m.%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y%m%d",
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(date_input, fmt)
                return dt.strftime(output_format)
            except ValueError:
                continue

        date_pattern = r'(\d{4})[年/\-.](\d{1,2})[月/\-.](\d{1,2})[日]?'
        match = re.match(date_pattern, date_input)
        if match:
            year, month, day = match.groups()
            try:
                dt = datetime(int(year), int(month), int(day))
                return dt.strftime(output_format)
            except ValueError:
                pass

    return None


def parse_case_date(date_str: str) -> Optional[datetime]:
    """
    Parse date string to datetime object for internal use.

    Args:
        date_str: Date string in various formats

    Returns:
        datetime object, or None if parsing fails
    """
    if not date_str:
        return None

    formatted = format_case_date(date_str, output_format="%Y-%m-%d")
    if formatted:
        try:
            return datetime.strptime(formatted, "%Y-%m-%d")
        except ValueError:
            pass

    return None


# ============================================================================
# Cache Key Generation
# ============================================================================

def generate_cache_key(
    prefix: str,
    *args,
    separator: str = ":",
    normalize_args: bool = True,
    **kwargs
) -> str:
    """
    Generate a consistent cache key from multiple components.

    Args:
        prefix: Key prefix (e.g., 'case', 'query', 'user')
        *args: Positional components to include in key
        separator: Separator between key components
        normalize_args: If True, sort kwargs and stringify consistently
        **kwargs: Additional key-value pairs to include

    Returns:
        Cache key string

    Examples:
        >>> generate_cache_key("case", "summary", "123")
        'case:summary:123'
        >>> generate_cache_key("query", user_id=1, page=2)
        'query:page:2:user_id:1'
        >>> generate_cache_key("case", text="很长很长的文本...", max_length=32)
        'case:max_length:32:text:a1b2c3...'
    """
    if not prefix:
        raise ValueError("Cache key prefix cannot be empty")

    parts = [prefix]

    for arg in args:
        if arg is not None:
            parts.append(_normalize_key_component(arg))

    if normalize_args:
        sorted_items = sorted(kwargs.items()) if kwargs else []
    else:
        sorted_items = kwargs.items()

    for key, value in sorted_items:
        if value is not None:
            parts.append(str(key))
            parts.append(_normalize_key_component(value))

    return separator.join(parts)


def _normalize_key_component(value: Any) -> str:
    """
    Normalize a value for use in cache key.

    Args:
        value: Any value to normalize

    Returns:
        Normalized string representation
    """
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.strftime("%Y%m%d")
    if isinstance(value, dict):
        serialized = json.dumps(value, sort_keys=True, ensure_ascii=False)
        return _hash_string(serialized)[:16]
    if isinstance(value, (list, tuple)):
        serialized = json.dumps(list(value), sort_keys=True, ensure_ascii=False)
        return _hash_string(serialized)[:16]

    str_val = str(value).strip()
    if len(str_val) > 128:
        return _hash_string(str_val)[:16]

    return str_val


def _hash_string(text: str) -> str:
    """
    Generate a short hash for a string.

    Args:
        text: Input string

    Returns:
        32-character MD5 hash hex string
    """
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def generate_cache_key_for_ai_request(
    prompt_type: str,
    case_id: Optional[str] = None,
    query_hash: Optional[str] = None,
    **params
) -> str:
    """
    Generate cache key specifically for AI service requests.

    Args:
        prompt_type: Type of AI prompt being used
        case_id: Optional case identifier
        query_hash: Optional pre-computed query hash
        **params: Additional parameters

    Returns:
        Cache key string for AI request

    Examples:
        >>> generate_cache_key_for_ai_request("case_summary", case_id="123")
        'ai:case_summary:case_id:123'
        >>> generate_cache_key_for_ai_request("query", query_hash="abc123")
        'ai:query:query_hash:abc123'
    """
    return generate_cache_key(
        f"ai:{prompt_type}",
        case_id,
        query_hash,
        **params
    )
