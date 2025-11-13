"""
简化版隐私政策分析器 - 本地NLP版本
使用 spaCy 进行本地分析，无需 LLM API

核心功能:
1. 提取数据类型 (Data Types)
2. 提取活动场景 (Activities/Purposes)
3. 建立数据-活动映射 (Data-Activity Mapping)

特点:
- 完全本地运行（无API成本）
- 基于 spaCy NLP
- 专注数据-活动映射（不做PIPEDA分类和风险评估）
"""

import spacy
from typing import List, Dict, Any, Set
import re
from collections import defaultdict


class SimpleLocalAnalyzer:
    """
    简化版本地分析器

    保留原系统的NLP能力，但简化输出
    只关注：数据收集 + 活动场景 + 映射关系
    """

    def __init__(self, model_name="en_core_web_sm"):
        """
        初始化分析器

        参数:
            model_name: spaCy模型名称
        """
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            print(f"模型 {model_name} 未找到。请运行: python -m spacy download {model_name}")
            raise

        # 数据收集相关的动词
        self.collection_verbs = {
            "collect", "gather", "obtain", "receive", "acquire", "capture",
            "record", "store", "save", "process", "use", "analyze", "access"
        }

        # 目的/活动相关的动词
        self.purpose_verbs = {
            "provide", "deliver", "offer", "enable", "support", "improve",
            "enhance", "personalize", "customize", "optimize", "develop",
            "maintain", "operate", "manage", "administer"
        }

        # 活动场景的模式（when/while/during引导的）
        self.activity_patterns = [
            r"when\s+(?:you|users?)\s+([^.,;]+)",
            r"while\s+(?:you|users?)\s+([^.,;]+)",
            r"during\s+(?:you|users?)\s+([^.,;]+)",
            r"(?:when|while|during)\s+([^.,;]{10,50})",
        ]

    def segment_policy(self, text: str) -> List[str]:
        """分段落"""
        # 按双换行符分割
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

        # 进一步按单换行分割
        segments = []
        for para in paragraphs:
            if '\n' in para:
                lines = [line.strip() for line in para.split('\n') if line.strip()]
                segments.extend(lines)
            else:
                segments.append(para)

        # 过滤太短的段落
        segments = [s for s in segments if len(s) > 20]

        return segments

    def extract_data_types(self, doc) -> Set[str]:
        """
        提取数据类型

        使用spaCy的依存句法分析和名词短语识别
        """
        data_types = set()

        # 方法1: 从收集动词的宾语提取
        for token in doc:
            if token.lemma_ in self.collection_verbs:
                # 找直接宾语
                for child in token.children:
                    if child.dep_ == "dobj":
                        # 提取完整名词短语
                        phrase = self._extract_noun_phrase(child)
                        if phrase and self._is_valid_data_type(phrase):
                            data_types.add(phrase.lower())

                        # 查找并列结构
                        for conj in child.children:
                            if conj.dep_ == "conj":
                                conj_phrase = self._extract_noun_phrase(conj)
                                if conj_phrase and self._is_valid_data_type(conj_phrase):
                                    data_types.add(conj_phrase.lower())

        # 方法2: 从名词短语中提取（在数据收集上下文中）
        for chunk in doc.noun_chunks:
            # 检查是否在收集上下文中
            sent_text = self._get_sentence_text(chunk.root, doc)
            if any(verb in sent_text.lower() for verb in self.collection_verbs):
                phrase = chunk.text.lower()
                if self._is_valid_data_type(phrase):
                    data_types.add(phrase)

        # 方法3: 使用正则提取常见模式
        text_lower = doc.text.lower()

        # "such as X, Y, and Z"
        such_as_pattern = r"such\s+as\s+([^.,;]+)"
        matches = re.finditer(such_as_pattern, text_lower)
        for match in matches:
            items_text = match.group(1)
            items = re.split(r',\s*(?:and|or)\s*|,\s*', items_text)
            for item in items:
                item = item.strip()
                if self._is_valid_data_type(item):
                    data_types.add(item)

        return data_types

    def extract_activities(self, doc) -> Set[str]:
        """
        提取活动场景

        识别用户进行的活动（when you..., while you..., during...）
        """
        activities = set()

        # 方法1: 使用正则模式
        text = doc.text
        for pattern in self.activity_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                activity = match.group(1).strip()
                # 清理activity
                activity = re.sub(r'\[\d+\]', '', activity)  # 移除引用
                if len(activity) > 5 and len(activity) < 80:
                    activities.add(activity.lower())

        # 方法2: 从目的短语提取
        for token in doc:
            if token.lemma_ in ["for", "to"]:
                # 检查前面是否有数据收集动词
                if token.head.lemma_ in self.collection_verbs | self.purpose_verbs:
                    purpose = self._extract_purpose_phrase(token, doc)
                    if purpose and len(purpose) > 3:
                        activities.add(purpose.lower())

        # 方法3: 从目的动词的宾语提取
        for token in doc:
            if token.lemma_ in self.purpose_verbs:
                for child in token.children:
                    if child.dep_ in ["dobj", "xcomp"]:
                        obj_phrase = self._extract_noun_phrase(child)
                        if obj_phrase and len(obj_phrase) > 3:
                            activities.add(obj_phrase.lower())

        return activities

    def map_data_to_activities(self, doc, data_types: Set[str], activities: Set[str]) -> List[Dict]:
        """
        建立数据-活动映射

        通过句子级别的共现关系建立映射
        """
        mappings = []

        # 为每个句子分析数据和活动的共现
        for sent in doc.sents:
            sent_text = sent.text.lower()

            # 找到该句子中出现的数据类型
            sent_data_types = [dt for dt in data_types if dt in sent_text]

            # 找到该句子中出现的活动
            sent_activities = [act for act in activities if act in sent_text]

            # 如果该句子同时包含数据和活动，建立映射
            if sent_data_types and sent_activities:
                for activity in sent_activities:
                    mappings.append({
                        "activity": activity,
                        "data_types": sent_data_types,
                        "context": sent.text[:200],  # 保留前200字符作为上下文
                        "method": "co-occurrence"
                    })

            # 如果句子中有数据但没有活动，尝试从上下文推断
            elif sent_data_types:
                # 检查句子中是否有"when/while/during"模式
                for pattern in self.activity_patterns:
                    match = re.search(pattern, sent_text, re.IGNORECASE)
                    if match:
                        activity = match.group(1).strip()
                        if len(activity) > 5:
                            mappings.append({
                                "activity": activity,
                                "data_types": sent_data_types,
                                "context": sent.text[:200],
                                "method": "pattern-matching"
                            })
                            break

        # 去重和合并相同活动的映射
        activity_data_map = defaultdict(lambda: {"data_types": set(), "contexts": []})
        for mapping in mappings:
            activity = mapping["activity"]
            activity_data_map[activity]["data_types"].update(mapping["data_types"])
            activity_data_map[activity]["contexts"].append(mapping["context"])

        # 构建最终映射列表
        final_mappings = []
        for activity, info in activity_data_map.items():
            final_mappings.append({
                "activity": activity,
                "data_types": sorted(list(info["data_types"])),
                "context": info["contexts"][0] if info["contexts"] else "",
                "num_occurrences": len(info["contexts"])
            })

        return final_mappings

    def _extract_noun_phrase(self, token) -> str:
        """提取完整的名词短语"""
        phrase_tokens = [token]

        # 收集修饰词
        for child in token.children:
            if child.dep_ in ["amod", "compound", "det", "poss", "nummod"]:
                phrase_tokens.append(child)

        # 排序并组合
        phrase_tokens.sort(key=lambda x: x.i)
        phrase = " ".join([t.text for t in phrase_tokens])

        # 清理
        phrase = re.sub(r'\[\d+\]', '', phrase).strip()

        return phrase

    def _extract_purpose_phrase(self, prep_token, doc) -> str:
        """提取目的短语"""
        purpose_tokens = []

        # 收集介词后的宾语
        for child in prep_token.children:
            if child.dep_ == "pobj":
                phrase = self._extract_noun_phrase(child)
                if phrase:
                    purpose_tokens.append(phrase)

        # 如果没找到，提取后续词
        if not purpose_tokens:
            start_idx = prep_token.i + 1
            end_idx = min(start_idx + 8, len(doc))
            for i in range(start_idx, end_idx):
                token = doc[i]
                if token.is_punct and token.text in [".", ",", ";"]:
                    break
                purpose_tokens.append(token.text)

        result = " ".join(purpose_tokens).strip()
        result = re.sub(r'\[\d+\]', '', result).strip()
        return result

    def _get_sentence_text(self, token, doc) -> str:
        """获取token所在句子的文本"""
        for sent in doc.sents:
            if sent.start <= token.i < sent.end:
                return sent.text
        return ""

    def _is_valid_data_type(self, text: str) -> bool:
        """判断是否是有效的数据类型"""
        if not text or len(text) < 2:
            return False

        text_lower = text.lower().strip()

        # 过滤噪音词
        noise_words = {
            "we", "you", "your", "our", "they", "it", "this", "that",
            "the", "a", "an", "is", "are", "be", "have", "has"
        }

        if text_lower in noise_words:
            return False

        # 必须包含字母
        if not any(c.isalpha() for c in text):
            return False

        return True

    def analyze(self, policy_text: str) -> Dict[str, Any]:
        """
        分析隐私政策

        参数:
            policy_text: 完整的隐私政策文本

        返回:
            分析结果字典
        """
        print("📄 分析隐私政策...")

        # 分段
        segments = self.segment_policy(policy_text)
        print(f"   分成 {len(segments)} 个段落")

        # 汇总所有数据和活动
        all_data_types = set()
        all_activities = set()
        all_mappings = []

        # 逐段分析
        for i, segment in enumerate(segments, 1):
            if i % 50 == 0:
                print(f"   处理第 {i}/{len(segments)} 个段落...")

            doc = self.nlp(segment)

            # 提取数据类型
            data_types = self.extract_data_types(doc)
            all_data_types.update(data_types)

            # 提取活动
            activities = self.extract_activities(doc)
            all_activities.update(activities)

            # 建立映射
            if data_types or activities:
                mappings = self.map_data_to_activities(doc, data_types, activities)
                all_mappings.extend(mappings)

        # 合并相同活动的映射
        activity_data_map = defaultdict(lambda: {"data_types": set(), "contexts": [], "occurrences": 0})
        for mapping in all_mappings:
            activity = mapping["activity"]
            activity_data_map[activity]["data_types"].update(mapping["data_types"])
            activity_data_map[activity]["contexts"].append(mapping["context"])
            activity_data_map[activity]["occurrences"] += mapping.get("num_occurrences", 1)

        # 构建最终映射
        final_mappings = []
        for activity, info in activity_data_map.items():
            final_mappings.append({
                "activity": activity,
                "data_types": sorted(list(info["data_types"])),
                "context": info["contexts"][0] if info["contexts"] else "",
                "occurrences": info["occurrences"]
            })

        # 按出现次数排序
        final_mappings.sort(key=lambda x: x["occurrences"], reverse=True)

        print("✅ 分析完成！\n")

        return {
            "summary": {
                "total_segments": len(segments),
                "total_data_types": len(all_data_types),
                "total_activities": len(all_activities),
                "total_mappings": len(final_mappings)
            },
            "data_types": sorted(list(all_data_types)),
            "activities": sorted(list(all_activities)),
            "mappings": final_mappings
        }

    def generate_report(self, results: Dict[str, Any], output_format: str = "markdown") -> str:
        """
        生成分析报告

        参数:
            results: analyze()返回的结果
            output_format: 输出格式 ("markdown" 或 "text")

        返回:
            格式化的报告
        """
        if output_format == "markdown":
            return self._generate_markdown_report(results)
        else:
            return self._generate_text_report(results)

    def _generate_markdown_report(self, results: Dict[str, Any]) -> str:
        """生成Markdown格式报告"""
        summary = results["summary"]
        data_types = results["data_types"]
        activities = results["activities"]
        mappings = results["mappings"]

        report = []
        report.append("# 隐私政策分析报告（本地NLP版本）\n")

        # 摘要
        report.append("## 📊 分析摘要\n")
        report.append(f"- **分析段落数**: {summary['total_segments']}")
        report.append(f"- **数据类型**: {summary['total_data_types']} 种")
        report.append(f"- **活动场景**: {summary['total_activities']} 个")
        report.append(f"- **数据-活动映射**: {summary['total_mappings']} 条\n")

        # 数据类型列表
        if data_types:
            report.append("## 📋 收集的数据类型\n")
            for dt in data_types[:30]:  # 最多显示30个
                report.append(f"- {dt}")
            if len(data_types) > 30:
                report.append(f"- ... 以及其他 {len(data_types) - 30} 种数据类型")
            report.append("\n")

        # 活动场景列表
        if activities:
            report.append("## 🎯 活动场景\n")
            for activity in activities[:20]:  # 最多显示20个
                report.append(f"- {activity}")
            if len(activities) > 20:
                report.append(f"- ... 以及其他 {len(activities) - 20} 个活动场景")
            report.append("\n")

        # 核心：数据-活动映射
        if mappings:
            report.append("## 🔗 数据-活动映射表\n")
            report.append("_哪些活动使用了哪些数据_\n\n")

            for mapping in mappings[:15]:  # 显示前15个最重要的映射
                report.append(f"### {mapping['activity']}\n")

                if mapping['data_types']:
                    report.append(f"**使用的数据**:")
                    for dt in mapping['data_types'][:10]:  # 每个活动最多显示10种数据
                        report.append(f"- {dt}")
                    if len(mapping['data_types']) > 10:
                        report.append(f"- ... 以及其他 {len(mapping['data_types']) - 10} 种")

                if mapping.get('context'):
                    report.append(f"\n**原文片段**: _{mapping['context']}_")

                report.append(f"\n**出现次数**: {mapping.get('occurrences', 1)}\n")
                report.append("\n---\n")

            if len(mappings) > 15:
                report.append(f"\n_... 以及其他 {len(mappings) - 15} 个映射关系_\n")

        return "\n".join(report)

    def _generate_text_report(self, results: Dict[str, Any]) -> str:
        """生成纯文本格式报告"""
        summary = results["summary"]
        mappings = results["mappings"]

        report = []
        report.append("=" * 60)
        report.append("隐私政策分析报告（本地NLP版本）")
        report.append("=" * 60)
        report.append("")

        report.append(f"分析段落数: {summary['total_segments']}")
        report.append(f"数据类型:   {summary['total_data_types']} 种")
        report.append(f"活动场景:   {summary['total_activities']} 个")
        report.append(f"数据-活动映射: {summary['total_mappings']} 条")
        report.append("")

        report.append("数据-活动映射详情:")
        report.append("-" * 60)

        for mapping in mappings[:15]:
            report.append(f"\n活动: {mapping['activity']}")
            report.append(f"使用数据: {', '.join(mapping['data_types'][:5])}")
            if len(mapping['data_types']) > 5:
                report.append(f"          ... 以及其他 {len(mapping['data_types']) - 5} 种")
            report.append(f"出现次数: {mapping.get('occurrences', 1)}")

        return "\n".join(report)


def main():
    """示例用法"""
    print("🚀 简化版本地分析器演示\n")

    # 示例隐私政策
    sample_policy = """
    用户信息收集与使用

    当您注册账号时，我们会收集您的姓名、邮箱地址和手机号码。这些信息用于创建您的账户并验证身份。

    当您浏览我们的网站时，我们会自动收集您的IP地址、浏览器类型、访问时间和浏览的页面。
    这些信息帮助我们改进网站性能和用户体验。

    当您使用位置服务时，我们会收集您的GPS定位、WiFi信息和基站信息。
    这些位置数据用于提供基于位置的服务，如附近商家推荐、导航等。

    当您购买商品时，我们会收集您的收货地址和支付信息（信用卡号、银行账户）。
    这些信息仅用于处理您的订单和完成交易。

    当您发布内容或评论时，我们会收集您发布的文字、图片和视频。
    这些内容会公开展示在平台上，供其他用户查看。
    """

    # 初始化分析器
    analyzer = SimpleLocalAnalyzer()

    # 分析
    results = analyzer.analyze(sample_policy)

    # 生成报告
    report = analyzer.generate_report(results, output_format="markdown")
    print(report)

    # 保存报告
    with open("local_analysis_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("\n✅ 报告已保存到: local_analysis_report.md")


if __name__ == "__main__":
    main()
