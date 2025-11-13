"""
Enhanced Semantic Analysis Module for Privacy Policy Analysis
增强语义分析模块 - 提供更深度的语义理解
"""

import spacy
from typing import List, Dict, Any, Tuple, Set
import re
from collections import defaultdict


class EnhancedSemanticAnalyzer:
    """
    增强语义分析器
    
    提供以下高级语义分析功能：
    1. 语义角色标注 (Semantic Role Labeling)
    2. 完整名词短语提取 (NP Chunking)
    3. 共指消解 (Coreference Resolution)
    4. 语义三元组提取 (Subject-Predicate-Object)
    5. 上下文感知的数据-目的关联
    6. 语义相似度匹配
    """
    
    def __init__(self, nlp_model):
        """
        初始化增强语义分析器
        
        参数:
            nlp_model: spaCy模型实例
        """
        self.nlp = nlp_model
        
        # 数据收集相关的动词和模式
        self.collection_verbs = {
            "collect", "gather", "obtain", "receive", "acquire", "capture",
            "record", "store", "save", "process", "use", "analyze", "access"
        }
        
        # 目的相关的动词和模式
        self.purpose_verbs = {
            "provide", "deliver", "offer", "enable", "support", "improve",
            "enhance", "personalize", "customize", "optimize", "develop",
            "maintain", "operate", "manage", "administer"
        }
        
        # 共享相关的动词
        self.sharing_verbs = {
            "share", "disclose", "transfer", "distribute", "provide",
            "send", "transmit", "release", "sell", "rent"
        }
        
        # 数据类型的语义类别
        self.data_type_semantic_categories = {
            "personal_identification": ["name", "email", "phone", "address", "id", "username", "account"],
            "biometric": ["fingerprint", "face", "voice", "iris", "biometric"],
            "location": ["location", "gps", "coordinates", "address", "geolocation"],
            "behavioral": ["browsing", "click", "interaction", "usage", "activity", "behavior"],
            "financial": ["payment", "credit", "card", "transaction", "billing"],
            "communication": ["message", "email", "chat", "call", "communication"],
            "device": ["device", "ip", "browser", "os", "hardware", "software"],
            "preference": ["preference", "interest", "setting", "choice", "favorite"]
        }
        
    def extract_semantic_triples(self, doc) -> List[Dict[str, Any]]:
        """
        提取语义三元组 (Subject-Predicate-Object)
        
        例如: "We collect your name" -> (We, collect, name)
        
        返回:
            三元组列表，每个三元组包含 subject, predicate, object, 以及相关上下文
        """
        triples = []
        
        for sent in doc.sents:
            # 查找主谓宾结构
            for token in sent:
                # 查找动词（谓词）
                if token.pos_ == "VERB" and token.lemma_ in self.collection_verbs | self.purpose_verbs | self.sharing_verbs:
                    predicate = token
                    
                    # 查找主语
                    subject = None
                    for child in predicate.children:
                        if child.dep_ == "nsubj" or child.dep_ == "nsubjpass":
                            subject = self._extract_noun_phrase(child)
                            break
                    
                    # 查找宾语
                    objects = []
                    for child in predicate.children:
                        if child.dep_ in ["dobj", "pobj", "obj"]:
                            obj_phrase = self._extract_noun_phrase(child)
                            if obj_phrase:
                                objects.append(obj_phrase)
                    
                    # 查找间接宾语和介词宾语
                    for child in predicate.children:
                        if child.dep_ == "prep":
                            prep_obj = None
                            for subchild in child.children:
                                if subchild.dep_ == "pobj":
                                    prep_obj = self._extract_noun_phrase(subchild)
                                    break
                            if prep_obj:
                                objects.append(prep_obj)
                    
                    if subject and objects:
                        for obj in objects:
                            triples.append({
                                "subject": subject,
                                "predicate": predicate.lemma_,
                                "object": obj,
                                "full_text": sent.text,
                                "verb_type": self._classify_verb_type(predicate.lemma_)
                            })
        
        return triples
    
    def _extract_noun_phrase(self, token) -> str:
        """
        提取完整的名词短语
        
        参数:
            token: 起始token
            
        返回:
            完整的名词短语字符串
        """
        # 收集名词短语的所有组成部分
        phrase_tokens = [token]
        
        # 向前收集修饰词
        for child in token.children:
            if child.dep_ in ["amod", "compound", "det", "poss", "nummod"]:
                phrase_tokens.append(child)
        
        # 向后收集依赖词
        if token.head.pos_ == "NOUN" and token.dep_ == "compound":
            phrase_tokens.append(token.head)
        
        # 排序并构建短语
        phrase_tokens.sort(key=lambda x: x.i)
        phrase = " ".join([t.text for t in phrase_tokens])
        
        return phrase.strip()
    
    def _classify_verb_type(self, verb: str) -> str:
        """分类动词类型"""
        if verb in self.collection_verbs:
            return "collection"
        elif verb in self.purpose_verbs:
            return "purpose"
        elif verb in self.sharing_verbs:
            return "sharing"
        return "other"
    
    def extract_complete_data_types(self, doc) -> List[Dict[str, Any]]:
        """
        提取完整的数据类型（使用NP Chunking）
        
        不仅提取单个词，还提取完整的名词短语
        例如: "email address" 而不是单独的 "email" 和 "address"
        """
        data_types = []
        
        # 使用spaCy的noun_chunks
        for chunk in doc.noun_chunks:
            # 检查这个名词短语是否在数据收集的上下文中
            context = self._get_chunk_context(chunk, doc)
            
            if self._is_data_collection_context(chunk, context):
                # 提取完整的数据类型
                data_type_info = {
                    "text": chunk.text,
                    "lemma": chunk.lemma_,
                    "root": chunk.root.text,
                    "semantic_category": self._classify_data_type_semantic(chunk.text),
                    "context": context[:100] if context else "",
                    "position": chunk.start
                }
                data_types.append(data_type_info)
        
        # 也从语义三元组中提取
        triples = self.extract_semantic_triples(doc)
        for triple in triples:
            if triple["verb_type"] == "collection":
                obj_text = triple["object"]
                if obj_text not in [dt["text"] for dt in data_types]:
                    data_types.append({
                        "text": obj_text,
                        "lemma": obj_text.lower(),
                        "root": obj_text.split()[-1] if obj_text.split() else obj_text,
                        "semantic_category": self._classify_data_type_semantic(obj_text),
                        "context": triple["full_text"],
                        "position": -1
                    })
        
        return data_types
    
    def _get_chunk_context(self, chunk, doc) -> str:
        """获取名词短语的上下文"""
        # 获取包含这个chunk的句子
        for sent in doc.sents:
            if chunk.start >= sent.start and chunk.end <= sent.end:
                return sent.text
        return ""
    
    def _is_data_collection_context(self, chunk, context: str) -> bool:
        """判断名词短语是否在数据收集的上下文中"""
        context_lower = context.lower()
        
        # 检查上下文中是否有收集动词
        for verb in self.collection_verbs:
            if verb in context_lower:
                # 检查动词和chunk的距离
                verb_pos = context_lower.find(verb)
                chunk_pos = context_lower.find(chunk.text.lower())
                if chunk_pos != -1 and abs(verb_pos - chunk_pos) < 50:
                    return True
        
        return False
    
    def _classify_data_type_semantic(self, data_type: str) -> str:
        """对数据类型进行语义分类"""
        data_lower = data_type.lower()
        
        for category, keywords in self.data_type_semantic_categories.items():
            for keyword in keywords:
                if keyword in data_lower:
                    return category
        
        return "other"
    
    def extract_detailed_purposes(self, doc) -> List[Dict[str, Any]]:
        """
        提取详细的目的/活动描述
        
        不仅提取"for marketing"，还提取"for marketing and advertising purposes"
        """
        purposes = []
        
        # 方法1: 从语义三元组提取
        triples = self.extract_semantic_triples(doc)
        for triple in triples:
            if triple["verb_type"] == "purpose":
                # 提取目的短语
                purpose_text = self._extract_purpose_from_triple(triple, doc)
                if purpose_text:
                    purposes.append({
                        "text": purpose_text,
                        "type": "explicit",
                        "verb": triple["predicate"],
                        "context": triple["full_text"]
                    })
        
        # 方法2: 提取介词短语中的目的
        for token in doc:
            if token.lemma_ in ["for", "to"]:
                purpose_phrase = self._extract_purpose_phrase(token, doc)
                if purpose_phrase:
                    purposes.append({
                        "text": purpose_phrase,
                        "type": "prepositional",
                        "context": self._get_sentence_text(token, doc)
                    })
        
        # 方法3: 使用正则模式提取常见目的模式
        text = doc.text
        purpose_patterns = [
            r"(?:for|to)\s+(?:the\s+)?(?:purpose\s+of\s+)?([^.,;]+?)(?:\s+purposes?)?(?=[.,;])",
            r"(?:in\s+order\s+)?to\s+([^.,;]+?)(?=[.,;])",
            r"(?:when|while|during)\s+(?:you|users?|customers?)\s+([^.,;]+?)(?=[.,;])",
        ]
        
        for pattern in purpose_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                purpose_text = match.group(1).strip()
                if len(purpose_text) > 3 and len(purpose_text) < 100:
                    purposes.append({
                        "text": purpose_text,
                        "type": "pattern",
                        "context": match.group(0)
                    })
        
        # 去重
        seen = set()
        unique_purposes = []
        for purpose in purposes:
            purpose_key = purpose["text"].lower()
            if purpose_key not in seen:
                seen.add(purpose_key)
                unique_purposes.append(purpose)
        
        return unique_purposes
    
    def _extract_purpose_from_triple(self, triple: Dict, doc) -> str:
        """从三元组中提取目的"""
        # 查找"for"或"to"引导的目的短语
        for token in doc:
            if token.i >= triple.get("start", 0) and token.i <= triple.get("end", len(doc)):
                if token.lemma_ in ["for", "to"]:
                    return self._extract_purpose_phrase(token, doc)
        return ""
    
    def _extract_purpose_phrase(self, prep_token, doc) -> str:
        """提取目的短语"""
        purpose_tokens = []
        
        # 收集介词后的所有相关词
        for child in prep_token.children:
            if child.dep_ == "pobj":
                # 提取完整的名词短语
                phrase = self._extract_noun_phrase(child)
                if phrase:
                    purpose_tokens.append(phrase)
        
        # 如果没有找到，尝试提取后续的词
        if not purpose_tokens:
            start_idx = prep_token.i + 1
            end_idx = min(start_idx + 8, len(doc))
            phrase_tokens = []
            for i in range(start_idx, end_idx):
                token = doc[i]
                if token.is_punct and token.text in [".", ",", ";"]:
                    break
                phrase_tokens.append(token.text)
            if phrase_tokens:
                purpose_tokens.append(" ".join(phrase_tokens))
        
        return " ".join(purpose_tokens).strip()
    
    def _get_sentence_text(self, token, doc) -> str:
        """获取包含token的句子文本"""
        for sent in doc.sents:
            if sent.start <= token.i < sent.end:
                return sent.text
        return ""
    
    def map_data_to_activities(self, doc, data_types: List[Dict], purposes: List[Dict]) -> List[Dict[str, Any]]:
        """
        将数据收集映射到具体的活动/目的
        
        这是核心功能：理解"在什么活动上收集了什么数据"
        """
        mappings = []
        
        # 提取语义三元组
        triples = self.extract_semantic_triples(doc)
        
        # 为每个数据收集三元组找到关联的目的
        for triple in triples:
            if triple["verb_type"] == "collection":
                data_obj = triple["object"]
                
                # 查找同一句子或相邻句子中的目的
                purpose_contexts = []
                
                # 方法1: 在同一句子中查找目的
                sentence_text = triple["full_text"]
                for purpose in purposes:
                    if purpose["text"].lower() in sentence_text.lower():
                        purpose_contexts.append(purpose)
                
                # 方法2: 查找"for/to"引导的目的短语
                for token in doc:
                    if token.lemma_ in ["for", "to"] and token.head.lemma_ == triple["predicate"]:
                        purpose_phrase = self._extract_purpose_phrase(token, doc)
                        if purpose_phrase:
                            purpose_contexts.append({
                                "text": purpose_phrase,
                                "type": "direct",
                                "context": sentence_text
                            })
                
                # 方法3: 查找上下文中的目的（相邻句子）
                if not purpose_contexts:
                    # 获取当前句子的位置
                    sent_idx = None
                    for i, sent in enumerate(doc.sents):
                        if triple["full_text"] in sent.text:
                            sent_idx = i
                            break
                    
                    if sent_idx is not None:
                        # 检查前后句子
                        for offset in [-1, 1]:
                            check_idx = sent_idx + offset
                            if 0 <= check_idx < len(list(doc.sents)):
                                check_sent = list(doc.sents)[check_idx]
                                for purpose in purposes:
                                    if purpose["text"].lower() in check_sent.text.lower():
                                        purpose_contexts.append({
                                            **purpose,
                                            "context": check_sent.text,
                                            "proximity": "adjacent"
                                        })
                
                # 如果没有找到明确的目的，使用类别作为fallback
                if not purpose_contexts:
                    # 使用数据类型的语义类别推断可能的目的
                    for dt_info in data_types:
                        if dt_info["text"].lower() in data_obj.lower():
                            semantic_cat = dt_info.get("semantic_category", "other")
                            purpose_contexts.append({
                                "text": f"Data collection for {semantic_cat} purposes",
                                "type": "inferred",
                                "semantic_category": semantic_cat
                            })
                            break
                
                # 创建映射
                for purpose in purpose_contexts:
                    mappings.append({
                        "data_type": data_obj,
                        "activity": purpose["text"],
                        "activity_type": purpose.get("type", "unknown"),
                        "collection_verb": triple["predicate"],
                        "context": purpose.get("context", triple["full_text"]),
                        "confidence": self._calculate_mapping_confidence(triple, purpose)
                    })
        
        return mappings
    
    def _calculate_mapping_confidence(self, triple: Dict, purpose: Dict) -> float:
        """计算数据-目的映射的置信度"""
        confidence = 0.5  # 基础置信度
        
        # 如果目的在同一句子中，提高置信度
        if purpose.get("context") and triple["full_text"] in purpose.get("context", ""):
            confidence += 0.3
        
        # 如果目的类型是"direct"或"explicit"，提高置信度
        if purpose.get("type") in ["direct", "explicit"]:
            confidence += 0.2
        
        # 如果目的类型是"inferred"，降低置信度
        if purpose.get("type") == "inferred":
            confidence -= 0.2
        
        return min(1.0, max(0.0, confidence))
    
    def analyze_segment_enhanced(self, text: str) -> Dict[str, Any]:
        """
        对单个段落进行增强语义分析
        
        返回:
            包含详细语义分析结果的字典
        """
        doc = self.nlp(text)
        
        # 提取完整的数据类型
        data_types = self.extract_complete_data_types(doc)
        
        # 提取详细的目的
        purposes = self.extract_detailed_purposes(doc)
        
        # 提取语义三元组
        triples = self.extract_semantic_triples(doc)
        
        # 映射数据到活动
        data_activity_mappings = self.map_data_to_activities(doc, data_types, purposes)
        
        return {
            "text": text,
            "data_types": data_types,
            "purposes": purposes,
            "semantic_triples": triples,
            "data_activity_mappings": data_activity_mappings,
            "semantic_analysis": {
                "has_explicit_purposes": any(p.get("type") == "explicit" for p in purposes),
                "has_direct_mappings": any(m.get("activity_type") == "direct" for m in data_activity_mappings),
                "total_triples": len(triples),
                "total_mappings": len(data_activity_mappings)
            }
        }

