import sqlite3
from datetime import datetime
from config import DB_NAME, OrderStatus

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Таблица заказов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                order_number TEXT UNIQUE NOT NULL,
                category TEXT,
                description TEXT NOT NULL,
                budget TEXT,
                deadline TEXT,
                contact TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                admin_id INTEGER,
                admin_comment TEXT,
                reject_reason TEXT,
                forwarded_to_group BOOLEAN DEFAULT 0
            )
        ''')
        
        # Таблица администраторов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY,
                username TEXT,
                can_review BOOLEAN DEFAULT 1,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица истории действий
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER,
                order_id INTEGER,
                action TEXT,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    # ===== МЕТОДЫ ДЛЯ ЗАКАЗОВ =====
    
    def create_order(self, user_id, username, order_data):
        cursor = self.conn.cursor()
        
        # Генерация номера заказа
        order_number = f"ORD-{datetime.now().strftime('%y%m%d')}-{user_id % 1000:03d}"
        
        cursor.execute('''
            INSERT INTO orders 
            (user_id, username, order_number, category, description, budget, deadline, contact, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, username, order_number,
            order_data.get('category'),
            order_data.get('description'),
            order_data.get('budget'),
            order_data.get('deadline'),
            order_data.get('contact'),
            OrderStatus.PENDING
        ))
        
        self.conn.commit()
        return order_number
    
    def get_order(self, order_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
        return cursor.fetchone()
    
    def get_order_by_number(self, order_number):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE order_number = ?', (order_number,))
        return cursor.fetchone()
    
    def get_user_orders(self, user_id, limit=10):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM orders 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        return cursor.fetchall()
    
    def update_order_status(self, order_id, status, admin_id=None, comment=None, reject_reason=None):
        cursor = self.conn.cursor()
        
        cursor.execute('''
            UPDATE orders 
            SET status = ?, 
                admin_id = ?, 
                admin_comment = ?, 
                reject_reason = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, admin_id, comment, reject_reason, order_id))
        
        self.conn.commit()
    
    def set_forwarded_to_group(self, order_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE orders 
            SET forwarded_to_group = 1 
            WHERE id = ?
        ''', (order_id,))
        self.conn.commit()
    
    def get_pending_orders(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM orders 
            WHERE status = 'pending' 
            ORDER BY created_at ASC
        ''')
        return cursor.fetchall()
    
    def get_orders_by_status(self, status):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM orders 
            WHERE status = ? 
            ORDER BY created_at DESC
        ''', (status,))
        return cursor.fetchall()
    
    # ===== МЕТОДЫ ДЛЯ АДМИНИСТРАТОРОВ =====
    
    def add_admin(self, admin_id, username):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO admins (id, username) 
                VALUES (?, ?)
            ''', (admin_id, username))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def remove_admin(self, admin_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM admins WHERE id = ?', (admin_id,))
        self.conn.commit()
    
    def is_admin(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM admins WHERE id = ?', (user_id,))
        return cursor.fetchone() is not None
    
    def get_admins(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, username FROM admins')
        return cursor.fetchall()
    
    # ===== ЛОГИРОВАНИЕ =====
    
    def log_activity(self, admin_id, order_id, action, details=None):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO activity_log (admin_id, order_id, action, details)
            VALUES (?, ?, ?, ?)
        ''', (admin_id, order_id, action, details))
        self.conn.commit()
    
    def close(self):
        self.conn.close()