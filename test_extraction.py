#!/usr/bin/env python3
"""
测试完整的提取流程
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
    print("测试完整提取流程")
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
        
        # 使用lxml解析
        soup = BeautifulSoup(html, 'lxml')
        
        # 移除噪音元素
        for tag in soup(["script", "style", "noscript", "iframe", "embed", "object"]):
            tag.decompose()
        
        # 找到主要内容
        body = soup.find('body') or soup
        
        # 测试不同的提取方法
        print("\n方法1: 直接get_text()")
        text1 = body.get_text(separator='\n', strip=True)
        print(f"  长度: {len(text1)}")
        print(f"  前300字符:")
        print("  " + text1[:300].replace('\n', ' '))
        
        print("\n方法2: 按段落提取（当前方法）")
        paragraphs = []
        for p in body.find_all(['p', 'div', 'section', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            text = p.get_text(strip=True, separator=' ')
            if text:
                paragraphs.append(text)
        
        if paragraphs:
            print(f"  段落数: {len(paragraphs)}")
            print(f"  第一段长度: {len(paragraphs[0])}")
            print(f"  第一段前300字符:")
            print("  " + paragraphs[0][:300])
            
            # 检查是否有乱码
            import re
            non_printable = re.findall(r'[^\x20-\x7E\n\r\t]', paragraphs[0][:300])
            readable = sum(1 for c in paragraphs[0][:300] if c.isprintable() or c.isspace())
            print(f"  可读字符: {readable}/300")
            print(f"  非打印字符: {len(non_printable)}")
        
    finally:
        driver.quit()
        
except Exception as e:
    import traceback
    print(f"错误: {e}")
    traceback.print_exc()

