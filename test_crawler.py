#!/usr/bin/env python3
"""
测试爬虫和分析功能
"""
import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent / 'api'))
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from api.services import PolicyService
from analyzer import PrivacyPolicyAnalyzer

def test_crawler_and_analyzer():
    url = "https://mbasic.facebook.com/privacy/policy/printable/"
    
    print("=" * 80)
    print("测试爬虫和分析功能")
    print("=" * 80)
    print(f"\n目标URL: {url}\n")
    
    # 1. 测试爬虫
    print("步骤1: 爬取内容...")
    service = PolicyService()
    
    try:
        content = service.fetch_policy_content(url, use_selenium=False)
        print(f"✓ 爬取成功！内容长度: {len(content)} 字符")
        
        # 显示前1000字符（检查编码）
        print("\n前1000字符预览:")
        print("-" * 80)
        print(content[:1000])
        print("-" * 80)
        
        # 检查是否有乱码
        import re
        # 检查是否有大量非ASCII非字母数字字符
        non_printable = re.findall(r'[^\x20-\x7E\n\r\t]', content[:1000])
        if len(non_printable) > 100:
            print(f"\n⚠️  警告: 检测到大量非打印字符 ({len(non_printable)}个)，可能存在编码问题")
        else:
            print(f"\n✓ 编码检查通过（非打印字符: {len(non_printable)}个）")
        
        # 2. 测试分析
        print("\n步骤2: 分析内容...")
        analyzer = PrivacyPolicyAnalyzer()
        result = analyzer.analyze(content)
        
        print(f"✓ 分析完成！")
        print(f"  - 段落数: {result['summary']['total_segments']}")
        print(f"  - 平均风险分数: {result['summary']['average_risk_score']:.2f}")
        print(f"  - 数据类型数量: {len(result['summary']['total_data_types'])}")
        print(f"  - 第三方数量: {len(result['summary']['total_third_parties'])}")
        
        # 显示第一个段落的文本（检查是否有乱码）
        if result['segment_analyses']:
            first_segment = result['segment_analyses'][0]
            print(f"\n第一个段落文本预览（前200字符）:")
            print("-" * 80)
            print(first_segment['text'][:200])
            print("-" * 80)
            
            # 检查段落文本是否有乱码
            non_printable_seg = re.findall(r'[^\x20-\x7E\n\r\t]', first_segment['text'][:200])
            if len(non_printable_seg) > 20:
                print(f"\n⚠️  警告: 段落文本包含大量非打印字符 ({len(non_printable_seg)}个)")
            else:
                print(f"\n✓ 段落文本编码正常（非打印字符: {len(non_printable_seg)}个）")
        
        return True
        
    except Exception as e:
        import traceback
        print(f"\n❌ 错误: {e}")
        print("\n详细错误信息:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_crawler_and_analyzer()
    sys.exit(0 if success else 1)

