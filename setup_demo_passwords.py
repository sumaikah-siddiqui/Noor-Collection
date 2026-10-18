"""
setup_demo_passwords.py
------------------------
The 3 sample employees in backend.sql have PLACEHOLDER password hashes
(since you should never store real plain-text passwords in a .sql file).

Run this ONCE after setting up your database and secrets.toml, to give
each sample employee a real, working demo password.

Usage:
    streamlit run app.py   (in another terminal, so secrets.toml loads correctly)
    -- or simply --
    python setup_demo_passwords.py
"""

import bcrypt
import mysql.connector

# ---- EDIT THESE to match your local MySQL setup ----
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "pw12345",
    "database": "noor_collections",
}

# Demo login credentials (change these before showing it off / submitting!)
DEMO_USERS = [
    ("fatima.noor", "admin123"),
    ("ahmed.raza", "sales123"),
    ("mehak.siddiqui", "inventory123"),
]


def main():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    for username, plain_password in DEMO_USERS:
        hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        cursor.execute(
            "UPDATE Employees SET password_hash = %s WHERE username = %s",
            (hashed, username),
        )
        print(f"Updated password for {username}")

    conn.commit()
    cursor.close()
    conn.close()
    print("\nDone! You can now log in with:")
    for username, plain_password in DEMO_USERS:
        print(f"  {username} / {plain_password}")


if __name__ == "__main__":
    main()
