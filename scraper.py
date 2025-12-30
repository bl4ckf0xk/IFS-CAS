"""
Web scraper for IFS documentation
Scrapes content from docs.ifs.com and extracts relevant information
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IFSDocsScraper:
    """Scraper for IFS documentation website"""
    
    def __init__(self, base_url: str = "https://docs.ifs.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_page(self, url: str) -> Dict[str, str]:
        """
        Scrape a single documentation page
        
        Args:
            url: URL of the page to scrape
            
        Returns:
            Dictionary containing page content
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('h1')
            title_text = title.get_text(strip=True) if title else "No Title"
            
            # Extract main content
            content_div = soup.find('div', {'class': ['content', 'main-content', 'documentation']})
            if not content_div:
                content_div = soup.find('main') or soup.find('article')
            
            # Extract text content
            text_content = ""
            if content_div:
                text_content = content_div.get_text(separator='\n', strip=True)
            
            # Extract code blocks
            code_blocks = []
            code_elements = soup.find_all(['code', 'pre'])
            for code in code_elements:
                code_text = code.get_text(strip=True)
                if code_text and len(code_text) > 10:  # Filter out small snippets
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
    
    def discover_links(self, start_url: str, max_pages: int = 50) -> List[str]:
        """
        Discover documentation links from the starting page
        
        Args:
            start_url: Starting URL for discovery
            max_pages: Maximum number of pages to discover
            
        Returns:
            List of discovered URLs
        """
        try:
            response = self.session.get(start_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = set()
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    full_url = self.base_url + href
                elif href.startswith('http'):
                    full_url = href
                else:
                    full_url = start_url.rsplit('/', 1)[0] + '/' + href
                
                # Only include docs.ifs.com links - check domain properly
                from urllib.parse import urlparse
                try:
                    parsed = urlparse(full_url)
                    # Validate that the hostname is docs.ifs.com or matches base_url
                    if (parsed.hostname and 
                        (parsed.hostname == 'docs.ifs.com' or 
                         parsed.hostname.endswith('.docs.ifs.com') or
                         full_url.startswith(self.base_url))):
                        links.add(full_url)
                except ValueError:
                    # Skip invalid URLs
                    continue
                
                if len(links) >= max_pages:
                    break
            
            return list(links)[:max_pages]
            
        except Exception as e:
            logger.error(f"Error discovering links from {start_url}: {str(e)}")
            return []
    
    def scrape_documentation(self, start_url: str = None, max_pages: int = 50) -> List[Dict[str, str]]:
        """
        Scrape multiple documentation pages
        
        Args:
            start_url: Starting URL (defaults to base_url)
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of scraped page data
        """
        if start_url is None:
            start_url = self.base_url
        
        logger.info(f"Starting documentation scrape from {start_url}")
        
        # Discover links
        logger.info("Discovering documentation pages...")
        urls = self.discover_links(start_url, max_pages)
        logger.info(f"Found {len(urls)} pages to scrape")
        
        # Scrape each page
        scraped_data = []
        for i, url in enumerate(urls, 1):
            logger.info(f"Scraping page {i}/{len(urls)}: {url}")
            data = self.scrape_page(url)
            if data['content'] or data['code_examples']:
                scraped_data.append(data)
            
            # Be respectful with rate limiting
            time.sleep(1)
        
        logger.info(f"Scraping complete. Collected {len(scraped_data)} pages with content")
        return scraped_data


if __name__ == "__main__":
    # Test the scraper
    scraper = IFSDocsScraper()
    # Note: This is a test - in production, use the actual docs.ifs.com URL
    data = scraper.scrape_documentation(max_pages=5)
    print(f"Scraped {len(data)} pages")
    if data:
        print(f"Example page: {data[0]['title']}")
