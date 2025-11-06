"""
隐私政策分析器 - 核心实现示例
基于文献综述中的方法论
"""

import spacy
from typing import List, Dict, Any
import re


class PrivacyPolicyAnalyzer:
    """
    隐私政策分析器主类
    
    实现基于以下方法：
    1. 依存句法解析 (Dependency Parsing)
    2. 命名实体识别 (NER)
    3. 基于规则的模式匹配
    4. 基于PIPEDA框架的分类
    """
    
    # PIPEDA的10个公平信息原则
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
        
        参数:
            model_name: spaCy模型名称（需要先下载: python -m spacy download en_core_web_sm）
        """
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            print(f"模型 {model_name} 未找到。请运行: python -m spacy download {model_name}")
            raise
        
        # 添加自定义规则
        self._setup_matchers()
    
    def _setup_matchers(self):
        """设置模式匹配器"""
        from spacy.matcher import Matcher
        
        self.matcher = Matcher(self.nlp.vocab)
        
        # 模式1: 数据收集
        # 匹配 "collect/gather/obtain [data/information]"
        collection_pattern = [
            {"LEMMA": {"IN": ["collect", "gather", "obtain", "receive", "acquire"]}},
            {"POS": {"IN": ["DET", "PRON"]}, "OP": "?"},
            {"LOWER": {"IN": ["personal", "user", "your"]}, "OP": "?"},
            {"LOWER": {"IN": ["data", "information", "details", "content"]}}
        ]
        self.matcher.add("DATA_COLLECTION", [collection_pattern])
        
        # 模式2: 数据共享
        # 匹配 "share/disclose/transfer [data] with/to [third party]"
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
        consent_pattern = [
            {"LOWER": {"IN": ["consent", "permission", "authorization", "agree", "accept"]}}
        ]
        self.matcher.add("CONSENT", [consent_pattern])
    
    def segment_policy(self, text: str) -> List[str]:
        """
        将隐私政策分段
        
        参数:
            text: 完整的隐私政策文本
            
        返回:
            段落列表
        """
        # 简单的分段：按段落分割
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
        matches = self.matcher(doc)
        for match_id, start, end in matches:
            span = doc[start:end]
            match_label = self.nlp.vocab.strings[match_id]
            
            if match_label == "DATA_COLLECTION":
                # 提取数据类型
                for token in span:
                    if token.pos_ == "NOUN":
                        params["data_types"].add(token.lemma_)
            
            elif match_label == "DATA_SHARING":
                # 提取第三方
                for token in span:
                    if token.pos_ in ["NOUN", "PROPN"] and token.dep_ in ["pobj", "dobj"]:
                        params["third_parties"].add(token.text)
        
        # 2. 使用依存句法分析
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
            if token.lemma_ in ["for", "to"] and token.head.lemma_ in ["use", "process", "collect"]:
                for child in token.children:
                    if child.pos_ in ["NOUN", "VERB"]:
                        params["purposes"].add(child.lemma_)
        
        # 3. 识别命名实体
        for ent in doc.ents:
            if ent.label_ == "ORG":
                # 组织可能是第三方
                params["third_parties"].add(ent.text)
            elif ent.label_ == "DATE":
                # 可能是数据保留期
                if not params["retention_period"]:
                    params["retention_period"] = ent.text
        
        # 4. 识别用户权利相关词汇
        rights_keywords = {
            "access", "correct", "delete", "withdraw", "opt-out", 
            "unsubscribe", "export", "portability"
        }
        for token in doc:
            if token.lemma_ in rights_keywords:
                params["user_rights"].add(token.lemma_)
        
        # 5. 识别安全措施
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
        
        参数:
            text: 文本段落
            params: 提取的隐私参数
            
        返回:
            PIPEDA类别
        """
        text_lower = text.lower()
        
        # 基于规则的分类
        if any(word in text_lower for word in ["collect", "gather", "obtain", "receive"]):
            if len(params["data_types"]) > 0:
                return "limiting_collection"
        
        if any(word in text_lower for word in ["consent", "permission", "agree", "accept"]):
            return "consent"
        
        if any(word in text_lower for word in ["share", "disclose", "transfer", "third party", "partner"]):
            return "limiting_use"
        
        if any(word in text_lower for word in ["secure", "protect", "encrypt", "safeguard"]):
            return "safeguards"
        
        if any(word in text_lower for word in ["access", "correct", "delete", "right"]):
            return "individual_access"
        
        if any(word in text_lower for word in ["purpose", "use for", "used to"]):
            return "identifying_purposes"
        
        if any(word in text_lower for word in ["accurate", "update", "correct"]):
            return "accuracy"
        
        if any(word in text_lower for word in ["responsible", "accountability", "liable"]):
            return "accountability"
        
        if any(word in text_lower for word in ["contact", "questions", "concerns"]):
            return "challenging_compliance"
        
        return "openness"  # 默认类别
    
    def assess_risk(self, params: Dict[str, Any], category: str) -> float:
        """
        评估隐私风险分数 (0-1)
        
        基于文献中的风险因素:
        - 敏感数据类型
        - 第三方共享数量
        - 数据保留期限
        - 安全措施的存在
        """
        risk_score = 0.0
        
        # 因素1: 敏感数据类型
        sensitive_data = {
            "location", "financial", "health", "biometric", 
            "social_security", "password", "credit_card"
        }
        data_types_str = " ".join(params["data_types"]).lower()
        if any(sensitive in data_types_str for sensitive in sensitive_data):
            risk_score += 0.3
        
        # 因素2: 第三方共享
        num_third_parties = len(params["third_parties"])
        if num_third_parties > 0:
            risk_score += min(0.3, num_third_parties * 0.1)
        
        # 因素3: 数据保留期限
        retention = params.get("retention_period", "")
        if retention:
            if "indefinite" in retention.lower() or "forever" in retention.lower():
                risk_score += 0.2
        else:
            risk_score += 0.1  # 未明确说明也是风险
        
        # 因素4: 安全措施（减少风险）
        if len(params["security_measures"]) > 0:
            risk_score -= 0.1
        
        # 因素5: 用户权利（减少风险）
        if len(params["user_rights"]) >= 3:
            risk_score -= 0.1
        
        return max(0.0, min(1.0, risk_score))
    
    def generate_explanation(self, params: Dict[str, Any], category: str, risk_score: float) -> str:
        """
        Generate explainable analysis description
        
        Args:
            params: Privacy parameters
            category: PIPEDA category
            risk_score: Risk score
            
        Returns:
            Explanation text
        """
        explanation_parts = []
        
        # Category description
        explanation_parts.append(f"This clause falls under the PIPEDA category of '{category}'.")
        
        # Data collection
        if params["data_types"]:
            data_list = ", ".join(params["data_types"][:5])  # Show up to 5
            explanation_parts.append(f"Data types collected include: {data_list}.")
        
        # Data purposes
        if params["purposes"]:
            purpose_list = ", ".join(params["purposes"][:3])
            explanation_parts.append(f"Data usage purposes: {purpose_list}.")
        
        # Third party sharing
        if params["third_parties"]:
            party_count = len(params["third_parties"])
            if party_count > 0:
                explanation_parts.append(f"Data may be shared with {party_count} third parties.")
        
        # Data retention
        if params["retention_period"]:
            explanation_parts.append(f"Data retention period: {params['retention_period']}.")
        
        # User rights
        if params["user_rights"]:
            rights_list = ", ".join(params["user_rights"])
            explanation_parts.append(f"User rights mentioned: {rights_list}.")
        
        # Security measures
        if params["security_measures"]:
            security_list = ", ".join(params["security_measures"][:3])
            explanation_parts.append(f"Security measures: {security_list}.")
        
        # Risk assessment
        risk_level = "Low" if risk_score < 0.3 else "Medium" if risk_score < 0.6 else "High"
        explanation_parts.append(f"\nRisk Assessment: {risk_level} risk (score: {risk_score:.2f})")
        
        if risk_score > 0.5:
            explanation_parts.append("⚠️ Recommendation: This clause presents higher privacy risks and requires careful review.")
        
        return "\n".join(explanation_parts)
    
    def analyze_segment(self, text: str) -> Dict[str, Any]:
        """
        分析单个文本段落
        
        参数:
            text: 文本段落
            
        返回:
            分析结果字典
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
        
        参数:
            policy_text: 完整的隐私政策文本
            
        返回:
            完整的分析报告
        """
        # 分段
        segments = self.segment_policy(policy_text)
        
        # 分析每个段落
        segment_results = []
        for segment in segments:
            if len(segment.strip()) > 20:  # 忽略太短的段落
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
        """
        生成分析报告
        
        参数:
            analysis_results: analyze()的返回结果
            output_format: 输出格式 ("markdown" 或 "text")
            
        返回:
            格式化的报告文本
        """
        if output_format == "markdown":
            return self._generate_markdown_report(analysis_results)
        else:
            return self._generate_text_report(analysis_results)
    
    def _generate_markdown_report(self, results: Dict[str, Any]) -> str:
        """Generate Markdown format report"""
        summary = results["summary"]
        segments = results["segment_analyses"]
        
        report = []
        report.append("# Privacy Policy Analysis Report\n")
        
        # Summary
        report.append("## Summary\n")
        report.append(f"- **Segments Analyzed**: {summary['total_segments']}")
        report.append(f"- **Average Risk Score**: {summary['average_risk_score']:.2f}")
        report.append(f"- **Data Types Found**: {len(summary['total_data_types'])} types")
        report.append(f"- **Third Parties Involved**: {len(summary['total_third_parties'])} entities\n")
        
        # Category distribution
        report.append("## PIPEDA Category Distribution\n")
        for category, count in sorted(summary['category_distribution'].items(), 
                                      key=lambda x: x[1], reverse=True):
            report.append(f"- {category}: {count} segments")
        report.append("\n")
        
        # Data types collected
        if summary['total_data_types']:
            report.append("## Data Types Collected\n")
            for dt in sorted(summary['total_data_types'])[:20]:  # Show top 20
                report.append(f"- {dt}")
            report.append("\n")
        
        # Third parties involved
        if summary['total_third_parties']:
            report.append("## Third Parties Involved\n")
            for tp in sorted(summary['total_third_parties'])[:20]:
                report.append(f"- {tp}")
            report.append("\n")
        
        # High risk segments
        high_risk_segments = [s for s in segments if s['risk_score'] > 0.5]
        if high_risk_segments:
            report.append("## ⚠️ High Risk Segments\n")
            for i, segment in enumerate(high_risk_segments[:5], 1):  # Show top 5
                report.append(f"### Segment {i} (Risk Score: {segment['risk_score']:.2f})\n")
                report.append(f"**Text**: {segment['text'][:200]}...\n")
                report.append(f"**Analysis**:\n{segment['explanation']}\n")
        
        # Detailed analysis
        report.append("## Detailed Analysis\n")
        for i, segment in enumerate(segments, 1):
            report.append(f"### Segment {i}\n")
            report.append(f"**Text**: {segment['text']}\n")
            report.append(f"**Category**: {segment['category']}\n")
            report.append(f"**Risk Score**: {segment['risk_score']:.2f}\n")
            report.append(f"**Analysis**:\n{segment['explanation']}\n")
            report.append("---\n")
        
        return "\n".join(report)
    
    def _generate_text_report(self, results: Dict[str, Any]) -> str:
        """Generate plain text format report"""
        summary = results["summary"]
        segments = results["segment_analyses"]
        
        report = []
        report.append("=" * 60)
        report.append("Privacy Policy Analysis Report")
        report.append("=" * 60)
        report.append("")
        
        report.append("Summary:")
        report.append(f"  Segments analyzed: {summary['total_segments']}")
        report.append(f"  Average risk score: {summary['average_risk_score']:.2f}")
        report.append(f"  Data types found: {len(summary['total_data_types'])}")
        report.append(f"  Third parties: {len(summary['total_third_parties'])}")
        report.append("")
        
        # Detailed analysis
        for i, segment in enumerate(segments, 1):
            report.append("-" * 60)
            report.append(f"Segment {i}:")
            report.append(f"Category: {segment['category']}")
            report.append(f"Risk score: {segment['risk_score']:.2f}")
            report.append(f"\n{segment['explanation']}")
            report.append("")
        
        return "\n".join(report)


def main():
    """
    示例用法
    """
    # 初始化分析器
    analyzer = PrivacyPolicyAnalyzer()
    
    # 示例隐私政策文本
    sample_policy = """
    Information We Collect
    
    We collect personal information that you provide to us, including your name, 
    email address, phone number, and location data. This information is used to 
    provide and improve our services.
    
    How We Share Your Information
    
    We may share your personal data with third-party service providers, advertising 
    partners, and analytics companies to help us operate our business. We also share 
    information with law enforcement when required by law.
    
    Your Rights
    
    You have the right to access, correct, or delete your personal information. 
    You may also withdraw your consent at any time by contacting us.
    
    Data Security
    
    We implement appropriate technical and organizational measures to protect your 
    personal data, including encryption and secure servers.
    """
    
    # 执行分析
    print("正在分析隐私政策...\n")
    results = analyzer.analyze(sample_policy)
    
    # 生成报告
    report = analyzer.generate_report(results, output_format="text")
    print(report)
    
    # 也可以生成Markdown报告
    # markdown_report = analyzer.generate_report(results, output_format="markdown")
    # with open("privacy_analysis_report.md", "w", encoding="utf-8") as f:
    #     f.write(markdown_report)


if __name__ == "__main__":
    main()






