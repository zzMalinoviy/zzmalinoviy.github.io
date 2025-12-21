import os
from dotenv import load_dotenv

load_dotenv()

# Токены бота
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_GROUP_ID = os.getenv('ADMIN_GROUP_ID', '-1001234567890')  # ID группы админов
MAIN_ADMIN_ID = os.getenv('MAIN_ADMIN_ID', '123456789')  # ID главного админа

# Настройки базы данных
DB_NAME = 'orders.db'

# Состояния бота
class States:
    WAITING_FOR_ORDER_TEXT = 1
    WAITING_FOR_CONTACT = 2
    WAITING_FOR_BUDGET = 3
    WAITING_FOR_DEADLINE = 4
    WAITING_FOR_REJECT_REASON = 5
    WAITING_FOR_ADMIN_COMMENT = 6

# Статусы заявок
class OrderStatus:
    PENDING = 'pending'        # Ожидает рассмотрения
    UNDER_REVIEW = 'review'    # На рассмотрении
    ACCEPTED = 'accepted'      # Принята
    REJECTED = 'rejected'      # Отклонена
    IN_PROGRESS = 'progress'   # В работе
    COMPLETED = 'completed'    # Завершена

# Категории проектов
PROJECT_CATEGORIES = [
    '🌐 Веб-разработка',
    '📱 Мобильное приложение',
    '🎨 UI/UX дизайн',
    '🤖 Чат-боты',
    '📊 Аналитика и данные',
    '⚙️ Другое'
]

# Бюджетные диапазоны
BUDGET_RANGES = [
    '💰 До 10 000 руб',
    '💰 10 000 - 30 000 руб',
    '💰 30 000 - 70 000 руб',
    '💰 70 000 - 150 000 руб',
    '💰 От 150 000 руб',
    '💰 Обсудим позже'
]

# Сроки выполнения
DEADLINE_OPTIONS = [
    '⏰ Срочно (до 3 дней)',
    '📅 1 неделя',
    '📅 2-3 недели',
    '📅 1 месяц',
    '📅 Более месяца',
    '📅 Обсудим сроки'
]