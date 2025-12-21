from datetime import datetime
from database import Database
from keyboards import get_order_actions_keyboard, get_reject_reasons_keyboard
from config import OrderStatus

class AdminPanel:
    def __init__(self, db: Database):
        self.db = db
    
    def format_order_message(self, order):
        """Форматирует заявку для отправки админу"""
        order_id, user_id, username, order_number, category, description, budget, deadline, contact, status, created_at, updated_at, admin_id, admin_comment, reject_reason, forwarded = order
        
        status_emojis = {
            OrderStatus.PENDING: "⏳",
            OrderStatus.UNDER_REVIEW: "👁️",
            OrderStatus.ACCEPTED: "✅",
            OrderStatus.REJECTED: "❌",
            OrderStatus.IN_PROGRESS: "⚙️",
            OrderStatus.COMPLETED: "🏁"
        }
        
        created = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S').strftime('%d.%m.%Y %H:%M')
        
        message = f"""
🆔 <b>Заявка #{order_number}</b>
━━━━━━━━━━━━━━━━━━━━
👤 <b>Клиент:</b> @{username if username else 'Без username'} (ID: {user_id})
📅 <b>Дата создания:</b> {created}
📊 <b>Статус:</b> {status_emojis.get(status, '❓')} {status}

🎯 <b>Категория:</b> {category if category else 'Не указана'}
💬 <b>Описание:</b>
{description}

💰 <b>Бюджет:</b> {budget if budget else 'Не указан'}
⏰ <b>Срок:</b> {deadline if deadline else 'Не указан'}
📞 <b>Контакт:</b> {contact if contact else 'Не указан'}
"""
        
        if admin_comment:
            message += f"\n💭 <b>Комментарий админа:</b>\n{admin_comment}"
        
        if reject_reason:
            message += f"\n🚫 <b>Причина отказа:</b>\n{reject_reason}"
        
        if forwarded:
            message += f"\n\n👥 <i>Заявка отправлена в группу админов</i>"
        
        return message
    
    async def notify_user(self, bot, user_id, order_number, action, details=None):
        """Уведомляет пользователя о действии с его заявкой"""
        messages = {
            'accepted': f"✅ Ваша заявка #{order_number} была принята! Скоро с вами свяжется наш менеджер.",
            'rejected': f"❌ К сожалению, ваша заявка #{order_number} была отклонена.\nПричина: {details}",
            'in_progress': f"⚙️ По вашей заявке #{order_number} начата работа!",
            'completed': f"🏁 Ваша заявка #{order_number} завершена! Спасибо за сотрудничество!",
            'comment': f"💬 К вашей заявке #{order_number} добавлен комментарий администратора:\n{details}"
        }
        
        if action in messages:
            await bot.send_message(user_id, messages[action])
    
    def get_statistics(self):
        """Получает статистику по заявкам"""
        cursor = self.db.conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM orders')
        total = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM orders WHERE status = ?', (OrderStatus.PENDING,))
        pending = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM orders WHERE status = ?', (OrderStatus.ACCEPTED,))
        accepted = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM orders WHERE status = ?', (OrderStatus.REJECTED,))
        rejected = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM orders WHERE created_at >= date("now", "-7 days")')
        last_week = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT user_id) FROM orders')
        unique_clients = cursor.fetchone()[0]
        
        return {
            'total': total,
            'pending': pending,
            'accepted': accepted,
            'rejected': rejected,
            'last_week': last_week,
            'unique_clients': unique_clients
        }