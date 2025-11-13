"""
语义角色标注（SRL）分析器
用于更准确地提取隐私政策中的数据类型、第三方、目的等参数

文献依据：
"Beyond the Text: Analysis of Privacy Statements through Syntactic and Semantic Role Labeling"
"""

import spacy
from typing import List, Dict, Any, Set
import re


class SemanticRoleAnalyzer:
    """
    基于spaCy依存解析的语义角色分析器

    虽然不是完整的SRL，但利用spaCy的依存解析可以实现类似效果：
    - ARG0 (施事) → nsubj (主语)
    - ARG1 (受事) → dobj (直接宾语)
    - ARG2 (接收者) → pobj, iobj (介词宾语、间接宾语)
    """

    def __init__(self, nlp):
        """
        初始化分析器

        参数:
            nlp: spaCy模型实例
        """
        self.nlp = nlp

        # 隐私相关的动词及其角色
        self.privacy_verbs = {
            # 数据收集动词
            "collect": {"ARG0": "collector", "ARG1": "data", "ARG2": "source"},
            "gather": {"ARG0": "collector", "ARG1": "data", "ARG2": "source"},
            "obtain": {"ARG0": "collector", "ARG1": "data", "ARG2": "source"},
            "receive": {"ARG0": "collector", "ARG1": "data", "ARG2": "source"},
            "acquire": {"ARG0": "collector", "ARG1": "data", "ARG2": "source"},

            # 数据使用动词
            "use": {"ARG0": "user", "ARG1": "data", "ARG2": "purpose"},
            "process": {"ARG0": "processor", "ARG1": "data", "ARG2": "purpose"},
            "analyze": {"ARG0": "analyzer", "ARG1": "data", "ARG2": "purpose"},

            # 数据共享动词
            "share": {"ARG0": "sharer", "ARG1": "data", "ARG2": "recipient"},
            "disclose": {"ARG0": "discloser", "ARG1": "data", "ARG2": "recipient"},
            "transfer": {"ARG0": "transferer", "ARG1": "data", "ARG2": "recipient"},
            "provide": {"ARG0": "provider", "ARG1": "data", "ARG2": "recipient"},
            "send": {"ARG0": "sender", "ARG1": "data", "ARG2": "recipient"},

            # 数据保护动词
            "protect": {"ARG0": "protector", "ARG1": "data", "ARG2": "method"},
            "secure": {"ARG0": "securer", "ARG1": "data", "ARG2": "method"},
            "encrypt": {"ARG0": "encrypter", "ARG1": "data", "ARG2": "method"},
            "safeguard": {"ARG0": "safeguarder", "ARG1": "data", "ARG2": "method"},
        }

    def extract_semantic_roles(self, text: str) -> List[Dict[str, Any]]:
        """
        从文本中提取语义角色

        参数:
            text: 输入文本

        返回:
            语义角色列表，每个包含 {verb, ARG0, ARG1, ARG2, ...}
        """
        doc = self.nlp(text)
        roles_list = []

        for token in doc:
            # 检查是否是隐私相关动词
            if token.lemma_ in self.privacy_verbs:
                roles = self._extract_roles_for_verb(token, doc)
                if roles:
                    roles_list.append(roles)

        return roles_list

    def _extract_roles_for_verb(self, verb_token, doc) -> Dict[str, Any]:
        """
        为特定动词提取语义角色

        利用spaCy的依存解析：
        - nsubj/nsubjpass → ARG0 (施事)
        - dobj → ARG1 (受事)
        - pobj (介词宾语) → ARG2 (通常是目的或接收者)
        """
        roles = {
            "verb": verb_token.lemma_,
            "verb_text": verb_token.text,
            "ARG0": None,  # 主语/施事
            "ARG1": None,  # 直接宾语/受事
            "ARG2": None,  # 介词宾语/目的/接收者
            "ARG_PURPOSE": None,  # 目的
            "ARG_TEMPORAL": None,  # 时间
        }

        # 提取ARG0 - 主语
        for child in verb_token.children:
            if child.dep_ in ["nsubj", "nsubjpass"]:
                roles["ARG0"] = self._extract_phrase(child, doc)

        # 提取ARG1 - 直接宾语
        for child in verb_token.children:
            if child.dep_ == "dobj":
                roles["ARG1"] = self._extract_phrase(child, doc)

        # 提取ARG2和其他 - 介词短语
        for child in verb_token.children:
            if child.dep_ == "prep":
                prep = child.text.lower()
                pobj = self._get_prep_object(child, doc)

                if pobj:
                    if prep in ["with", "to"]:
                        # "share with partners", "transfer to servers"
                        roles["ARG2"] = pobj
                    elif prep in ["for"]:
                        # "use for marketing"
                        roles["ARG_PURPOSE"] = pobj
                    elif prep in ["during", "when", "while"]:
                        # "collect during registration"
                        roles["ARG_TEMPORAL"] = pobj

        # 如果有to不定式，提取目的
        for child in verb_token.children:
            if child.dep_ == "xcomp" or child.dep_ == "advcl":
                purpose = self._extract_phrase(child, doc)
                if purpose:
                    roles["ARG_PURPOSE"] = purpose

        return roles

    def _extract_phrase(self, token, doc) -> str:
        """
        提取以token为核心的完整短语

        使用spaCy的subtree功能
        """
        # 获取token的所有子树（包括修饰词、复合词等）
        subtree_tokens = list(token.subtree)

        # 按位置排序
        subtree_tokens.sort(key=lambda t: t.i)

        # 组合成短语
        phrase = " ".join([t.text for t in subtree_tokens])

        # 清理
        phrase = re.sub(r'\s+', ' ', phrase).strip()
        phrase = re.sub(r'\[\d+\]', '', phrase)  # 移除引用标记

        return phrase if phrase else None

    def _get_prep_object(self, prep_token, doc) -> str:
        """获取介词的宾语"""
        for child in prep_token.children:
            if child.dep_ == "pobj":
                return self._extract_phrase(child, doc)
        return None

    def extract_privacy_parameters(self, text: str) -> Dict[str, Set[str]]:
        """
        从文本中提取隐私参数（使用SRL）

        参数:
            text: 隐私政策文本

        返回:
            包含数据类型、第三方、目的等的字典
        """
        params = {
            "data_types": set(),
            "third_parties": set(),
            "purposes": set(),
            "collectors": set(),
            "methods": set(),
        }

        # 提取语义角色
        roles_list = self.extract_semantic_roles(text)

        for roles in roles_list:
            verb = roles["verb"]

            # 根据动词类型提取不同参数
            if verb in ["collect", "gather", "obtain", "receive", "acquire"]:
                # ARG1是收集的数据
                if roles["ARG1"]:
                    params["data_types"].add(roles["ARG1"])
                # ARG0是收集者
                if roles["ARG0"]:
                    params["collectors"].add(roles["ARG0"])

            elif verb in ["use", "process", "analyze"]:
                # ARG1是使用的数据
                if roles["ARG1"]:
                    params["data_types"].add(roles["ARG1"])
                # ARG2或ARG_PURPOSE是使用目的
                if roles["ARG2"]:
                    params["purposes"].add(roles["ARG2"])
                if roles["ARG_PURPOSE"]:
                    params["purposes"].add(roles["ARG_PURPOSE"])

            elif verb in ["share", "disclose", "transfer", "provide", "send"]:
                # ARG1是共享的数据
                if roles["ARG1"]:
                    params["data_types"].add(roles["ARG1"])
                # ARG2是接收方（第三方）
                if roles["ARG2"]:
                    params["third_parties"].add(roles["ARG2"])

            elif verb in ["protect", "secure", "encrypt", "safeguard"]:
                # ARG1是保护的数据
                if roles["ARG1"]:
                    params["data_types"].add(roles["ARG1"])
                # ARG2是保护方法
                if roles["ARG2"]:
                    params["methods"].add(roles["ARG2"])

        return params


# 测试代码
if __name__ == "__main__":
    import spacy

    print("="*80)
    print("语义角色标注（SRL）分析器测试")
    print("="*80)

    # 加载spaCy模型
    nlp = spacy.load("en_core_web_sm")
    analyzer = SemanticRoleAnalyzer(nlp)

    # 测试句子
    test_sentences = [
        "We collect your email address and phone number for account registration.",
        "Your information may be shared with third-party advertising partners.",
        "We use encryption to protect your personal data.",
        "We process user location for improving our services.",
        "Personal data is transferred to servers in the United States.",
    ]

    for i, sentence in enumerate(test_sentences, 1):
        print(f"\n{i}. 句子: {sentence}")
        print("-" * 80)

        # 提取语义角色
        roles_list = analyzer.extract_semantic_roles(sentence)

        print("语义角色:")
        for roles in roles_list:
            print(f"  动词: {roles['verb']}")
            if roles['ARG0']:
                print(f"    ARG0 (施事): {roles['ARG0']}")
            if roles['ARG1']:
                print(f"    ARG1 (受事): {roles['ARG1']}")
            if roles['ARG2']:
                print(f"    ARG2 (接收者): {roles['ARG2']}")
            if roles['ARG_PURPOSE']:
                print(f"    目的: {roles['ARG_PURPOSE']}")

        # 提取隐私参数
        params = analyzer.extract_privacy_parameters(sentence)
        print("\n提取的隐私参数:")
        if params['data_types']:
            print(f"  数据类型: {list(params['data_types'])}")
        if params['third_parties']:
            print(f"  第三方: {list(params['third_parties'])}")
        if params['purposes']:
            print(f"  目的: {list(params['purposes'])}")
        if params['collectors']:
            print(f"  收集者: {list(params['collectors'])}")
        if params['methods']:
            print(f"  方法: {list(params['methods'])}")
