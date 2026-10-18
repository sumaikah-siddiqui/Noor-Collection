"""
app.py
------
Entry point. Shows the login screen. Once logged in, sends the employee
to the Dashboard page. Every other page (in pages/) checks
auth.require_login() at the top, so this login gate can't be skipped
by navigating directly to another page.
"""

import streamlit as st
from auth import attempt_login, is_logged_in, logout
from style import apply_theme
from db import test_connection

st.set_page_config(
    page_title="Noor Collections | Business Management",
   
    layout="centered",
)
apply_theme()

# ---------------------------------------------------------------
# Already logged in? Show a simple landing card instead of the form.
# ---------------------------------------------------------------
if is_logged_in():
    st.title("Noor Collections")
    st.subheader(f"Welcome back, {st.session_state['name']} ")
    st.caption(f"Role: {st.session_state['role']}")
    st.write("Use the sidebar to navigate to Dashboard, Products, Orders, Customers or Employees.")

    if st.button("Go to Dashboard →"):
        st.switch_page("pages/1_Dashboard.py")

    st.divider()
    if st.button("Log out"):
        logout()
        st.rerun()

    st.stop()

# ---------------------------------------------------------------
# Login form
# ---------------------------------------------------------------
st.markdown(
    """
    <div style="text-align:center; margin-top: 20px; margin-bottom: 10px;">
        <h1 style="margin-bottom:0;">Noor Collections</h1>
        <p style="color:#7B1E3A; font-weight:600; margin-top:4px;">
            Business Management System
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.container(border=True):
    st.markdown("#### Employee Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log In", use_container_width=True)

    if submitted:
        if not username or not password:
            st.error("Please enter both username and password.")
        else:
            employee = attempt_login(username, password)
            if employee:
                st.session_state["logged_in"] = True
                st.session_state["employee_id"] = employee["employee_id"]
                st.session_state["name"] = employee["name"]
                st.session_state["role"] = employee["role"]
                st.session_state["username"] = employee["username"]
                st.success(f"Welcome, {employee['name']}!")
                st.switch_page("pages/1_Dashboard.py")
            else:
                st.error("Invalid username or password.")

st.caption(
    "Internal tool for Noor Collections staff. "
    "Contact your Admin if you don't have login credentials."
)

with st.expander("Trouble connecting?"):
    st.write("Checking database connection status...")
    if test_connection():
        st.success("Database connection OK.")
    else:
        st.error(
            "Could not reach MySQL. Make sure your MySQL server is running "
            "and .streamlit/secrets.toml has the correct credentials."
        )
