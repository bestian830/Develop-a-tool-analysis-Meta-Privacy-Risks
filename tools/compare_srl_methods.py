"""
对比不同 SRL 方法的效果

比较:
1. spaCy 依存解析 SRL
2. Transformer NER-based SRL
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import spacy
from srl_extractor import SemanticRoleAnalyzer
from transformer_srl import TransformerSRLExtractor


def compare_srl_methods():
    """对比两种 SRL 方法"""
    print("\n" + "="*80)
    print("SRL 方法对比测试")
    print("="*80 + "\n")

    # 初始化两种提取器
    print("初始化 spaCy SRL...")
    nlp = spacy.load("en_core_web_sm")
    spacy_srl = SemanticRoleAnalyzer(nlp)

    print("初始化 Transformer SRL...")
    transformer_srl = TransformerSRLExtractor()

    # 测试句子
    test_sentences = [
        "We collect your name, email address, and location data when you use our services.",
        "We share your personal information with Facebook, Google, and advertising partners.",
        "You have the right to access, modify, and delete your personal data.",
        "We use cookies and device identifiers to analyze user behavior for marketing purposes.",
        "Your payment information is encrypted and stored securely on our servers.",
        "We may disclose your data to law enforcement agencies when required by law.",
    ]

    print("\n" + "="*80)
    print("开始对比测试")
    print("="*80 + "\n")

    spacy_total = {"data_types": 0, "third_parties": 0, "purposes": 0}
    transformer_total = {"data_types": 0, "third_parties": 0, "purposes": 0}

    for i, sentence in enumerate(test_sentences, 1):
        print(f"\n【测试 {i}】")
        print(f"句子: {sentence}\n")

        # spaCy SRL
        print("spaCy SRL 结果:")
        spacy_result = spacy_srl.extract_privacy_parameters(sentence)
        print(f"  数据类型 ({len(spacy_result['data_types'])}): {spacy_result['data_types']}")
        print(f"  第三方 ({len(spacy_result['third_parties'])}): {spacy_result['third_parties']}")
        print(f"  目的 ({len(spacy_result['purposes'])}): {spacy_result['purposes']}")

        spacy_total["data_types"] += len(spacy_result['data_types'])
        spacy_total["third_parties"] += len(spacy_result['third_parties'])
        spacy_total["purposes"] += len(spacy_result['purposes'])

        # Transformer SRL
        print("\nTransformer SRL 结果:")
        transformer_result = transformer_srl.extract_privacy_parameters(sentence)
        print(f"  数据类型 ({len(transformer_result['data_types'])}): {transformer_result['data_types']}")
        print(f"  第三方 ({len(transformer_result['third_parties'])}): {transformer_result['third_parties']}")
        print(f"  目的 ({len(transformer_result['purposes'])}): {transformer_result['purposes']}")

        transformer_total["data_types"] += len(transformer_result['data_types'])
        transformer_total["third_parties"] += len(transformer_result['third_parties'])
        transformer_total["purposes"] += len(transformer_result['purposes'])

        print("\n" + "-"*80)

    # 总结
    print("\n" + "="*80)
    print("总结对比")
    print("="*80 + "\n")

    print(f"测试句子数: {len(test_sentences)}\n")

    print("spaCy SRL 总计:")
    print(f"  数据类型: {spacy_total['data_types']}")
    print(f"  第三方: {spacy_total['third_parties']}")
    print(f"  目的: {spacy_total['purposes']}")
    print(f"  总计: {sum(spacy_total.values())}\n")

    print("Transformer SRL 总计:")
    print(f"  数据类型: {transformer_total['data_types']}")
    print(f"  第三方: {transformer_total['third_parties']}")
    print(f"  目的: {transformer_total['purposes']}")
    print(f"  总计: {sum(transformer_total.values())}\n")

    print("="*80)
    print("结论:")
    print("="*80)

    if sum(transformer_total.values()) > sum(spacy_total.values()):
        improvement = (sum(transformer_total.values()) - sum(spacy_total.values())) / sum(spacy_total.values()) * 100
        print(f"✓ Transformer SRL 提取了更多参数 (+{improvement:.1f}%)")
        print("  建议: 集成 Transformer SRL 到主分析器")
    elif sum(spacy_total.values()) > sum(transformer_total.values()):
        print("✓ spaCy SRL 提取了更多参数")
        print("  建议: 继续使用 spaCy SRL")
    else:
        print("✓ 两种方法提取的参数数量相同")
        print("  建议: 可以组合使用两种方法以获得最佳覆盖")

    print("\n注意: 数量不是唯一指标，准确性和相关性同样重要。")
    print("      建议手工检查提取结果的质量。")
    print("="*80 + "\n")


if __name__ == "__main__":
    compare_srl_methods()
