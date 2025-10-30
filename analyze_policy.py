#!/usr/bin/env python3
"""
隐私政策分析器 - 命令行工具

用法:
    python analyze_policy.py <input_file> [options]

示例:
    python analyze_policy.py example_policy.txt
    python analyze_policy.py policy.txt --output report.md --format markdown
"""

import sys
import argparse
import json
from pathlib import Path
from privacy_analyzer_example import PrivacyPolicyAnalyzer


def main():
    parser = argparse.ArgumentParser(
        description="隐私政策分析器 - 基于PIPEDA框架和NLP方法",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s privacy_policy.txt
  %(prog)s policy.txt -o report.md -f markdown
  %(prog)s policy.txt -o report.json -f json
  %(prog)s policy.txt --model en_core_web_trf

更多信息请查看 README.md
        """
    )
    
    parser.add_argument(
        "input_file",
        help="输入的隐私政策文本文件路径"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="输出报告文件路径（默认：输入文件名_analysis.md）"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["markdown", "text", "json"],
        default="markdown",
        help="输出格式（默认：markdown）"
    )
    
    parser.add_argument(
        "-m", "--model",
        default="en_core_web_sm",
        help="spaCy模型名称（默认：en_core_web_sm）"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细输出"
    )
    
    parser.add_argument(
        "--show-summary-only",
        action="store_true",
        help="仅显示摘要，不生成完整报告"
    )
    
    args = parser.parse_args()
    
    # 检查输入文件
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ 错误: 文件不存在: {args.input_file}")
        sys.exit(1)
    
    # 确定输出文件路径
    if args.output:
        output_path = Path(args.output)
    else:
        ext = ".md" if args.format == "markdown" else ".txt" if args.format == "text" else ".json"
        output_path = input_path.with_name(f"{input_path.stem}_analysis{ext}")
    
    # 读取输入文件
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            policy_text = f.read()
    except Exception as e:
        print(f"❌ 错误: 无法读取文件: {e}")
        sys.exit(1)
    
    if args.verbose:
        print(f"📄 读取文件: {input_path}")
        print(f"   文件大小: {len(policy_text)} 字符")
        print(f"📊 使用模型: {args.model}")
        print(f"⚙️  输出格式: {args.format}")
        print()
    
    # 初始化分析器
    print("🔧 初始化分析器...")
    try:
        analyzer = PrivacyPolicyAnalyzer(model_name=args.model)
    except Exception as e:
        print(f"❌ 错误: 无法初始化分析器: {e}")
        print(f"\n提示: 请确保已安装spaCy模型:")
        print(f"    python -m spacy download {args.model}")
        sys.exit(1)
    
    # 执行分析
    print("🔍 正在分析隐私政策...")
    try:
        results = analyzer.analyze(policy_text)
    except Exception as e:
        print(f"❌ 错误: 分析失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # 显示摘要
    summary = results["summary"]
    print("\n" + "="*60)
    print("📋 分析摘要")
    print("="*60)
    print(f"分析段落数:     {summary['total_segments']}")
    print(f"平均风险分数:   {summary['average_risk_score']:.2f}")
    print(f"数据类型数量:   {len(summary['total_data_types'])}")
    print(f"第三方数量:     {len(summary['total_third_parties'])}")
    print()
    
    print("PIPEDA类别分布:")
    for category, count in sorted(summary['category_distribution'].items(), 
                                  key=lambda x: x[1], reverse=True):
        category_cn = analyzer.PIPEDA_CATEGORIES.get(category, category)
        print(f"  • {category_cn}: {count} 个段落")
    print()
    
    # 高风险警告
    high_risk_count = sum(1 for s in results['segment_analyses'] if s['risk_score'] > 0.5)
    if high_risk_count > 0:
        print(f"⚠️  发现 {high_risk_count} 个高风险段落")
        print()
    
    if args.show_summary_only:
        print("✓ 完成（仅显示摘要）")
        return
    
    # 生成报告
    print(f"📝 生成 {args.format} 格式报告...")
    
    if args.format == "json":
        # JSON格式
        report_data = {
            "input_file": str(input_path),
            "analysis_results": results
        }
        output_content = json.dumps(report_data, ensure_ascii=False, indent=2)
    else:
        # Markdown或Text格式
        output_content = analyzer.generate_report(results, output_format=args.format)
    
    # 保存报告
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output_content)
        print(f"✓ 报告已保存到: {output_path}")
    except Exception as e:
        print(f"❌ 错误: 无法保存报告: {e}")
        sys.exit(1)
    
    # 如果是verbose模式，显示一些额外信息
    if args.verbose:
        print()
        print("收集的数据类型（前10个）:")
        for dt in sorted(summary['total_data_types'])[:10]:
            print(f"  • {dt}")
        
        if summary['total_third_parties']:
            print()
            print("涉及的第三方（前10个）:")
            for tp in sorted(summary['total_third_parties'])[:10]:
                print(f"  • {tp}")
    
    print()
    print("="*60)
    print("✓ 分析完成!")
    print("="*60)


if __name__ == "__main__":
    main()




