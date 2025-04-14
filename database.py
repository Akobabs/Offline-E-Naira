import sqlite3
from datetime import datetime
import time
from flask import g

def get_db_connection_flask():
    """Get a database connection for Flask request context using g."""
    if 'db' not in g:
        conn = sqlite3.connect('enaira.db', timeout=10)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db

def get_db_connection():
    """Get a standalone database connection for non-Flask contexts (e.g., tests)."""
    conn = sqlite3.connect('enaira.db', timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def close_db_connection():
    """Close the database connection in Flask context."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    conn = sqlite3.connect('enaira.db', timeout=10)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Drop and recreate transactions table to clear old data
    cursor.execute('DROP TABLE IF EXISTS transactions')
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

    # Recreate users table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            phone_number TEXT UNIQUE,
            balance REAL,
            pin TEXT
        )
    ''')
    
    cursor.execute('INSERT OR IGNORE INTO users (id, phone_number, balance, pin) VALUES (?, ?, ?, ?)',
                   ('user1', '08012345678', 5000.0, '1234'))
    cursor.execute('INSERT OR IGNORE INTO users (id, phone_number, balance, pin) VALUES (?, ?, ?, ?)',
                   ('user2', '08098765432', 3000.0, '5678'))
    
    conn.commit()
    conn.close()

def get_user(phone_number):
    try:
        conn = get_db_connection_flask()
    except RuntimeError:
        conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE phone_number = ?', (phone_number,))
    user = cursor.fetchone()
    return user

def get_user_by_id(user_id):
    try:
        conn = get_db_connection_flask()
    except RuntimeError:
        conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    return user

def save_transaction(sender_id, recipient_id, amount):
    try:
        conn = get_db_connection_flask()
    except RuntimeError:
        conn = get_db_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    cursor.execute('INSERT INTO transactions (sender_id, recipient_id, amount, timestamp, status) VALUES (?, ?, ?, ?, ?)',
                  (sender_id, recipient_id, amount, timestamp, 'pending'))
    conn.commit()

def get_transactions(user_id):
    try:
        conn = get_db_connection_flask()
    except RuntimeError:
        conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM transactions WHERE sender_id = ? OR recipient_id = ?', (user_id, user_id))
    transactions = cursor.fetchall()
    return transactions

def complete_transaction(tx_id, sender_id, recipient_id, amount):
    max_retries = 3
    retry_delay = 0.1
    for attempt in range(max_retries):
        try:
            conn = get_db_connection_flask()
        except RuntimeError:
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
        