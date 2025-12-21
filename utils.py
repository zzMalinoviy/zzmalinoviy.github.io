import re
from datetime import datetime

def validate_phone(phone):
    """Валидация телефонного номера"""
    # Убираем все нецифровые символы кроме +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Проверяем российские номера
    if cleaned.startswith('+7') and len(cleaned) == 12:
        return cleaned
    elif cleaned.startswith('8') and len(cleaned) == 11:
        return '+7' + cleaned[1:]
    elif cleaned.startswith('7') and len(cleaned) == 11:
        return '+' + cleaned
    
    # Проверяем международные номера
    elif cleaned.startswith('+') and 10 <= len(cleaned) <= 15:
        return cleaned
    
    return None

def validate_email(email):
    """Валидация email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def format_datetime(dt_string):
    """Форматирует дату-время"""
    try:
        dt = datetime.strptime(dt_string, '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%d.%m.%Y %H:%M')
    except:
        return dt_string

def truncate_text(text, max_length=100):
    """Обрезает текст до максимальной длины"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def generate_order_summary(order_data):
    """Генерирует краткое описание заявки"""
    summary = []
    
    if order_data.get('category'):
        summary.append(f"🎯 Категория: {order_data['category']}")
    
    if order_data.get('budget'):
        summary.append(f"💰 Бюджет: {order_data['budget']}")
    
    if order_data.get('deadline'):
        summary.append(f"⏰ Срок: {order_data['deadline']}")
    
    return "\n".join(summary)

def escape_markdown(text):
    """Экранирует символы Markdown"""
    if not text:
        return ""
    
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join(['\\' + char if char in escape_chars else char for char in text])