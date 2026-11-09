import sqlite3
from werkzeug.security import generate_password_hash

db = sqlite3.connect("leaky.db")

try:
    db.execute("BEGIN")

    users = db.execute(
        "SELECT id, username, password FROM users"
    ).fetchall()

    db.execute("""
        CREATE TABLE users_new (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            email TEXT UNIQUE,
            password_hash TEXT NOT NULL
        )
    """)
    for user_id, username, old_password in users:
        db.execute(
            """
            INSERT INTO users_new (id, username, email, password_hash)
            VALUES (?, ?, NULL, ?)
            """,
            (
                user_id,
                username,
                generate_password_hash(
                    old_password,
                    method="pbkdf2:sha256"
                )
            )
        )
    db.execute("DROP TABLE users")
    db.execute("ALTER TABLE users_new RENAME TO users")
    db.commit()

    print("Database migration completed successfully.")

except Exception:
    db.rollback()
    raise

finally:
    db.close()