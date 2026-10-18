import streamlit as st
import pandas as pd
from auth import require_login, logout
from style import apply_theme
from db import run_select, run_write

st.set_page_config(page_title="Customers | Noor Collections", layout="wide")
apply_theme()
require_login()

with st.sidebar:
    st.markdown(f"**{st.session_state['name']}**")
    st.caption(st.session_state["role"])
    if st.button("Log out"):
        logout()
        st.switch_page("app.py")

st.title("Customers")

search_term = st.text_input("Search by name or email")

query = "SELECT * FROM Customers WHERE 1=1"
params = []
if search_term:
    query += " AND (name LIKE %s OR email LIKE %s)"
    params += [f"%{search_term}%", f"%{search_term}%"]
query += " ORDER BY name"

customers = run_select(query, tuple(params))
st.caption(f"{len(customers)} customer(s) found")

if customers:
    df = pd.DataFrame(customers)
    df.columns = ["ID", "Name", "Email", "Phone", "Address"]
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No customers match your search.")

st.divider()

can_edit = st.session_state["role"] in ("Admin", "Sales")

st.subheader("Add New Customer")
if not can_edit:
    st.caption("Only Admin and Sales roles can add customers.")
else:
    with st.form("add_customer_form", clear_on_submit=True):
        colA, colB = st.columns(2)
        with colA:
            name = st.text_input("Full Name")
            email = st.text_input("Email")
        with colB:
            phone = st.text_input("Phone")
            address = st.text_area("Address", height=80)

        submitted = st.form_submit_button("Add Customer")
        if submitted:
            if not (name and email and phone and address):
                st.error("All fields are required.")
            else:
                ok, err, _ = run_write(
                    "INSERT INTO Customers (name, email, phone, address) VALUES (%s, %s, %s, %s)",
                    (name, email, phone, address),
                )
                if ok:
                    st.success(f"'{name}' added successfully.")
                    st.rerun()
                else:
                    st.error(f"Could not add customer: {err}")
