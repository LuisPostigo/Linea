import sqlite3
import bcrypt
import os

DB_PATH = os.path.join("data", "database", "users.db")

# Ensure the users table exists with secure constraints
def initialize_users_table():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'admin'))
            );
        """)
        conn.commit()

        # Ensure the maintenance user always exists
        cursor.execute("SELECT * FROM users WHERE username = 'maintenance'")
        if cursor.fetchone() is None:
            default_password = bcrypt.hashpw("maintenance".encode(), bcrypt.gensalt())
            cursor.execute("""
                INSERT INTO users (username, hashed_password, name, email, role)
                VALUES (?, ?, ?, ?, ?)
            """, ("maintenance", default_password, "Maintenance Bot", "maintenance@local", "user"))
            conn.commit()
            print("[INIT] Created default 'maintenance' user.")
        else:
            print("[INIT] 'maintenance' user already exists.")


if __name__ == "__main__":
    initialize_users_table()
