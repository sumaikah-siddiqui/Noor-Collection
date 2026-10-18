"""
auth.py
-------
Handles login checking and password hashing (bcrypt).
Also provides require_login() which every page in pages/ calls at the top,
so nobody can view a page without logging in first.
"""

import bcrypt
import streamlit as st
from db import run_select


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        # Happens if the stored value isn't a real bcrypt hash yet (e.g. placeholder)
        return False


def attempt_login(username: str, password: str):
    """Returns the employee dict on success, or None on failure."""
    rows = run_select(
        "SELECT employee_id, name, username, password_hash, role "
        "FROM Employees WHERE username = %s",
        (username,),
    )
    if not rows:
        return None
    employee = rows[0]
    if check_password(password, employee["password_hash"]):
        return employee
    return None


def is_logged_in() -> bool:
    return st.session_state.get("logged_in", False)


def require_login(allowed_roles=None):
    """
    Call this at the very top of every page in pages/.
    Stops the page from rendering if the user isn't logged in,
    or isn't allowed to see it based on role.
    """
    if not is_logged_in():
        st.warning("Please log in first.")
        st.page_link("app.py", label="Go to Login")
        st.stop()

    if allowed_roles is not None and st.session_state.get("role") not in allowed_roles:
        st.error("You don't have permission to view this page.")
        st.stop()


def logout():
    for key in ["logged_in", "employee_id", "name", "role", "username"]:
        st.session_state.pop(key, None)
