"""
简化版 RAG 隐私政策分析器
使用 RAG (Retrieval-Augmented Generation) 简化分析流程

核心功能:
1. 提取数据类型 (Data Types)
2. 提取活动场景 (Activities)
3. 建立数据-活动映射 (Data-Activity Mapping)
"""

import json
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class DataActivityMapping:
    """数据-活动映射"""
    activity: str           # 活动名称 (e.g., "注册账号", "浏览内容")
    data_types: List[str]   # 该活动使用的数据类型
    context: str            # 原文上下文
    confidence: float       # 置信度


class SimpleRAGAnalyzer:
    """
    简化版 RAG 分析器

    使用 LLM 提取关键信息，避免复杂的 NLP 管道
    """

    def __init__(self, llm_provider: str = "deepseek", api_key: Optional[str] = None):
        """
        初始化分析器

        参数:
            llm_provider: LLM提供商 ("deepseek", "openai", "claude")
            api_key: API密钥
        """
        self.llm_provider = llm_provider
        self.api_key = api_key or self._get_api_key_from_env()

        # 初始化 LLM 客户端
        self._init_llm_client()

    def _get_api_key_from_env(self) -> Optional[str]:
        """从环境变量获取API密钥"""
        import os

        key_map = {
            "deepseek": "DEEPSEEK_API_KEY",
            "openai": "OPENAI_API_KEY",
            "claude": "ANTHROPIC_API_KEY"
        }

        env_var = key_map.get(self.llm_provider)
        if env_var:
            return os.getenv(env_var)
        return None

    def _init_llm_client(self):
        """初始化LLM客户端"""
        if self.llm_provider == "deepseek":
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )
            self.model = "deepseek-chat"

        elif self.llm_provider == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            self.model = "gpt-4o-mini"

        elif self.llm_provider == "claude":
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.model = "claude-3-5-sonnet-20241022"

        else:
            raise ValueError(f"不支持的LLM提供商: {self.llm_provider}")

    def chunk_policy(self, policy_text: str, chunk_size: int = 1000) -> List[str]:
        """
        将隐私政策分块

        参数:
            policy_text: 完整的隐私政策文本
            chunk_size: 每块的最大字符数

        返回:
            分块列表
        """
        # 按段落分割
        paragraphs = [p.strip() for p in re.split(r'\n\n+', policy_text) if p.strip()]

        chunks = []
        current_chunk = []
        current_size = 0

        for para in paragraphs:
            para_size = len(para)

            # 如果当前块加上新段落会超过限制
            if current_size + para_size > chunk_size and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = [para]
                current_size = para_size
            else:
                current_chunk.append(para)
                current_size += para_size

        # 添加最后一块
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def extract_with_llm(self, text: str) -> Dict[str, Any]:
        """
        使用 LLM 提取数据和活动信息

        参数:
            text: 要分析的文本段落

        返回:
            提取结果字典
        """
        prompt = f"""请分析以下隐私政策文本，提取：
1. **数据类型** (Data Types): 收集了哪些用户数据？
2. **活动场景** (Activities): 在哪些活动/场景下收集数据？
3. **数据-活动映射** (Data-Activity Mapping): 每个活动使用了哪些数据？

要求：
- 使用简洁的中文关键词
- 数据类型示例：姓名、邮箱、位置、浏览记录
- 活动场景示例：注册账号、浏览内容、购买商品、发布帖子

请以JSON格式返回，格式如下：
```json
{{
  "data_types": ["数据类型1", "数据类型2", ...],
  "activities": ["活动1", "活动2", ...],
  "mappings": [
    {{
      "activity": "活动名称",
      "data_types": ["该活动使用的数据1", "数据2"],
      "context": "原文相关片段"
    }}
  ]
}}
```

隐私政策文本：
{text}

请只返回JSON，不要添加其他说明。
"""

        try:
            if self.llm_provider in ["deepseek", "openai"]:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "你是一个隐私政策分析专家，擅长提取数据收集和使用信息。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,  # 降低随机性，提高一致性
                )
                result_text = response.choices[0].message.content

            elif self.llm_provider == "claude":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    temperature=0.1,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                result_text = response.content[0].text

            # 解析JSON
            # 提取```json...```块（如果有）
            json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group(1)

            result = json.loads(result_text)
            return result

        except Exception as e:
            print(f"LLM提取失败: {e}")
            return {
                "data_types": [],
                "activities": [],
                "mappings": []
            }

    def analyze(self, policy_text: str) -> Dict[str, Any]:
        """
        分析完整的隐私政策

        参数:
            policy_text: 完整的隐私政策文本

        返回:
            分析结果
        """
        print("📄 分析隐私政策...")

        # 1. 分块
        chunks = self.chunk_policy(policy_text, chunk_size=2000)
        print(f"   分成 {len(chunks)} 个块")

        # 2. 逐块提取
        all_data_types = set()
        all_activities = set()
        all_mappings = []

        for i, chunk in enumerate(chunks, 1):
            print(f"   处理第 {i}/{len(chunks)} 块...")

            result = self.extract_with_llm(chunk)

            # 合并结果
            all_data_types.update(result.get("data_types", []))
            all_activities.update(result.get("activities", []))

            for mapping in result.get("mappings", []):
                all_mappings.append(DataActivityMapping(
                    activity=mapping.get("activity", ""),
                    data_types=mapping.get("data_types", []),
                    context=mapping.get("context", "")[:200],  # 限制上下文长度
                    confidence=0.8  # LLM提取默认置信度
                ))

        # 3. 合并相同活动的映射
        activity_data_map = {}
        for mapping in all_mappings:
            activity = mapping.activity
            if activity not in activity_data_map:
                activity_data_map[activity] = {
                    "data_types": set(),
                    "contexts": []
                }
            activity_data_map[activity]["data_types"].update(mapping.data_types)
            activity_data_map[activity]["contexts"].append(mapping.context)

        # 4. 构建最终映射
        final_mappings = []
        for activity, info in activity_data_map.items():
            final_mappings.append(DataActivityMapping(
                activity=activity,
                data_types=sorted(list(info["data_types"])),
                context=info["contexts"][0] if info["contexts"] else "",
                confidence=0.8
            ))

        print("✅ 分析完成！\n")

        return {
            "summary": {
                "total_chunks": len(chunks),
                "total_data_types": len(all_data_types),
                "total_activities": len(all_activities),
                "total_mappings": len(final_mappings)
            },
            "data_types": sorted(list(all_data_types)),
            "activities": sorted(list(all_activities)),
            "mappings": [asdict(m) for m in final_mappings]
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
        report.append("# 隐私政策分析报告\n")

        # 摘要
        report.append("## 📊 分析摘要\n")
        report.append(f"- **数据类型**: {summary['total_data_types']} 种")
        report.append(f"- **活动场景**: {summary['total_activities']} 个")
        report.append(f"- **数据-活动映射**: {summary['total_mappings']} 条\n")

        # 数据类型列表
        report.append("## 📋 收集的数据类型\n")
        for dt in data_types:
            report.append(f"- {dt}")
        report.append("\n")

        # 活动场景列表
        report.append("## 🎯 活动场景\n")
        for activity in activities:
            report.append(f"- {activity}")
        report.append("\n")

        # 核心：数据-活动映射
        report.append("## 🔗 数据-活动映射表\n")
        report.append("_哪些活动使用了哪些数据_\n\n")

        for mapping in sorted(mappings, key=lambda x: x["activity"]):
            report.append(f"### {mapping['activity']}\n")
            report.append(f"**使用的数据**:")
            for dt in mapping["data_types"]:
                report.append(f"- {dt}")

            if mapping.get("context"):
                report.append(f"\n**原文片段**: _{mapping['context']}_\n")

            report.append("\n---\n")

        return "\n".join(report)

    def _generate_text_report(self, results: Dict[str, Any]) -> str:
        """生成纯文本格式报告"""
        summary = results["summary"]
        mappings = results["mappings"]

        report = []
        report.append("=" * 60)
        report.append("隐私政策分析报告")
        report.append("=" * 60)
        report.append("")

        report.append(f"数据类型: {summary['total_data_types']} 种")
        report.append(f"活动场景: {summary['total_activities']} 个")
        report.append(f"数据-活动映射: {summary['total_mappings']} 条")
        report.append("")

        report.append("数据-活动映射详情:")
        report.append("-" * 60)

        for mapping in sorted(mappings, key=lambda x: x["activity"]):
            report.append(f"\n活动: {mapping['activity']}")
            report.append(f"使用数据: {', '.join(mapping['data_types'])}")

        return "\n".join(report)


def main():
    """示例用法"""
    import sys

    # 示例隐私政策文本
    sample_policy = """
    用户信息收集与使用

    当您注册账号时，我们会收集您的姓名、邮箱地址和手机号码。这些信息用于创建您的账户并验证身份。

    当您浏览我们的网站时，我们会自动收集您的IP地址、浏览器类型、访问时间和浏览的页面。
    这些信息帮助我们改进网站性能和用户体验。

    当您购买商品时，我们会收集您的收货地址和支付信息（信用卡号、银行账户）。
    这些信息仅用于处理您的订单和完成交易。

    当您发布内容或评论时，我们会收集您发布的文字、图片和视频。
    这些内容会公开展示在平台上，供其他用户查看。
    """

    # 初始化分析器
    analyzer = SimpleRAGAnalyzer(llm_provider="deepseek")

    # 分析
    results = analyzer.analyze(sample_policy)

    # 生成报告
    report = analyzer.generate_report(results, output_format="markdown")
    print(report)

    # 保存到文件
    with open("simple_analysis_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("\n报告已保存到: simple_analysis_report.md")


if __name__ == "__main__":
    main()
