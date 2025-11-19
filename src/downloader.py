from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from pathlib import Path

def fetch_policy(url, out_path):
    """
    Fetches the HTML content from the given URL using Selenium and saves it to the output path.
    """
    try:
        options = Options()
        options.add_argument("--headless=new") # Newer headless mode is more stealthy
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Execute CDP commands to hide selenium
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        })
        
        print(f"Downloading {url} with Selenium...")
        driver.get(url)
        time.sleep(5)  # Wait for JS to load
        
        html = driver.page_source
        driver.quit()
        
        # Ensure directory exists
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        
        Path(out_path).write_text(html, encoding="utf-8")
        print(f"Successfully downloaded {url} to {out_path}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        raise
