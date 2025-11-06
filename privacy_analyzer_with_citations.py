"""
隐私政策分析器 - 带文献引用的版本
===========================================

本实现基于以下文献的方法论：

文献列表：
[1] "You Don't Need a University Degree to Comprehend Data Protection This Way": 
    LLM-Powered Interactive Privacy Policy Assessment
[2] A Systematic Review of Privacy Policy Literature  
[3] An Empirical Study on Oculus Virtual Reality Applications: Security and Privacy Perspectives
[4] CLEAR: Towards Contextual LLM-Empowered Privacy Policy Analysis and Risk Generation
[5] Decoding the Privacy Policies of Assistive Technologies
[6] Democratizing GDPR Compliance: AI-Driven Privacy Policy Interpretation
[7] Privacy Policy Compliance in Miniapps: An Analytical Study
[8] Toward LLM-Driven GDPR Compliance Checking for Android Apps
[9] PIPEDA Framework: https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/

完整方法论见: METHODOLOGY_WITH_CITATIONS.md
"""

import spacy
from typing import List, Dict, Any
import re


class PrivacyPolicyAnalyzer:
    """
    隐私政策分析器主类
    
    基于PIPEDA框架的隐私政策分析系统
    
    文献依据:
    - [9] PIPEDA官方框架 - 10个公平信息原则
    - [2] Systematic Review - NLP方法在隐私政策分析中的应用
    - [4] CLEAR - 上下文化的隐私分析架构
    """
    
    # PIPEDA的10个公平信息原则
    # 文献引用: [9] PIPEDA Framework
    PIPEDA_CATEGORIES = {
        "accountability": "问责性",
        "identifying_purposes": "确定目的",
        "consent": "同意",
        "limiting_collection": "限制收集",
        "limiting_use": "限制使用、披露和保留",
        "accuracy": "准确性",
        "safeguards": "安全保障",
        "openness": "公开性",
        "individual_access": "个人访问权",
        "challenging_compliance": "质疑合规性"
    }
    
    def __init__(self, model_name="en_core_web_sm"):
        """
        初始化分析器
        
        文献依据:
        - [2] Systematic Review - spaCy是隐私政策分析中广泛使用的工具
        
        参数:
            model_name: spaCy模型名称
        """
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            print(f"模型 {model_name} 未找到。请运行: python -m spacy download {model_name}")
            raise
        
        self._setup_matchers()
    
    def _setup_matchers(self):
        """
        设置模式匹配器
        
        文献依据:
        - [7] Miniapps - 基于规则的隐私政策合规性检查
        - [2] Systematic Review - 模式匹配在隐私政策分析中的应用
        """
        from spacy.matcher import Matcher
        
        self.matcher = Matcher(self.nlp.vocab)
        
        # 模式1: 数据收集
        # 引用: [7] Miniapps - 识别数据收集声明
        collection_pattern = [
            {"LEMMA": {"IN": ["collect", "gather", "obtain", "receive", "acquire"]}},
            {"POS": {"IN": ["DET", "PRON"]}, "OP": "?"},
            {"LOWER": {"IN": ["personal", "user", "your"]}, "OP": "?"},
            {"LOWER": {"IN": ["data", "information", "details", "content"]}}
        ]
        self.matcher.add("DATA_COLLECTION", [collection_pattern])
        
        # 模式2: 数据共享
        # 引用: [7] Miniapps - 识别第三方共享
        sharing_pattern = [
            {"LEMMA": {"IN": ["share", "disclose", "transfer", "provide", "send"]}},
            {"IS_SPACE": True, "OP": "*"},
            {"TEXT": {"REGEX": ".*"}, "OP": "*"},
            {"LOWER": {"IN": ["with", "to"]}},
            {"IS_SPACE": True, "OP": "*"},
            {"POS": {"IN": ["NOUN", "PROPN"]}}
        ]
        self.matcher.add("DATA_SHARING", [sharing_pattern])
        
        # 模式3: 用户同意
        # 引用: [6] GDPR-AI - GDPR第13条要求的同意机制
        consent_pattern = [
            {"LOWER": {"IN": ["consent", "permission", "authorization", "agree", "accept"]}}
        ]
        self.matcher.add("CONSENT", [consent_pattern])
    
    def segment_policy(self, text: str) -> List[str]:
        """
        将隐私政策分段
        
        文献依据:
        - [2] Systematic Review - 文本分段是隐私政策分析的标准预处理步骤
        - [4] CLEAR - 段落级分析提供更好的上下文
        
        参数:
            text: 完整的隐私政策文本
            
        返回:
            段落列表
        """
        # 按段落分割
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        # 进一步按句子分割（如果段落太长）
        segments = []
        for para in paragraphs:
            if len(para) > 500:  # 如果段落超过500字符
                doc = self.nlp(para)
                segments.extend([sent.text for sent in doc.sents])
            else:
                segments.append(para)
        
        return segments
    
    def extract_privacy_parameters(self, doc) -> Dict[str, Any]:
        """
        从文本中提取隐私参数
        
        文献依据:
        - [4] CLEAR - 上下文化的特征提取方法
        - [2] Systematic Review - 依存解析在参数提取中的应用
        
        提取的参数基于GDPR第13条要求：
        - [6] GDPR-AI: 数据类型、目的、接收者、保留期限
        
        参数:
            doc: spaCy Doc对象
            
        返回:
            包含隐私参数的字典
        """
        params = {
            "data_types": set(),
            "purposes": set(),
            "third_parties": set(),
            "retention_period": None,
            "user_rights": set(),
            "security_measures": set()
        }
        
        # 1. 使用模式匹配器
        # 引用: [7] Miniapps - 基于规则的模式识别
        matches = self.matcher(doc)
        for match_id, start, end in matches:
            span = doc[start:end]
            match_label = self.nlp.vocab.strings[match_id]
            
            if match_label == "DATA_COLLECTION":
                for token in span:
                    if token.pos_ == "NOUN":
                        params["data_types"].add(token.lemma_)
            
            elif match_label == "DATA_SHARING":
                for token in span:
                    if token.pos_ in ["NOUN", "PROPN"] and token.dep_ in ["pobj", "dobj"]:
                        params["third_parties"].add(token.text)
        
        # 2. 使用依存句法分析
        # 引用: [2] Systematic Review - 依存解析提取语义关系
        for token in doc:
            # 识别数据收集动词的宾语
            if token.lemma_ in ["collect", "gather", "process", "use", "store"]:
                for child in token.children:
                    if child.dep_ == "dobj":
                        params["data_types"].add(child.lemma_)
                        # 查找复合名词
                        for subchild in child.children:
                            if subchild.dep_ == "compound":
                                params["data_types"].add(f"{subchild.lemma_}_{child.lemma_}")
            
            # 识别目的
            # 引用: [6] GDPR-AI - GDPR第13.1(c)要求说明处理目的
            if token.lemma_ in ["for", "to"] and token.head.lemma_ in ["use", "process", "collect"]:
                for child in token.children:
                    if child.pos_ in ["NOUN", "VERB"]:
                        params["purposes"].add(child.lemma_)
        
        # 3. 识别命名实体
        # 引用: [2] Systematic Review - NER在隐私政策分析中的应用
        for ent in doc.ents:
            if ent.label_ == "ORG":
                # 组织可能是第三方
                # 引用: [7] Miniapps - 识别第三方共享实体
                params["third_parties"].add(ent.text)
            elif ent.label_ == "DATE":
                # 可能是数据保留期
                # 引用: [6] GDPR-AI - GDPR第13.2(a)要求说明保留期限
                if not params["retention_period"]:
                    params["retention_period"] = ent.text
        
        # 4. 识别用户权利相关词汇
        # 引用: [5] Assistive-Tech - 用户权利是隐私保护的关键
        # 引用: [6] GDPR-AI - GDPR第13.2(b)要求说明用户权利
        rights_keywords = {
            "access", "correct", "delete", "withdraw", "opt-out", 
            "unsubscribe", "export", "portability"
        }
        for token in doc:
            if token.lemma_ in rights_keywords:
                params["user_rights"].add(token.lemma_)
        
        # 5. 识别安全措施
        # 引用: [3] Oculus-Study - 安全措施是降低风险的关键因素
        security_keywords = {
            "encrypt", "secure", "protect", "safeguard", "ssl", 
            "https", "firewall", "authentication"
        }
        for token in doc:
            if token.lemma_ in security_keywords or token.text.lower() in security_keywords:
                params["security_measures"].add(token.text)
        
        # 转换set为list以便JSON序列化
        return {k: list(v) if isinstance(v, set) else v for k, v in params.items()}
    
    def classify_category(self, text: str, params: Dict[str, Any]) -> str:
        """
        将文本段落分类到PIPEDA类别
        
        文献依据:
        - [9] PIPEDA Framework - 10个公平信息原则
        - [7] Miniapps - 基于规则的分类方法
        
        参数:
            text: 文本段落
            params: 提取的隐私参数
            
        返回:
            PIPEDA类别
        """
        text_lower = text.lower()
        
        # 基于规则的分类
        # 引用: [7] Miniapps - 规则方法在隐私政策分析中有效
        
        # 规则1: 限制收集
        # PIPEDA原则4: 仅收集必要信息
        if any(word in text_lower for word in ["collect", "gather", "obtain", "receive"]):
            if len(params["data_types"]) > 0:
                return "limiting_collection"
        
        # 规则2: 同意
        # PIPEDA原则3: 获取知情同意
        # 引用: [6] GDPR-AI - 同意是GDPR的核心要求
        if any(word in text_lower for word in ["consent", "permission", "agree", "accept"]):
            return "consent"
        
        # 规则3: 限制使用
        # PIPEDA原则5: 限制使用、披露和保留
        # 引用: [7] Miniapps - 第三方共享是重要的隐私实践
        if any(word in text_lower for word in ["share", "disclose", "transfer", "third party", "partner"]):
            return "limiting_use"
        
        # 规则4: 安全保障
        # PIPEDA原则7: 实施适当的安全措施
        # 引用: [3] Oculus-Study - 安全措施分析
        if any(word in text_lower for word in ["secure", "protect", "encrypt", "safeguard"]):
            return "safeguards"
        
        # 规则5: 个人访问权
        # PIPEDA原则9: 用户可访问自己的信息
        # 引用: [5] Assistive-Tech - 用户权利分析
        if any(word in text_lower for word in ["access", "correct", "delete", "right"]):
            return "individual_access"
        
        # 规则6: 确定目的
        # PIPEDA原则2: 明确收集目的
        if any(word in text_lower for word in ["purpose", "use for", "used to"]):
            return "identifying_purposes"
        
        # 规则7: 准确性
        # PIPEDA原则6: 保持信息准确
        if any(word in text_lower for word in ["accurate", "update", "correct"]):
            return "accuracy"
        
        # 规则8: 问责性
        # PIPEDA原则1: 组织负责
        if any(word in text_lower for word in ["responsible", "accountability", "liable"]):
            return "accountability"
        
        # 规则9: 质疑合规性
        # PIPEDA原则10: 投诉机制
        if any(word in text_lower for word in ["contact", "questions", "concerns", "complaint"]):
            return "challenging_compliance"
        
        # 默认: 公开性
        # PIPEDA原则8: 政策透明
        return "openness"
    
    def assess_risk(self, params: Dict[str, Any], category: str) -> float:
        """
        评估隐私风险分数 (0-1)
        
        文献依据:
        - [4] CLEAR - 多因素风险评估模型
        - [3] Oculus-Study - VR应用的隐私风险因素
        - [5] Assistive-Tech - 辅助技术的风险评估
        
        风险因素基于:
        1. 数据敏感性 - [3] Oculus-Study
        2. 第三方共享 - [7] Miniapps
        3. 数据保留期限 - [6] GDPR-AI
        4. 用户控制 - [5] Assistive-Tech
        5. 安全措施 - [3] Oculus-Study
        
        返回:
            风险分数 (0.0 - 1.0)
        """
        risk_score = 0.0
        
        # 因素1: 敏感数据类型
        # 引用: [3] Oculus-Study - 识别VR中的敏感数据
        # 引用: [6] GDPR-AI - GDPR Article 9特殊类别数据
        sensitive_data = {
            "location", "financial", "health", "biometric", 
            "social_security", "password", "credit_card",
            "face", "fingerprint", "voice"  # 生物特征
        }
        data_types_str = " ".join(params["data_types"]).lower()
        if any(sensitive in data_types_str for sensitive in sensitive_data):
            risk_score += 0.3  # 权重: 0.3
        
        # 因素2: 第三方共享
        # 引用: [7] Miniapps - 第三方共享增加隐私风险
        # 引用: [4] CLEAR - 第三方数量是风险因素
        num_third_parties = len(params["third_parties"])
        if num_third_parties > 0:
            risk_score += min(0.3, num_third_parties * 0.1)  # 权重: 0.3
        
        # 因素3: 数据保留期限
        # 引用: [6] GDPR-AI - GDPR要求明确保留期限
        retention = params.get("retention_period", "")
        if retention:
            if "indefinite" in retention.lower() or "forever" in retention.lower():
                risk_score += 0.2  # 无限期保留高风险
        else:
            risk_score += 0.1  # 未明确说明也是风险
        
        # 因素4: 安全措施（减少风险）
        # 引用: [3] Oculus-Study - 安全措施降低风险
        if len(params["security_measures"]) > 0:
            risk_score -= 0.1  # 权重: -0.1
        
        # 因素5: 用户权利（减少风险）
        # 引用: [5] Assistive-Tech - 用户控制是隐私保护的关键
        if len(params["user_rights"]) >= 3:
            risk_score -= 0.1  # 权重: -0.1
        
        return max(0.0, min(1.0, risk_score))
    
    def generate_explanation(self, params: Dict[str, Any], category: str, risk_score: float) -> str:
        """
        生成可解释的分析说明
        
        文献依据:
        - [1] LLM-Assessment - 用户友好的隐私政策解释
        - [4] CLEAR - 可解释的风险分析
        
        参数:
            params: 隐私参数
            category: PIPEDA类别
            risk_score: 风险分数
            
        返回:
            解释文本
        """
        explanation_parts = []
        
        # 类别说明
        # 引用: [9] PIPEDA Framework
        category_cn = self.PIPEDA_CATEGORIES.get(category, category)
        explanation_parts.append(f"该条款属于PIPEDA框架中的「{category_cn}」类别。")
        
        # 数据收集
        # 引用: [6] GDPR-AI - GDPR第13.1(c)要求
        if params["data_types"]:
            data_list = ", ".join(params["data_types"][:5])
            explanation_parts.append(f"收集的数据类型包括: {data_list}。")
        
        # 数据使用目的
        if params["purposes"]:
            purpose_list = ", ".join(params["purposes"][:3])
            explanation_parts.append(f"数据使用目的: {purpose_list}。")
        
        # 第三方共享
        # 引用: [7] Miniapps - 第三方共享透明度
        if params["third_parties"]:
            party_count = len(params["third_parties"])
            if party_count > 0:
                explanation_parts.append(f"数据可能与 {party_count} 个第三方共享。")
        
        # 数据保留
        # 引用: [6] GDPR-AI - GDPR第13.2(a)要求
        if params["retention_period"]:
            explanation_parts.append(f"数据保留期限: {params['retention_period']}。")
        
        # 用户权利
        # 引用: [5] Assistive-Tech - 用户权利是关键保护措施
        if params["user_rights"]:
            rights_list = ", ".join(params["user_rights"])
            explanation_parts.append(f"提到的用户权利: {rights_list}。")
        
        # 安全措施
        # 引用: [3] Oculus-Study - 安全措施分析
        if params["security_measures"]:
            security_list = ", ".join(params["security_measures"][:3])
            explanation_parts.append(f"安全措施: {security_list}。")
        
        # 风险评估
        # 引用: [4] CLEAR - 风险评分和解释
        risk_level = "低" if risk_score < 0.3 else "中" if risk_score < 0.6 else "高"
        explanation_parts.append(f"\n风险评估: {risk_level}风险 (分数: {risk_score:.2f})")
        
        if risk_score > 0.5:
            explanation_parts.append("⚠️ 建议: 该条款存在较高的隐私风险，需要仔细审查。")
        
        return "\n".join(explanation_parts)
    
    def analyze_segment(self, text: str) -> Dict[str, Any]:
        """
        分析单个文本段落
        
        完整的分析流程基于:
        - [2] Systematic Review - 隐私政策分析的标准流程
        - [4] CLEAR - 上下文化分析架构
        """
        # 处理文本
        doc = self.nlp(text)
        
        # 提取参数
        params = self.extract_privacy_parameters(doc)
        
        # 分类
        category = self.classify_category(text, params)
        
        # 风险评估
        risk_score = self.assess_risk(params, category)
        
        # 生成解释
        explanation = self.generate_explanation(params, category, risk_score)
        
        return {
            "text": text,
            "category": category,
            "category_cn": self.PIPEDA_CATEGORIES.get(category, category),
            "parameters": params,
            "risk_score": risk_score,
            "explanation": explanation
        }
    
    def analyze(self, policy_text: str) -> Dict[str, Any]:
        """
        分析完整的隐私政策
        
        文献依据:
        - [2] Systematic Review - 完整的隐私政策分析流程
        - [4] CLEAR - 段落级上下文分析
        """
        # 分段
        segments = self.segment_policy(policy_text)
        
        # 分析每个段落
        segment_results = []
        for segment in segments:
            if len(segment.strip()) > 20:
                result = self.analyze_segment(segment)
                segment_results.append(result)
        
        # 生成总体统计
        total_risk = sum(r["risk_score"] for r in segment_results)
        avg_risk = total_risk / len(segment_results) if segment_results else 0
        
        # 统计类别分布
        category_counts = {}
        for result in segment_results:
            cat = result["category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        # 汇总所有数据类型和第三方
        all_data_types = set()
        all_third_parties = set()
        for result in segment_results:
            all_data_types.update(result["parameters"]["data_types"])
            all_third_parties.update(result["parameters"]["third_parties"])
        
        return {
            "summary": {
                "total_segments": len(segment_results),
                "average_risk_score": round(avg_risk, 2),
                "category_distribution": category_counts,
                "total_data_types": list(all_data_types),
                "total_third_parties": list(all_third_parties)
            },
            "segment_analyses": segment_results
        }
    
    def generate_report(self, analysis_results: Dict[str, Any], output_format="markdown") -> str:
        """生成分析报告"""
        if output_format == "markdown":
            return self._generate_markdown_report(analysis_results)
        else:
            return self._generate_text_report(analysis_results)
    
    def _generate_markdown_report(self, results: Dict[str, Any]) -> str:
        """生成Markdown格式报告，包含方法论引用"""
        summary = results["summary"]
        segments = results["segment_analyses"]
        
        report = []
        report.append("# 隐私政策分析报告\n")
        report.append("**分析方法论**: 基于PIPEDA框架和NLP技术\n")
        report.append("**文献依据**: 详见 METHODOLOGY_WITH_CITATIONS.md\n")
        
        # 总体摘要
        report.append("## 总体摘要\n")
        report.append(f"- **分析段落数**: {summary['total_segments']}")
        report.append(f"- **平均风险分数**: {summary['average_risk_score']:.2f}")
        report.append(f"- **发现的数据类型**: {len(summary['total_data_types'])} 种")
        report.append(f"- **涉及的第三方**: {len(summary['total_third_parties'])} 个\n")
        
        # 类别分布
        report.append("## PIPEDA类别分布\n")
        report.append("_基于PIPEDA的10个公平信息原则_\n")
        for category, count in sorted(summary['category_distribution'].items(), 
                                      key=lambda x: x[1], reverse=True):
            category_cn = self.PIPEDA_CATEGORIES.get(category, category)
            report.append(f"- {category_cn} ({category}): {count} 个段落")
        report.append("\n")
        
        # 收集的数据类型
        if summary['total_data_types']:
            report.append("## 收集的数据类型\n")
            for dt in sorted(summary['total_data_types'])[:20]:
                report.append(f"- {dt}")
            report.append("\n")
        
        # 涉及的第三方
        if summary['total_third_parties']:
            report.append("## 涉及的第三方\n")
            for tp in sorted(summary['total_third_parties'])[:20]:
                report.append(f"- {tp}")
            report.append("\n")
        
        # 高风险段落
        high_risk_segments = [s for s in segments if s['risk_score'] > 0.5]
        if high_risk_segments:
            report.append("## ⚠️ 高风险段落\n")
            report.append("_风险评估基于多因素模型（见METHODOLOGY_WITH_CITATIONS.md第二章）_\n")
            for i, segment in enumerate(high_risk_segments[:5], 1):
                report.append(f"### 段落 {i} (风险分数: {segment['risk_score']:.2f})\n")
                report.append(f"**原文**: {segment['text'][:200]}...\n")
                report.append(f"**分析**:\n{segment['explanation']}\n")
        
        # 详细分析
        report.append("## 详细分析\n")
        for i, segment in enumerate(segments, 1):
            report.append(f"### 段落 {i}\n")
            report.append(f"**原文**: {segment['text']}\n")
            report.append(f"**类别**: {segment['category_cn']}\n")
            report.append(f"**风险分数**: {segment['risk_score']:.2f}\n")
            report.append(f"**分析**:\n{segment['explanation']}\n")
            report.append("---\n")
        
        # 方法论说明
        report.append("\n---\n")
        report.append("## 方法论说明\n")
        report.append("本分析基于以下方法：\n")
        report.append("- **分类框架**: PIPEDA 10个公平信息原则\n")
        report.append("- **NLP技术**: 依存句法解析、命名实体识别\n")
        report.append("- **风险评估**: 多因素风险模型\n")
        report.append("- **文献支持**: 8篇学术文献（详见METHODOLOGY_WITH_CITATIONS.md）\n")
        
        return "\n".join(report)
    
    def _generate_text_report(self, results: Dict[str, Any]) -> str:
        """生成纯文本格式报告"""
        summary = results["summary"]
        segments = results["segment_analyses"]
        
        report = []
        report.append("=" * 60)
        report.append("隐私政策分析报告")
        report.append("=" * 60)
        report.append("")
        
        report.append("总体摘要:")
        report.append(f"  分析段落数: {summary['total_segments']}")
        report.append(f"  平均风险分数: {summary['average_risk_score']:.2f}")
        report.append(f"  数据类型数量: {len(summary['total_data_types'])}")
        report.append(f"  第三方数量: {len(summary['total_third_parties'])}")
        report.append("")
        
        # 详细分析
        for i, segment in enumerate(segments, 1):
            report.append("-" * 60)
            report.append(f"段落 {i}:")
            report.append(f"类别: {segment['category_cn']}")
            report.append(f"风险分数: {segment['risk_score']:.2f}")
            report.append(f"\n{segment['explanation']}")
            report.append("")
        
        return "\n".join(report)


def main():
    """示例用法"""
    print("="*70)
    print("隐私政策分析器 - 基于文献的实现")
    print("="*70)
    print("\n文献依据:")
    print("  [1] LLM-Powered Interactive Privacy Policy Assessment")
    print("  [2] A Systematic Review of Privacy Policy Literature")
    print("  [3] Oculus VR Privacy Study")
    print("  [4] CLEAR Framework")
    print("  [5] Assistive Technologies Privacy")
    print("  [6] GDPR AI-Driven Compliance")
    print("  [7] Miniapps Privacy Compliance")
    print("  [8] Android GDPR Compliance")
    print("  [9] PIPEDA Framework")
    print("\n" + "="*70 + "\n")
    
    analyzer = PrivacyPolicyAnalyzer()
    
    sample_policy = """
    We collect personal information including your name, email address, and location data.
    
    Your information may be shared with third-party advertising partners and analytics providers.
    
    You have the right to access, correct, and delete your personal information.
    
    We implement encryption and secure servers to protect your data.
    """
    
    print("正在分析隐私政策...\n")
    results = analyzer.analyze(sample_policy)
    
    report = analyzer.generate_report(results, output_format="text")
    print(report)


if __name__ == "__main__":
    main()





