import streamlit as st
import pandas as pd
from auth import require_login, logout, hash_password
from style import apply_theme
from db import run_select, run_write

st.set_page_config(page_title="Employees | Noor Collections", layout="wide")
apply_theme()
require_login(allowed_roles=["Admin"])  # Admin-only page

with st.sidebar:
    st.markdown(f"**{st.session_state['name']}**")
    st.caption(st.session_state["role"])
    if st.button("Log out"):
        logout()
        st.switch_page("app.py")

st.title("Employees")
st.caption("Admin-only: manage staff accounts and roles.")

employees = run_select(
    "SELECT employee_id, name, username, role, created_at FROM Employees ORDER BY employee_id"
)
if employees:
    df = pd.DataFrame(employees)
    df.columns = ["ID", "Name", "Username", "Role", "Created At"]
    st.dataframe(df, use_container_width=True, hide_index=True)

st.divider()

st.subheader("Add New Employee")
ROLES = ["Admin", "Sales", "Inventory Manager"]

with st.form("add_employee_form", clear_on_submit=True):
    colA, colB = st.columns(2)
    with colA:
        name = st.text_input("Full Name")
        username = st.text_input("Username")
    with colB:
        role = st.selectbox("Role", ROLES)
        password = st.text_input("Temporary Password", type="password")

    submitted = st.form_submit_button("Add Employee")
    if submitted:
        if not (name and username and password):
            st.error("All fields are required.")
        else:
            existing = run_select("SELECT employee_id FROM Employees WHERE username = %s", (username,))
            if existing:
                st.error("That username is already taken.")
            else:
                hashed = hash_password(password)
                ok, err, _ = run_write(
                    "INSERT INTO Employees (name, username, password_hash, role) VALUES (%s, %s, %s, %s)",
                    (name, username, hashed, role),
                )
                if ok:
                    st.success(f"'{name}' added as {role}. They can now log in with the username/password you set.")
                    st.rerun()
                else:
                    st.error(f"Could not add employee: {err}")
