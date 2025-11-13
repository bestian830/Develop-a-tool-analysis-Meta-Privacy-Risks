"""
RAG 分析器 + 向量数据库增强版

支持大文档检索和交互式查询
"""

from simple_rag_analyzer import SimpleRAGAnalyzer, DataActivityMapping
from typing import List, Dict, Any, Optional
import json


class RAGAnalyzerWithVectorDB(SimpleRAGAnalyzer):
    """
    带向量数据库的RAG分析器

    额外功能:
    1. 向量化存储隐私政策
    2. 基于问题检索相关段落
    3. 支持交互式查询
    """

    def __init__(self, llm_provider: str = "deepseek", api_key: Optional[str] = None,
                 vectordb_type: str = "chroma"):
        """
        初始化

        参数:
            llm_provider: LLM提供商
            api_key: API密钥
            vectordb_type: 向量数据库类型 ("chroma" 或 "faiss")
        """
        super().__init__(llm_provider, api_key)

        self.vectordb_type = vectordb_type
        self._init_vectordb()

    def _init_vectordb(self):
        """初始化向量数据库"""
        if self.vectordb_type == "chroma":
            self._init_chroma()
        elif self.vectordb_type == "faiss":
            self._init_faiss()
        else:
            raise ValueError(f"不支持的向量数据库类型: {self.vectordb_type}")

    def _init_chroma(self):
        """初始化ChromaDB"""
        try:
            import chromadb
            from chromadb.utils import embedding_functions

            self.chroma_client = chromadb.Client()

            # 创建或获取集合
            try:
                self.collection = self.chroma_client.get_collection(
                    name="privacy_policies"
                )
            except:
                self.collection = self.chroma_client.create_collection(
                    name="privacy_policies",
                    embedding_function=embedding_functions.DefaultEmbeddingFunction()
                )

            print("✓ ChromaDB初始化成功")

        except ImportError:
            print("❌ ChromaDB未安装，请运行: pip install chromadb")
            raise

    def _init_faiss(self):
        """初始化FAISS"""
        try:
            import faiss
            import numpy as np
            from sentence_transformers import SentenceTransformer

            # 初始化embedding模型
            self.encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

            # FAISS索引（初始为空）
            self.index = None
            self.chunks = []
            self.chunk_metadatas = []

            print("✓ FAISS初始化成功")

        except ImportError:
            print("❌ FAISS或sentence-transformers未安装")
            print("   请运行: pip install faiss-cpu sentence-transformers")
            raise

    def index_policy(self, policy_text: str, policy_id: str = "default"):
        """
        将隐私政策索引到向量数据库

        参数:
            policy_text: 隐私政策文本
            policy_id: 政策ID（用于区分不同政策）
        """
        print(f"📊 索引隐私政策: {policy_id}")

        # 分块
        chunks = self.chunk_policy(policy_text)
        print(f"   分成 {len(chunks)} 个块")

        if self.vectordb_type == "chroma":
            self._index_to_chroma(chunks, policy_id)
        elif self.vectordb_type == "faiss":
            self._index_to_faiss(chunks, policy_id)

        print("✓ 索引完成\n")

    def _index_to_chroma(self, chunks: List[str], policy_id: str):
        """索引到ChromaDB"""
        self.collection.add(
            documents=chunks,
            ids=[f"{policy_id}_{i}" for i in range(len(chunks))],
            metadatas=[{
                "chunk_id": i,
                "policy_id": policy_id,
                "chunk_length": len(chunk)
            } for i, chunk in enumerate(chunks)]
        )

    def _index_to_faiss(self, chunks: List[str], policy_id: str):
        """索引到FAISS"""
        import faiss
        import numpy as np

        # 生成embeddings
        print("   生成向量...")
        embeddings = self.encoder.encode(chunks, show_progress_bar=True)

        # 创建或更新索引
        if self.index is None:
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)

        # 添加向量
        self.index.add(np.array(embeddings).astype('float32'))

        # 保存chunks和元数据
        self.chunks.extend(chunks)
        self.chunk_metadatas.extend([{
            "chunk_id": i,
            "policy_id": policy_id,
            "chunk_length": len(chunk)
        } for i, chunk in enumerate(chunks)])

    def query(self, question: str, n_results: int = 3) -> Dict[str, Any]:
        """
        基于问题查询隐私政策

        参数:
            question: 用户问题
            n_results: 返回的相关段落数量

        返回:
            包含答案和相关段落的字典
        """
        print(f"🔍 查询: {question}")

        # 检索相关段落
        if self.vectordb_type == "chroma":
            relevant_chunks = self._query_chroma(question, n_results)
        elif self.vectordb_type == "faiss":
            relevant_chunks = self._query_faiss(question, n_results)

        print(f"   找到 {len(relevant_chunks)} 个相关段落\n")

        # 合并上下文
        context = "\n\n".join([
            f"[段落 {i+1}]\n{chunk}"
            for i, chunk in enumerate(relevant_chunks)
        ])

        # 用LLM回答
        prompt = f"""请基于以下隐私政策内容回答问题。

问题: {question}

相关内容:
{context}

要求:
1. 直接回答问题
2. 引用原文作为证据
3. 如果内容中没有相关信息，请明确说明

请以JSON格式返回:
{{
  "answer": "简洁的答案",
  "evidence": ["引用1", "引用2"],
  "data_types": ["相关的数据类型"],
  "activities": ["相关的活动"]
}}
"""

        try:
            if self.llm_provider in ["deepseek", "openai"]:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "你是一个隐私政策分析专家。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                )
                result_text = response.choices[0].message.content

            elif self.llm_provider == "claude":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1500,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt}]
                )
                result_text = response.content[0].text

            # 解析JSON
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group(1)

            answer_data = json.loads(result_text)

            return {
                "question": question,
                "answer": answer_data.get("answer", ""),
                "evidence": answer_data.get("evidence", []),
                "data_types": answer_data.get("data_types", []),
                "activities": answer_data.get("activities", []),
                "relevant_chunks": relevant_chunks
            }

        except Exception as e:
            print(f"❌ LLM回答失败: {e}")
            return {
                "question": question,
                "answer": "无法生成答案",
                "error": str(e),
                "relevant_chunks": relevant_chunks
            }

    def _query_chroma(self, question: str, n_results: int) -> List[str]:
        """从ChromaDB检索"""
        results = self.collection.query(
            query_texts=[question],
            n_results=n_results
        )
        return results['documents'][0] if results['documents'] else []

    def _query_faiss(self, question: str, n_results: int) -> List[str]:
        """从FAISS检索"""
        import numpy as np

        if self.index is None or len(self.chunks) == 0:
            return []

        # 生成查询向量
        query_vec = self.encoder.encode([question])

        # 检索
        D, I = self.index.search(
            np.array(query_vec).astype('float32'),
            min(n_results, len(self.chunks))
        )

        # 返回相关段落
        return [self.chunks[i] for i in I[0] if i < len(self.chunks)]

    def interactive_query(self, policy_text: str, policy_id: str = "default"):
        """
        交互式查询模式

        参数:
            policy_text: 隐私政策文本
            policy_id: 政策ID
        """
        # 先索引政策
        self.index_policy(policy_text, policy_id)

        print("="*60)
        print("🤖 交互式查询模式")
        print("="*60)
        print("提示: 输入问题查询隐私政策，输入 'quit' 退出\n")
        print("示例问题:")
        print("  - 收集了哪些数据？")
        print("  - 什么活动使用了位置数据？")
        print("  - 数据会分享给第三方吗？")
        print("  - 用户有哪些权利？\n")

        while True:
            try:
                question = input("❓ 你的问题: ").strip()

                if question.lower() in ['quit', 'exit', 'q']:
                    print("👋 再见！")
                    break

                if not question:
                    continue

                # 查询
                result = self.query(question, n_results=3)

                # 显示答案
                print("\n" + "="*60)
                print("💡 答案:")
                print("-"*60)
                print(result['answer'])

                if result.get('evidence'):
                    print("\n📝 证据:")
                    for i, evidence in enumerate(result['evidence'], 1):
                        print(f"  {i}. {evidence}")

                if result.get('data_types'):
                    print(f"\n📊 相关数据类型: {', '.join(result['data_types'])}")

                if result.get('activities'):
                    print(f"🎯 相关活动: {', '.join(result['activities'])}")

                print("="*60 + "\n")

            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break
            except Exception as e:
                print(f"\n❌ 错误: {e}\n")


def main():
    """示例用法"""
    import sys

    sample_policy = """
    用户信息收集与使用

    当您注册账号时，我们会收集您的姓名、邮箱地址和手机号码。这些信息用于创建您的账户并验证身份。

    当您浏览我们的网站时，我们会自动收集您的IP地址、浏览器类型、访问时间和浏览的页面。
    这些信息帮助我们改进网站性能和用户体验。

    当您使用位置服务时，我们会收集您的GPS定位、WiFi信息和基站信息。
    这些位置数据用于提供基于位置的服务，如附近商家推荐、导航等。

    当您购买商品时，我们会收集您的收货地址和支付信息（信用卡号、银行账户）。
    这些信息仅用于处理您的订单和完成交易。

    数据共享
    我们可能与第三方广告商分享您的浏览记录和兴趣偏好，用于投放个性化广告。
    我们也可能与物流公司分享您的收货地址和联系方式，以便配送商品。
    """

    print("🚀 RAG分析器 + 向量数据库演示\n")

    # 初始化分析器（使用ChromaDB）
    try:
        analyzer = RAGAnalyzerWithVectorDB(
            llm_provider="deepseek",
            vectordb_type="chroma"  # 或 "faiss"
        )
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        print("\n💡 请安装依赖:")
        print("   pip install chromadb")
        print("   或")
        print("   pip install faiss-cpu sentence-transformers")
        sys.exit(1)

    # 方式1: 自动分析
    print("\n1️⃣ 自动分析模式")
    print("-"*60)
    results = analyzer.analyze(sample_policy)
    print("\n数据类型:", results['data_types'])
    print("活动场景:", results['activities'])
    print("\n数据-活动映射:")
    for m in results['mappings'][:3]:
        print(f"  • {m['activity']}: {', '.join(m['data_types'][:3])}")

    # 方式2: 交互式查询
    print("\n\n2️⃣ 交互式查询模式")
    print("-"*60)
    choice = input("是否进入交互式查询？(y/n): ").strip().lower()

    if choice == 'y':
        analyzer.interactive_query(sample_policy, policy_id="demo")


if __name__ == "__main__":
    main()
