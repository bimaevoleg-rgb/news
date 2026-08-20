#!/usr/bin/env python3
"""
Генератор карточек новостей для Telegram с тематическими AI-иллюстрациями.
Использует Pollinations.ai для генерации изображений.
Использование: python3 generate_news_card.py "Заголовок" "Описание" "URL" "категория" "дата" "output.png"
"""

import sys
import os
import urllib.request
import urllib.parse
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def get_font(size, bold=False):
    """Находит подходящий шрифт с поддержкой кириллицы."""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
    return ImageFont.load_default()

def generate_image_for_news(title, category, output_path):
    """Генерирует тематическое изображение через Pollinations.ai."""
    # Создаём промпт на основе категории и заголовка
    category_prompts = {
        "models": "futuristic AI neural network brain, glowing circuits, digital mind, dark background, high tech, cinematic lighting",
        "investments": "golden coins falling, stock market chart going up, venture capital, startup rocket, dark luxury background, fintech style",
        "regulation": "government building with digital lock, scales of justice, legal documents with glowing text, dark blue official style",
        "opensource": "open padlock with code flowing out, github-style green matrix, collaborative coding, community hands, dark tech",
        "research": "laboratory microscope, DNA helix glowing, scientific beakers, quantum particles, futuristic research lab",
        "enterprise": "corporate skyscrapers, business handshake hologram, server room, enterprise cloud, dark professional style",
        "security": "cybersecurity shield with lock, digital firewall, hacker code matrix, protection barrier, dark red alert style",
        "infrastructure": "massive data center, server racks glowing, fiber optic cables, chip semiconductor, futuristic hardware",
        "default": "futuristic AI technology, abstract digital art, glowing neon lines, dark background, high tech concept",
    }
    
    base_prompt = category_prompts.get(category, category_prompts["default"])
    # Добавляем заголовок для контекста (первые 3 слова)
    title_words = " ".join(title.split()[:3])
    full_prompt = f"{title_words}, {base_prompt}, photorealistic, 8k, dramatic lighting, no text, no words, no letters"
    
    # URL-кодируем промпт
    encoded_prompt = urllib.parse.quote(full_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&nologo=true&seed={hash(title) % 10000}"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=60) as response:
            with open(output_path, 'wb') as f:
                f.write(response.read())
        return True
    except Exception as e:
        print(f"Image generation failed: {e}")
        return False

def wrap_text(draw, text, font, max_width):
    """Переносит текст по словам."""
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def generate_card(title, description, url, category, date_str, output_path):
    W, H = 1080, 1080
    margin = 60
    
    # Сначала генерируем тематическое изображение
    temp_img_path = output_path + ".tmp.jpg"
    img_generated = generate_image_for_news(title, category, temp_img_path)
    
    if img_generated and os.path.exists(temp_img_path):
        img = Image.open(temp_img_path)
        img = img.resize((W, H), Image.LANCZOS)
        # Добавляем тёмный overlay для читаемости текста
        overlay = Image.new('RGBA', (W, H), (0, 0, 0, 160))
        img = img.convert('RGBA')
        img = Image.alpha_composite(img, overlay)
        img = img.convert('RGB')
        os.remove(temp_img_path)
    else:
        # Fallback: градиентный фон
        img = Image.new("RGB", (W, H), "#1a1a2e")
    
    draw = ImageDraw.Draw(img)
    
    # Цвета акцентов по категории
    accent_colors = {
        "models": "#e94560",
        "investments": "#16c79a",
        "regulation": "#801336",
        "opensource": "#3282b8",
        "research": "#e43f5a",
        "enterprise": "#0f4c75",
        "security": "#ff005c",
        "infrastructure": "#f39c12",
        "default": "#ff6b6b",
    }
    accent = accent_colors.get(category, accent_colors["default"])
    
    # Рисуем акцентную линию сверху
    draw.rectangle([0, 0, W, 8], fill=accent)
    
    # Шрифты
    font_title = get_font(52, bold=True)
    font_desc = get_font(34)
    font_url = get_font(26)
    font_date = get_font(24)
    font_cat = get_font(30, bold=True)
    
    y = 50
    
    # Категория
    cat_display = category.upper()
    draw.text((margin, y), cat_display, font=font_cat, fill=accent)
    y += 70
    
    # Заголовок
    title_lines = wrap_text(draw, title, font_title, W - margin * 2)
    for line in title_lines[:4]:
        # Тень для читаемости
        draw.text((margin+2, y+2), line, font=font_title, fill="black")
        draw.text((margin, y), line, font=font_title, fill="white")
        bbox = draw.textbbox((0, 0), line, font=font_title)
        y += bbox[3] - bbox[1] + 12
    y += 20
    
    # Описание
    desc_lines = wrap_text(draw, description, font_desc, W - margin * 2)
    for line in desc_lines[:5]:
        draw.text((margin+1, y+1), line, font=font_desc, fill="black")
        draw.text((margin, y), line, font=font_desc, fill="#eeeeee")
        bbox = draw.textbbox((0, 0), line, font=font_desc)
        y += bbox[3] - bbox[1] + 10
    y += 30
    
    # URL
    url_lines = wrap_text(draw, url, font_url, W - margin * 2)
    for line in url_lines[:2]:
        draw.text((margin, y), line, font=font_url, fill=accent)
        bbox = draw.textbbox((0, 0), line, font=font_url)
        y += bbox[3] - bbox[1] + 6
    
    # Дата внизу
    draw.text((margin, H - 70), f"🔥 AI News • {date_str}", font=font_date, fill="#aaaaaa")
    
    # Декоративный блок
    draw.rectangle([W - 180, H - 70, W - margin, H - 40], fill=accent)
    
    img.save(output_path, "PNG")
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Usage: python3 generate_news_card.py 'Title' 'Description' 'URL' 'category' 'date' [output.png]")
        sys.exit(1)
    
    title = sys.argv[1]
    description = sys.argv[2]
    url = sys.argv[3]
    category = sys.argv[4]
    date_str = sys.argv[5]
    output = sys.argv[6] if len(sys.argv) > 6 else "/tmp/news_card.png"
    
    generate_card(title, description, url, category, date_str, output)
