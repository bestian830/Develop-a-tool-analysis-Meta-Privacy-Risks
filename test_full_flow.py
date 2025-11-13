#!/usr/bin/env python3
"""
测试完整的爬取-分析流程
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'api'))
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from api.services import PolicyService
from analyzer import PrivacyPolicyAnalyzer

def test_full_flow():
    url = "https://mbasic.facebook.com/privacy/policy/printable/"
    
    print("=" * 80)
    print("测试完整流程：爬取 -> 提取 -> 分析")
    print("=" * 80)
    print(f"\nURL: {url}\n")
    
    # 1. 爬取（使用Selenium）
    print("步骤1: 使用Selenium爬取...")
    service = PolicyService()
    try:
        # 直接使用Selenium，跳过requests
        content = service.fetch_policy_content(url, use_selenium=True)
        print(f"✓ 爬取成功！内容长度: {len(content)} 字符")
        print(f"\n前500字符预览:")
        print("-" * 80)
        print(content[:500])
        print("-" * 80)
        
        # 检查编码
        import re
        non_printable = re.findall(r'[^\x20-\x7E\n\r\t]', content[:1000])
        readable = sum(1 for c in content[:1000] if c.isprintable() or c.isspace())
        print(f"\n编码检查（前1000字符）:")
        print(f"  可读字符: {readable}/1000")
        print(f"  非打印字符: {len(non_printable)}")
        
        if readable < 800:
            print("  ⚠️  警告: 内容可能包含乱码")
            return False
        
        # 2. 分析
        print("\n步骤2: 分析内容...")
        analyzer = PrivacyPolicyAnalyzer()
        
        # 先测试分段
        segments = analyzer.segment_policy(content)
        print(f"  分段数: {len(segments)}")
        if segments:
            print(f"  第一段长度: {len(segments[0])}")
            print(f"  第一段前200字符:")
            print("  " + segments[0][:200])
            
            # 检查第一段编码
            non_printable_seg = re.findall(r'[^\x20-\x7E\n\r\t]', segments[0][:200])
            readable_seg = sum(1 for c in segments[0][:200] if c.isprintable() or c.isspace())
            print(f"  第一段编码检查:")
            print(f"    可读字符: {readable_seg}/200")
            print(f"    非打印字符: {len(non_printable_seg)}")
        
        # 完整分析
        result = analyzer.analyze(content)
        print(f"\n✓ 分析完成！")
        print(f"  - 段落数: {result['summary']['total_segments']}")
        print(f"  - 平均风险分数: {result['summary']['average_risk_score']:.2f}")
        
        # 检查第一个段落结果
        if result['segment_analyses']:
            first_seg = result['segment_analyses'][0]
            print(f"\n第一个段落分析结果:")
            print(f"  文本长度: {len(first_seg['text'])}")
            print(f"  文本前200字符:")
            print("  " + first_seg['text'][:200])
            
            # 检查编码（检查实际文本长度，而不是固定200字符）
            text_to_check = first_seg['text'][:min(200, len(first_seg['text']))]
            non_printable_result = re.findall(r'[^\x20-\x7E\n\r\t]', text_to_check)
            readable_result = sum(1 for c in text_to_check if c.isprintable() or c.isspace())
            print(f"  编码检查:")
            print(f"    可读字符: {readable_result}/{len(text_to_check)}")
            print(f"    非打印字符: {len(non_printable_result)}")
            
            # 如果文本长度足够，检查可读字符比例
            if len(text_to_check) > 50:
                readable_ratio = readable_result / len(text_to_check)
                if readable_ratio < 0.7:  # 如果可读字符少于70%，可能是乱码
                    print("  ⚠️  警告: 分析结果包含乱码")
                    return False
                else:
                    print(f"  ✓ 编码正常（可读字符比例: {readable_ratio:.1%}）")
        
        return True
        
    except Exception as e:
        import traceback
        print(f"\n❌ 错误: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_full_flow()
    sys.exit(0 if success else 1)

