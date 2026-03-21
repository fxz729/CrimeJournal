#!/usr/bin/env python3
"""
Crime Journal 数据统计脚本
统计 679 个案例的关键信息：语言、国家、内容长度、犯罪类型
"""

import json
import os
from collections import Counter
from pathlib import Path
import re

# 路径配置
BASE_DIR = Path(__file__).parent.parent
METADATA_DIR = BASE_DIR / "data" / "content" / "metadata"
MARKDOWN_DIR = BASE_DIR / "data" / "content" / "markdown"
OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 犯罪类型关键词（多语言）
CRIME_KEYWORDS = {
    "murder": ["murder", "homicide", "killing", "killed", "asesinato", "asesinado", "asesinada","crimen", "homicidio", "mord", "getötet", "убийство", "谋杀", "杀人","mató", "mataron", "asesinaron"],
    "theft": ["theft", "robbery", "burglary", "stolen", "robo", "hurto", "robbery","diebstahl", "gestohlen", "кража", "盗窃", "偷窃", "robó", "robaron"],
    "fraud": ["fraud", "scam", "embezzlement", "fraude", "estafa", "betrug","мошенничество", "诈骗", "欺诈", "corrupción", "corruption"],
    "assault": ["assault", "attack", "violence", "ataque", "asalto", "agresión","angriff", "нападение", "袭击", "攻击", "agredió"],
    "drug": ["drug", "narcotic", "cocaine", "marijuana", "narcotráfico","droga", "drogen", "наркотик", "毒品", "毒贩", "narco"],
    "corruption": ["corruption", "bribery", "soborno", "cohecho", "korruption","коррупция", "腐败", "贪污", "bribe"],
    "terrorism": ["terrorism", "terrorist", "terrorismo", "terrorismus","терроризм", "恐怖主义", "terrorista"],
    "trafficking": ["trafficking", "smuggling", "tráfico", "trata", "schmuggel","торговля", "贩卖", "人口贩卖", "contrabando"],
    "sexual": ["sexual", "rape", "abuse", "abuso", "sexual", "sexuel","сексуал", "性侵", "强奸", "violación"],
    "cybercrime": ["cyber", "hacking", "phishing", "ciber", "hack", "кибер","网络犯罪", "黑客"]
}

def load_metadata():
    """加载所有 metadata JSON 文件"""
    metadata_list = []
    for json_file in METADATA_DIR.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                metadata_list.append(data)
        except Exception as e:
            print(f"Error loading {json_file}: {e}")
    return metadata_list

def load_markdown_content(filename):
    """读取 markdown 文件内容"""
    md_file = MARKDOWN_DIR / filename
    if md_file.exists():
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return ""
    return ""

def detect_crime_types(title, content):
    """基于关键词检测犯罪类型"""
    text = (title + " " + content[:2000]).lower()  # 标题 + 前2000字符
    detected = []

    for crime_type, keywords in CRIME_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text:
                detected.append(crime_type)
                break

    return detected if detected else ["unidentified"]

def calculate_statistics(metadata_list):
    """计算统计数据"""
    stats = {
        "total_cases": len(metadata_list),
        "language_distribution": Counter(),
        "country_distribution": Counter(),
        "content_lengths": [],
        "crime_type_distribution": Counter(),
        "domain_distribution": Counter(),
        "date_distribution": Counter()
    }

    print(f"正在处理 {len(metadata_list)} 个案例...")

    for i, meta in enumerate(metadata_list):
        if (i + 1) % 100 == 0:
            print(f"  已处理 {i + 1}/{len(metadata_list)} 个案例")

        # 语言分布
        lang = meta.get("language", "Unknown")
        stats["language_distribution"][lang] += 1

        # 国家分布
        country = meta.get("sourcecountry", "Unknown")
        stats["country_distribution"][country] += 1

        # 内容长度
        content_length = meta.get("content_length", 0)
        if content_length > 0:
            stats["content_lengths"].append(content_length)

        # 域名分布
        domain = meta.get("domain", "Unknown")
        stats["domain_distribution"][domain] += 1

        # 日期分布
        seendate = meta.get("seendate", "")
        if seendate:
            date_str = seendate[:8]  # YYYYMMDD
            stats["date_distribution"][date_str] += 1

        # 犯罪类型检测
        title = meta.get("title", "")
        if not isinstance(title, str):
            title = ""
        # 尝试读取对应的 markdown 文件
        hash_val = meta.get("hash", "")
        sourcecountry = meta.get("sourcecountry", "")
        if not isinstance(sourcecountry, str):
            sourcecountry = ""
        md_filename = f"{sourcecountry.lower()}_{title[:50]}_{hash_val}.md"
        content = load_markdown_content(md_filename)

        crime_types = detect_crime_types(title, content)
        for ct in crime_types:
            stats["crime_type_distribution"][ct] += 1

    return stats

def save_statistics(stats):
    """保存统计数据"""
    # 计算内容长度统计
    lengths = stats["content_lengths"]
    length_stats = {}
    if lengths:
        length_stats = {
            "count": len(lengths),
            "mean": sum(lengths) / len(lengths),
            "median": sorted(lengths)[len(lengths) // 2],
            "min": min(lengths),
            "max": max(lengths),
            "total_chars": sum(lengths)
        }

    # 保存完整统计（JSON）
    full_stats = {
        "total_cases": stats["total_cases"],
        "language_distribution": dict(stats["language_distribution"].most_common(50)),
        "country_distribution": dict(stats["country_distribution"].most_common(50)),
        "content_length_stats": length_stats,
        "crime_type_distribution": dict(stats["crime_type_distribution"].most_common(20)),
        "domain_distribution": dict(stats["domain_distribution"].most_common(30)),
        "date_distribution": dict(stats["date_distribution"])
    }

    with open(OUTPUT_DIR / "data_statistics.json", 'w', encoding='utf-8') as f:
        json.dump(full_stats, f, ensure_ascii=False, indent=2)

    # 保存语言分布（CSV）
    with open(OUTPUT_DIR / "language_distribution.csv", 'w', encoding='utf-8') as f:
        f.write("language,count,percentage\n")
        total = stats["total_cases"]
        for lang, count in stats["language_distribution"].most_common(50):
            pct = round(count / total * 100, 2)
            f.write(f'"{lang}",{count},{pct}\n')

    # 保存国家分布（CSV）
    with open(OUTPUT_DIR / "country_distribution.csv", 'w', encoding='utf-8') as f:
        f.write("country,count,percentage\n")
        total = stats["total_cases"]
        for country, count in stats["country_distribution"].most_common(50):
            pct = round(count / total * 100, 2)
            f.write(f'"{country}",{count},{pct}\n')

    # 保存犯罪类型分布（CSV）
    with open(OUTPUT_DIR / "crime_type_distribution.csv", 'w', encoding='utf-8') as f:
        f.write("crime_type,count,percentage\n")
        total = stats["total_cases"]
        for crime_type, count in stats["crime_type_distribution"].most_common(20):
            pct = round(count / total * 100, 2)
            f.write(f'"{crime_type}",{count},{pct}\n')

    return full_stats

def print_summary(stats):
    """打印统计摘要"""
    print("\n" + "="*60)
    print("Crime Journal 数据统计摘要")
    print("="*60)

    print(f"\n总案例数: {stats['total_cases']}")

    # 语言分布 Top 15
    print("\n语言分布 Top 15:")
    total = stats["total_cases"]
    for i, (lang, count) in enumerate(stats["language_distribution"].most_common(15), 1):
        pct = round(count / total * 100, 1)
        print(f"  {i:2d}. {lang}: {count} ({pct}%)")

    # 国家分布 Top 20
    print("\n国家分布 Top 20:")
    for i, (country, count) in enumerate(stats["country_distribution"].most_common(20), 1):
        pct = round(count / total * 100, 1)
        print(f"  {i:2d}. {country}: {count} ({pct}%)")

    # 犯罪类型分布
    print("\n犯罪类型分布:")
    for crime_type, count in stats["crime_type_distribution"].most_common(15):
        pct = round(count / total * 100, 1)
        print(f"  - {crime_type}: {count} ({pct}%)")

    # 内容长度统计
    lengths = stats["content_lengths"]
    if lengths:
        print(f"\n内容长度统计:")
        print(f"  - 平均字数: {sum(lengths)/len(lengths):.0f} 字符")
        print(f"  - 中位数: {sorted(lengths)[len(lengths)//2]} 字符")
        print(f"  - 最大值: {max(lengths)} 字符")
        print(f"  - 最小值: {min(lengths)} 字符")

def main():
    print("Crime Journal 数据统计脚本")
    print("="*60)

    # 加载 metadata
    print("\n正在加载 metadata 文件...")
    metadata_list = load_metadata()
    print(f"已加载 {len(metadata_list)} 个 metadata 文件")

    # 计算统计数据
    print("\n正在计算统计数据...")
    stats = calculate_statistics(metadata_list)

    # 保存统计数据
    print("\n正在保存统计数据...")
    full_stats = save_statistics(stats)
    print(f"统计数据已保存到: {OUTPUT_DIR}")

    # 打印摘要
    print_summary(stats)

    print("\n" + "="*60)
    print("统计完成！")
    print("="*60)

if __name__ == "__main__":
    main()
