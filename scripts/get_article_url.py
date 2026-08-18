#!/usr/bin/env python3
"""
Генератор URL для Telegram-постов.
Использует ту же логику slugify, что и generate_news_pages.py.

Usage:
  python3 get_article_url.py "Заголовок новости" [YYYY-MM-DD]
"""

import sys
import re
from datetime import datetime

def slugify(text):
    """Создаёт URL-friendly slug из заголовка."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')[:80]

def get_article_urls(title, date_str=None):
    """Возвращает URL для статьи на GitHub."""
    if date_str is None:
        date_obj = datetime.now()
    else:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    
    slug = slugify(title)
    year = date_obj.year
    month = f"{date_obj.month:02d}"
    day = f"{date_obj.day:02d}"
    
    base_url = f"https://github.com/bimaevoleg-rgb/news/blob/main/{year}/{month}/{day}/{slug}.html"
    preview_url = f"https://htmlpreview.github.io/?https://github.com/bimaevoleg-rgb/news/blob/main/{year}/{month}/{day}/{slug}.html"
    
    return {
        "slug": slug,
        "github": base_url,
        "preview": preview_url,
        "date": f"{year}-{month}-{day}"
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 get_article_url.py 'Заголовок новости' [YYYY-MM-DD]")
        sys.exit(1)
    
    title = sys.argv[1]
    date_str = sys.argv[2] if len(sys.argv) > 2 else None
    
    urls = get_article_urls(title, date_str)
    
    print(f"Заголовок: {title}")
    print(f"Slug: {urls['slug']}")
    print(f"GitHub: {urls['github']}")
    print(f"Preview: {urls['preview']}")
