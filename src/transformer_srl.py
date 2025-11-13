"""
基于 Transformers 的语义角色标注 (SRL) 提取器

由于 AllenNLP 和 transformer-srl 包与当前环境不兼容（Python 3.13 + spaCy 3.7），
我们使用 Hugging Face transformers 直接实现 SRL 功能。

注意：这是一个简化版本，使用 NER 模型来近似 SRL 功能。
对于完整的 SRL，需要专门的 SRL 模型和解码层。
"""

from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
from typing import List, Dict, Set, Any
import re


class TransformerSRLExtractor:
    """基于 Transformers 的 SRL 提取器"""

    def __init__(self):
        """初始化 SRL 提取器"""
        print("初始化 Transformer SRL 提取器...")

        # 使用 NER 模型作为近似（可以识别实体，我们将其用于参数提取）
        # 这不是真正的 SRL，但可以提取相关实体
        try:
            self.ner_pipeline = pipeline(
                "ner",
                model="dslim/bert-base-NER",
                aggregation_strategy="simple"
            )
            print("✓ NER 模型加载成功")
        except Exception as e:
            print(f"✗ NER 模型加载失败: {e}")
            self.ner_pipeline = None

        # 隐私相关的动词列表
        self.privacy_verbs = {
            "collect", "gather", "obtain", "receive", "acquire",
            "share", "disclose", "provide", "transfer", "sell",
            "use", "process", "analyze", "store", "retain",
            "protect", "secure", "encrypt", "safeguard",
            "delete", "remove", "destroy"
        }

        # 数据类型关键词
        self.data_type_keywords = {
            "information", "data", "name", "email", "address", "phone",
            "location", "ip address", "cookie", "device", "identifier",
            "photo", "image", "video", "audio", "message", "content",
            "age", "gender", "preferences", "behavior", "activity",
            "password", "credential", "financial", "payment", "credit card"
        }

    def extract_privacy_parameters(self, text: str) -> Dict[str, Set[str]]:
        """
        从文本中提取隐私相关参数

        参数:
            text: 输入文本

        返回:
            包含 data_types, third_parties, purposes 的字典
        """
        result = {
            "data_types": set(),
            "third_parties": set(),
            "purposes": set()
        }

        if not self.ner_pipeline:
            return result

        try:
            # 使用 NER 提取实体
            entities = self.ner_pipeline(text)

            for entity in entities:
                entity_text = entity['word'].lower().strip()
                entity_type = entity['entity_group']

                # 组织名称 → 第三方
                if entity_type in ['ORG', 'ORGANIZATION']:
                    result["third_parties"].add(entity_text)

                # 其他实体可能是数据类型
                elif entity_type in ['PER', 'PERSON', 'LOC', 'LOCATION', 'MISC']:
                    # 检查是否与数据类型相关
                    if any(keyword in entity_text for keyword in self.data_type_keywords):
                        result["data_types"].add(entity_text)

            # 使用规则提取数据类型（补充 NER）
            text_lower = text.lower()
            for keyword in self.data_type_keywords:
                if keyword in text_lower:
                    result["data_types"].add(keyword)

            # 提取目的（简单规则匹配）
            purpose_patterns = [
                r"for ([\w\s]+?) purposes?",
                r"to ([\w\s]+?) your",
                r"in order to ([\w\s]+)",
            ]

            for pattern in purpose_patterns:
                matches = re.findall(pattern, text_lower)
                for match in matches:
                    if len(match.strip().split()) <= 5:  # 限制长度
                        result["purposes"].add(match.strip())

        except Exception as e:
            print(f"提取参数时出错: {e}")

        return result

    def analyze_sentence(self, text: str) -> List[Dict[str, Any]]:
        """
        分析句子的语义角色（简化版）

        参数:
            text: 输入句子

        返回:
            角色列表
        """
        if not self.ner_pipeline:
            return []

        try:
            entities = self.ner_pipeline(text)

            # 将 NER 结果转换为类似 SRL 的格式
            roles = []
            for entity in entities:
                role = {
                    "text": entity['word'],
                    "type": entity['entity_group'],
                    "score": entity['score'],
                    "start": entity['start'],
                    "end": entity['end']
                }
                roles.append(role)

            return roles

        except Exception as e:
            print(f"分析句子时出错: {e}")
            return []


def test_transformer_srl():
    """测试 Transformer SRL 提取器"""
    print("\n" + "="*70)
    print("测试 Transformer SRL 提取器")
    print("="*70 + "\n")

    extractor = TransformerSRLExtractor()

    # 测试句子
    test_sentences = [
        "We collect your name, email address, and location data.",
        "We share your information with Facebook and Google for advertising purposes.",
        "You can delete your personal data at any time.",
        "We use cookies to analyze your behavior and preferences."
    ]

    print("\n测试参数提取:\n")
    for sentence in test_sentences:
        print(f"句子: {sentence}")
        params = extractor.extract_privacy_parameters(sentence)
        print(f"  数据类型: {params['data_types']}")
        print(f"  第三方: {params['third_parties']}")
        print(f"  目的: {params['purposes']}")
        print()


if __name__ == "__main__":
    test_transformer_srl()
