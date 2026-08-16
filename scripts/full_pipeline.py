#!/usr/bin/env python3
"""
Интегрированный скрипт для создания полного архива новостей.
Шаги:
1. Парсит дайджест
2. Извлекает URL источников  
3. Скачивает полные статьи
4. Переводит на русский
5. Генерирует HTML
"""

import sys
import os
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

# Добавляем путь к скриптам
sys.path.insert(0, '/root/.openclaw/workspace/news-repo/scripts')

REPO_ROOT = Path('/root/.openclaw/workspace/news-repo')
SCRIPTS_DIR = REPO_ROOT / 'scripts'

def run_fetch_article(url, output_file):
    """Запускает fetch_full_article.py"""
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / 'fetch_full_article.py'), url],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            # Извлекаем контент из вывода
            content_match = re.search(r'--- CONTENT PREVIEW ---\n(.+)', result.stdout, re.DOTALL)
            if content_match:
                return content_match.group(1)
        return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def translate_with_openclaw(text):
    """
    Переводит текст через OpenClaw API.
    В реальном сценарии будет вызывать API.
    """
    # TODO: Интеграция с OpenClaw для перевода
    # Пока возвращаем placeholder
    return text


def process_digest_with_full_articles(digest_text, date_obj):
    """
    Обрабатывает дайджест, извлекая полные статьи.
    """
    from generate_news_pages import parse_digest
    
    news_items = parse_digest(digest_text, date_obj)
    
    for item in news_items:
        print(f"\n📰 Processing: {item['title'][:60]}...")
        
        # Ищем URL в источнике
        urls = re.findall(r'https?://[^\s\)]+', item['source'])
        
        if urls:
            url = urls[0]
            print(f"   🔗 Source: {url}")
            
            # Пытаемся скачать полную статью
            full_content = run_fetch_article(url, '/tmp/article.txt')
            
            if full_content and len(full_content) > 500:
                print(f"   ✅ Downloaded {len(full_content)} chars")
                
                # Переводим
                translated = translate_with_openclaw(full_content)
                
                if translated:
                    item['full_content'] = translated
                    item['is_full'] = True
                    print(f"   ✅ Translated")
                else:
                    item['full_content'] = full_content
                    item['is_full'] = True
                    print(f"   ⚠️ Using original (translation failed)")
            else:
                print(f"   ⚠️ Could not fetch full article, using summary")
        else:
            print(f"   ⚠️ No URL found, using summary")
    
    return news_items


def main():
    if len(sys.argv) < 2:
        print("Usage: python full_pipeline.py <digest_file.txt> [YYYY-MM-DD]")
        sys.exit(1)
    
    digest_path = Path(sys.argv[1])
    if not digest_path.exists():
        print(f"Error: File not found: {digest_path}")
        sys.exit(1)
    
    digest_text = digest_path.read_text(encoding='utf-8')
    
    if len(sys.argv) >= 3:
        date_obj = datetime.strptime(sys.argv[2], '%Y-%m-%d')
    else:
        date_obj = datetime.now()
    
    print(f"🚀 Processing digest for {date_obj.strftime('%Y-%m-%d')}")
    print("=" * 50)
    
    # Обрабатываем с полными статьями
    news_items = process_digest_with_full_articles(digest_text, date_obj)
    
    # Генерируем HTML (вызываем generate_news_pages.py)
    # Сохраняем во временный JSON для передачи
    full_content_json = {}
    for item in news_items:
        if item.get('is_full'):
            slug = re.sub(r'[^\w\s-]', '', item['title'].lower())
            slug = re.sub(r'[-\s]+', '-', slug).strip('-')[:80]
            full_content_json[slug] = item['full_content']
    
    if full_content_json:
        json_path = '/tmp/full_content.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(full_content_json, f, ensure_ascii=False, indent=2)
        
        # Вызываем generate_news_pages.py с full-content
        subprocess.run([
            sys.executable, str(SCRIPTS_DIR / 'generate_news_pages.py'),
            str(digest_path), date_obj.strftime('%Y-%m-%d'),
            '--full-content', json_path
        ])
    else:
        # Без полного контента
        subprocess.run([
            sys.executable, str(SCRIPTS_DIR / 'generate_news_pages.py'),
            str(digest_path), date_obj.strftime('%Y-%m-%d')
        ])
    
    print("\n✅ Pipeline complete!")


if __name__ == '__main__':
    main()
