"""
隐私政策分析器 - 核心实现示例
基于文献综述中的方法论
"""

import spacy
from typing import List, Dict, Any, Set
import re
try:
    from semantic_analyzer import EnhancedSemanticAnalyzer
    ENHANCED_SEMANTIC_AVAILABLE = True
except ImportError:
    ENHANCED_SEMANTIC_AVAILABLE = False
    print("Warning: Enhanced semantic analyzer not available. Using basic analysis.")

try:
    from srl_extractor import SemanticRoleAnalyzer
    SRL_AVAILABLE = True
except ImportError:
    SRL_AVAILABLE = False
    print("Warning: SRL analyzer not available. Using basic parameter extraction.")

try:
    from transformer_srl import TransformerSRLExtractor
    TRANSFORMER_SRL_AVAILABLE = True
except ImportError:
    TRANSFORMER_SRL_AVAILABLE = False
    print("Warning: Transformer SRL not available.")

try:
    from llm_extractor import LLMExtractor
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("Warning: LLM extractor not available.")


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
    
    def __init__(self, model_name="en_core_web_sm", use_enhanced_semantic=True, use_srl=True,
                 use_transformer_srl=True, use_llm=False, llm_provider="deepseek", llm_api_key=None):
        """
        初始化分析器

        参数:
            model_name: spaCy模型名称（需要先下载: python -m spacy download en_core_web_sm）
            use_enhanced_semantic: 是否使用增强语义分析（默认True）
            use_srl: 是否使用spaCy语义角色标注提取参数（默认True）
            use_transformer_srl: 是否使用Transformer SRL提取参数（默认True，推荐）
            use_llm: 是否使用LLM增强提取（默认False，需要API key）
            llm_provider: LLM提供商 ("deepseek", "openai", "claude")
            llm_api_key: LLM API密钥（可选，也可从环境变量读取）
        """
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            print(f"模型 {model_name} 未找到。请运行: python -m spacy download {model_name}")
            raise

        # 初始化增强语义分析器
        self.use_enhanced_semantic = use_enhanced_semantic and ENHANCED_SEMANTIC_AVAILABLE
        if self.use_enhanced_semantic:
            self.enhanced_analyzer = EnhancedSemanticAnalyzer(self.nlp)
        else:
            self.enhanced_analyzer = None

        # 初始化spaCy SRL分析器
        self.use_srl = use_srl and SRL_AVAILABLE
        if self.use_srl:
            print("🔧 Loading spaCy SRL analyzer...")
            self.srl_analyzer = SemanticRoleAnalyzer(self.nlp)
            print("   ✓ spaCy SRL analyzer loaded")
        else:
            self.srl_analyzer = None

        # 初始化Transformer SRL分析器
        self.use_transformer_srl = use_transformer_srl and TRANSFORMER_SRL_AVAILABLE
        if self.use_transformer_srl:
            print("🔧 Loading Transformer SRL analyzer...")
            self.transformer_srl = TransformerSRLExtractor()
            print("   ✓ Transformer SRL analyzer loaded")
        else:
            self.transformer_srl = None

        # 初始化LLM增强器（可选，默认关闭）
        self.use_llm = use_llm and LLM_AVAILABLE
        if self.use_llm:
            print(f"🔧 Loading LLM extractor ({llm_provider})...")
            try:
                self.llm_extractor = LLMExtractor(provider=llm_provider, api_key=llm_api_key)
                print(f"   ✓ LLM extractor loaded (辅助模式)")
            except Exception as e:
                print(f"   ✗ LLM extractor failed: {e}")
                self.use_llm = False
                self.llm_extractor = None
        else:
            self.llm_extractor = None

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

        # 常见的干扰内容关键词（UI元素、导航等）
        self.noise_keywords = {
            "click here", "learn more", "read more", "see more", "menu", "footer",
            "header", "navigation", "cookie settings", "settings", "home", "back",
            "next", "previous", "skip", "continue", "submit", "cancel", "close",
            "accept all", "reject all", "manage preferences", "sign in", "log in",
            "sign up", "register", "subscribe", "share", "print", "download",
            "search", "go", "ok", "yes", "no", "highlights", "explore the policy",
            "privacy policy", "terms of service", "read the full policy below",
            "return to top", "back to top", "go to top", "scroll to top"
        }

        # 常见的页面导航和元数据模式
        self.noise_patterns = [
            r"^learn more",
            r"^read more",
            r"^see more",
            r"^click here",
            r"^explore",
            r"updated.*policy",
            r"effective\s+\w+\s+\d+,?\s+\d{4}$",  # "Effective June 26, 2024"
            r"^\d+$",  # 纯数字（脚注编号）
            r"^\[\d+\]$",  # [1], [2] 等
            r"^table of contents",
            r"^back to top",
            r"^privacy center",
        ]

    def is_noise_content(self, text: str) -> bool:
        """
        使用spaCy判断文本是否为干扰内容（爬虫抓取的非政策内容）

        参数:
            text: 待检查的文本

        返回:
            True表示是干扰内容，应该过滤
        """
        text_lower = text.lower().strip()

        # 规则1: 空文本或过短
        if len(text_lower) < 3:
            return True

        # 规则2: 全是数字或特殊字符
        if not any(c.isalpha() for c in text_lower):
            return True

        # 规则3: 检查是否是常见UI元素（精确匹配）
        if text_lower in self.noise_keywords:
            return True

        # 规则3.5: 使用正则模式匹配常见噪音
        for pattern in self.noise_patterns:
            if re.match(pattern, text_lower):
                return True

        # 规则4: 全大写的短文本（通常是标题或按钮）
        if text.isupper() and len(text.split()) <= 4:
            return True

        # 规则5: 使用spaCy进行语言学分析
        doc = self.nlp(text)

        # 计算有效token数（排除空格和标点）
        valid_tokens = [t for t in doc if not t.is_space and not t.is_punct]
        num_tokens = len(valid_tokens)

        # 太短（少于3个有效词）
        if num_tokens < 3:
            return True

        # 检查是否有动词
        has_verb = any(token.pos_ == "VERB" for token in valid_tokens)

        # 检查是否有名词
        has_noun = any(token.pos_ == "NOUN" or token.pos_ == "PROPN" for token in valid_tokens)

        # 规则6: 短句且没有动词（通常是导航链接或标题）
        if num_tokens < 5 and not has_verb:
            return True

        # 规则7: 没有动词也没有名词（可能是无意义片段）
        if not has_verb and not has_noun and num_tokens < 10:
            return True

        # 规则8: 检查是否包含版权符号或常见页脚模式
        if any(char in text for char in ['©', '®', '™']) or text_lower.startswith('copyright'):
            return True

        # 规则9: 单个问号或感叹号（可能是UI元素）
        if text.strip() in ['?', '!', '...']:
            return True

        # 规则10: 疑问句形式的标题（通常是导航目录）
        # 例如："What information do we collect?"
        # 但要确保确实是简短的疑问句
        if text.strip().endswith('?') and num_tokens <= 10:
            # 检查是否像目录项（没有详细说明）
            if not any(word in text_lower for word in ['this', 'that', 'these', 'because', 'when', 'which']):
                return True

        # 规则11: 只包含产品名称列表的行（常见于产品列表）
        # 例如："Facebook", "Instagram", "Messenger"
        if num_tokens <= 3 and all(token.pos_ == "PROPN" for token in valid_tokens):
            return True

        # 规则12: 页脚链接模式（"Policy" 结尾的短语）
        if text_lower.endswith('policy') and num_tokens <= 3:
            return True

        # 规则13: 包含"privacy center"等元数据引用（但不是解释性文字）
        if 'privacy center' in text_lower:
            # "Learn more in Privacy Center" 类型的链接
            if num_tokens < 12:
                return True

        # 规则14: 只提到 "Privacy Policy" 但没有实质内容
        if 'privacy policy' in text_lower:
            # 如果只是标题或链接（不包含 "this", "explains", "describes" 等实质动词）
            if num_tokens < 8 and not any(word in text_lower for word in ['this', 'explains', 'describes', 'lets', 'helps']):
                return True

        # 规则15: 解释性小节标题（没有具体信息，只是描述性的）
        # 例如："The feature we use it for, and how that feature works"
        if num_tokens <= 15 and not text.endswith('.'):
            # 检查是否是描述性标题（包含how/what/why但没有具体内容）
            if any(word in text_lower for word in ['how that', 'what that', 'why that']):
                return True
            # 检查是否是列表标题（包含"for"但很短）
            if text_lower.startswith(('the ', 'a ', 'an ')) and num_tokens < 12:
                # 如果没有句号且像是标题
                if not any(char in text for char in [';', '"', "'"]):
                    return True

        # 规则16: 以标点符号开头的片段（肯定是分段错误）
        if text_lower.startswith((',', ';', ':', 'and ', 'or ', 'but ')):
            return True

        return False

    def segment_policy(self, text: str) -> List[str]:
        """
        将隐私政策分段，并过滤干扰内容

        参数:
            text: 完整的隐私政策文本

        返回:
            过滤后的段落列表
        """
        # 分段：首先按双换行符分割，然后对每个段落按单换行符分割
        paragraphs = []

        # 先按双换行分割大段落
        large_paras = [p.strip() for p in text.split('\n\n') if p.strip()]

        # 对每个大段落，再按单换行分割
        for para in large_paras:
            # 如果包含单换行符，分割成多行
            if '\n' in para:
                lines = [line.strip() for line in para.split('\n') if line.strip()]
                paragraphs.extend(lines)
            else:
                paragraphs.append(para)

        # 进一步按句子分割（如果段落太长）
        segments = []
        for para in paragraphs:
            # 首先检查整个段落是否是干扰内容
            if self.is_noise_content(para):
                continue

            if len(para) > 500:  # 如果段落超过500字符
                doc = self.nlp(para)
                for sent in doc.sents:
                    # 对每个句子也进行干扰内容检查
                    if not self.is_noise_content(sent.text):
                        segments.append(sent.text)
            else:
                segments.append(para)

        return segments
    
    def extract_privacy_parameters(self, doc) -> Dict[str, Any]:
        """
        从文本中提取隐私参数（增强版）

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

        # ===== 方法1: 使用spaCy SRL提取（如果可用） =====
        if self.use_srl and self.srl_analyzer:
            srl_params = self.srl_analyzer.extract_privacy_parameters(doc.text)

            # 合并SRL提取的参数
            if srl_params.get("data_types"):
                params["data_types"].update(srl_params["data_types"])
            if srl_params.get("third_parties"):
                params["third_parties"].update(srl_params["third_parties"])
            if srl_params.get("purposes"):
                params["purposes"].update(srl_params["purposes"])
            if srl_params.get("methods"):
                params["security_measures"].update(srl_params["methods"])

        # ===== 方法1.5: 使用Transformer SRL提取（如果可用，推荐） =====
        if self.use_transformer_srl and self.transformer_srl:
            transformer_params = self.transformer_srl.extract_privacy_parameters(doc.text)

            # 合并Transformer SRL提取的参数
            if transformer_params.get("data_types"):
                params["data_types"].update(transformer_params["data_types"])
            if transformer_params.get("third_parties"):
                params["third_parties"].update(transformer_params["third_parties"])
            if transformer_params.get("purposes"):
                params["purposes"].update(transformer_params["purposes"])

        # ===== 方法1.6: 使用LLM辅助提取（可选，优先级最低） =====
        if self.use_llm and self.llm_extractor:
            try:
                llm_params = self.llm_extractor.extract_privacy_parameters(doc.text)

                # LLM作为辅助，只添加本地模型未发现的新信息
                if llm_params.get("data_types"):
                    params["data_types"].update(llm_params["data_types"])
                if llm_params.get("third_parties"):
                    params["third_parties"].update(llm_params["third_parties"])
                if llm_params.get("purposes"):
                    params["purposes"].update(llm_params["purposes"])
            except Exception as e:
                # LLM失败不影响整体分析
                pass

        # 如果启用了增强语义分析，先使用它
        if self.use_enhanced_semantic and self.enhanced_analyzer:
            enhanced_result = self.enhanced_analyzer.analyze_segment_enhanced(doc.text)
            
            # 提取完整的数据类型
            for dt_info in enhanced_result.get("data_types", []):
                params["data_types"].add(dt_info["text"])
                # 也添加词根形式
                if dt_info.get("root") and dt_info["root"] != dt_info["text"]:
                    params["data_types"].add(dt_info["root"])
            
            # 提取详细的目的
            for purpose_info in enhanced_result.get("purposes", []):
                purpose_text = purpose_info["text"]
                params["purposes"].add(purpose_text)
                # 如果目的很长，也提取关键词
                if len(purpose_text.split()) > 3:
                    # 提取关键词（名词和动词）
                    purpose_doc = self.nlp(purpose_text)
                    keywords = [t.lemma_ for t in purpose_doc if t.pos_ in ["NOUN", "VERB"]]
                    params["purposes"].update(keywords)
            
            # 从数据-活动映射中提取更多信息
            for mapping in enhanced_result.get("data_activity_mappings", []):
                activity = mapping.get("activity", "")
                if activity:
                    params["purposes"].add(activity)
        
        # 继续使用原有的基础方法作为补充
        
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
            
            # 识别目的 - 提取更详细的短语
            if token.lemma_ in ["for", "to"] and token.head.lemma_ in ["use", "process", "collect", "analyze", "provide", "improve"]:
                # 提取完整的介词短语作为目的
                purpose_span = None
                for child in token.children:
                    if child.pos_ in ["NOUN", "VERB", "PROPN"]:
                        # 尝试提取完整的名词短语
                        purpose_tokens = [child]
                        # 收集修饰词和复合词
                        for subchild in child.children:
                            if subchild.dep_ in ["amod", "compound", "prep"]:
                                purpose_tokens.append(subchild)
                        # 构建目的短语
                        purpose_text = " ".join([t.text for t in sorted(purpose_tokens, key=lambda x: x.i)])
                        if len(purpose_text) > 2:
                            params["purposes"].add(purpose_text.lower())
                        # 也添加单个词作为fallback
                        params["purposes"].add(child.lemma_)
                
                # 如果没有找到子词，尝试提取整个介词短语
                if not any(child.pos_ in ["NOUN", "VERB"] for child in token.children):
                    # 提取"for/to"后面的完整短语
                    start_idx = token.i
                    end_idx = min(start_idx + 5, len(doc))  # 最多5个词
                    if end_idx > start_idx + 1:
                        purpose_span = doc[start_idx + 1:end_idx]
                        purpose_text = purpose_span.text.strip()
                        if len(purpose_text) > 2 and len(purpose_text) < 50:
                            params["purposes"].add(purpose_text.lower())
        
        # 额外提取：识别常见的活动模式
        activity_patterns = [
            r"to\s+(?:provide|deliver|offer|enable|support|improve|enhance|personalize|customize)\s+([^.,]+)",
            r"for\s+(?:marketing|advertising|analytics|research|development|service|operation|security|compliance)\s*([^.,]*)",
            r"(?:when|while|during)\s+(?:you|users?)\s+(?:use|access|visit|browse|interact|purchase|register|sign)\s+([^.,]+)",
        ]
        import re
        text_lower = doc.text.lower()
        for pattern in activity_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                activity = match.group(1).strip() if match.lastindex else match.group(0).strip()
                if activity and len(activity) > 2 and len(activity) < 50:
                    params["purposes"].add(activity)
        
        # ===== 基于spaCy模型能力的数据类型提取 =====
        # 方法1: 利用subtree提取收集动词的完整宾语
        collection_verbs = {"collect", "gather", "obtain", "receive", "acquire", "capture", "store", "process", "use"}
        
        for token in doc:
            if token.lemma_ in collection_verbs:
                # 找到直接宾语（dobj）
                for child in token.children:
                    if child.dep_ == "dobj":
                        # 使用spaCy的subtree功能 - 自动包含所有依赖词
                        subtree_tokens = list(child.subtree)
                        phrase = " ".join([t.text for t in subtree_tokens])
                        # 清理引用标记
                        phrase = re.sub(r'\[\d+\]', '', phrase).strip()
                        if self._is_valid_data_type(phrase):
                            params["data_types"].add(phrase.lower())
                        
                        # 查找并列结构（conj依赖）- spaCy自动识别
                        for conj_child in child.children:
                            if conj_child.dep_ == "conj":
                                conj_subtree = list(conj_child.subtree)
                                conj_phrase = " ".join([t.text for t in conj_subtree])
                                conj_phrase = re.sub(r'\[\d+\]', '', conj_phrase).strip()
                                if self._is_valid_data_type(conj_phrase):
                                    params["data_types"].add(conj_phrase.lower())
        
        # 方法2: 利用noun_chunks在收集上下文中提取
        # spaCy自动识别所有名词短语块
        collection_verb_indices = {i for i, token in enumerate(doc) if token.lemma_ in collection_verbs}
        
        for chunk in doc.noun_chunks:
            # 检查chunk是否在包含收集动词的句子中
            chunk_sent = None
            for sent in doc.sents:
                if chunk.start >= sent.start and chunk.end <= sent.end:
                    chunk_sent = sent
                    break
            
            if chunk_sent:
                # 检查句子中是否有收集动词
                sent_has_collection = any(i in collection_verb_indices 
                                         for i in range(chunk_sent.start, chunk_sent.end))
                
                if sent_has_collection:
                    # 检查chunk的根是否依赖于收集动词（利用head链）
                    chunk_root = chunk.root
                    for verb_idx in collection_verb_indices:
                        if chunk_sent.start <= verb_idx < chunk_sent.end:
                            verb_token = doc[verb_idx]
                            # 检查依赖关系
                            if self._is_dependent_of(chunk_root, verb_token, doc):
                                phrase = chunk.text.lower()
                                phrase = re.sub(r'\[\d+\]', '', phrase).strip()
                                if self._is_valid_data_type(phrase):
                                    params["data_types"].add(phrase)
        
        # 方法3: 利用依存解析提取"like/such as"引导的列表
        for token in doc:
            # spaCy自动识别"like"作为prep
            if token.lemma_ == "like" or (token.text.lower() == "as" and token.i > 0 
                                         and doc[token.i-1].lemma_ == "such"):
                # 找到pobj（介词宾语）
                for child in token.children:
                    if child.dep_ == "pobj":
                        # 提取pobj的subtree（包含所有并列项）
                        pobj_subtree = list(child.subtree)
                        # 提取所有名词（利用spaCy的POS标注）
                        for t in pobj_subtree:
                            if t.pos_ == "NOUN":
                                # 提取该名词的完整短语
                                noun_chunk = None
                                for chunk in doc.noun_chunks:
                                    if t.i >= chunk.start and t.i < chunk.end:
                                        noun_chunk = chunk
                                        break
                                if noun_chunk:
                                    phrase = noun_chunk.text.lower()
                                    phrase = re.sub(r'\[\d+\]', '', phrase).strip()
                                    if self._is_valid_data_type(phrase):
                                        params["data_types"].add(phrase)
                        
                        # 检查并列结构（conj）- spaCy自动识别
                        for conj in child.children:
                            if conj.dep_ == "conj":
                                for t in conj.subtree:
                                    if t.pos_ == "NOUN":
                                        noun_chunk = None
                                        for chunk in doc.noun_chunks:
                                            if t.i >= chunk.start and t.i < chunk.end:
                                                noun_chunk = chunk
                                                break
                                        if noun_chunk:
                                            phrase = noun_chunk.text.lower()
                                            phrase = re.sub(r'\[\d+\]', '', phrase).strip()
                                            if self._is_valid_data_type(phrase):
                                                params["data_types"].add(phrase)
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
        
        # 清理和过滤数据类型
        cleaned_data_types = set()
        for dt in params["data_types"]:
            cleaned = self._clean_data_type(dt)
            if cleaned and self._is_valid_data_type(cleaned):
                # 统一转换为小写以避免重复（如 "Apps" vs "apps"）
                cleaned_data_types.add(cleaned.lower())
        params["data_types"] = cleaned_data_types

        # 同样对第三方和目的进行小写归一化
        params["third_parties"] = {tp.lower() for tp in params["third_parties"] if tp}
        params["purposes"] = {p.lower() for p in params["purposes"] if p}

        # 转换set为list以便JSON序列化
        return {k: sorted(list(v)) if isinstance(v, set) else v for k, v in params.items()}
    
    def _is_dependent_of(self, token, ancestor, doc, max_depth=5):
        """检查token是否依赖于ancestor（利用spaCy的head链）"""
        current = token
        depth = 0
        while current != ancestor and current.head != current and depth < max_depth:
            current = current.head
            depth += 1
            if current == ancestor:
                return True
        return False
    
    def _extract_example_list(self, obj_token, doc, params):
        """提取"like"或"such as"引导的示例列表（改进版）"""
        # 查找obj_token后面的"like"或"such as"
        sentence_end = len(doc)
        for sent in doc.sents:
            if obj_token.i >= sent.start and obj_token.i < sent.end:
                sentence_end = sent.end
                break
        
        for i in range(obj_token.i + 1, min(obj_token.i + 20, sentence_end)):
            token = doc[i]
            
            # 检查是否是"like"或"such as"
            is_like = token.lemma_ == "like"
            is_such_as = (token.text.lower() == "as" and i > 0 and doc[i-1].lemma_ == "such")
            
            if is_like or is_such_as:
                # 提取后续的列表项
                list_start = i + 1
                list_end = min(list_start + 20, sentence_end)
                list_text_tokens = []
                
                # 收集列表文本
                for j in range(list_start, list_end):
                    t = doc[j]
                    if t.is_punct and t.text in [".", ";", "\n"]:
                        break
                    # 跳过引用标记如[7]
                    if t.text.startswith('[') and t.text.endswith(']'):
                        continue
                    list_text_tokens.append(t.text)
                
                # 构建列表文本
                list_text = " ".join(list_text_tokens)
                
                # 清理和分割列表项
                list_text = re.sub(r'\[\d+\]', '', list_text).strip()
                
                # 分割列表项（处理 "X, Y, or Z" 格式）
                items = []
                parts = re.split(r'\s*,\s*', list_text)
                for part in parts:
                    part = part.strip()
                    # 处理"or X"
                    if re.match(r'^or\s+', part, re.IGNORECASE):
                        part = re.sub(r'^or\s+', '', part, flags=re.IGNORECASE)
                    
                    # 如果part包含"or"，进一步分割
                    if ' or ' in part.lower():
                        or_items = re.split(r'\s+or\s+', part, flags=re.IGNORECASE)
                        items.extend([item.strip() for item in or_items])
                    else:
                        items.append(part)
                
                # 添加有效的数据类型
                for item in items:
                    item = item.strip()
                    if self._is_valid_data_type(item) and len(item) > 2:
                        params["data_types"].add(item.lower())
                
                break
    
    def _extract_conjunction_items(self, token, doc) -> List[str]:
        """提取并列结构中的项（X, Y, and Z）"""
        items = [token.text]
        
        # 查找并列连词
        for child in token.children:
            if child.dep_ == "conj":
                items.append(child.text)
                # 递归查找更多并列项
                items.extend(self._extract_conjunction_items(child, doc))
        
        # 查找"and"或"or"连接的项
        if token.head.pos_ == "NOUN":
            for sibling in token.head.children:
                if sibling.dep_ == "conj" and sibling.pos_ == "NOUN":
                    items.append(sibling.text)
        
        return items
    
    def _is_valid_data_type(self, text: str) -> bool:
        """判断是否是有效的数据类型"""
        if not text or len(text) < 2:
            return False
        
        text_lower = text.lower().strip()
        
        # 过滤掉噪音
        noise_words = {
            "we", "you", "your", "our", "they", "them", "it", "this", "that",
            "these", "those", "i", "me", "my", "he", "she", "him", "her",
            "]", "[", "(", ")", "{", "}", ".", ",", ";", ":", "!", "?",
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "have", "has", "had", "do", "does", "did", "will", "would",
            "can", "could", "may", "might", "must", "should"
        }
        
        if text_lower in noise_words:
            return False
        
        # 过滤掉纯标点
        if not any(c.isalnum() for c in text):
            return False
        
        # 过滤掉单个字符（除非是特殊的数据类型缩写）
        if len(text_lower) == 1 and text_lower not in ["id", "ip"]:
            return False
        
        return True
    
    def _clean_data_type(self, text: str) -> str:
        """清理数据类型文本"""
        if not text:
            return ""
        
        # 移除前后空格
        text = text.strip()
        
        # 移除标点符号（保留连字符）
        import re
        text = re.sub(r'[^\w\s-]', '', text)
        
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
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
        all_purposes = set()
        
        # 收集数据收集与活动的关联关系
        # 格式: {activity/purpose: {data_types: [...], description: "...", segments: [...]}}
        data_collection_by_activity = {}
        
        for result in segment_results:
            params = result["parameters"]
            all_data_types.update(params["data_types"])
            all_third_parties.update(params["third_parties"])
            all_purposes.update(params["purposes"])
            
            # 构建活动描述
            activities = []
            
            # 优先使用详细的purposes
            if params["purposes"]:
                for purpose in params["purposes"]:
                    # 如果purpose是详细短语（长度>5），直接使用
                    if len(purpose) > 5:
                        activities.append(purpose)
                    else:
                        # 短词，尝试构建更详细的描述
                        category = result["category"]
                        category_desc = self.PIPEDA_CATEGORIES.get(category, category).replace("_", " ").title()
                        detailed_activity = f"{category_desc}: {purpose}"
                        activities.append(detailed_activity)
            
            # 如果没有purposes但有数据收集，使用category作为活动
            if not activities and params["data_types"]:
                category = result["category"]
                category_desc = self.PIPEDA_CATEGORIES.get(category, category).replace("_", " ").title()
                # 尝试从文本中提取上下文
                text_snippet = result["text"][:150].lower()
                if "when" in text_snippet or "while" in text_snippet or "during" in text_snippet:
                    # 提取活动上下文
                    import re
                    # 改进的正则：匹配有意义的词，排除标点符号开头
                    activity_match = re.search(r"(?:when|while|during)\s+([a-zA-Z][^.,;:!?]{3,40})", text_snippet)
                    if activity_match:
                        activity_context = activity_match.group(1).strip()
                        # 验证提取的内容是否有意义（至少包含2个单词）
                        if len(activity_context.split()) >= 2:
                            activities.append(f"{category_desc}: {activity_context}")
                        else:
                            activities.append(category_desc)
                    else:
                        activities.append(category_desc)
                else:
                    activities.append(category_desc)
            
            # 为每个活动建立数据收集关联
            for activity in activities:
                # 过滤无效的活动名（以标点开头、太短等）
                activity_clean = activity.strip()
                if (len(activity_clean) < 3 or
                    activity_clean.startswith((',', ';', ':', 'and ', 'or ', 'but ')) or
                    self.is_noise_content(activity_clean)):
                    continue

                if activity_clean not in data_collection_by_activity:
                    data_collection_by_activity[activity_clean] = {
                        "data_types": set(),
                        "description": activity_clean,
                        "segments": []
                    }
                data_collection_by_activity[activity_clean]["data_types"].update(params["data_types"])
                data_collection_by_activity[activity_clean]["segments"].append({
                    "segment_id": len(data_collection_by_activity[activity_clean]["segments"]) + 1,
                    "text_preview": result["text"][:150] + "..." if len(result["text"]) > 150 else result["text"],
                    "risk_score": result["risk_score"]
                })
        
        # 转换为可序列化的格式
        data_collection_summary = {}
        for activity, info in data_collection_by_activity.items():
            data_collection_summary[activity] = {
                "data_types": sorted(list(info["data_types"])),
                "description": info["description"],
                "segment_count": len(info["segments"]),
                "segments": info["segments"][:3]  # 只保留前3个段落示例
            }
        
        return {
            "summary": {
                "total_segments": len(segment_results),
                "average_risk_score": round(avg_risk, 2),
                "category_distribution": category_counts,
                "total_data_types": list(all_data_types),
                "total_third_parties": list(all_third_parties),
                "total_purposes": list(all_purposes),
                "data_collection_by_activity": data_collection_summary
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
        
        # Data collection by activity/purpose
        if summary.get('data_collection_by_activity'):
            report.append("## 📊 Data Collection by Activity\n")
            report.append("_What data is collected on what activities, based on their privacy policy_\n\n")
            
            data_collection = summary['data_collection_by_activity']
            # Sort by activity name for consistent output
            for activity in sorted(data_collection.keys()):
                activity_info = data_collection[activity]
                data_types = activity_info.get('data_types', [])
                description = activity_info.get('description', activity)
                segment_count = activity_info.get('segment_count', 0)
                
                if data_types:
                    report.append(f"### {description}\n")
                    report.append(f"**Activity Context**: {description}\n")
                    report.append(f"**Segments Found**: {segment_count}\n")
                    report.append("**Data Collected:**\n")
                    # Show all data types, but limit display if too many
                    display_types = data_types[:15]  # Show up to 15 types
                    for dt in display_types:
                        report.append(f"- {dt}")
                    if len(data_types) > 15:
                        report.append(f"- ... and {len(data_types) - 15} more")
                    
                    # Show example segments if available
                    if activity_info.get('segments'):
                        report.append("\n**Example Segments:**\n")
                        for seg in activity_info['segments'][:2]:  # Show first 2 examples
                            report.append(f"- *Risk: {seg.get('risk_score', 0):.2f}* - {seg.get('text_preview', '')}\n")
                    report.append("\n")
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






