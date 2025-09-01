"""
Web scraping module for extracting business information from competitor websites.
This module provides tools to scrape business data like names, addresses, services, and pricing.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import time
import logging
from urllib.parse import urljoin, urlparse
import re

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebScraper:
    """
    A web scraper class for extracting business information from websites.
    
    This class provides methods to scrape various types of business data
    including company names, contact information, services, and pricing.
    """
    
    def __init__(self, delay: float = 1.0):
        """
        Initialize the web scraper.
        
        Args:
            delay: Delay between requests to be respectful to websites (in seconds)
        """
        self.delay = delay
        self.session = requests.Session()
        # Set a user agent to appear like a regular browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_website(self, url: str) -> Dict[str, str]:
        """
        Scrape a website and extract business information.
        
        Args:
            url: The website URL to scrape
            
        Returns:
            Dictionary containing extracted business information
        """
        try:
            logger.info(f"Scraping website: {url}")
            
            # Add delay to be respectful to the website
            time.sleep(self.delay)
            
            # Make the HTTP request
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract business information
            business_data = {
                'url': url,
                'business_name': self._extract_business_name(soup, url),
                'description': self._extract_description(soup),
                'services': self._extract_services(soup),
                'contact_info': self._extract_contact_info(soup),
                'address': self._extract_address(soup),
                'pricing_info': self._extract_pricing(soup)
            }
            
            logger.info(f"Successfully scraped {url}")
            return business_data
            
        except requests.RequestException as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return {
                'url': url,
                'error': f"Failed to scrape: {str(e)}",
                'business_name': 'Unknown',
                'description': 'Unable to extract information',
                'services': 'Unable to extract services',
                'contact_info': 'Not available',
                'address': 'Not available',
                'pricing_info': 'Not available'
            }
    
    def _extract_business_name(self, soup: BeautifulSoup, url: str) -> str:
        """Extract the business name from the webpage."""
        # Try multiple strategies to find the business name
        
        # Strategy 1: Look for title tag
        title = soup.find('title')
        if title and title.text.strip():
            # Clean up the title (remove common suffixes)
            name = title.text.strip()
            name = re.sub(r'\s*[-|–]\s*(Home|Welcome|Official Site).*$', '', name, flags=re.IGNORECASE)
            if name and len(name) < 100:  # Reasonable length check
                return name
        
        # Strategy 2: Look for h1 tags
        h1_tags = soup.find_all('h1')
        for h1 in h1_tags:
            if h1.text.strip() and len(h1.text.strip()) < 50:
                return h1.text.strip()
        
        # Strategy 3: Extract from URL domain
        domain = urlparse(url).netloc
        domain_name = domain.replace('www.', '').split('.')[0]
        return domain_name.title()
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract business description from meta tags or content."""
        # Try meta description first
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        
        # Look for about us or description sections
        description_selectors = [
            'section[class*="about"]',
            'div[class*="about"]',
            'section[class*="description"]',
            'div[class*="description"]',
            '.hero-text',
            '.intro'
        ]
        
        for selector in description_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text().strip()
                if text and len(text) > 50:  # Ensure it's substantial
                    return text[:500]  # Limit length
        
        # Fallback: get text from first few paragraphs
        paragraphs = soup.find_all('p')
        description_parts = []
        for p in paragraphs[:3]:
            text = p.get_text().strip()
            if text and len(text) > 20:
                description_parts.append(text)
        
        return ' '.join(description_parts)[:500] if description_parts else "No description available"
    
    def _extract_services(self, soup: BeautifulSoup) -> str:
        """Extract services offered by the business."""
        service_keywords = ['service', 'offering', 'product', 'solution', 'specialt']
        services = []
        
        # Look for sections with service-related keywords
        for keyword in service_keywords:
            elements = soup.find_all(['div', 'section', 'ul'], 
                                   class_=re.compile(keyword, re.I))
            for element in elements:
                # Extract list items or text
                list_items = element.find_all('li')
                if list_items:
                    services.extend([li.get_text().strip() for li in list_items[:10]])
                else:
                    text = element.get_text().strip()
                    if text and len(text) < 200:
                        services.append(text)
        
        # Also look for navigation menus that might list services
        nav_elements = soup.find_all(['nav', 'ul', 'ol'])
        for nav in nav_elements:
            links = nav.find_all('a')
            for link in links:
                link_text = link.get_text().strip()
                if link_text and any(keyword in link_text.lower() 
                                   for keyword in ['service', 'product', 'solution']):
                    services.append(link_text)
        
        # Remove duplicates and return
        unique_services = list(set(services))[:10]  # Limit to 10 services
        return '; '.join(unique_services) if unique_services else "Services not specified"
    
    def _extract_contact_info(self, soup: BeautifulSoup) -> str:
        """Extract contact information like phone numbers and emails."""
        contact_info = []
        
        # Look for phone numbers
        phone_pattern = re.compile(r'(\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})')
        phone_matches = phone_pattern.findall(soup.get_text())
        if phone_matches:
            contact_info.append(f"Phone: {phone_matches[0]}")
        
        # Look for email addresses
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        email_matches = email_pattern.findall(soup.get_text())
        if email_matches:
            # Filter out common non-business emails
            business_emails = [email for email in email_matches 
                             if not any(exclude in email.lower() 
                                      for exclude in ['noreply', 'no-reply', 'example'])]
            if business_emails:
                contact_info.append(f"Email: {business_emails[0]}")
        
        return '; '.join(contact_info) if contact_info else "Contact information not available"
    
    def _extract_address(self, soup: BeautifulSoup) -> str:
        """Extract business address information."""
        # Look for address-related elements
        address_selectors = [
            '[class*="address"]',
            '[class*="location"]',
            '[class*="contact"]',
            'address'
        ]
        
        for selector in address_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text().strip()
                # Check if it looks like an address (contains numbers and words)
                if re.search(r'\d+.*[A-Za-z].*\d+', text) or 'street' in text.lower() or 'ave' in text.lower():
                    return text[:200]  # Limit length
        
        return "Address not available"
    
    def _extract_pricing(self, soup: BeautifulSoup) -> str:
        """Extract pricing information from the website."""
        pricing_keywords = ['price', 'cost', 'rate', 'fee', 'pricing', '$']
        pricing_info = []
        
        # Look for pricing sections
        for keyword in pricing_keywords:
            elements = soup.find_all(['div', 'section', 'span', 'p'], 
                                   class_=re.compile(keyword, re.I))
            for element in elements:
                text = element.get_text().strip()
                # Look for dollar signs and numbers
                if '$' in text or re.search(r'\b\d+.*(?:hour|day|month|year|project)\b', text, re.I):
                    pricing_info.append(text[:100])  # Limit length
        
        # Look for pricing tables
        tables = soup.find_all('table')
        for table in tables:
            table_text = table.get_text().lower()
            if any(keyword in table_text for keyword in ['price', 'cost', 'rate', '$']):
                rows = table.find_all('tr')[:5]  # Limit to first 5 rows
                for row in rows:
                    row_text = row.get_text().strip()
                    if '$' in row_text:
                        pricing_info.append(row_text[:100])
        
        # Remove duplicates and return
        unique_pricing = list(set(pricing_info))[:5]  # Limit to 5 pricing items
        return '; '.join(unique_pricing) if unique_pricing else "Pricing information not available"


def scrape_competitor_list(urls: List[str]) -> List[Dict[str, str]]:
    """
    Scrape multiple competitor websites and return their business information.
    
    Args:
        urls: List of website URLs to scrape
        
    Returns:
        List of dictionaries containing business information for each website
    """
    scraper = WebScraper(delay=1.0)  # 1 second delay between requests
    results = []
    
    for url in urls:
        try:
            # Ensure URL has proper protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            business_data = scraper.scrape_website(url)
            results.append(business_data)
            
        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")
            results.append({
                'url': url,
                'error': str(e),
                'business_name': 'Error',
                'description': 'Failed to scrape',
                'services': 'Not available',
                'contact_info': 'Not available',
                'address': 'Not available',
                'pricing_info': 'Not available'
            })
    
    return results
