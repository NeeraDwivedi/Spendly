import sqlite3
import os
from datetime import date
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "expense_tracker.db")

CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()


def seed_db():
    conn = get_db()
    existing = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()
    if existing["c"] > 0:
        conn.close()
        return

    password_hash = generate_password_hash("demo123")
    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", password_hash),
    )
    user_id = cursor.lastrowid

    today = date.today()
    # (amount, category, day-of-month, description) — one entry per fixed
    # category plus one extra, all anchored to a day <= today's day-of-month
    # so every date stays within the current calendar month.
    sample_expenses = [
        (45.50, "Food", 1, "Groceries"),
        (12.00, "Food", 3, "Lunch with coworkers"),
        (30.00, "Transport", 2, "Gas fill-up"),
        (150.00, "Bills", 1, "Electricity bill"),
        (60.00, "Health", 4, "Pharmacy"),
        (25.00, "Entertainment", 5, "Movie tickets"),
        (89.99, "Shopping", 6, "New shoes"),
        (15.00, "Other", 7, "Miscellaneous"),
    ]
    for amount, category, day_target, description in sample_expenses:
        day_of_month = min(day_target, today.day)
        expense_date = today.replace(day=day_of_month).strftime("%Y-%m-%d")
        conn.execute(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            (user_id, amount, category, expense_date, description),
        )

    conn.commit()
    conn.close()
