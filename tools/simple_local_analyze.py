#!/usr/bin/env python3
"""
简化版隐私政策分析工具 - 本地NLP版本
使用 spaCy 进行本地分析，无需 LLM API
"""

import sys
import os
import argparse

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from simple_local_analyzer import SimpleLocalAnalyzer


def main():
    parser = argparse.ArgumentParser(
        description="简化版隐私政策分析工具 - 本地NLP版本（无需API）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 分析隐私政策文件
  python simple_local_analyze.py policy.txt

  # 生成Markdown报告
  python simple_local_analyze.py policy.txt -o report.md

  # 使用中文spaCy模型
  python simple_local_analyze.py policy.txt --model zh_core_web_sm

  # 从URL抓取并分析
  python simple_local_analyze.py --url https://example.com/privacy

特点:
  ✅ 完全本地运行，无API成本
  ✅ 基于spaCy NLP
  ✅ 专注数据-活动映射
  ✅ 不做复杂的PIPEDA分类和风险评估
        """
    )

    parser.add_argument('input_file', nargs='?', help='隐私政策文件路径')
    parser.add_argument('--url', help='隐私政策URL（代替文件输入）')
    parser.add_argument('-o', '--output', help='输出报告文件路径')
    parser.add_argument('-f', '--format', choices=['markdown', 'text'], default='markdown',
                        help='报告格式 (默认: markdown)')
    parser.add_argument('--model', default='en_core_web_sm',
                        help='spaCy模型名称 (默认: en_core_web_sm)')
    parser.add_argument('--show-summary-only', action='store_true',
                        help='只显示摘要，不显示完整报告')

    args = parser.parse_args()

    # 检查输入
    if not args.input_file and not args.url:
        parser.print_help()
        print("\n❌ 错误: 请提供输入文件或URL")
        sys.exit(1)

    # 读取隐私政策文本
    if args.url:
        print(f"📥 从URL获取隐私政策: {args.url}")
        # 使用fetch_policy工具
        try:
            from fetch_policy import PolicyFetcher
            fetcher = PolicyFetcher()
            policy_text = fetcher.fetch(args.url)
            if not policy_text:
                print("❌ 无法获取隐私政策")
                sys.exit(1)
        except ImportError:
            print("❌ fetch_policy模块不可用，请手动下载隐私政策")
            sys.exit(1)
    else:
        print(f"📖 读取文件: {args.input_file}")
        try:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                policy_text = f.read()
        except FileNotFoundError:
            print(f"❌ 文件不存在: {args.input_file}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
            sys.exit(1)

    print(f"   文本长度: {len(policy_text)} 字符\n")

    # 初始化分析器
    print(f"🔧 初始化分析器 (使用 {args.model})...")
    try:
        analyzer = SimpleLocalAnalyzer(model_name=args.model)
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        print("\n💡 提示: 请确保安装了spaCy模型")
        print(f"   运行: python -m spacy download {args.model}")
        sys.exit(1)

    # 执行分析
    print("\n" + "="*60)
    results = analyzer.analyze(policy_text)
    print("="*60 + "\n")

    # 显示摘要
    summary = results['summary']
    print("📊 分析摘要")
    print("-"*60)
    print(f"分析段落数:     {summary['total_segments']}")
    print(f"数据类型:       {summary['total_data_types']} 种")
    print(f"活动场景:       {summary['total_activities']} 个")
    print(f"数据-活动映射:   {summary['total_mappings']} 条")
    print("="*60 + "\n")

    # 如果只显示摘要，到此为止
    if args.show_summary_only:
        sys.exit(0)

    # 生成报告
    report = analyzer.generate_report(results, output_format=args.format)

    # 输出报告
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"✅ 报告已保存到: {args.output}")
        except Exception as e:
            print(f"❌ 保存报告失败: {e}")
            print("\n报告内容:\n")
            print(report)
    else:
        print(report)


if __name__ == "__main__":
    main()
