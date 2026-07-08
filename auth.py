import sqlite3
import hashlib


DB_NAME = "users.db"


def create_user_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def signup_user(username, email, password):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        hashed_password = hash_password(password)

        cursor.execute("""
            INSERT INTO users (username, email, password)
            VALUES (?, ?, ?)
        """, (username, email, hashed_password))

        conn.commit()
        conn.close()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError:
        return False, "Email already exists. Please use another email."


def login_user(email, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    hashed_password = hash_password(password)

    cursor.execute("""
        SELECT id, username, email FROM users
        WHERE email = ? AND password = ?
    """, (email, hashed_password))

    user = cursor.fetchone()
    conn.close()

    if user:
        return True, {"id": user[0], "username": user[1], "email": user[2]}
    else:
        return False, "Invalid email or password."