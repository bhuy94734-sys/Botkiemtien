import sqlite3

class Database:
    def __init__(self, db_file="shared_game.db"):
        self.db_file = db_file
        self.create_table()

    def get_connection(self):
        return sqlite3.connect(self.db_file)

    def create_table(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                balance REAL DEFAULT 0.0,
                total_bet REAL DEFAULT 0.0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS giftcodes (
                code TEXT PRIMARY KEY,
                amount REAL,
                used INTEGER DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()

    def get_user(self, user_id, username):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, username, balance, total_bet FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            cursor.execute("INSERT INTO users (user_id, username, balance, total_bet) VALUES (?, ?, 0.0, 0.0)", (user_id, username))
            conn.commit()
            row = (user_id, username, 0.0, 0.0)
        else:
            cursor.execute("UPDATE users SET username = ? WHERE user_id = ?", (username, user_id))
            conn.commit()
        conn.close()
        return {"user_id": row[0], "username": row[1], "balance": row[2], "total_bet": row[3]}

    def update_balance(self, user_id, amount):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            new_bal = row[0] + amount
            cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_bal, user_id))
            conn.commit()
        conn.close()

    def create_giftcode(self, code, amount):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO giftcodes (code, amount, used) VALUES (?, ?, 0)", (code, amount))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False

    def use_giftcode(self, user_id, code):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT amount, used FROM giftcodes WHERE code = ?", (code,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return "not_found"
        if row[1] == 1:
            conn.close()
            return "used"
        
        amount = row[0]
        cursor.execute("UPDATE giftcodes SET used = 1 WHERE code = ?", (code,))
        cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        user_row = cursor.fetchone()
        if user_row:
            new_bal = user_row[0] + amount
            cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_bal, user_id))
        conn.commit()
        conn.close()
        return amount

    def get_all_users(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        users = [row[0] for row in cursor.fetchall()]
        conn.close()
        return users

db = Database()
