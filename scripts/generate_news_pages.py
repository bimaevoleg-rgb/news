#!/usr/bin/env python3
"""
Генератор HTML-страниц новостей из AI-дайджеста.
Создаёт отдельные HTML для каждой новости + обновляет index.html
"""

import re
import os
import sys
from datetime import datetime
from pathlib import Path

# Цвета категорий
CATEGORY_COLORS = {
    "🏆 Главное событие дня": "#ff6b35",
    "🤖 Релизы моделей": "#4285f4",
    "💰 Инвестиции и рынок": "#10a37f",
    "🔓 Open-source": "#ff6a00",
    "🔬 Исследования и аналитика": "#cc785c",
    "🏢 Enterprise": "#7c3aed",
    "🛡️ Безопасность": "#dc2626",
    "⚖️ Регулирование": "#f59e0b",
}

DEFAULT_COLOR = "#666"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — AI Дайджест</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f0f0f;
            color: #e0e0e0;
            line-height: 1.7;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}
        .meta {{
            color: #888;
            font-size: 0.9em;
            margin-bottom: 10px;
        }}
        .category {{
            display: inline-block;
            background: {color};
            color: white;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: 600;
            margin-bottom: 20px;
        }}
        h1 {{
            font-size: 2em;
            color: #fff;
            margin-bottom: 20px;
            line-height: 1.3;
        }}
        .content {{
            font-size: 1.1em;
            color: #d0d0d0;
            margin-bottom: 30px;
        }}
        .content p {{
            margin-bottom: 18px;
            text-align: justify;
        }}
        .content h2, .content h3 {{
            color: #fff;
            margin: 30px 0 15px;
        }}
        .content ul, .content ol {{
            margin: 15px 0 15px 25px;
        }}
        .content li {{
            margin-bottom: 8px;
        }}
        .content blockquote {{
            border-left: 3px solid {color};
            padding-left: 20px;
            margin: 20px 0;
            color: #aaa;
            font-style: italic;
        }}
        .content strong {{
            color: #fff;
        }}
        .highlight {{
            background: {color}15;
            border-left: 3px solid {color};
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
        }}
        .source {{
            border-top: 1px solid #333;
            padding-top: 20px;
            color: #888;
            font-size: 0.9em;
        }}
        .source a {{
            color: #4a9eff;
            text-decoration: none;
        }}
        .source a:hover {{
            text-decoration: underline;
        }}
        .original {{
            margin-top: 10px;
            font-size: 0.85em;
        }}
        .original a {{
            color: #666;
        }}
        .back {{
            margin-top: 40px;
        }}
        .back a {{
            color: #888;
            text-decoration: none;
            font-size: 0.9em;
        }}
        .preview-link {{
            margin-top: 15px;
            padding: 10px 15px;
            background: {color}22;
            border: 1px solid {color}44;
            border-radius: 6px;
        }}
        .preview-link a {{
            color: {color};
            text-decoration: none;
            font-weight: 500;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="meta">{date_str} • AI Дайджест</div>
        <div class="category">{category}</div>
        <h1>{title}</h1>
        <div class="content">
            {content}
        </div>
        <div class="source">
            <div><strong>Источник:</strong> {source}</div>
            <div class="original"><a href="{source_url}" target="_blank">🔗 Оригинальная статья</a></div>
        </div>
        <div class="back">
            <a href="{back_path}">← Назад к архиву</a>
        </div>
    </div>
</body>
</html>
"""

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Дайджест — Архив новостей</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
            line-height: 1.6;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        header {{
            text-align: center;
            margin-bottom: 50px;
            padding-bottom: 30px;
            border-bottom: 1px solid #222;
        }}
        h1 {{
            font-size: 2.5em;
            color: #fff;
            margin-bottom: 10px;
        }}
        .subtitle {{
            color: #666;
            font-size: 1.1em;
        }}
        .date-section {{
            margin-bottom: 40px;
        }}
        .date-header {{
            font-size: 1.5em;
            color: #fff;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #333;
        }}
        .news-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 15px;
        }}
        .news-card {{
            background: #161616;
            border: 1px solid #222;
            border-radius: 8px;
            padding: 20px;
            transition: transform 0.2s, border-color 0.2s;
        }}
        .news-card:hover {{
            transform: translateY(-2px);
            border-color: #444;
        }}
        .news-card a {{
            color: #e0e0e0;
            text-decoration: none;
            display: block;
        }}
        .news-card .category {{
            display: inline-block;
            font-size: 0.75em;
            font-weight: 600;
            padding: 3px 10px;
            border-radius: 4px;
            margin-bottom: 10px;
            color: white;
        }}
        .news-card h3 {{
            font-size: 1.1em;
            line-height: 1.4;
            color: #fff;
        }}
        .footer {{
            text-align: center;
            margin-top: 60px;
            padding-top: 30px;
            border-top: 1px solid #222;
            color: #444;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔥 AI Дайджест</h1>
            <div class="subtitle">Архив новостей AI-индустрии</div>
        </header>

{date_sections}

        <div class="footer">
            Составлено с помощью AI • Источники указаны в каждой новости
        </div>
    </div>
</body>
</html>
"""


def slugify(text):
    """Создаёт URL-friendly slug из заголовка."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')[:80]


def parse_digest(digest_text, date_obj):
    """Парсит текст дайджеста на отдельные новости."""
    news_items = []
    
    # Разбиваем на секции по категориям
    category_pattern = r'(?:^|\n)(🏆|🤖|💰|🔓|🔬|🏢|🛡️|⚖️)[^\n]*\n'
    sections = re.split(category_pattern, digest_text)
    
    # sections: ['header', 'emoji', 'content', 'emoji', 'content', ...]
    current_category = None
    
    for i in range(1, len(sections), 2):
        if i + 1 >= len(sections):
            break
            
        emoji = sections[i]
        section_content = sections[i + 1]
        
        # Извлекаем название категории
        cat_match = re.search(rf'{emoji}([^\n]+)', section_content[:200])
        if cat_match:
            current_category = emoji + cat_match.group(1).strip()
        else:
            current_category = emoji + ' Новости'
        
        # Ищем заголовки внутри секции: **жирный текст** в начале строки/абзаца
        # Разбиваем на блоки по заголовкам
        headline_pattern = r'\*\*([^*]+)\*\*'
        
        # Находим все заголовки в секции
        parts = re.split(r'(?=\*\*[^*]+\*\*)', section_content)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
                
            # Ищем заголовок в начале
            title_match = re.match(r'\*\*([^*]+)\*\*(.*)', part, re.DOTALL)
            if not title_match:
                continue
                
            title = title_match.group(1).strip()
            rest = title_match.group(2).strip()
            
            # Убираем точку в конце заголовка, если она есть
            if title.endswith('.'):
                title = title[:-1].strip()
            
            # Извлекаем контент и источник
            content_lines = []
            source = 'aiweekly.co'
            source_url = ''
            
            for line in rest.split('\n'):
                line = line.strip()
                if not line or line.startswith('---'):
                    continue
                if line.startswith('*(Источник:') or line.startswith('Источник:'):
                    source_raw = re.sub(r'\*?\(Источник:\s*', '', line)
                    source_raw = re.sub(r'\)\*?', '', source_raw).strip()
                    source = source_raw
                    # Извлекаем URL из источника
                    urls = re.findall(r'https?://[^\s\)]+', source_raw)
                    if urls:
                        source_url = urls[0]
                        # Убираем URL из отображаемого источника
                        source = re.sub(r'https?://[^\s\)]+', '', source_raw).strip(' /')
                    continue
                content_lines.append(line)
            
            if title and content_lines:
                news_items.append({
                    'category': current_category,
                    'title': title,
                    'content': '\n'.join(content_lines),
                    'source': source,
                    'source_url': source_url
                })
    
    return news_items


def content_to_html(content_text):
    """Преобразует текст контента в HTML параграфы."""
    paragraphs = []
    for para in content_text.split('\n'):
        para = para.strip()
        if para:
            # Выделяем списки с •
            if para.startswith('•'):
                if not paragraphs or not paragraphs[-1].startswith('<ul>'):
                    paragraphs.append('<ul>')
                paragraphs.append(f'<li>{para[1:].strip()}</li>')
            else:
                if paragraphs and paragraphs[-1].startswith('<ul>'):
                    paragraphs.append('</ul>')
                paragraphs.append(f'<p>{para}</p>')
    
    if paragraphs and paragraphs[-1].startswith('<ul>'):
        paragraphs.append('</ul>')
    
    return '\n            '.join(paragraphs)


def generate_news_page(news_item, date_obj, output_dir, repo_url="https://github.com/bimaevoleg-rgb/news/blob/main"):
    """Генерирует HTML-страницу для одной новости."""
    color = CATEGORY_COLORS.get(news_item['category'], DEFAULT_COLOR)
    slug = slugify(news_item['title'])
    filename = f"{slug}.html"
    filepath = output_dir / filename
    
    # Рассчитываем путь назад
    depth = len(output_dir.relative_to(Path.cwd()).parts)
    back_path = '/'.join(['..'] * depth) or '.'
    
    content_html = content_to_html(news_item.get('full_content', news_item['content']))
    
    # Извлекаем URL источника
    source_url = news_item.get('source_url', '')
    if not source_url:
        urls = re.findall(r'https?://[^\s\)]+', news_item['source'])
        source_url = urls[0] if urls else '#'
    
    # Форматируем источники как ссылки
    sources = news_item['source']
    source_html = sources
    for url in re.findall(r'https?://[^\s\)]+', sources):
        domain = url.replace('https://', '').replace('http://', '').split('/')[0]
        source_html = source_html.replace(url, f'<a href="{url}" target="_blank">{domain}</a>')
    
    html = HTML_TEMPLATE.format(
        title=news_item['title'],
        color=color,
        date_str=date_obj.strftime('%d %B %Y'),
        category=news_item['category'],
        content=content_html,
        source=source_html,
        source_url=source_url,
        back_path=back_path
    )
    
    filepath.write_text(html, encoding='utf-8')
    return filename


def generate_index(all_news, repo_root):
    """Генерирует index.html со всеми новостями."""
    # Группируем по датам
    by_date = {}
    for item in all_news:
        date_key = item['date'].strftime('%Y/%m/%d')
        if date_key not in by_date:
            by_date[date_key] = []
        by_date[date_key].append(item)
    
    # Сортируем даты (новые сверху)
    sorted_dates = sorted(by_date.keys(), reverse=True)
    
    date_sections = []
    for date_key in sorted_dates:
        items = by_date[date_key]
        date_obj = items[0]['date']
        date_str = date_obj.strftime('%d %B %Y')
        
        cards = []
        for item in items:
            color = CATEGORY_COLORS.get(item['category'], DEFAULT_COLOR)
            rel_path = f"{date_key}/{item['filename']}"
            # Генерируем preview URL через htmlpreview.github.io
            preview_url = f"https://htmlpreview.github.io/?https://github.com/bimaevoleg-rgb/news/blob/main/{rel_path}"
            cards.append(f"""                <div class="news-card">
                    <a href="{rel_path}">
                        <span class="category" style="background: {color};">{item['category']}</span>
                        <h3>{item['title']}</h3>
                    </a>
                    <div style="margin-top: 10px; font-size: 0.85em;">
                        <a href="{preview_url}" target="_blank" style="color: {color};">👁️ Предпросмотр</a>
                    </div>
                </div>""")
        
        section = f"""        <div class="date-section">
            <div class="date-header">{date_str}</div>
            <div class="news-grid">
{cards}
            </div>
        </div>"""
        date_sections.append(section)
    
    index_html = INDEX_TEMPLATE.format(date_sections='\n\n'.join(date_sections))
    (repo_root / 'index.html').write_text(index_html, encoding='utf-8')


def scan_existing_news(repo_root):
    """Сканирует существующие новости в репозитории."""
    all_news = []
    
    for year_dir in sorted(repo_root.iterdir()):
        if not year_dir.is_dir() or not year_dir.name.isdigit():
            continue
        
        for month_dir in sorted(year_dir.iterdir()):
            if not month_dir.is_dir():
                continue
            
            for day_dir in sorted(month_dir.iterdir()):
                if not day_dir.is_dir():
                    continue
                
                try:
                    date_obj = datetime(int(year_dir.name), int(month_dir.name), int(day_dir.name))
                except ValueError:
                    continue
                
                for html_file in day_dir.glob('*.html'):
                    # Извлекаем заголовок из HTML
                    content = html_file.read_text(encoding='utf-8')
                    title_match = re.search(r'<title>(.+?) — AI Дайджест</title>', content)
                    cat_match = re.search(r'<div class="category">(.+?)</div>', content)
                    
                    if title_match:
                        all_news.append({
                            'date': date_obj,
                            'filename': html_file.name,
                            'title': title_match.group(1),
                            'category': cat_match.group(1) if cat_match else '🔹 Новости'
                        })
    
    return sorted(all_news, key=lambda x: (x['date'], x['filename']), reverse=True)


def main():
    repo_root = Path('/root/.openclaw/workspace/news-repo')
    
    # Проверяем, передан ли текст дайджеста
    if len(sys.argv) < 2:
        print("Usage: python generate_news_pages.py <digest_file.txt> [YYYY-MM-DD]")
        print("   or: cat digest.txt | python generate_news_pages.py -")
        sys.exit(1)
    
    # Читаем дайджест
    if sys.argv[1] == '-':
        digest_text = sys.stdin.read()
    else:
        digest_path = Path(sys.argv[1])
        if not digest_path.exists():
            print(f"Error: File not found: {digest_path}")
            sys.exit(1)
        digest_text = digest_path.read_text(encoding='utf-8')
    
    # Определяем дату
    if len(sys.argv) >= 3:
        date_obj = datetime.strptime(sys.argv[2], '%Y-%m-%d')
    else:
        # Пытаемся извлечь из текста
        date_match = re.search(r'Дайджест — (\d{1,2})\s+([а-яА-Я]+)\s+(\d{4})', digest_text)
        if date_match:
            months = {
                'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
                'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
                'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
            }
            day = int(date_match.group(1))
            month = months.get(date_match.group(2).lower(), 8)
            year = int(date_match.group(3))
            date_obj = datetime(year, month, day)
        else:
            date_obj = datetime.now()
    
    # Создаём директорию
    output_dir = repo_root / str(date_obj.year) / f"{date_obj.month:02d}" / f"{date_obj.day:02d}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Парсим и генерируем
    news_items = parse_digest(digest_text, date_obj)
    
    if not news_items:
        print("No news items found in digest")
        sys.exit(0)
    
    print(f"Found {len(news_items)} news items for {date_obj.strftime('%Y-%m-%d')}")
    
    new_entries = []
    for item in news_items:
        filename = generate_news_page(item, date_obj, output_dir)
        new_entries.append({
            'date': date_obj,
            'filename': filename,
            'title': item['title'],
            'category': item['category']
        })
        print(f"  ✓ {filename}")
    
    # Сканируем существующие + добавляем новые
    all_news = scan_existing_news(repo_root)
    
    # Обновляем index
    generate_index(all_news, repo_root)
    print(f"  ✓ index.html updated")
    
    # Git коммит
    os.chdir(repo_root)
    os.system('git add -A')
    os.system(f'git commit -m "Add news for {date_obj.strftime("%Y-%m-%d")}: {len(news_items)} articles"')
    os.system('git push origin main')
    print(f"  ✓ Pushed to GitHub")


if __name__ == '__main__':
    main()
