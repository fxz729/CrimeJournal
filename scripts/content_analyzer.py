#!/ GDELT 内容分析脚本
# 批量爬取 + 多语言处理

import pandas as pd
import json
import os
from collections import Counter
from datetime import datetime

class ContentAnalyzer:
    def __init__(self, content_dir="D:/Projects/CrimeJournal/data/content/markdown"):
        self.content_dir = content_dir
        self.output_dir = "D:/Projects/CrimeJournal/outputs/content_analysis"
        os.makedirs(self.output_dir, exist_ok_ok)
        self.results = []

    def load_content(self):
        """加载所有爬取的内容"""
        content_files = [f for f in os.listdir(self.content_dir) if f.endswith('.md')]
        print(f"Found {len(content_files)} content files")
        return content_files

    def analyze_content(self, file_path):
        """分析单个内容文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取元数据
        metadata = {}
        if '---' in content:
            parts = content.split('---', 1)
            header = parts[0]
            content = parts[1] if len(parts) > 1 else content

            # 解析元数据
            for line in header.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()

        return {
            'content': content,
            'metadata': metadata,
            'word_count': len(content.split())
        }

    def classify_crime(self, text):
        """基于关键词分类犯罪类型"""
        text_lower = text.lower()

        crime_patterns = {
            'murder': ['murder', 'homicide', 'killing', 'assassin', 'shot', 'stabbed', 'muerto', 'asesinato', 'tötung', '谋杀', '杀害'],
            'theft': ['theft', 'robbery', 'burglary', 'stolen', 'robar', 'hurto', 'robo', 'robo', '盗窃', '抢劫'],
            'assault': ['assault', 'attack', 'violence', 'fight', 'ataque', 'asalto', '袭击', '暴力'],
            'fraud': ['fraud', 'scam', 'embezzlement', 'swindle', 'estafa', 'fraude', '诈骗', '欺诈'],
            'kidnapping': ['kidnapping', 'abduction', 'missing', 'secuestro', 'rapto', '绑架', '绑架', '失踪'],
            'terrorism': ['terrorism', 'extremist', 'attack', 'terror', 'terrorismo'],
            'corruption': ['corruption', 'bribery', 'embezzlement', 'corrupción', '腐败', '贿赂']
        }

        for crime_type, patterns in crime_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return crime_type

        return 'other'

    def analyze_sentiment(self, text):
        """简单情感分析"""
        text_lower = text.lower()

        negative_words = ['murder', 'kill', 'death', 'victim', 'attack', 'violence', 'terror', 'fear', 'pain', 'tragedy']
        neutral_words = ['arrest', 'investigate', 'reported', 'police', 'court', 'trial']

        score = 0
        for word in negative_words:
            if word in text_lower:
                score -= 1
        for word in neutral_words:
            if word in text_lower:
                score += 0

        if score < -0.5:
            return 'negative'
        elif score > 0.5:
            return 'positive'
        else:
            return 'neutral'

    def run_analysis(self):
        """运行完整分析"""
        content_files = self.load_content()

        print(f"\n[1/4] Analyzing {len(content_files)} content files...")

        for i, file in enumerate(content_files):
            print(f"[{i+1}/{len(content_files)}] Processing: {file}")

            try:
                data = self.analyze_content(os.path.join(self.content_dir, file))

                result = {
                    'file': file,
                    'crime_type': self.classify_crime(data['content']),
                    'sentiment': self.analyze_sentiment(data['content']),
                    'word_count': data['word_count'],
                    'language': data['metadata'].get('Language', 'unknown')
                }
                self.results.append(result)
            except Exception as e:
                print(f"Error processing {file}: {e}")

        # 保存结果
        self.save_results()

        print(f"\n=== Analysis Complete ===")
        self.print_summary()
    def save_results(self):
        """保存分析结果"""
        output_file = os.path.join(self.output_dir, 'analysis_results.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"Saved to: {output_file}")

    def print_summary(self):
        """打印分析摘要"""
        df = pd.DataFrame(self.results)

        print(f"\n--- Crime Type Distribution ---")
        print(df['crime_type'].value_counts())

        print(f"\n--- Sentiment Distribution ---")
        print(df['sentiment'].value_counts())

        print(f"\n--- Language Distribution ---")
        print(df['language'].value_counts())

        print(f"\n--- Word Count Stats ---")
        print(f"Average: {df['word_count'].mean():.0f}")
        print(f"Max: {df['word_count'].max()}")
        print(f"Min: {df['word_count'].min()}")

if __name__ == "__main__":
    analyzer = ContentAnalyzer()
    analyzer.run_analysis()
