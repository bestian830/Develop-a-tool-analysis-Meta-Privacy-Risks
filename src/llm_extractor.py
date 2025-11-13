"""
基于大语言模型（LLM）的隐私参数提取器

支持多种 LLM 服务：
- DeepSeek (推荐，性价比高)
- OpenAI GPT
- Anthropic Claude

使用方法:
    extractor = LLMExtractor(provider="deepseek", api_key="your-key")
    result = extractor.extract_privacy_parameters(text)
"""

import json
import os
from typing import Dict, Set, Optional
import requests
from pathlib import Path

# 尝试加载 .env 文件
try:
    from dotenv import load_dotenv
    # 查找项目根目录的 .env 文件
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # dotenv 未安装，跳过


class LLMExtractor:
    """基于大语言模型的隐私参数提取器"""

    def __init__(self, provider: str = "deepseek", api_key: Optional[str] = None):
        """
        初始化 LLM 提取器

        参数:
            provider: LLM 提供商 ("deepseek", "openai", "claude")
            api_key: API 密钥（如果不提供，会从环境变量读取）
        """
        self.provider = provider.lower()
        self.api_key = api_key or self._get_api_key()

        # 配置不同提供商的 API 端点
        self.endpoints = {
            "deepseek": "https://api.deepseek.com/v1/chat/completions",
            "openai": "https://api.openai.com/v1/chat/completions",
            "claude": "https://api.anthropic.com/v1/messages"
        }

        if self.provider not in self.endpoints:
            raise ValueError(f"不支持的 LLM 提供商: {provider}")

        if not self.api_key:
            raise ValueError(f"未提供 {provider} API 密钥")

        print(f"✓ LLM 提取器初始化成功 (提供商: {provider})")

    def _get_api_key(self) -> Optional[str]:
        """从环境变量获取 API 密钥"""
        env_vars = {
            "deepseek": "DEEPSEEK_API_KEY",
            "openai": "OPENAI_API_KEY",
            "claude": "ANTHROPIC_API_KEY"
        }
        env_var = env_vars.get(self.provider)
        return os.getenv(env_var) if env_var else None

    def extract_privacy_parameters(self, text: str) -> Dict[str, Set[str]]:
        """
        使用 LLM 从文本中提取隐私参数

        参数:
            text: 隐私政策文本片段

        返回:
            包含 data_types, third_parties, purposes 的字典
        """
        # 限制文本长度（避免过长的请求）
        if len(text) > 2000:
            text = text[:2000] + "..."

        # 构建提示词
        prompt = self._build_prompt(text)

        try:
            # 调用 LLM API
            response = self._call_llm(prompt)

            # 解析响应
            result = self._parse_response(response)

            return result

        except Exception as e:
            print(f"✗ LLM 提取失败: {e}")
            return {
                "data_types": set(),
                "third_parties": set(),
                "purposes": set()
            }

    def _build_prompt(self, text: str) -> str:
        """构建提示词"""
        prompt = f"""You are a privacy policy analyzer. Extract the following information from the given text:

1. **Data Types**: What types of personal information are mentioned? (e.g., "email", "location", "name")
2. **Third Parties**: Which third-party companies or entities are mentioned? (e.g., "Facebook", "Google", "advertisers")
3. **Purposes**: Why is the data collected or used? (e.g., "advertising", "analytics", "security")

Text:
\"\"\"
{text}
\"\"\"

Return your answer in this exact JSON format:
{{
  "data_types": ["type1", "type2", ...],
  "third_parties": ["party1", "party2", ...],
  "purposes": ["purpose1", "purpose2", ...]
}}

Rules:
- Return ONLY valid JSON, no additional text
- Use lowercase for all items
- Be specific and extract actual terms from the text
- If nothing is found for a category, return an empty list []
"""
        return prompt

    def _call_llm(self, prompt: str) -> str:
        """调用 LLM API"""
        if self.provider in ["deepseek", "openai"]:
            return self._call_openai_compatible(prompt)
        elif self.provider == "claude":
            return self._call_claude(prompt)
        else:
            raise ValueError(f"不支持的提供商: {self.provider}")

    def _call_openai_compatible(self, prompt: str) -> str:
        """
        调用 OpenAI 兼容的 API (DeepSeek, OpenAI)
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # DeepSeek 使用的模型名称
        model = "deepseek-chat" if self.provider == "deepseek" else "gpt-3.5-turbo"

        data = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a privacy policy analyzer. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,  # 降低随机性，提高一致性
            "response_format": {"type": "json_object"} if self.provider == "openai" else None
        }

        # 移除 None 值
        data = {k: v for k, v in data.items() if v is not None}

        response = requests.post(
            self.endpoints[self.provider],
            headers=headers,
            json=data,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"API 请求失败: {response.status_code} - {response.text}")

        result = response.json()
        return result["choices"][0]["message"]["content"]

    def _call_claude(self, prompt: str) -> str:
        """调用 Claude API"""
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }

        data = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        response = requests.post(
            self.endpoints[self.provider],
            headers=headers,
            json=data,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"API 请求失败: {response.status_code} - {response.text}")

        result = response.json()
        return result["content"][0]["text"]

    def _parse_response(self, response: str) -> Dict[str, Set[str]]:
        """解析 LLM 响应"""
        try:
            # 尝试直接解析 JSON
            data = json.loads(response)
        except json.JSONDecodeError:
            # 如果失败，尝试提取 JSON 部分
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise ValueError("无法从响应中提取 JSON")

        # 转换为 set 并统一小写
        result = {
            "data_types": set(item.lower().strip() for item in data.get("data_types", [])),
            "third_parties": set(item.lower().strip() for item in data.get("third_parties", [])),
            "purposes": set(item.lower().strip() for item in data.get("purposes", []))
        }

        return result


def test_llm_extractor():
    """测试 LLM 提取器"""
    print("\n" + "="*70)
    print("测试 DeepSeek LLM 提取器")
    print("="*70 + "\n")

    # 从环境变量或直接使用你提供的 API key
    api_key = os.getenv("DEEPSEEK_API_KEY") or "sk-b0b770ea4c6c40aca383cdf5e5f6008e"

    extractor = LLMExtractor(provider="deepseek", api_key=api_key)

    # 测试句子
    test_texts = [
        "We collect your name, email address, and location data when you use our services.",
        "We share your personal information with Facebook, Google, and advertising partners for marketing purposes.",
        "You have the right to access, modify, and delete your personal information at any time.",
    ]

    print("开始测试...\n")

    for i, text in enumerate(test_texts, 1):
        print(f"【测试 {i}】")
        print(f"文本: {text}\n")

        result = extractor.extract_privacy_parameters(text)

        print(f"数据类型: {result['data_types']}")
        print(f"第三方: {result['third_parties']}")
        print(f"目的: {result['purposes']}")
        print("\n" + "-"*70 + "\n")

    print("✓ 测试完成")


if __name__ == "__main__":
    test_llm_extractor()
