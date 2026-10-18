import streamlit as st
import pandas as pd
from auth import require_login, logout
from style import apply_theme
from db import run_select, run_write

st.set_page_config(page_title="Products | Noor Collections", layout="wide")
apply_theme()
require_login()

with st.sidebar:
    st.markdown(f"**{st.session_state['name']}**")
    st.caption(st.session_state["role"])
    if st.button("Log out"):
        logout()
        st.switch_page("app.py")

st.title("Products")

CATEGORIES = ["Earrings", "Bracelet", "Choker", "Ring", "Chain", "Bangles",
              "Bridal Set", "Necklace", "Anklet"]
MATERIALS = ["Gold Plated", "Sterling Silver", "Brass/Gold Leaf"]

can_edit = st.session_state["role"] in ("Admin", "Inventory Manager")

# ---------------- Search & filters ----------------
c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    search_term = st.text_input("Search by product name")
with c2:
    category_filter = st.selectbox("Category", ["All"] + CATEGORIES)
with c3:
    material_filter = st.selectbox("Material", ["All"] + MATERIALS)

query = "SELECT * FROM Products WHERE 1=1"
params = []

if search_term:
    query += " AND name LIKE %s"
    params.append(f"%{search_term}%")
if category_filter != "All":
    query += " AND category = %s"
    params.append(category_filter)
if material_filter != "All":
    query += " AND material = %s"
    params.append(material_filter)

query += " ORDER BY product_id"

products = run_select(query, tuple(params))

st.caption(f"{len(products)} product(s) found")

if products:
    df = pd.DataFrame(products)
    display_df = df[["product_id", "name", "category", "material", "price", "stock_quantity"]]
    display_df.columns = ["ID", "Name", "Category", "Material", "Price (Rs)", "Stock"]
    st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.info("No products match your search.")

st.divider()

# ---------------- Add / restock (Admin & Inventory Manager only) ----------------
if can_edit:
    tab_add, tab_restock = st.tabs(["Add New Product", "Restock Existing Product"])

    with tab_add:
        with st.form("add_product_form", clear_on_submit=True):
            colA, colB = st.columns(2)
            with colA:
                name = st.text_input("Product Name")
                category = st.selectbox("Category", CATEGORIES, key="add_cat")
                material = st.selectbox("Material", MATERIALS, key="add_mat")
            with colB:
                price = st.number_input("Price (Rs)", min_value=1.0, step=100.0)
                stock = st.number_input("Initial Stock Quantity", min_value=0, step=1)

            submitted = st.form_submit_button("Add Product")
            if submitted:
                if not name:
                    st.error("Product name is required.")
                else:
                    ok, err, _ = run_write(
                        "INSERT INTO Products (name, category, material, price, stock_quantity) "
                        "VALUES (%s, %s, %s, %s, %s)",
                        (name, category, material, price, stock),
                    )
                    if ok:
                        st.success(f"'{name}' added successfully.")
                        st.rerun()
                    else:
                        st.error(f"Could not add product: {err}")

    with tab_restock:
        if products:
            product_options = {f"{p['name']} (Stock: {p['stock_quantity']})": p["product_id"] for p in products}
            with st.form("restock_form"):
                chosen = st.selectbox("Select Product", list(product_options.keys()))
                add_qty = st.number_input("Quantity to Add", min_value=1, step=1)
                submitted = st.form_submit_button("Restock")
                if submitted:
                    product_id = product_options[chosen]
                    ok, err, _ = run_write(
                        "UPDATE Products SET stock_quantity = stock_quantity + %s WHERE product_id = %s",
                        (add_qty, product_id),
                    )
                    if ok:
                        st.success("Stock updated. (Logged automatically via trigger.)")
                        st.rerun()
                    else:
                        st.error(f"Could not update stock: {err}")
        else:
            st.info("No products to restock yet.")
else:
    st.caption("Only Admin and Inventory Manager roles can add or restock products.")
