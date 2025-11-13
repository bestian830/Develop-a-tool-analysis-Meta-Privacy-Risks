"""
业务逻辑服务
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from database import db_session
from models import PolicyAnalysis, PolicyComparison
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))
from analyzer import PrivacyPolicyAnalyzer
from compare_versions import PolicyVersionComparator
import re


class PolicyService:
    """隐私政策服务"""
    
    def __init__(self):
        self.analyzer = PrivacyPolicyAnalyzer()
        self.comparator = PolicyVersionComparator()
    
    def fetch_policy_content(self, url: str, use_selenium: bool = False) -> str:
        """
        爬取隐私政策内容
        
        参数:
            url: 隐私政策URL
            use_selenium: 是否使用Selenium（用于需要JavaScript渲染的页面）
            
        返回:
            清理后的文本内容
        """
        # 如果明确要求使用Selenium，直接使用
        if use_selenium:
            return self._fetch_with_selenium(url)
        
        # 否则先尝试使用requests方法
        try:
            return self._fetch_with_requests(url)
        except Exception as e:
            # 如果requests失败且允许使用Selenium，尝试Selenium
            error_msg = str(e)
            if "400" in error_msg or "403" in error_msg or "forbidden" in error_msg.lower() or "detected" in error_msg.lower():
                print(f"⚠️  Requests方法失败: {error_msg}")
                print("🔄 尝试使用Selenium方法...")
                try:
                    return self._fetch_with_selenium(url)
                except Exception as selenium_error:
                    raise Exception(f"Requests方法失败: {error_msg}。Selenium方法也失败: {str(selenium_error)}")
            else:
                raise Exception(f"Failed to fetch policy content: {str(e)}")
    
    def _fetch_with_requests(self, url: str) -> str:
        """使用requests库爬取（基础方法）"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',  # requests会自动处理gzip
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Referer': 'https://www.google.com/',  # 添加Referer，让它看起来像从Google跳转来的
        }
        
        session = requests.Session()
        session.headers.update(headers)
        
        # 允许重定向
        response = session.get(url, timeout=30, allow_redirects=True)
        
        # 检查状态码
        if response.status_code == 400:
            # Facebook返回400可能是反爬虫，尝试使用Selenium
            raise Exception(f"Bad Request (400). Facebook may have detected automated access. Try using Selenium method.")
        elif response.status_code == 403:
            raise Exception(f"Access forbidden (403). The website may have anti-scraping protection.")
        elif response.status_code == 404:
            raise Exception(f"Page not found (404). Please check if the URL is correct.")
        elif response.status_code >= 400:
            raise Exception(f"HTTP {response.status_code} error. The website may require authentication or have restrictions.")
        
        response.raise_for_status()
        
        # 检查内容类型
        content_type = response.headers.get('Content-Type', '').lower()
        
        # 检查是否是错误页面
        response_text = response.text.lower()
        if 'error' in response_text[:500] and ('facebook' in response_text[:500] or 'not found' in response_text[:500]):
            raise Exception("Received error page instead of content. Facebook may have blocked the request.")
        
        # 使用requests自动处理的文本（它已经正确处理了编码和gzip）
        html_content = response.text
        
        # 如果response.text有问题，手动处理
        if not html_content or len(html_content) < 100:
            # 手动处理编码
            raw_content = response.content
            
            # 检查是否是压缩内容（虽然requests应该已经处理了）
            content_encoding = response.headers.get('Content-Encoding', '').lower()
            if content_encoding == 'gzip':
                import gzip
                try:
                    raw_content = gzip.decompress(raw_content)
                except:
                    pass
            
            # 检测编码
            encoding = 'utf-8'
            if 'charset=' in content_type:
                try:
                    charset = content_type.split('charset=')[1].split(';')[0].strip()
                    if charset:
                        encoding = charset
                except:
                    pass
            
            # 解码
            try:
                html_content = raw_content.decode(encoding, errors='replace')
            except:
                html_content = raw_content.decode('utf-8', errors='replace')
        
        if 'application/json' in content_type:
            # 如果是JSON，尝试解析
            try:
                json_data = response.json()
                # 尝试提取文本内容
                if isinstance(json_data, dict):
                    # 查找可能的文本字段
                    text_fields = ['content', 'text', 'body', 'html', 'data']
                    for field in text_fields:
                        if field in json_data:
                            return str(json_data[field])
                raise Exception("Received JSON response but couldn't extract text content")
            except:
                raise Exception("Received JSON response instead of HTML")
        
        # 解析HTML并提取文本
        return self._extract_text_from_html(html_content)
    
    def _fetch_with_selenium(self, url: str) -> str:
        """使用Selenium爬取（用于需要JavaScript渲染的页面）"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.chrome.service import Service
            import time
        except ImportError:
            raise Exception("Selenium未安装。运行: pip install selenium")
        
        # 配置Chrome选项
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')  # 使用新的headless模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # 隐藏自动化特征
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        driver = None
        try:
            driver = webdriver.Chrome(options=chrome_options)
            
            # 执行脚本隐藏webdriver特征
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                '''
            })
            
            driver.get(url)
            
            # 等待页面加载
            time.sleep(8)  # Facebook页面可能需要更长时间加载
            
            # 尝试等待主要内容加载
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except:
                pass
            
            # 获取页面内容 - 使用原来的方法：直接获取body文本（Selenium已经处理了编码）
            try:
                # 方法1: 直接获取body文本（最简单可靠，Selenium已经处理了编码）
                body_element = driver.find_element(By.TAG_NAME, "body")
                text_content = body_element.text
                
                # 如果获取的文本太短，可能是页面还没加载完，尝试获取HTML
                if len(text_content) < 500:
                    html_content = driver.page_source
                    # 确保HTML内容是字符串
                    if isinstance(html_content, bytes):
                        html_content = html_content.decode('utf-8', errors='replace')
                    # 使用BeautifulSoup提取
                    return self._extract_text_from_html(html_content)
                else:
                    # 直接返回文本（已经清理过了）
                    return text_content
            except Exception as e:
                # 如果直接获取文本失败，回退到HTML解析
                html_content = driver.page_source
                # 确保HTML内容是字符串
                if isinstance(html_content, bytes):
                    html_content = html_content.decode('utf-8', errors='replace')
                # 使用BeautifulSoup提取
                return self._extract_text_from_html(html_content)
            
        except Exception as e:
            raise Exception(f"Selenium爬取失败: {str(e)}")
        finally:
            if driver:
                driver.quit()
    
    def _extract_text_from_html(self, html_content: str) -> str:
        """
        从HTML内容中智能提取隐私政策文本（预处理阶段）
        
        策略：
        1. 移除脚本和样式
        2. 直接提取body文本（最简单可靠）
        3. 基本过滤噪音内容
        """
        # 确保HTML内容是字符串且编码正确
        if isinstance(html_content, bytes):
            try:
                html_content = html_content.decode('utf-8', errors='replace')
            except:
                html_content = html_content.decode('latin1', errors='replace').encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        
        # 使用lxml解析器，它对编码处理更好
        # 如果lxml不可用，使用html.parser
        try:
            soup = BeautifulSoup(html_content, 'lxml')
        except:
            # 如果lxml失败，使用html.parser
            soup = BeautifulSoup(html_content, 'html.parser')
        
        # 第一步：只移除脚本和样式（不要移除其他元素，避免破坏结构）
        for tag in soup(["script", "style", "noscript", "iframe", "embed", "object"]):
            tag.decompose()
        
        # 第二步：直接使用body提取文本（最简单可靠）
        main_content = soup.find('body') or soup
        
        # 第三步：直接提取文本（get_text已经正确处理了编码）
        text = main_content.get_text(separator='\n\n', strip=True)
        
        # 第四步：基本过滤（只过滤明显的噪音）
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        filtered_lines = []
        
        noise_keywords = {
            "click here", "learn more", "read more", "see more", "menu", "footer",
            "header", "navigation", "cookie settings", "settings", "home", "back",
            "next", "previous", "skip", "continue", "submit", "cancel", "close",
            "accept all", "reject all", "manage preferences", "sign in", "log in",
            "sign up", "register", "subscribe", "share", "print", "download",
            "search", "go", "ok", "yes", "no", "return to top", "back to top"
        }
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # 跳过太短的行
            if len(line_lower) < 10:
                continue
            
            # 跳过纯数字或特殊字符
            if not any(c.isalpha() for c in line_lower):
                continue
            
            # 跳过明显的噪音关键词（但不要太严格，避免误删）
            if line_lower in noise_keywords and len(line_lower) < 50:
                continue
            
            filtered_lines.append(line)
        
        text = '\n\n'.join(filtered_lines)
        
        # 第五步：验证内容质量
        if len(text) < 500:  # 隐私政策通常至少500字符
            raise Exception("Extracted content is too short. The page may require JavaScript to load content, or the URL doesn't contain a privacy policy.")
        
        return text
    
    def _remove_noise_elements(self, soup):
        """移除HTML中的噪音元素"""
        # 移除脚本和样式
        for tag in soup(["script", "style", "noscript", "iframe", "embed", "object"]):
            tag.decompose()
        
        # 移除导航和页眉页脚
        for tag in soup.find_all(["nav", "header", "footer", "aside"]):
            tag.decompose()
        
        # 移除常见的广告和无关内容容器
        noise_classes = [
            'advertisement', 'ad', 'ads', 'sidebar', 'menu', 'navigation',
            'cookie-banner', 'cookie-notice', 'popup', 'modal', 'overlay',
            'social-media', 'share-buttons', 'related-posts', 'comments',
            'breadcrumb', 'breadcrumbs', 'skip-link', 'skip-to-content'
        ]
        
        for class_name in noise_classes:
            for tag in soup.find_all(class_=lambda x: x and class_name in str(x).lower()):
                tag.decompose()
        
        # 移除aria-label包含导航、菜单等的元素
        for tag in soup.find_all(attrs={"aria-label": lambda x: x and any(
            word in x.lower() for word in ['menu', 'navigation', 'skip', 'cookie']
        )}):
            tag.decompose()
        
        # 移除role为navigation, banner, complementary的元素
        for role in ['navigation', 'banner', 'complementary', 'search']:
            for tag in soup.find_all(attrs={"role": role}):
                tag.decompose()
    
    def _find_policy_content(self, soup):
        """
        智能查找隐私政策的主要内容区域
        
        策略：
        1. 查找包含隐私政策关键词的元素
        2. 查找常见的内容容器
        3. 选择包含最多政策相关文本的区域
        """
        # 隐私政策相关的关键词
        policy_keywords = [
            'privacy policy', 'privacy notice', 'data protection', 'personal information',
            'data collection', 'data use', 'data sharing', 'your rights', 'your data',
            'information we collect', 'how we use', 'third party', 'cookies',
            'gdpr', 'ccpa', 'pipeda', 'data retention', 'data security'
        ]
        
        # 优先级选择器（从最具体到最通用）
        selectors = [
            # 最具体的隐私政策容器
            '[class*="privacy"]', '[class*="policy"]', '[id*="privacy"]', '[id*="policy"]',
            '[class*="legal"]', '[class*="terms"]',
            # 通用内容容器
            'main', '[role="main"]', 'article', '[role="article"]',
            '.main-content', '.content', '.article-content', '.post-content',
            '.policy-content', '.legal-content', '#content', '#main', '#article'
        ]
        
        best_match = None
        best_score = 0
        
        # 尝试每个选择器
        for selector in selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text().lower()
                    # 计算包含政策关键词的数量
                    score = sum(1 for keyword in policy_keywords if keyword in text)
                    if score > best_score:
                        best_score = score
                        best_match = element
            except:
                continue
        
        # 如果找到了包含政策关键词的区域，返回它
        if best_match and best_score >= 2:
            return best_match
        
        # 否则尝试查找包含最多文本的article或main元素
        for tag_name in ['article', 'main', 'div']:
            elements = soup.find_all(tag_name)
            for element in elements:
                text = element.get_text().strip()
                # 检查是否包含政策关键词且文本足够长
                if len(text) > 1000:
                    keyword_count = sum(1 for keyword in policy_keywords if keyword in text.lower())
                    if keyword_count >= 1:
                        return element
        
        return None
    
    def _extract_and_clean_text(self, element) -> str:
        """
        提取文本并进行预处理清理
        
        在爬取阶段只做基本清理，保留原始文本内容
        避免过度清理导致编码问题
        """
        if not element:
            return ""
        
        # 方法1: 直接使用get_text()提取（最简单可靠）
        # 这已经正确处理了编码
        # 使用separator='\n\n'来保持段落结构
        text = element.get_text(separator='\n\n', strip=True)
        
        # 如果提取的内容太短，可能是提取方法有问题
        # 尝试更细致的提取
        if len(text) < 500:
            # 尝试按段落提取
            paragraphs = []
            for p in element.find_all(['p', 'div', 'section', 'article', 'main']):
                para_text = p.get_text(strip=True, separator=' ')
                # 只保留有意义的段落
                if para_text and len(para_text.strip()) > 20:
                    paragraphs.append(para_text)
            
            if paragraphs:
                text = '\n\n'.join(paragraphs)
        
        # 如果还是没有足够内容，直接提取所有文本
        if len(text) < 500:
            text = element.get_text(separator='\n\n')
        
        # 过滤噪音段落（基于内容，不基于字符编码）
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        filtered_lines = []
        
        noise_keywords = {
            "click here", "learn more", "read more", "see more", "menu", "footer",
            "header", "navigation", "cookie settings", "settings", "home", "back",
            "next", "previous", "skip", "continue", "submit", "cancel", "close",
            "accept all", "reject all", "manage preferences", "sign in", "log in",
            "sign up", "register", "subscribe", "share", "print", "download",
            "search", "go", "ok", "yes", "no", "return to top", "back to top"
        }
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # 跳过太短的行
            if len(line_lower) < 10:
                continue
            
            # 跳过纯数字或特殊字符（但保留Unicode字符）
            if not any(c.isalpha() for c in line_lower):
                continue
            
            # 跳过噪音关键词
            if line_lower in noise_keywords:
                continue
            
            # 跳过常见的UI元素模式
            if any(pattern in line_lower for pattern in [
                '^learn more', '^read more', '^click here', '^explore',
                '^back to top', '^table of contents', '^privacy center$'
            ]):
                continue
            
            # 跳过版权信息（通常在页脚）
            if 'copyright' in line_lower or any(char in line for char in ['©', '®', '™']):
                continue
            
            # 跳过纯链接文本（通常很短且没有标点）
            if len(line.split()) <= 3 and not any(char in line for char in ['.', ',', ':', ';']):
                if line_lower.startswith(('http', 'www.', 'mailto:')):
                    continue
            
            filtered_lines.append(line)
        
        # 合并行，用双换行分隔
        return '\n\n'.join(filtered_lines)
    
    def _ensure_serializable(self, obj):
        """确保对象可以被JSON序列化（处理set等类型）"""
        import json
        try:
            # 先尝试序列化，如果失败则递归处理
            json.dumps(obj, ensure_ascii=False)
            return obj
        except (TypeError, ValueError):
            if isinstance(obj, dict):
                return {k: self._ensure_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [self._ensure_serializable(item) for item in obj]
            elif isinstance(obj, set):
                return list(obj)
            elif isinstance(obj, str):
                # 确保字符串是UTF-8编码（但不做过度清理）
                try:
                    if isinstance(obj, bytes):
                        return obj.decode('utf-8', errors='replace')
                    # 只确保是字符串类型，不做内容清理
                    # 清理工作留给显示层处理
                    return str(obj)
                except:
                    return str(obj)
            elif hasattr(obj, '__dict__'):
                return self._ensure_serializable(obj.__dict__)
            else:
                return str(obj)
    
    def analyze_policy_from_url(self, url: str) -> dict:
        """
        从URL爬取并分析隐私政策
        
        参数:
            url: 隐私政策URL
            
        返回:
            分析结果字典
        """
        # 1. 爬取内容
        # 对于Facebook等有反爬虫保护的网站，直接使用Selenium
        if 'facebook.com' in url or 'mbasic.facebook.com' in url:
            policy_content = self.fetch_policy_content(url, use_selenium=True)
        else:
            # 其他网站先尝试requests，失败则使用Selenium
            try:
                policy_content = self.fetch_policy_content(url, use_selenium=False)
            except Exception as e:
                # 如果requests失败（特别是400/403错误），尝试使用Selenium
                error_msg = str(e)
                if "400" in error_msg or "403" in error_msg or "forbidden" in error_msg.lower() or "detected" in error_msg.lower():
                    print(f"⚠️  Requests方法失败: {error_msg}")
                    print("🔄 尝试使用Selenium方法...")
                    try:
                        policy_content = self.fetch_policy_content(url, use_selenium=True)
                    except Exception as selenium_error:
                        raise Exception(f"Requests方法失败: {error_msg}。Selenium方法也失败: {str(selenium_error)}")
                else:
                    raise
        
        # 2. 分析
        analysis_result = self.analyzer.analyze(policy_content)
        
        # 确保分析结果是可序列化的（处理set等类型）
        # 注意：这里只做序列化处理，不做文本清理（避免破坏原始内容）
        analysis_result = self._ensure_serializable(analysis_result)
        
        # 3. 保存到数据库
        summary = analysis_result.get('summary', {})
        policy_analysis = PolicyAnalysis(
            url=url,
            policy_content=policy_content,  # 存储原始内容但不返回
            analysis_result=analysis_result,
            total_segments=summary.get('total_segments', 0),
            average_risk_score=summary.get('average_risk_score', 0),
            total_data_types=len(summary.get('total_data_types', [])),
            total_third_parties=len(summary.get('total_third_parties', []))
        )
        
        db_session.add(policy_analysis)
        db_session.commit()
        
        # 4. 返回结果（不包含原始内容）
        return {
            'id': policy_analysis.id,
            'url': url,
            'analysis_result': analysis_result,
            'created_at': policy_analysis.created_at.isoformat() if policy_analysis.created_at else None
        }
    
    def get_all_reports(self) -> list:
        """获取所有分析报告列表"""
        reports = db_session.query(PolicyAnalysis).order_by(PolicyAnalysis.created_at.desc()).all()
        return [report.to_dict() for report in reports]
    
    def get_report_by_id(self, report_id: int) -> dict:
        """根据ID获取分析报告"""
        report = db_session.query(PolicyAnalysis).filter_by(id=report_id).first()
        if report:
            return report.to_dict()
        return None
    
    def delete_report(self, report_id: int) -> bool:
        """删除分析报告"""
        report = db_session.query(PolicyAnalysis).filter_by(id=report_id).first()
        if report:
            db_session.delete(report)
            db_session.commit()
            return True
        return False
    
    def compare_policy_versions(self, old_url: str, new_url: str) -> dict:
        """
        对比两个版本的隐私政策
        
        参数:
            old_url: 旧版本URL
            new_url: 新版本URL
            
        返回:
            对比结果字典
        """
        # 爬取两个版本的内容
        old_content = self.fetch_policy_content(old_url, use_selenium=('facebook.com' in old_url or 'mbasic.facebook.com' in old_url))
        new_content = self.fetch_policy_content(new_url, use_selenium=('facebook.com' in new_url or 'mbasic.facebook.com' in new_url))
        
        # 执行对比
        comparison_result = self.comparator.compare_versions(old_content, new_content)
        
        # 确保结果可序列化
        comparison_result = self._ensure_serializable(comparison_result)
        
        return {
            'old_url': old_url,
            'new_url': new_url,
            'comparison_result': comparison_result
        }
    
    def compare_policy_texts(self, old_text: str, new_text: str) -> dict:
        """
        对比两个版本的隐私政策文本
        
        参数:
            old_text: 旧版本文本
            new_text: 新版本文本
            
        返回:
            对比结果字典
        """
        # 执行对比
        comparison_result = self.comparator.compare_versions(old_text, new_text)
        
        # 确保结果可序列化
        comparison_result = self._ensure_serializable(comparison_result)
        
        return {
            'comparison_result': comparison_result
        }
    
    def save_comparison(self, old_url: str = None, new_url: str = None, comparison_result: dict = None) -> dict:
        """
        保存版本对比结果到数据库
        
        参数:
            old_url: 旧版本URL（可选）
            new_url: 新版本URL（可选）
            comparison_result: 对比结果字典
            
        返回:
            保存后的结果字典（包含ID）
        """
        if not comparison_result:
            raise ValueError("comparison_result is required")
        
        # 提取摘要信息
        risk_change_data = comparison_result.get('risk_change', {})
        
        # 创建对比记录
        comparison = PolicyComparison(
            old_url=old_url,
            new_url=new_url,
            comparison_result=comparison_result,
            risk_change=risk_change_data.get('risk_change', 0),
            old_average_risk=risk_change_data.get('old_average_risk', 0),
            new_average_risk=risk_change_data.get('new_average_risk', 0)
        )
        
        db_session.add(comparison)
        db_session.commit()
        
        return comparison.to_dict()
    
    def get_all_comparisons(self) -> list:
        """获取所有对比报告列表"""
        comparisons = db_session.query(PolicyComparison).order_by(PolicyComparison.created_at.desc()).all()
        return [comp.to_dict() for comp in comparisons]
    
    def get_comparison_by_id(self, comparison_id: int) -> dict:
        """根据ID获取对比报告"""
        comparison = db_session.query(PolicyComparison).filter_by(id=comparison_id).first()
        if comparison:
            return comparison.to_dict()
        return None
    
    def delete_comparison(self, comparison_id: int) -> bool:
        """删除对比报告"""
        comparison = db_session.query(PolicyComparison).filter_by(id=comparison_id).first()
        if comparison:
            db_session.delete(comparison)
            db_session.commit()
            return True
        return False

