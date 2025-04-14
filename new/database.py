import sqlite3
from datetime import datetime
import time
import bcrypt

def get_db_connection():
    conn = sqlite3.connect('enaira.db', timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Drop tables to ensure fresh start
    cursor.execute('DROP TABLE IF EXISTS users')
    cursor.execute('DROP TABLE IF EXISTS transactions')
    
    # Create tables
    cursor.execute('''
        CREATE TABLE users (
            id TEXT PRIMARY KEY,
            phone_number TEXT UNIQUE,
            balance REAL,
            pin TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id TEXT,
            recipient_id TEXT,
            amount REAL,
            timestamp TEXT,
            status TEXT
        )
    ''')
    
    # Insert users with hashed PINs
    hashed_pin1 = bcrypt.hashpw('1234'.encode(), bcrypt.gensalt())
    hashed_pin2 = bcrypt.hashpw('5678'.encode(), bcrypt.gensalt())
    cursor.execute('INSERT INTO users (id, phone_number, balance, pin) VALUES (?, ?, ?, ?)',
                   ('user1', '08012345678', 5000.0, hashed_pin1.decode()))
    cursor.execute('INSERT INTO users (id, phone_number, balance, pin) VALUES (?, ?, ?, ?)',
                   ('user2', '08098765432', 3000.0, hashed_pin2.decode()))
    
    conn.commit()
    conn.close()

def get_user(phone_number):
    max_retries = 3
    retry_delay = 0.1
    for attempt in range(max_retries):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE phone_number = ?', (phone_number,))
            user = cursor.fetchone()
            return user
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            raise
        finally:
            conn.close()

def get_user_by_id(user_id):
    max_retries = 3
    retry_delay = 0.1
    for attempt in range(max_retries):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            return user
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            raise
        finally:
            conn.close()

def save_transaction(sender_id, recipient_id, amount):
    max_retries = 3
    retry_delay = 0.1
    for attempt in range(max_retries):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT balance FROM users WHERE id = ? FOR UPDATE', (sender_id,))
            balance = cursor.fetchone()[0]
            if amount > balance:
                raise ValueError("Insufficient balance")
            timestamp = datetime.now().isoformat()
            cursor.execute('INSERT INTO transactions (sender_id, recipient_id, amount, timestamp, status) VALUES (?, ?, ?, ?, ?)',
                          (sender_id, recipient_id, amount, timestamp, 'pending'))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            raise
        except ValueError as e:
            conn.rollback()
            raise
        finally:
            conn.close()

def get_transactions(user_id):
    max_retries = 3
    retry_delay = 0.1
    for attempt in range(max_retries):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM transactions WHERE sender_id = ? OR recipient_id = ?', (user_id, user_id))
            transactions = cursor.fetchall()
            return transactions
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            raise
        finally:
            conn.close()

def complete_transaction(tx_id, sender_id, recipient_id, amount):
    max_retries = 3
    retry_delay = 0.1
    for attempt in range(max_retries):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('UPDATE transactions SET status = ? WHERE id = ?', ('completed', tx_id))
            cursor.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (amount, sender_id))
            cursor.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount, recipient_id))
            conn.commit()
            return
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            raise
        finally:
            conn.close()