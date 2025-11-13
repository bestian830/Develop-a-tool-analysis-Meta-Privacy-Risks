#!/usr/bin/env python3
"""
调试Facebook页面的编码问题
"""
import requests
import sys

url = "https://mbasic.facebook.com/privacy/policy/printable/"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

print("=" * 80)
print("调试Facebook页面编码")
print("=" * 80)
print(f"\nURL: {url}\n")

response = requests.get(url, headers=headers, timeout=30)

print("响应头信息:")
print(f"  Content-Type: {response.headers.get('Content-Type', 'N/A')}")
print(f"  Content-Encoding: {response.headers.get('Content-Encoding', 'N/A')}")
print(f"  Status Code: {response.status_code}")
print()

# 检查原始内容
raw_content = response.content
print(f"原始内容长度: {len(raw_content)} 字节")
print(f"前100字节（hex）: {raw_content[:100].hex()}")
print()

# 检查是否是gzip
content_encoding = response.headers.get('Content-Encoding', '').lower()
print(f"Content-Encoding: {content_encoding}")

# 尝试不同的解码方式
encodings_to_try = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']

for encoding in encodings_to_try:
    try:
        decoded = raw_content.decode(encoding, errors='strict')
        # 检查是否包含可读文本
        readable_chars = sum(1 for c in decoded[:1000] if c.isprintable() or c.isspace())
        print(f"\n尝试 {encoding}:")
        print(f"  可读字符数（前1000）: {readable_chars}/1000")
        if readable_chars > 800:
            print(f"  ✓ {encoding} 看起来正确！")
            print(f"  前500字符预览:")
            print("  " + "-" * 76)
            print("  " + decoded[:500].replace('\n', ' '))
            print("  " + "-" * 76)
            break
        else:
            print(f"  ✗ {encoding} 看起来不对（太多乱码）")
    except Exception as e:
        print(f"\n尝试 {encoding}: 失败 - {e}")

# 尝试chardet
try:
    import chardet
    detected = chardet.detect(raw_content[:10000])
    print(f"\nchardet检测结果:")
    print(f"  编码: {detected.get('encoding', 'N/A')}")
    print(f"  置信度: {detected.get('confidence', 0):.2%}")
    if detected.get('encoding'):
        encoding = detected['encoding']
        try:
            decoded = raw_content.decode(encoding, errors='replace')
            readable_chars = sum(1 for c in decoded[:1000] if c.isprintable() or c.isspace())
            print(f"  可读字符数（前1000）: {readable_chars}/1000")
            if readable_chars > 800:
                print(f"  ✓ chardet检测的编码看起来正确！")
                print(f"  前500字符预览:")
                print("  " + "-" * 76)
                print("  " + decoded[:500].replace('\n', ' '))
                print("  " + "-" * 76)
        except Exception as e:
            print(f"  解码失败: {e}")
except ImportError:
    print("\nchardet未安装，跳过自动检测")

# 检查response.text（requests自动处理）
print(f"\nresponse.text (requests自动处理):")
print(f"  response.encoding: {response.encoding}")
print(f"  response.apparent_encoding: {response.apparent_encoding}")
if response.text:
    readable_chars = sum(1 for c in response.text[:1000] if c.isprintable() or c.isspace())
    print(f"  可读字符数（前1000）: {readable_chars}/1000")
    if readable_chars > 800:
        print(f"  ✓ response.text 看起来正确！")
        print(f"  前500字符预览:")
        print("  " + "-" * 76)
        print("  " + response.text[:500].replace('\n', ' '))
        print("  " + "-" * 76)
    else:
        print(f"  ✗ response.text 包含太多乱码")

