"""
Web scraper for IFS documentation
Scrapes content from docs.ifs.com and extracts relevant information
"""

from bs4 import BeautifulSoup
from typing import List, Dict
import time
import logging
import re
from urllib.parse import urlparse
from playwright_stealth import Stealth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IFSDocsScraper:
    """Scraper for IFS documentation website using Playwright"""
    
    def __init__(self, base_url: str = "https://docs.ifs.com"):
        self.base_url = base_url
        self.dataset_url = "https://docs.ifs.com/techdocs/23r2/" 
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def start_browser(self):
        """Start the persistent browser session"""
        from playwright.sync_api import sync_playwright
        
        if self.playwright:
            return

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        self.context = self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = self.context.new_page()
        stealth = Stealth()
        stealth.apply_stealth_sync(self.page)
        logger.info("Browser session started")

    def close_browser(self):
        """Close the persistent browser session"""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        
        self.page = None
        self.context = None
        self.browser = None
        self.playwright = None
        logger.info("Browser session closed")
    
    def get_page_content(self, url: str) -> str:
        """
        Get page content using persistent Playwright session
        """
        if not self.page:
            self.start_browser()
            
        try:
            logger.info(f"Navigating to {url}")
            self.page.goto(url, wait_until='domcontentloaded', timeout=60000)
            
            # Wait for potential verification or redirect
            # Reduced wait time since we are reusing session
            self.page.wait_for_timeout(5000) 
            
            # Check for verification challenge
            content = self.page.content()
            if "browser" in self.page.title().lower() and "verif" in self.page.title().lower():
                logger.warning("Verification page detected, waiting longer...")
                self.page.wait_for_timeout(15000)
            
            # Wait for main content to appear
            try:
                self.page.wait_for_selector('main, .content, .main-content', timeout=5000)
            except:
                logger.warning("Main content selector not found, proceeding with current content")
            
            return self.page.content()
            
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return ""

    def scrape_page(self, url: str) -> Dict[str, str]:
        """
        Scrape a single documentation page
        """
        try:
            html_content = self.get_page_content(url)
            if not html_content:
                return {
                    'url': url,
                    'title': '',
                    'content': '',
                    'code_examples': []
                }

            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract title
            title = soup.find('h1')
            title_text = title.get_text(strip=True) if title else "No Title"
            
            # Check for verification page
            if "browser" in title_text.lower() and "verif" in title_text.lower():
                logger.warning("Still hitting verification page")
                return {
                    'url': url,
                    'title': '',
                    'content': '',
                    'code_examples': []
                }

            # Extract main content
            content_div = soup.find('div', {'class': ['content', 'main-content', 'documentation']})
            if not content_div:
                content_div = soup.find('main') or soup.find('article') or soup.find('body')
            
            # Extract text content
            text_content = ""
            if content_div:
                # Remove sripts and styles
                for script in content_div(["script", "style"]):
                    script.decompose()
                text_content = content_div.get_text(separator='\n', strip=True)
            
            # Extract code blocks
            code_blocks = []
            code_elements = soup.find_all(['code', 'pre'])
            for code in code_elements:
                code_text = code.get_text(strip=True)
                if code_text and len(code_text) > 10:
                    code_blocks.append(code_text)
            
            return {
                'url': url,
                'title': title_text,
                'content': text_content,
                'code_examples': code_blocks
            }
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return {
                'url': url,
                'title': '',
                'content': '',
                'code_examples': []
            }
    
    def normalize_filename(self, url: str) -> str:
        """Video specific filename from URL"""
        parsed = urlparse(url)
        path = parsed.path
        
        if path.endswith('/'):
            path = path[:-1]
            
        name = path.split('/')[-1]
        
        if not name or name == 'docs.ifs.com':
            name = 'index'
            
        clean_name = re.sub(r'[<>:"/\\|?*]', '_', name)
        
        if not clean_name.endswith('.md'):
            clean_name += '.md'
            
        return clean_name

    def save_page(self, page: Dict[str, str], output_dir: str):
        """Save a single scraped page to disk"""
        import os
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        if not page['content']:
            return
            
        filename = self.normalize_filename(page['url'])
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"---\n")
            f.write(f"url: {page['url']}\n")
            f.write(f"title: {page['title']}\n")
            f.write(f"---\n\n")
            f.write(f"# {page['title']}\n\n")
            f.write(f"{page['content']}")
            
            if page['code_examples']:
                f.write("\n\n## Extracted Code Examples\n\n")
                for i, code in enumerate(page['code_examples'], 1):
                    f.write(f"### Example {i}\n")
                    f.write("```\n")
                    f.write(f"{code}")
                    f.write("\n```\n\n")
        
        logger.info(f"Saved {filepath}")

    def discover_links(self, start_url: str, max_pages: int = 50, stay_under_start_url: bool = False) -> List[str]:
        """
        Discover documentation links from the starting page using Playwright
        """
        try:
            html_content = self.get_page_content(start_url)
            if not html_content:
                return [start_url]

            soup = BeautifulSoup(html_content, 'html.parser')
            links = set()
            links.add(start_url)
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                if href.startswith('/'):
                    full_url = self.base_url + href
                    if not self.base_url.endswith('/') and not href.startswith('/'):
                         full_url = self.base_url + '/' + href
                elif href.startswith('http'):
                    full_url = href
                else:
                    base_path = start_url.rsplit('/', 1)[0]
                    if not base_path.endswith('/'):
                        base_path += '/'
                    full_url = base_path + href
                
                # Clean URL
                full_url = full_url.split('#')[0]

                if stay_under_start_url:
                    if not full_url.startswith(start_url):
                        continue
                
                try:
                    parsed = urlparse(full_url)
                    if (parsed.hostname and 
                        (parsed.hostname == 'docs.ifs.com' or 
                         parsed.hostname.endswith('.docs.ifs.com') or
                         full_url.startswith(self.base_url))):
                        links.add(full_url)
                except ValueError:
                    continue
                
                if len(links) >= max_pages:
                    break
            
            return list(links)[:max_pages]
            
        except Exception as e:
            logger.error(f"Error discovering links from {start_url}: {str(e)}")
            return [start_url]
    
    def scrape_documentation(self, start_url: str = None, max_pages: int = 50, output_dir: str = None) -> List[Dict[str, str]]:
        """
        Scrape multiple documentation pages
        """
        if start_url is None:
            start_url = self.base_url
        
        logger.info(f"Starting documentation scrape from {start_url}")
        
        # Ensure browser is started
        self.start_browser()
        
        try:
            logger.info("Discovering documentation pages...")
            urls = self.discover_links(start_url, max_pages, stay_under_start_url=bool(output_dir))
            logger.info(f"Found {len(urls)} pages to scrape")
            
            scraped_data = []
            for i, url in enumerate(urls, 1):
                logger.info(f"Scraping page {i}/{len(urls)}: {url}")
                data = self.scrape_page(url)
                if data['content']:
                    scraped_data.append(data)
                    
                    # Save incrementally if output_dir is specified
                    if output_dir:
                        self.save_page(data, output_dir)
                
                # Be respectful with rate limiting (Browser is slower anyway)
                time.sleep(1)
            
            logger.info(f"Scraping complete. Collected {len(scraped_data)} pages with content")
                
            return scraped_data
            
        finally:
            self.close_browser()


if __name__ == "__main__":
    # Test the scraper
    scraper = IFSDocsScraper()
    # Note: Requires 'playwright install' to be run first
    print("Scraper now uses Playwright. Make sure to run 'playwright install' first.")
