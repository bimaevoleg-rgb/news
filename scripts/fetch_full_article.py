#!/usr/bin/env python3
"""
Скрипт для извлечения полного контента статей из URL.
Поддерживает aiweekly.co и другие источники.
"""

import sys
import json
import re
import time
from pathlib import Path
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "requests", "beautifulsoup4"])
    import requests
    from bs4 import BeautifulSoup


def extract_aiweekly_article(url):
    """Извлекает статью с aiweekly.co"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ищем основной контент
        article = soup.find('article') or soup.find('main') or soup.find('div', class_='content')
        
        if not article:
            # Пробуем найти по другим селекторам
            article = soup.find('div', class_=re.compile('article|content|post'))
        
        if article:
            # Удаляем навигацию, рекламу, сайдбары
            for elem in article.find_all(['nav', 'aside', 'footer', 'header', 'script', 'style']):
                elem.decompose()
            
            # Извлекаем текст
            paragraphs = []
            for p in article.find_all(['p', 'h1', 'h2', 'h3', 'li']):
                text = p.get_text().strip()
                if text and len(text) > 20:
                    paragraphs.append(text)
            
            return '\n\n'.join(paragraphs)
        
        return None
    except Exception as e:
        print(f"Error extracting {url}: {e}")
        return None


def extract_generic_article(url):
    """Универсальный извлекатель для других сайтов"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Удаляем ненужные элементы
        for elem in soup.find_all(['nav', 'aside', 'footer', 'header', 'script', 'style', 'noscript']):
            elem.decompose()
        
        # Ищем основной контент
        article = soup.find('article')
        if article:
            paragraphs = []
            for p in article.find_all(['p', 'h1', 'h2', 'h3', 'li']):
                text = p.get_text().strip()
                if text and len(text) > 20:
                    paragraphs.append(text)
            return '\n\n'.join(paragraphs)
        
        # Fallback: берём все параграфы из body
        body = soup.find('body')
        if body:
            paragraphs = []
            for p in body.find_all('p'):
                text = p.get_text().strip()
                if text and len(text) > 50:
                    paragraphs.append(text)
            return '\n\n'.join(paragraphs)
        
        return None
    except Exception as e:
        print(f"Error extracting {url}: {e}")
        return None


def extract_article(url):
    """Определяет тип сайта и извлекает статью"""
    domain = urlparse(url).netloc.lower()
    
    if 'aiweekly.co' in domain:
        return extract_aiweekly_article(url)
    else:
        return extract_generic_article(url)


def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch_full_article.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    print(f"Fetching: {url}")
    
    content = extract_article(url)
    
    if content:
        print(f"\nExtracted {len(content)} characters")
        print("\n--- CONTENT PREVIEW ---")
        print(content[:500] + "..." if len(content) > 500 else content)
    else:
        print("Failed to extract content")
        sys.exit(1)


if __name__ == '__main__':
    main()
