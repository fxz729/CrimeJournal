#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
URL Crawler for Crime Journal Project
======================================
爬取 GDELT 犯罪新闻 URL 获取完整正文内容（纯 Python 本地实现）

Features:
- 三层爬取策略（newspaper3k → httpx+BS4 → requests+BS4）
- 断点续传（progress.json）
- 进度显示（[n/total] + tqdm）
- 内容验证（长度、语言检测）
- 错误分类记录

Usage:
    python url_crawler.py              # 全量爬取
    python url_crawler.py --test 20    # 测试模式（仅爬取前20条）
    python url_crawler.py --retry      # 重试失败的URL
"""

import os
import sys
import json
import time
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple

# 延迟导入，检查依赖
MISSING_DEPS = []

try:
    import pandas as pd
except ImportError:
    MISSING_DEPS.append("pandas")

try:
    import requests
except ImportError:
    MISSING_DEPS.append("requests")

try:
    from bs4 import BeautifulSoup
except ImportError:
    MISSING_DEPS.append("beautifulsoup4")

try:
    from tqdm import tqdm
except ImportError:
    MISSING_DEPS.append("tqdm")

# 可选依赖
try:
    import newspaper
    from newspaper import Article
    HAS_NEWSPAPER = True
except ImportError:
    HAS_NEWSPAPER = False

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

try:
    from langdetect import detect, LangDetectException
    HAS_LANGDETECT = True
except ImportError:
    HAS_LANGDETECT = False


# ============================================================================
# 配置
# ============================================================================

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_CSV = DATA_DIR / "raw" / "gdelt_crime_articles.csv"
CONTENT_DIR = DATA_DIR / "content"
MARKDOWN_DIR = CONTENT_DIR / "markdown"
METADATA_DIR = CONTENT_DIR / "metadata"
FAILED_DIR = CONTENT_DIR / "failed"
PROGRESS_FILE = CONTENT_DIR / "progress.json"
SUMMARY_FILE = CONTENT_DIR / "summary.json"
FAILED_CSV = FAILED_DIR / "failed_urls.csv"

# 爬取配置
MIN_CONTENT_LENGTH = 200      # 最小内容长度（字符）
REQUEST_TIMEOUT = 30          # 请求超时（秒）
DELAY_BETWEEN_REQUESTS = 2    # 请求间隔（秒）

# User-Agent 轮换
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]


# ============================================================================
# 工具函数
# ============================================================================

def get_user_agent() -> str:
    """随机获取 User-Agent"""
    import random
    return random.choice(USER_AGENTS)


def url_to_hash(url: str) -> str:
    """将 URL 转换为短哈希（用于文件名）"""
    return hashlib.md5(url.encode()).hexdigest()[:12]


def detect_language(text: str) -> str:
    """检测文本语言"""
    if not HAS_LANGDETECT or len(text) < 50:
        return "unknown"
    try:
        return detect(text[:1000])
    except Exception:
        return "unknown"


def clean_text(text: str) -> str:
    """清理文本（去除多余空白）"""
    if not text:
        return ""
    lines = [line.strip() for line in text.split('\n')]
    lines = [line for line in lines if line]
    return '\n\n'.join(lines)


def sanitize_filename(name: str) -> str:
    """清理文件名（去除非法字符）"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name[:80]


# ============================================================================
# 爬取类
# ============================================================================

class ContentCrawler:
    """URL 内容爬取器"""

    def __init__(self):
        self.progress: set = set()
        self.failed: List[Dict] = []
        self.stats = {
            "total": 0,
            "completed": 0,
            "failed": 0,
            "skipped": 0,
            "start_time": None,
            "end_time": None,
        }

        self._ensure_dirs()
        self._load_progress()

    def _ensure_dirs(self):
        """确保目录存在"""
        for d in [MARKDOWN_DIR, METADATA_DIR, FAILED_DIR]:
            d.mkdir(parents=True, exist_ok=True)

    def _load_progress(self):
        """加载已完成的进度"""
        if PROGRESS_FILE.exists():
            try:
                data = json.loads(PROGRESS_FILE.read_text(encoding='utf-8'))
                self.progress = set(data.get("completed", []))
                print(f"[INFO] 加载进度：已完成 {len(self.progress)} 条")
            except Exception as e:
                print(f"[WARN] 加载进度失败：{e}")
                self.progress = set()

    def _save_progress(self):
        """保存进度"""
        data = {
            "completed": list(self.progress),
            "updated": datetime.now().isoformat()
        }
        PROGRESS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    def _save_failed(self):
        """保存失败记录"""
        if not self.failed:
            return
        df = pd.DataFrame(self.failed)
        df.to_csv(FAILED_CSV, index=False, encoding='utf-8-sig')
        print(f"[INFO] 失败记录已保存：{FAILED_CSV}")

    def _save_summary(self):
        """保存汇总"""
        summary = {
            **self.stats,
            "success_rate": f"{self.stats['completed']}/{self.stats['total']} ({100*self.stats['completed']/max(self.stats['total'],1):.1f}%)",
            "markdown_files": len(list(MARKDOWN_DIR.glob("*.md"))),
            "metadata_files": len(list(METADATA_DIR.glob("*.json"))),
        }
        SUMMARY_FILE.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"[INFO] 汇总已保存：{SUMMARY_FILE}")

    # ----------------------------------------------------------------
    # 爬取方法
    # ----------------------------------------------------------------

    def fetch_with_newspaper3k(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """方法1：使用 newspaper3k 爬取"""
        if not HAS_NEWSPAPER:
            return None, "newspaper3k 未安装"

        try:
            article = Article(url, language='auto', request_timeout=REQUEST_TIMEOUT)
            article.download()
            article.parse()

            text = article.text
            if text and len(text) >= MIN_CONTENT_LENGTH:
                return clean_text(text), None
            else:
                return None, "内容过短"
        except Exception as e:
            return None, f"newspaper3k 错误: {str(e)[:50]}"

    def fetch_with_httpx(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """方法2：使用 httpx + BeautifulSoup 爬取"""
        headers = {"User-Agent": get_user_agent()}

        try:
            if HAS_HTTPX:
                with httpx.Client(timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
                    resp = client.get(url, headers=headers)
                    resp.raise_for_status()
                html = resp.text
            else:
                # 回退到 requests
                resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
                resp.raise_for_status()
                html = resp.text

            soup = BeautifulSoup(html, 'lxml')
            text = self._extract_content(soup)

            if text and len(text) >= MIN_CONTENT_LENGTH:
                return text, None
            else:
                return None, "内容提取失败"

        except Exception as e:
            return None, f"httpx/requests 错误: {str(e)[:50]}"

    def _extract_content(self, soup: BeautifulSoup) -> Optional[str]:
        """从 BeautifulSoup 中提取正文"""
        # 移除不需要的标签
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe', 'noscript']):
            tag.decompose()

        # 尝试常见的正文容器
        selectors = [
            'article',
            '[class*="content"]',
            '[class*="article"]',
            '[class*="post"]',
            '[class*="body"]',
            'main',
            '.entry-content',
            '.post-content',
            '.article-content',
        ]

        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                longest = max(elements, key=lambda e: len(e.get_text(strip=True)))
                text = longest.get_text(separator='\n', strip=True)
                if len(text) >= MIN_CONTENT_LENGTH:
                    return clean_text(text)

        # 回退到 body
        body = soup.find('body')
        if body:
            text = body.get_text(separator='\n', strip=True)
            return clean_text(text)

        return None

    def crawl_single(self, row: pd.Series) -> Tuple[Optional[str], Optional[str]]:
        """爬取单个URL，返回 (内容, 错误信息)"""
        url = row['url']

        # 方法1：newspaper3k
        content, error = self.fetch_with_newspaper3k(url)
        if content:
            return content, None

        # 方法2：httpx/requests + BS4
        content, error = self.fetch_with_httpx(url)
        if content:
            return content, None

        return None, error or "内容提取失败"

    # ----------------------------------------------------------------
    # 保存方法
    # ----------------------------------------------------------------

    def save_content(self, row: pd.Series, content: str, url_hash: str):
        """保存内容到 Markdown 和 JSON"""
        country = str(row.get('sourcecountry', 'unknown')).lower()[:15]
        title = sanitize_filename(str(row.get('title', 'untitled'))[:50])
        filename = f"{country}_{title}_{url_hash}"

        # 保存 Markdown
        md_path = MARKDOWN_DIR / f"{filename}.md"
        md_content = f"""# {row.get('title', 'Untitled')}

**Source**: {row.get('url', '')}
**Date**: {row.get('seendate', '')}
**Language**: {row.get('language', '')}
**Country**: {row.get('sourcecountry', '')}
**Domain**: {row.get('domain', '')}

---

{content}
"""
        md_path.write_text(md_content, encoding='utf-8')

        # 保存元数据 JSON
        json_path = METADATA_DIR / f"{filename}.json"
        metadata = {
            "url": row.get('url', ''),
            "url_mobile": row.get('url_mobile', ''),
            "title": row.get('title', ''),
            "seendate": row.get('seendate', ''),
            "language": row.get('language', ''),
            "sourcecountry": row.get('sourcecountry', ''),
            "domain": row.get('domain', ''),
            "content_length": len(content),
            "detected_language": detect_language(content),
            "crawled_at": datetime.now().isoformat(),
            "hash": url_hash,
        }
        json_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')

    # ----------------------------------------------------------------
    # 主运行方法
    # ----------------------------------------------------------------

    def run(self, test_mode: int = 0, retry_mode: bool = False):
        """运行爬取任务"""
        # 检查依赖
        if MISSING_DEPS:
            print(f"[ERROR] 缺少依赖: {', '.join(MISSING_DEPS)}")
            print(f"[INFO] 请运行: pip install {' '.join(MISSING_DEPS)}")
            return

        print("=" * 60)
        print("Crime Journal URL Crawler")
        print("=" * 60)
        print(f"[INFO] newspaper3k: {'OK' if HAS_NEWSPAPER else 'X (推荐安装)'}")
        print(f"[INFO] httpx: {'OK' if HAS_HTTPX else 'X (将使用 requests)'}")
        print(f"[INFO] langdetect: {'OK' if HAS_LANGDETECT else 'X'}")
        print()

        # 加载数据
        if not RAW_CSV.exists():
            print(f"[ERROR] 数据文件不存在: {RAW_CSV}")
            return

        df = pd.read_csv(RAW_CSV)
        self.stats["total"] = len(df)

        # 测试模式
        if test_mode > 0:
            df = df.head(test_mode)
            print(f"[INFO] 测试模式：仅处理前 {test_mode} 条")

        # 重试模式
        if retry_mode and FAILED_CSV.exists():
            failed_df = pd.read_csv(FAILED_CSV)
            failed_urls = set(failed_df['url'].tolist())
            df = df[df['url'].isin(failed_urls)]
            print(f"[INFO] 重试模式：处理 {len(df)} 条失败的 URL")
            self.progress = set()

        self.stats["start_time"] = datetime.now().isoformat()

        # 主循环
        iterator = tqdm(df.iterrows(), total=len(df), desc="爬取中")
        for idx, row in iterator:
            url = row['url']
            url_hash = url_to_hash(url)

            # 断点续传
            if url_hash in self.progress:
                self.stats["skipped"] += 1
                continue

            # 更新进度显示
            iterator.set_postfix({
                "完成": self.stats["completed"],
                "失败": self.stats["failed"],
            })

            # 爬取
            content, error = self.crawl_single(row)

            if content:
                self.save_content(row, content, url_hash)
                self.progress.add(url_hash)
                self.stats["completed"] += 1
            else:
                self.failed.append({
                    "url": url,
                    "title": row.get('title', ''),
                    "domain": row.get('domain', ''),
                    "language": row.get('language', ''),
                    "sourcecountry": row.get('sourcecountry', ''),
                    "error": error or "unknown",
                    "timestamp": datetime.now().isoformat(),
                })
                self.stats["failed"] += 1

            # 定期保存进度
            if (self.stats["completed"] + self.stats["failed"]) % 10 == 0:
                self._save_progress()

            time.sleep(DELAY_BETWEEN_REQUESTS)

        # 结束
        self.stats["end_time"] = datetime.now().isoformat()
        self._save_progress()
        self._save_failed()
        self._save_summary()

        # 打印统计
        print()
        print("=" * 60)
        print("爬取完成")
        print("=" * 60)
        print(f"总计: {self.stats['total']}")
        print(f"完成: {self.stats['completed']}")
        print(f"失败: {self.stats['failed']}")
        print(f"跳过: {self.stats['skipped']}")
        print(f"成功率: {100*self.stats['completed']/max(self.stats['total'],1):.1f}%")
        print()
        print(f"Markdown 文件: {MARKDOWN_DIR}")
        print(f"元数据文件: {METADATA_DIR}")
        print(f"失败记录: {FAILED_CSV}")
        print(f"汇总文件: {SUMMARY_FILE}")


# ============================================================================
# 入口
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Crime Journal URL Crawler")
    parser.add_argument("--test", type=int, default=0, help="测试模式：仅爬取前 N 条 URL")
    parser.add_argument("--retry", action="store_true", help="重试模式：仅处理失败的 URL")
    args = parser.parse_args()

    crawler = ContentCrawler()
    crawler.run(test_mode=args.test, retry_mode=args.retry)


if __name__ == "__main__":
    main()
