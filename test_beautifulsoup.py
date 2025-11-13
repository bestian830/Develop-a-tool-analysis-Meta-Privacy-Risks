#!/usr/bin/env python3
"""
测试BeautifulSoup解析
"""
import sys
from pathlib import Path
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent / 'api'))

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    import time
    
    url = "https://mbasic.facebook.com/privacy/policy/printable/"
    
    print("=" * 80)
    print("测试BeautifulSoup解析")
    print("=" * 80)
    
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(url)
        time.sleep(8)
        html = driver.page_source
        
        print(f"\n原始HTML长度: {len(html)}")
        print(f"前200字符: {html[:200]}\n")
        
        # 测试不同的解析器
        parsers = ['lxml', 'html.parser', 'html5lib']
        
        for parser_name in parsers:
            try:
                print(f"\n使用 {parser_name} 解析器:")
                soup = BeautifulSoup(html, parser_name)
                
                # 移除script和style
                for tag in soup(["script", "style"]):
                    tag.decompose()
                
                # 获取body文本
                body = soup.find('body')
                if body:
                    text = body.get_text(separator=' ', strip=True)
                    print(f"  提取的文本长度: {len(text)}")
                    print(f"  前500字符:")
                    print("  " + "-" * 76)
                    preview = text[:500]
                    print("  " + preview)
                    print("  " + "-" * 76)
                    
                    # 检查乱码
                    import re
                    non_printable = re.findall(r'[^\x20-\x7E\n\r\t]', preview)
                    readable = sum(1 for c in preview if c.isprintable() or c.isspace())
                    print(f"  可读字符: {readable}/500")
                    print(f"  非打印字符: {len(non_printable)}")
                    
                    if readable > 400:
                        print(f"  ✓ {parser_name} 解析成功！")
                        break
                    else:
                        print(f"  ✗ {parser_name} 解析结果包含太多乱码")
            except Exception as e:
                print(f"  ✗ {parser_name} 解析失败: {e}")
        
    finally:
        driver.quit()
        
except Exception as e:
    import traceback
    print(f"错误: {e}")
    traceback.print_exc()

