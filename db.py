"""
db.py
-----
Central place for everything that talks to MySQL.
Every page imports functions from here instead of connecting on its own.
"""

import streamlit as st
import mysql.connector
from mysql.connector import Error


def get_connection():
    """Open a fresh connection to the MySQL database using secrets.toml."""
    try:
        conn = mysql.connector.connect(
            host=st.secrets["db"]["host"],
            port=st.secrets["db"].get("port", 3306),
            user=st.secrets["db"]["user"],
            password=st.secrets["db"]["password"],
            database=st.secrets["db"]["database"],
        )
        return conn
    except Error as e:
        st.error(f"Could not connect to the database: {e}")
        return None


def run_select(query, params=None):
    """Run a SELECT query and return the results as a list of dicts."""
    conn = get_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        return cursor.fetchall()
    except Error as e:
        st.error(f"Query failed: {e}")
        return []
    finally:
        conn.close()


def run_write(query, params=None):
    """
    Run an INSERT / UPDATE / DELETE.
    Returns (success: bool, error_message: str | None, last_id: int | None)
    """
    conn = get_connection()
    if conn is None:
        return False, "No database connection.", None
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        return True, None, cursor.lastrowid
    except Error as e:
        conn.rollback()
        return False, str(e), None
    finally:
        conn.close()


def call_procedure(proc_name, params):
    """
    Call a stored procedure (e.g. sp_process_secure_checkout).
    Returns (success: bool, error_message: str | None)
    """
    conn = get_connection()
    if conn is None:
        return False, "No database connection."
    try:
        cursor = conn.cursor()
        cursor.callproc(proc_name, params)
        conn.commit()
        return True, None
    except Error as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


def test_connection():
    """Used on the login page to show a friendly message if MySQL isn't reachable."""
    conn = get_connection()
    if conn:
        conn.close()
        return True
    return False
