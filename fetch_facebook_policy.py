"""
Facebook隐私政策抓取工具

由于Facebook有反爬虫保护，这个脚本提供几种方法：
1. 使用Selenium模拟浏览器（需要安装Chrome/Firefox）
2. 使用requests + headers伪装
3. 手动输入（最可靠）
"""

import requests
from pathlib import Path


def fetch_with_requests(url: str) -> str:
    """
    方法1: 使用requests库（可能被阻止）
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"❌ Requests方法失败: {e}")
        return None


def fetch_with_selenium(url: str) -> str:
    """
    方法2: 使用Selenium（需要安装: pip install selenium）
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import time

        # 配置Chrome选项
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 无头模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

        print("🌐 启动浏览器...")
        driver = webdriver.Chrome(options=chrome_options)

        print(f"📄 访问页面: {url}")
        driver.get(url)

        # 等待页面加载
        time.sleep(5)

        # 尝试找到主要内容区域
        try:
            # Facebook隐私政策通常在特定的div中
            content = driver.find_element(By.TAG_NAME, "body").text
        except:
            content = driver.page_source

        driver.quit()
        return content

    except ImportError:
        print("❌ Selenium未安装。运行: pip install selenium")
        print("   还需要下载ChromeDriver: https://chromedriver.chromium.org/")
        return None
    except Exception as e:
        print(f"❌ Selenium方法失败: {e}")
        return None


def manual_input_guide():
    """
    方法3: 手动输入指南
    """
    print("\n" + "="*80)
    print("📝 手动获取Facebook隐私政策指南")
    print("="*80)
    print("""
1. 在浏览器中打开以下链接：
   https://www.facebook.com/privacy/policy
   或
   https://www.facebook.com/privacy/policy/?entry_point=data_policy_redirect

2. 等待页面完全加载

3. 方式A - 复制整个页面：
   - 按 Ctrl+A (Windows) 或 Cmd+A (Mac) 全选
   - 按 Ctrl+C (Windows) 或 Cmd+C (Mac) 复制
   - 创建新文件 facebook_policy_v1.txt 并粘贴

4. 方式B - 浏览器保存：
   - 按 Ctrl+S (Windows) 或 Cmd+S (Mac)
   - 选择保存格式为 "Text" 或 "txt"
   - 保存为 facebook_policy_v1.txt

5. 方式C - 使用打印功能：
   - 按 Ctrl+P (Windows) 或 Cmd+P (Mac)
   - 选择 "Save as PDF" 或 "Print to PDF"
   - 之后可以用PDF转文本工具转换

6. 验证文件：
   - 确保文件至少有几千字
   - 包含完整的章节标题
   - 开头应该是 "Meta Privacy Policy" 或类似标题
""")
    print("="*80)


def clean_html_text(html_content: str) -> str:
    """
    清理HTML内容，提取纯文本
    """
    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html_content, 'html.parser')

        # 移除script和style标签
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()

        # 获取文本
        text = soup.get_text()

        # 清理空行
        lines = [line.strip() for line in text.splitlines()]
        lines = [line for line in lines if line]

        return '\n\n'.join(lines)
    except ImportError:
        print("⚠️  BeautifulSoup未安装。运行: pip install beautifulsoup4")
        return html_content


def main():
    print("="*80)
    print("Facebook隐私政策抓取工具")
    print("="*80)

    url = input("\n请输入Facebook隐私政策URL（直接回车使用默认）: ").strip()
    if not url:
        url = "https://www.facebook.com/privacy/policy"

    print(f"\n目标URL: {url}")
    print("\n尝试获取内容...\n")

    content = None

    # 尝试方法1: Requests
    print("尝试方法1: HTTP请求...")
    content = fetch_with_requests(url)

    if content and len(content) > 1000:
        print("✅ 成功获取内容！")
        content = clean_html_text(content)
    else:
        # 尝试方法2: Selenium
        print("\n尝试方法2: 浏览器模拟...")
        content = fetch_with_selenium(url)

    if content and len(content) > 1000:
        # 生成唯一的文件名，避免覆盖
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 从URL中提取网站名称
        import re
        domain_match = re.search(r'://(?:www\.)?([^/\.]+)', url)
        site_name = domain_match.group(1) if domain_match else "policy"

        # 生成文件名：[网站名]_policy_[时间戳].txt
        output_file = f"{site_name}_policy_{timestamp}.txt"

        # 检查文件是否已存在，如果存在则添加序号
        counter = 1
        original_output = output_file
        while Path(output_file).exists():
            output_file = f"{site_name}_policy_{timestamp}_{counter}.txt"
            counter += 1

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"\n✅ 成功保存到: {output_file}")
        print(f"   文件大小: {len(content)} 字符")
        print(f"   文件路径: {Path(output_file).absolute()}")

        # 显示前500字符预览
        print("\n📄 内容预览（前500字符）:")
        print("-" * 80)
        print(content[:500])
        print("-" * 80)
    else:
        # 如果自动方法都失败，显示手动指南
        print("\n⚠️  自动获取失败。Facebook有反爬虫保护。")
        manual_input_guide()

        # 询问是否手动输入
        print("\n是否要现在手动粘贴内容？(y/n): ", end='')
        choice = input().strip().lower()

        if choice == 'y':
            print("\n请粘贴Facebook隐私政策的完整内容（粘贴完成后按Ctrl+D（Mac/Linux）或Ctrl+Z+Enter（Windows）结束）:")
            print("-" * 80)

            lines = []
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                pass

            content = '\n'.join(lines)

            if len(content) > 100:
                # 生成唯一的文件名
                from datetime import datetime
                import re
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                # 从URL中提取网站名称
                domain_match = re.search(r'://(?:www\.)?([^/\.]+)', url)
                site_name = domain_match.group(1) if domain_match else "policy"

                output_file = f"{site_name}_policy_{timestamp}.txt"

                # 检查文件是否已存在
                counter = 1
                while Path(output_file).exists():
                    output_file = f"{site_name}_policy_{timestamp}_{counter}.txt"
                    counter += 1

                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"\n✅ 已保存到: {output_file}")
                print(f"   文件路径: {Path(output_file).absolute()}")
            else:
                print("\n❌ 内容太短，未保存")


if __name__ == "__main__":
    main()
