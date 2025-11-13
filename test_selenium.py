#!/usr/bin/env python3
"""
测试Selenium获取的原始HTML
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'api'))

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    import time
    
    url = "https://mbasic.facebook.com/privacy/policy/printable/"
    
    print("=" * 80)
    print("测试Selenium获取Facebook页面")
    print("=" * 80)
    print(f"\nURL: {url}\n")
    
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("访问页面...")
        driver.get(url)
        time.sleep(10)
        
        print("获取页面源码...")
        html = driver.page_source
        
        print(f"\nHTML长度: {len(html)} 字符")
        print(f"\n前1000字符:")
        print("-" * 80)
        print(html[:1000])
        print("-" * 80)
        
        # 检查是否包含隐私政策关键词
        keywords = ['privacy', 'policy', 'information', 'data', 'collect']
        found_keywords = [kw for kw in keywords if kw.lower() in html.lower()[:5000]]
        print(f"\n找到的关键词: {found_keywords}")
        
        if not found_keywords:
            print("\n⚠️  警告: 页面内容可能不正确（未找到隐私政策关键词）")
        
        # 尝试获取body文本
        try:
            body_text = driver.find_element("tag name", "body").text
            print(f"\nBody文本长度: {len(body_text)} 字符")
            print(f"\nBody前500字符:")
            print("-" * 80)
            print(body_text[:500])
            print("-" * 80)
        except Exception as e:
            print(f"\n无法获取body文本: {e}")
        
    finally:
        driver.quit()
        
except ImportError:
    print("Selenium未安装")
except Exception as e:
    import traceback
    print(f"错误: {e}")
    traceback.print_exc()

