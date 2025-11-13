"""
测试 LLM 集成到主分析器的效果

对比：
1. 纯本地模型（spaCy + Transformer SRL）
2. 本地模型 + LLM 辅助
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from analyzer import PrivacyPolicyAnalyzer


def test_llm_integration():
    """测试 LLM 集成效果"""
    print("\n" + "="*80)
    print("LLM 集成测试 - 对比本地模型 vs LLM增强")
    print("="*80 + "\n")

    # 测试文本
    test_texts = [
        "We collect your name, email address, phone number, and location data when you use our services.",
        "We share your personal information with Facebook, Google, Amazon, and other advertising partners for marketing and analytics purposes.",
        "You have the right to access, modify, export, and delete your personal information at any time through your account settings.",
    ]

    # API key
    api_key = "sk-b0b770ea4c6c40aca383cdf5e5f6008e"

    print("初始化分析器...\n")

    # 本地模型
    print("【1】纯本地模型 (spaCy + Transformer SRL):")
    analyzer_local = PrivacyPolicyAnalyzer(
        use_transformer_srl=True,
        use_llm=False
    )
    print()

    # LLM 增强
    print("【2】LLM 增强模式 (本地 + DeepSeek):")
    analyzer_llm = PrivacyPolicyAnalyzer(
        use_transformer_srl=True,
        use_llm=True,
        llm_provider="deepseek",
        llm_api_key=api_key
    )
    print()

    print("="*80)
    print("开始对比测试")
    print("="*80 + "\n")

    for i, text in enumerate(test_texts, 1):
        print(f"\n【测试 {i}】")
        print(f"文本: {text}\n")

        # 本地模型分析
        result_local = analyzer_local.analyze_segment(text)
        params_local = result_local["parameters"]

        print("本地模型结果:")
        print(f"  数据类型 ({len(params_local['data_types'])}): {sorted(params_local['data_types'])[:5]}")
        print(f"  第三方 ({len(params_local['third_parties'])}): {sorted(params_local['third_parties'])}")
        print(f"  目的 ({len(params_local['purposes'])}): {sorted(params_local['purposes'])}")

        # LLM 增强分析
        result_llm = analyzer_llm.analyze_segment(text)
        params_llm = result_llm["parameters"]

        print("\nLLM 增强结果:")
        print(f"  数据类型 ({len(params_llm['data_types'])}): {sorted(params_llm['data_types'])[:5]}")
        print(f"  第三方 ({len(params_llm['third_parties'])}): {sorted(params_llm['third_parties'])}")
        print(f"  目的 ({len(params_llm['purposes'])}): {sorted(params_llm['purposes'])}")

        # 计算提升
        improvement = {
            "data_types": len(params_llm['data_types']) - len(params_local['data_types']),
            "third_parties": len(params_llm['third_parties']) - len(params_local['third_parties']),
            "purposes": len(params_llm['purposes']) - len(params_local['purposes'])
        }

        print("\n提升:")
        for key, value in improvement.items():
            if value > 0:
                print(f"  {key}: +{value}")
            elif value < 0:
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: 无变化")

        print("\n" + "-"*80)

    print("\n" + "="*80)
    print("测试完成")
    print("="*80)


if __name__ == "__main__":
    test_llm_integration()
