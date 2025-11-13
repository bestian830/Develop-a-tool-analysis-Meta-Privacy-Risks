"""
测试噪音过滤效果

对比增强前后的噪音过滤能力
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import spacy
from analyzer import PrivacyPolicyAnalyzer


def test_noise_filtering():
    """测试噪音过滤"""
    print("\n" + "="*80)
    print("噪音过滤效果测试")
    print("="*80 + "\n")

    # 初始化分析器（禁用 Transformer SRL 以加快测试）
    analyzer = PrivacyPolicyAnalyzer(use_transformer_srl=False)

    # 测试用例：这些应该被识别为噪音
    noise_samples = [
        "Privacy Policy",
        "Explore the policy",
        "Highlights",
        "Learn more in Privacy Center about managing your privacy",
        "1",
        "2",
        "[1]",
        "[2]",
        "Effective June 26, 2024",
        "We've updated our Privacy Policy. Read the new policy.",
        "What information do we collect?",
        "How do we use your information?",
        "Facebook",
        "Instagram",
        "Messenger",
        "Terms of Service",
        "Cookies Policy",
        "Read the full policy below",
        "Click here",
        "Learn more",
        "Back to top",
    ]

    # 测试用例：这些应该被保留（真实的政策内容）
    valid_samples = [
        "We collect your name, email address, and location data when you use our services.",
        "This Privacy Policy explains how we collect, use and share your information.",
        "We share your information with advertising partners and analytics companies.",
        "You have the right to access, correct, and delete your personal information.",
        "We implement encryption and secure servers to protect your data.",
        "We may disclose your data to law enforcement agencies when required by law.",
        "The Privacy Policy also lets you know your rights.",
        "We at Meta want you to understand what information we collect, and how we use and share it.",
    ]

    print("【噪音内容识别测试】\n")
    noise_correct = 0
    for sample in noise_samples:
        is_noise = analyzer.is_noise_content(sample)
        status = "✓" if is_noise else "✗"
        print(f"{status} {'噪音' if is_noise else '保留'}: {sample[:60]}")
        if is_noise:
            noise_correct += 1

    noise_accuracy = noise_correct / len(noise_samples) * 100
    print(f"\n噪音识别准确率: {noise_correct}/{len(noise_samples)} = {noise_accuracy:.1f}%\n")

    print("\n【有效内容保留测试】\n")
    valid_correct = 0
    for sample in valid_samples:
        is_noise = analyzer.is_noise_content(sample)
        status = "✓" if not is_noise else "✗"
        print(f"{status} {'保留' if not is_noise else '噪音'}: {sample[:60]}...")
        if not is_noise:
            valid_correct += 1

    valid_accuracy = valid_correct / len(valid_samples) * 100
    print(f"\n有效内容保留准确率: {valid_correct}/{len(valid_samples)} = {valid_accuracy:.1f}%\n")

    print("\n" + "="*80)
    print("总体测试结果")
    print("="*80)
    total_correct = noise_correct + valid_correct
    total_samples = len(noise_samples) + len(valid_samples)
    total_accuracy = total_correct / total_samples * 100
    print(f"总准确率: {total_correct}/{total_samples} = {total_accuracy:.1f}%")
    print(f"  - 噪音识别: {noise_accuracy:.1f}%")
    print(f"  - 有效内容保留: {valid_accuracy:.1f}%")
    print("="*80 + "\n")


def test_real_policy_filtering():
    """测试真实政策文件的过滤效果"""
    print("\n" + "="*80)
    print("真实政策文件过滤测试")
    print("="*80 + "\n")

    analyzer = PrivacyPolicyAnalyzer(use_transformer_srl=False)

    policy_file = Path(__file__).parent.parent / "data" / "examples" / "facebook_policy.txt"

    if not policy_file.exists():
        print(f"✗ 文件不存在: {policy_file}")
        return

    with open(policy_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 分段并统计
    lines = content.split('\n')
    total_lines = len([l for l in lines if l.strip()])

    segments = analyzer.segment_policy(content)
    kept_segments = len(segments)

    filtered_count = total_lines - kept_segments
    filter_rate = filtered_count / total_lines * 100 if total_lines > 0 else 0

    print(f"原始行数: {total_lines}")
    print(f"保留段落: {kept_segments}")
    print(f"过滤掉: {filtered_count}")
    print(f"过滤率: {filter_rate:.1f}%\n")

    # 显示一些被过滤的示例
    print("【被过滤的内容示例（前20个）】\n")
    filtered_samples = []
    for line in lines[:100]:  # 只检查前100行
        line = line.strip()
        if line and analyzer.is_noise_content(line):
            filtered_samples.append(line)
            if len(filtered_samples) >= 20:
                break

    for i, sample in enumerate(filtered_samples, 1):
        print(f"{i}. {sample}")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    test_noise_filtering()
    test_real_policy_filtering()
