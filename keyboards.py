from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from config import PROJECT_CATEGORIES, BUDGET_RANGES, DEADLINE_OPTIONS, OrderStatus

# ===== ОСНОВНЫЕ КЛАВИАТУРЫ =====

def get_main_keyboard(is_admin=False):
    """Основная клавиатура"""
    keyboard = [
        [KeyboardButton(text="📝 Создать заявку")],
        [KeyboardButton(text="📋 Мои заявки")]
    ]
    
    if is_admin:
        keyboard.append([KeyboardButton(text="👨‍💼 Панель администратора")])
    
    keyboard.append([KeyboardButton(text="❓ Помощь")])
    
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_cancel_keyboard():
    """Клавиатура отмены"""
    keyboard = [[KeyboardButton(text="❌ Отмена")]]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# ===== ИНЛАЙН КЛАВИАТУРЫ =====

def get_categories_keyboard():
    """Клавиатура выбора категории"""
    builder = InlineKeyboardBuilder()
    
    for category in PROJECT_CATEGORIES:
        builder.button(text=category, callback_data=f"category_{category}")
    
    builder.button(text="⏩ Пропустить", callback_data="category_skip")
    
    builder.adjust(2, 2, 2, 1)  # 2 кнопки в ряду, последняя отдельно
    
    return builder.as_markup()

def get_budget_keyboard():
    """Клавиатура выбора бюджета"""
    builder = InlineKeyboardBuilder()
    
    for budget in BUDGET_RANGES:
        builder.button(text=budget, callback_data=f"budget_{budget}")
    
    builder.button(text="⏩ Пропустить", callback_data="budget_skip")
    
    builder.adjust(2, 2, 2, 1)  # 2 кнопки в ряду, последняя отдельно
    
    return builder.as_markup()

def get_deadline_keyboard():
    """Клавиатура выбора срока"""
    builder = InlineKeyboardBuilder()
    
    for deadline in DEADLINE_OPTIONS:
        builder.button(text=deadline, callback_data=f"deadline_{deadline}")
    
    builder.button(text="⏩ Пропустить", callback_data="deadline_skip")
    
    builder.adjust(2, 2, 2, 1)  # 2 кнопки в ряду, последняя отдельно
    
    return builder.as_markup()

def get_contact_keyboard():
    """Клавиатура для контакта"""
    keyboard = [
        [KeyboardButton(text="📱 Отправить контакт", request_contact=True)],
        [KeyboardButton(text="✏️ Ввести вручную")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# ===== АДМИН КЛАВИАТУРЫ =====

def get_admin_panel_keyboard():
    """Клавиатура админ-панели"""
    builder = InlineKeyboardBuilder()
    
    buttons = [
        ("📥 Новые заявки", "admin_new_orders"),
        ("📊 Все заявки", "admin_all_orders"),
        ("👥 Администраторы", "admin_list"),
        ("📈 Статистика", "admin_stats"),
        ("⚙️ Настройки", "admin_settings"),
        ("📋 Мои действия", "admin_my_actions")
    ]
    
    for text, callback_data in buttons:
        builder.button(text=text, callback_data=callback_data)
    
    builder.adjust(2, 2, 2)  # 3 ряда по 2 кнопки
    
    return builder.as_markup()

def get_order_actions_keyboard(order_id):
    """Клавиатура действий с заявкой"""
    builder = InlineKeyboardBuilder()
    
    buttons = [
        ("✅ Принять", f"order_accept_{order_id}"),
        ("❌ Отклонить", f"order_reject_{order_id}"),
        ("💬 Комментировать", f"order_comment_{order_id}"),
        ("👥 В группу", f"order_forward_{order_id}"),
        ("📋 Подробнее", f"order_details_{order_id}"),
        ("👤 Связаться", f"order_contact_{order_id}")
    ]
    
    for text, callback_data in buttons:
        builder.button(text=text, callback_data=callback_data)
    
    builder.adjust(2, 2, 2)  # 3 ряда по 2 кнопки
    
    return builder.as_markup()

def get_reject_reasons_keyboard(order_id):
    """Клавиатура причин отказа"""
    builder = InlineKeyboardBuilder()
    
    reasons = [
        "🚫 Не соответствует требованиям",
        "⏱️ Нет возможности выполнить в срок",
        "💰 Бюджет не подходит",
        "🎯 Не наша специализация",
        "📅 Занятость команды",
        "✏️ Другая причина"
    ]
    
    for reason in reasons:
        callback_data = f"reject_{order_id}_{reason.replace(' ', '_')}"
        builder.button(text=reason, callback_data=callback_data)
    
    builder.adjust(1)  # Все кнопки в один столбец
    
    return builder.as_markup()

def get_order_status_filter_keyboard():
    """Клавиатура фильтрации по статусам"""
    builder = InlineKeyboardBuilder()
    
    statuses = [
        ("📥 Ожидают", OrderStatus.PENDING),
        ("👁️ На рассмотрении", OrderStatus.UNDER_REVIEW),
        ("✅ Принятые", OrderStatus.ACCEPTED),
        ("❌ Отклоненные", OrderStatus.REJECTED),
        ("⚙️ В работе", OrderStatus.IN_PROGRESS),
        ("🏁 Завершенные", OrderStatus.COMPLETED)
    ]
    
    for text, status in statuses:
        builder.button(text=text, callback_data=f"filter_{status}")
    
    builder.button(text="🔄 Сбросить фильтр", callback_data="filter_all")
    
    builder.adjust(2, 2, 2, 1)  # 3 ряда по 2 кнопки, последняя отдельно
    
    return builder.as_markup()

def get_admin_management_keyboard(admin_id):
    """Клавиатура управления администратором"""
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="❌ Удалить из админов", 
        callback_data=f"admin_remove_{admin_id}"
    )
    
    return builder.as_markup()

def get_confirmation_keyboard(action, data):
    """Клавиатура подтверждения"""
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="✅ Да", 
        callback_data=f"confirm_{action}_{data}"
    )
    
    builder.button(
        text="❌ Нет", 
        callback_data=f"cancel_{action}"
    )
    
    builder.adjust(2)  # 2 кнопки в одном ряду
    
    return builder.as_markup()

# ===== ДОПОЛНИТЕЛЬНЫЕ КЛАВИАТУРЫ ДЛЯ ВСЕХ ФАЙЛОВ =====

def get_simple_reply_keyboard(buttons, columns=1):
    """
    Создает простую reply-клавиатуру из списка кнопок
    
    Args:
        buttons: список текстов кнопок или список словарей с параметрами
        columns: количество кнопок в ряду (по умолчанию 1)
    """
    keyboard = []
    current_row = []
    
    for i, button in enumerate(buttons):
        if isinstance(button, dict):
            # Если передали словарь с параметрами
            btn = KeyboardButton(**button)
        else:
            # Если передали просто текст
            btn = KeyboardButton(text=str(button))
        
        current_row.append(btn)
        
        # Если набрали нужное количество кнопок в ряду или это последняя кнопка
        if len(current_row) == columns or i == len(buttons) - 1:
            keyboard.append(current_row)
            current_row = []
    
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_simple_inline_keyboard(buttons, columns=2):
    """
    Создает простую inline-клавиатуру из списка кнопок
    
    Args:
        buttons: список кортежей (текст, callback_data) или словарей с параметрами
        columns: количество кнопок в ряду (по умолчанию 2)
    """
    builder = InlineKeyboardBuilder()
    
    for button in buttons:
        if isinstance(button, dict):
            # Если передали словарь с параметрами
            builder.button(**button)
        elif isinstance(button, tuple) and len(button) == 2:
            # Если передали кортеж (текст, callback_data)
            text, callback_data = button
            builder.button(text=text, callback_data=callback_data)
    
    builder.adjust(columns)
    
    return builder.as_markup()