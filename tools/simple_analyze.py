#!/usr/bin/env python3
"""
简化版隐私政策分析工具
使用 RAG 方法，专注于数据-活动映射
"""

import sys
import os
import argparse

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from simple_rag_analyzer import SimpleRAGAnalyzer


def main():
    parser = argparse.ArgumentParser(
        description="简化版隐私政策分析工具 - 使用RAG提取数据和活动映射",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 分析隐私政策文件
  python simple_analyze.py policy.txt

  # 生成Markdown报告
  python simple_analyze.py policy.txt -o report.md

  # 使用OpenAI代替DeepSeek
  python simple_analyze.py policy.txt --llm openai --api-key sk-xxx

  # 从URL抓取并分析
  python simple_analyze.py --url https://example.com/privacy
        """
    )

    parser.add_argument('input_file', nargs='?', help='隐私政策文件路径')
    parser.add_argument('--url', help='隐私政策URL（代替文件输入）')
    parser.add_argument('-o', '--output', help='输出报告文件路径')
    parser.add_argument('-f', '--format', choices=['markdown', 'text'], default='markdown',
                        help='报告格式 (默认: markdown)')
    parser.add_argument('--llm', choices=['deepseek', 'openai', 'claude'], default='deepseek',
                        help='LLM提供商 (默认: deepseek)')
    parser.add_argument('--api-key', help='LLM API密钥（可选，也可从环境变量读取）')
    parser.add_argument('--chunk-size', type=int, default=2000,
                        help='文本分块大小 (默认: 2000)')

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
        from fetch_policy import PolicyFetcher
        fetcher = PolicyFetcher()
        policy_text = fetcher.fetch(args.url)
        if not policy_text:
            print("❌ 无法获取隐私政策")
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
    print(f"🔧 初始化分析器 (使用 {args.llm})...")
    try:
        analyzer = SimpleRAGAnalyzer(
            llm_provider=args.llm,
            api_key=args.api_key
        )
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        print("\n💡 提示: 请确保设置了正确的API密钥")
        print(f"   环境变量: {args.llm.upper()}_API_KEY")
        print(f"   或使用: --api-key 参数")
        sys.exit(1)

    # 执行分析
    print("\n" + "="*60)
    results = analyzer.analyze(policy_text)
    print("="*60 + "\n")

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

    # 显示摘要
    print("\n" + "="*60)
    print("📊 分析摘要")
    print("="*60)
    summary = results['summary']
    print(f"数据类型:     {summary['total_data_types']} 种")
    print(f"活动场景:     {summary['total_activities']} 个")
    print(f"数据-活动映射: {summary['total_mappings']} 条")
    print("="*60)


if __name__ == "__main__":
    main()
