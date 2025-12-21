import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.enums import ParseMode, ContentType
from aiogram.client.default import DefaultBotProperties  # НОВЫЙ ИМПОРТ
from aiogram import F

from config import BOT_TOKEN, ADMIN_GROUP_ID, MAIN_ADMIN_ID
from database import Database
from admin_panel import AdminPanel
from keyboards import (
    get_main_keyboard, get_cancel_keyboard, get_categories_keyboard,
    get_budget_keyboard, get_deadline_keyboard, get_contact_keyboard,
    get_admin_panel_keyboard, get_order_actions_keyboard, get_reject_reasons_keyboard,
    get_order_status_filter_keyboard, get_admin_management_keyboard, get_confirmation_keyboard
)
from utils import validate_phone, validate_email, format_datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация с новым синтаксисом aiogram 3.7.0+
bot = Bot(
    token=BOT_TOKEN, 
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)  # ИСПРАВЛЕНО
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Инициализация базы данных и панели админа
db = Database()
admin_panel = AdminPanel(db)

# Состояния FSM
class OrderStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_contact = State()
    waiting_for_budget = State()
    waiting_for_deadline = State()
    waiting_for_category = State()
    waiting_for_reject_reason = State()
    waiting_for_admin_comment = State()

# ===== ОБРАБОТЧИКИ КОМАНД =====

@dp.message(Command("start", "help"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    username = message.from_user.username
    is_admin = db.is_admin(user_id)
    
    welcome_text = """
👋 Добро пожаловать в бот для заказа проектов!

Здесь вы можете:
📝 Создать заявку на разработку проекта
📋 Отслеживать статус своих заявок
💬 Получать уведомления о изменениях

Для начала работы используйте кнопки ниже 👇
"""
    
    await message.answer(welcome_text, reply_markup=get_main_keyboard(is_admin))

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    """Команда для админ-панели"""
    user_id = message.from_user.id
    
    if not db.is_admin(user_id):
        await message.answer("⛔ У вас нет прав доступа к админ-панели.")
        return
    
    await message.answer("👨‍💼 Панель администратора", reply_markup=get_admin_panel_keyboard())

@dp.message(F.text == "👨‍💼 Панель администратора")
async def admin_panel_handler(message: types.Message):
    """Обработчик кнопки админ-панели"""
    await cmd_admin(message)

# ===== СОЗДАНИЕ ЗАЯВКИ =====

@dp.message(F.text == "📝 Создать заявку")
async def create_order_start(message: types.Message):
    """Начало создания заявки"""
    await message.answer(
        "🎯 Выберите категорию проекта:",
        reply_markup=get_categories_keyboard()
    )

@dp.callback_query(F.data.startswith("category_"))
async def process_category(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка выбора категории"""
    await callback_query.answer()
    
    if callback_query.data == 'category_skip':
        await state.update_data(category=None)
    else:
        category = callback_query.data.replace('category_', '')
        await state.update_data(category=category)
        await callback_query.message.edit_text(f"✅ Выбрана категория: {category}")
    
    await callback_query.message.answer(
        "💰 Выберите бюджет проекта:",
        reply_markup=get_budget_keyboard()
    )

@dp.callback_query(F.data.startswith("budget_"))
async def process_budget(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка выбора бюджета"""
    await callback_query.answer()
    
    if callback_query.data == 'budget_skip':
        await state.update_data(budget=None)
    else:
        budget = callback_query.data.replace('budget_', '')
        await state.update_data(budget=budget)
        await callback_query.message.edit_text(f"✅ Выбран бюджет: {budget}")
    
    await callback_query.message.answer(
        "⏰ Выберите срок выполнения:",
        reply_markup=get_deadline_keyboard()
    )

@dp.callback_query(F.data.startswith("deadline_"))
async def process_deadline(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка выбора срока"""
    await callback_query.answer()
    
    if callback_query.data == 'deadline_skip':
        await state.update_data(deadline=None)
    else:
        deadline = callback_query.data.replace('deadline_', '')
        await state.update_data(deadline=deadline)
        await callback_query.message.edit_text(f"✅ Выбран срок: {deadline}")
    
    await callback_query.message.answer(
        "💬 Теперь опишите ваш проект:\n\n"
        "• Что нужно сделать?\n"
        "• Какие требования?\n"
        "• Особенности проекта?\n\n"
        "Опишите подробно, это поможет нам лучше понять задачу.",
        reply_markup=get_cancel_keyboard()
    )
    
    await state.set_state(OrderStates.waiting_for_text)

@dp.message(OrderStates.waiting_for_text)
async def process_order_text(message: types.Message, state: FSMContext):
    """Обработка текста заявки"""
    if len(message.text) < 10:
        await message.answer("⚠️ Описание слишком короткое. Пожалуйста, опишите проект подробнее.")
        return
    
    await state.update_data(description=message.text)
    
    await message.answer(
        "📞 Как с вами связаться?\n\n"
        "Отправьте номер телефона или email. "
        "Можете отправить контакт через кнопку ниже или ввести вручную.",
        reply_markup=get_contact_keyboard()
    )
    
    await state.set_state(OrderStates.waiting_for_contact)

@dp.message(OrderStates.waiting_for_contact, F.content_type == ContentType.CONTACT)
async def process_contact_auto(message: types.Message, state: FSMContext):
    """Обработка автоматического контакта"""
    phone = message.contact.phone_number
    await state.update_data(contact=f"📱 {phone}")
    await finish_order_creation(message, state)

@dp.message(OrderStates.waiting_for_contact)
async def process_contact_manual(message: types.Message, state: FSMContext):
    """Обработка ручного ввода контакта"""
    if message.text == "❌ Отмена":
        await cancel_order(message, state)
        return
    
    contact = message.text.strip()
    
    # Проверяем, является ли контакт телефоном или email
    if validate_phone(contact):
        await state.update_data(contact=f"📱 {contact}")
    elif validate_email(contact):
        await state.update_data(contact=f"📧 {contact}")
    elif contact.lower() == '✏️ ввести вручную':
        await message.answer("Введите ваш контакт (телефон или email):")
        return
    else:
        await message.answer("⚠️ Пожалуйста, введите корректный телефон или email.")
        return
    
    await finish_order_creation(message, state)

async def finish_order_creation(message: types.Message, state: FSMContext):
    """Завершение создания заявки"""
    user_data = await state.get_data()
    user_id = message.from_user.id
    username = message.from_user.username
    
    # Создаем заявку в базе данных
    order_number = db.create_order(user_id, username, user_data)
    
    # Форматируем данные для отображения
    summary = admin_panel.format_order_message(db.get_order_by_number(order_number))
    
    # Отправляем подтверждение пользователю
    await message.answer(
        f"✅ Заявка #{order_number} успешно создана!\n\n"
        f"{summary}\n\n"
        f"📬 Мы рассмотрим вашу заявку в ближайшее время и свяжемся с вами.",
        reply_markup=get_main_keyboard(db.is_admin(user_id))
    )
    
    # Уведомляем админов
    await notify_admins_about_new_order(order_number)
    
    await state.clear()

async def notify_admins_about_new_order(order_number):
    """Уведомляет админов о новой заявке"""
    order = db.get_order_by_number(order_number)
    if not order:
        return
    
    message_text = admin_panel.format_order_message(order)
    order_id = order[0]
    
    # Отправляем главному админу
    try:
        await bot.send_message(
            MAIN_ADMIN_ID,
            message_text,
            reply_markup=get_order_actions_keyboard(order_id)
        )
    except Exception as e:
        logger.error(f"Ошибка отправки главному админу: {e}")
    
    # Логируем создание заявки
    db.log_activity(None, order_id, 'order_created', f"Создана заявка #{order_number}")

# ===== ПРОСМОТР ЗАЯВОК ПОЛЬЗОВАТЕЛЕМ =====

@dp.message(F.text == "📋 Мои заявки")
async def show_user_orders(message: types.Message):
    """Показывает заявки пользователя"""
    user_id = message.from_user.id
    orders = db.get_user_orders(user_id, limit=5)
    
    if not orders:
        await message.answer("📭 У вас еще нет заявок.")
        return
    
    status_emojis = {
        'pending': '⏳',
        'review': '👁️',
        'accepted': '✅',
        'rejected': '❌',
        'progress': '⚙️',
        'completed': '🏁'
    }
    
    response = "📋 Ваши заявки:\n\n"
    
    for order in orders:
        order_id, _, _, order_number, category, description, budget, deadline, contact, status, created_at, *_ = order
        emoji = status_emojis.get(status, '❓')
        created = format_datetime(created_at)
        short_desc = description[:50] + "..." if len(description) > 50 else description
        
        response += f"{emoji} <b>#{order_number}</b> - {status}\n"
        response += f"📅 {created}\n"
        response += f"💬 {short_desc}\n"
        
        if category:
            response += f"🎯 {category}\n"
        
        response += "━━━━━━━━━━━━━━\n"
    
    await message.answer(response, reply_markup=get_main_keyboard(db.is_admin(user_id)))

# ===== АДМИН-ПАНЕЛЬ =====

@dp.callback_query(F.data == "admin_new_orders")
async def show_new_orders(callback_query: types.CallbackQuery):
    """Показывает новые заявки"""
    await callback_query.answer()
    
    orders = db.get_pending_orders()
    
    if not orders:
        await callback_query.message.edit_text("📭 Новых заявок нет.")
        return
    
    for order in orders:
        message_text = admin_panel.format_order_message(order)
        order_id = order[0]
        
        await bot.send_message(
            callback_query.from_user.id,
            message_text,
            reply_markup=get_order_actions_keyboard(order_id)
        )
    
    await callback_query.message.answer(f"📥 Найдено {len(orders)} новых заявок.")

@dp.callback_query(F.data.startswith("order_"))
async def handle_order_action(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка действий с заявкой"""
    data = callback_query.data
    admin_id = callback_query.from_user.id
    
    if data.startswith('order_accept_'):
        order_id = int(data.replace('order_accept_', ''))
        await process_order_accept(callback_query, order_id, admin_id)
    
    elif data.startswith('order_reject_'):
        order_id = int(data.replace('order_reject_', ''))
        await process_order_reject(callback_query, order_id, state)
    
    elif data.startswith('order_comment_'):
        order_id = int(data.replace('order_comment_', ''))
        await process_order_comment(callback_query, order_id, state)
    
    elif data.startswith('order_forward_'):
        order_id = int(data.replace('order_forward_', ''))
        await process_order_forward(callback_query, order_id, admin_id)
    
    elif data.startswith('order_details_'):
        order_id = int(data.replace('order_details_', ''))
        await show_order_details(callback_query, order_id)
    
    elif data.startswith('order_contact_'):
        order_id = int(data.replace('order_contact_', ''))
        await show_order_contact(callback_query, order_id)

async def process_order_accept(callback_query: types.CallbackQuery, order_id: int, admin_id: int):
    """Принятие заявки"""
    order = db.get_order(order_id)
    if not order:
        await callback_query.answer("Заявка не найдена", show_alert=True)
        return
    
    db.update_order_status(order_id, 'accepted', admin_id)
    order_number = order[3]
    
    # Уведомляем пользователя
    await admin_panel.notify_user(bot, order[1], order_number, 'accepted')
    
    # Логируем действие
    db.log_activity(admin_id, order_id, 'order_accepted')
    
    await callback_query.answer(f"✅ Заявка #{order_number} принята")
    await callback_query.message.edit_text(
        f"{admin_panel.format_order_message(order)}\n\n"
        f"✅ <b>Принята администратором</b>"
    )

async def process_order_reject(callback_query: types.CallbackQuery, order_id: int, state: FSMContext):
    """Отклонение заявки - запрос причины"""
    await callback_query.answer()
    
    await callback_query.message.answer(
        "📝 Укажите причину отказа:",
        reply_markup=get_reject_reasons_keyboard(order_id)
    )
    
    await state.update_data(reject_order_id=order_id)
    await state.set_state(OrderStates.waiting_for_reject_reason)

@dp.callback_query(OrderStates.waiting_for_reject_reason, F.data.startswith("reject_"))
async def process_reject_reason(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка причины отказа"""
    await callback_query.answer()
    
    data = callback_query.data.split('_')
    order_id = int(data[1])
    reason = " ".join(data[2:])
    
    if reason == "Другая причина":
        await callback_query.message.answer("✏️ Введите свою причину отказа:")
        await state.update_data(reject_order_id=order_id, waiting_for_custom_reason=True)
        return
    
    await finalize_order_rejection(callback_query, order_id, reason, state)

@dp.message(OrderStates.waiting_for_reject_reason)
async def process_custom_reject_reason(message: types.Message, state: FSMContext):
    """Обработка кастомной причины отказа"""
    user_data = await state.get_data()
    
    if user_data.get('waiting_for_custom_reason'):
        order_id = user_data['reject_order_id']
        reason = message.text
        
        await finalize_order_rejection(None, order_id, reason, state, message)

async def finalize_order_rejection(callback_query, order_id, reason, state, message=None):
    """Финальное отклонение заявки"""
    order = db.get_order(order_id)
    if not order:
        if callback_query:
            await callback_query.answer("Заявка не найдена", show_alert=True)
        return
    
    admin_id = callback_query.from_user.id if callback_query else message.from_user.id
    order_number = order[3]
    
    # Обновляем статус
    db.update_order_status(order_id, 'rejected', admin_id, reject_reason=reason)
    
    # Уведомляем пользователя
    await admin_panel.notify_user(bot, order[1], order_number, 'rejected', reason)
    
    # Логируем действие
    db.log_activity(admin_id, order_id, 'order_rejected', reason)
    
    if callback_query:
        await callback_query.answer(f"❌ Заявка #{order_number} отклонена")
        await callback_query.message.edit_text(
            f"{admin_panel.format_order_message(order)}\n\n"
            f"❌ <b>Отклонена</b>\n"
            f"📝 <b>Причина:</b> {reason}"
        )
    
    await state.clear()

async def process_order_comment(callback_query: types.CallbackQuery, order_id: int, state: FSMContext):
    """Добавление комментария к заявке"""
    await callback_query.answer()
    
    await callback_query.message.answer(
        "💬 Введите комментарий к заявке:"
    )
    
    await state.update_data(comment_order_id=order_id)
    await state.set_state(OrderStates.waiting_for_admin_comment)

@dp.message(OrderStates.waiting_for_admin_comment)
async def save_admin_comment(message: types.Message, state: FSMContext):
    """Сохранение комментария админа"""
    user_data = await state.get_data()
    order_id = user_data['comment_order_id']
    comment = message.text
    
    order = db.get_order(order_id)
    if not order:
        await message.answer("Заявка не найдена")
        await state.clear()
        return
    
    # Сохраняем комментарий
    db.update_order_status(order_id, 'review', message.from_user.id, comment=comment)
    
    # Уведомляем пользователя
    order_number = order[3]
    await admin_panel.notify_user(bot, order[1], order_number, 'comment', comment)
    
    # Логируем
    db.log_activity(message.from_user.id, order_id, 'added_comment', comment[:100])
    
    await message.answer(
        f"💬 Комментарий добавлен к заявке #{order_number}"
    )
    
    await state.clear()

async def process_order_forward(callback_query: types.CallbackQuery, order_id: int, admin_id: int):
    """Пересылка заявки в группу админов"""
    order = db.get_order(order_id)
    if not order:
        await callback_query.answer("Заявка не найдена", show_alert=True)
        return
    
    order_number = order[3]
    
    try:
        # Отправляем в группу админов
        message_text = admin_panel.format_order_message(order)
        
        await bot.send_message(
            ADMIN_GROUP_ID,
            f"👥 <b>Заявка требует коллективного обсуждения</b>\n\n{message_text}",
            reply_markup=get_order_actions_keyboard(order_id)
        )
        
        # Помечаем как пересланную
        db.set_forwarded_to_group(order_id)
        
        # Логируем
        db.log_activity(admin_id, order_id, 'forwarded_to_group')
        
        await callback_query.answer(f"👥 Заявка #{order_number} отправлена в группу")
        
        await callback_query.message.edit_text(
            f"{message_text}\n\n"
            f"📤 <b>Отправлена в группу админов</b>"
        )
        
    except Exception as e:
        logger.error(f"Ошибка отправки в группу: {e}")
        await callback_query.answer("Ошибка отправки в группу", show_alert=True)

async def show_order_details(callback_query: types.CallbackQuery, order_id: int):
    """Показывает детали заявки"""
    order = db.get_order(order_id)
    if not order:
        await callback_query.answer("Заявка не найдена", show_alert=True)
        return
    
    message_text = admin_panel.format_order_message(order)
    
    # Получаем историю действий
    cursor = db.conn.cursor()
    cursor.execute('''
        SELECT al.action, al.details, al.timestamp, a.username 
        FROM activity_log al 
        LEFT JOIN admins a ON al.admin_id = a.id 
        WHERE al.order_id = ? 
        ORDER BY al.timestamp DESC
    ''', (order_id,))
    
    history = cursor.fetchall()
    
    if history:
        message_text += "\n\n📜 <b>История действий:</b>\n"
        for action, details, timestamp, admin_name in history:
            time_str = format_datetime(timestamp)
            admin_str = f"@{admin_name}" if admin_name else "Система"
            message_text += f"• {time_str} - {admin_str}: {action}"
            if details:
                message_text += f" ({details})"
            message_text += "\n"
    
    await callback_query.message.answer(message_text)
    await callback_query.answer()

async def show_order_contact(callback_query: types.CallbackQuery, order_id: int):
    """Показывает контакт клиента"""
    order = db.get_order(order_id)
    if not order:
        await callback_query.answer("Заявка не найдена", show_alert=True)
        return
    
    user_id = order[1]
    username = order[2]
    contact = order[8]
    order_number = order[3]
    
    contact_info = f"📞 Контакт клиента по заявке #{order_number}:\n"
    contact_info += f"👤 ID: {user_id}\n"
    
    if username:
        contact_info += f"👤 Username: @{username}\n"
    
    if contact:
        contact_info += f"📱 Контакт: {contact}"
    else:
        contact_info += "📱 Контакт не указан"
    
    await callback_query.message.answer(contact_info)
    await callback_query.answer("Контакт отправлен в чат")

# ===== УПРАВЛЕНИЕ АДМИНАМИ =====

@dp.callback_query(F.data == "admin_list")
async def show_admins_list(callback_query: types.CallbackQuery):
    """Показывает список админов"""
    admins = db.get_admins()
    
    if not admins:
        await callback_query.message.answer("👥 Список администраторов пуст.")
        return
    
    response = "👥 <b>Администраторы:</b>\n\n"
    
    for admin_id, username in admins:
        response += f"• @{username if username else 'без username'} (ID: {admin_id})\n"
    
    await callback_query.message.answer(response)
    await callback_query.answer()

@dp.message(Command("addadmin"))
async def add_admin_command(message: types.Message):
    """Добавление администратора"""
    if message.from_user.id != int(MAIN_ADMIN_ID):
        await message.answer("⛔ Только главный администратор может добавлять других админов.")
        return
    
    try:
        # Ожидаем: /addadmin @username или /addadmin 123456789
        args = message.text.split()
        
        if len(args) != 2:
            await message.answer("Использование: /addadmin @username или /addadmin user_id")
            return
        
        target = args[1]
        
        if target.startswith('@'):
            # Нужно будет получить ID по username (упрощенная версия)
            await message.answer("Добавление по username пока не поддерживается. Используйте user_id.")
            return
        else:
            admin_id = int(target)
            
            # Получаем информацию о пользователе
            try:
                user = await bot.get_chat(admin_id)
                username = user.username
                
                if db.add_admin(admin_id, username):
                    await message.answer(f"✅ Администратор @{username} добавлен.")
                else:
                    await message.answer("⚠️ Администратор уже существует.")
                    
            except Exception as e:
                await message.answer(f"❌ Ошибка: пользователь с ID {admin_id} не найден.")
    
    except ValueError:
        await message.answer("❌ Неверный формат. Используйте: /addadmin user_id")

# ===== ОБЩИЕ ОБРАБОТЧИКИ =====

@dp.message(F.text == "❌ Отмена")
async def cancel_order(message: types.Message, state: FSMContext):
    """Отмена создания заявки"""
    current_state = await state.get_state()
    if current_state is None:
        return
    
    await state.clear()
    await message.answer(
        "❌ Создание заявки отменено.",
        reply_markup=get_main_keyboard(db.is_admin(message.from_user.id))
    )

@dp.message(F.text == "❓ Помощь")
async def show_help(message: types.Message):
    """Показывает справку"""
    help_text = """
📚 <b>Справка по боту</b>

<b>Для клиентов:</b>
📝 <b>Создать заявку</b> - оформить заказ на проект
📋 <b>Мои заявки</b> - просмотр статуса ваших заявок

<b>Для администраторов:</b>
👨‍💼 <b>Панель администратора</b> - управление заявками
/admin - команда для админ-панели

<b>Процесс работы:</b>
1. Создайте заявку с описанием проекта
2. Администратор рассмотрит заявку
3. Вы получите уведомление о решении
4. При принятии - менеджер свяжется с вами

<b>Контакты:</b>
По вопросам работы бота обращайтесь к администратору.
"""
    
    await message.answer(help_text, reply_markup=get_main_keyboard(db.is_admin(message.from_user.id)))

@dp.message()
async def handle_unknown_message(message: types.Message):
    """Обработка неизвестных сообщений"""
    await message.answer(
        "🤔 Я не понял ваше сообщение. Используйте кнопки ниже для навигации.",
        reply_markup=get_main_keyboard(db.is_admin(message.from_user.id))
    )

# ===== ЗАПУСК БОТА =====

async def main():
    """Основная функция запуска бота"""
    logger.info("Запуск бота...")
    
    # Добавляем главного админа если его нет
    try:
        db.add_admin(int(MAIN_ADMIN_ID), "main_admin")
        logger.info(f"Главный администратор добавлен: {MAIN_ADMIN_ID}")
    except:
        pass
    
    try:
        await dp.start_polling(bot)
    finally:
        db.close()

if __name__ == '__main__':
    asyncio.run(main())