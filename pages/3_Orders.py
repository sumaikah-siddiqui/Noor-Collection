import streamlit as st
import pandas as pd
from auth import require_login, logout
from style import apply_theme, status_badge
from db import run_select, call_procedure

st.set_page_config(page_title="Orders | Noor Collections", layout="wide")
apply_theme()
require_login()

with st.sidebar:
    st.markdown(f"**{st.session_state['name']}**")
    st.caption(st.session_state["role"])
    if st.button("Log out"):
        logout()
        st.switch_page("app.py")

st.title("Orders")

STATUSES = ["Pending", "Confirmed", "Shipped", "Delivered", "Cancelled"]

# ---------------- Search & filters ----------------
c1, c2 = st.columns([2, 1])
with c1:
    search_term = st.text_input("Search by customer name")
with c2:
    status_filter = st.selectbox("Status", ["All"] + STATUSES)

query = """
    SELECT o.order_id, c.name AS customer, o.order_date, o.total_amount, o.status, o.notes
    FROM Orders o
    JOIN Customers c ON c.customer_id = o.customer_id
    WHERE 1=1
"""
params = []
if search_term:
    query += " AND c.name LIKE %s"
    params.append(f"%{search_term}%")
if status_filter != "All":
    query += " AND o.status = %s"
    params.append(status_filter)
query += " ORDER BY o.order_date DESC, o.order_id DESC"

orders = run_select(query, tuple(params))
st.caption(f"{len(orders)} order(s) found")

if orders:
    df = pd.DataFrame(orders)
    df["Status"] = df["status"].apply(status_badge)
    display_df = df[["order_id", "customer", "order_date", "total_amount", "Status", "notes"]]
    display_df.columns = ["Order ID", "Customer", "Date", "Total (Rs)", "Status", "Notes"]
    st.markdown(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)
else:
    st.info("No orders match your search.")

st.divider()

# ---------------- View items for a specific order ----------------
st.subheader("Order Details")
if orders:
    order_options = {f"Order #{o['order_id']} — {o['customer']}": o["order_id"] for o in orders}
    chosen_label = st.selectbox("Select an order to view items", list(order_options.keys()))
    order_id = order_options[chosen_label]

    items = run_select(
        """
        SELECT p.name, oi.quantity, oi.unit_price, (oi.quantity * oi.unit_price) AS line_total
        FROM Order_Items oi
        JOIN Products p ON p.product_id = oi.product_id
        WHERE oi.order_id = %s
        """,
        (order_id,),
    )
    if items:
        df_items = pd.DataFrame(items)
        df_items.columns = ["Product", "Qty", "Unit Price (Rs)", "Line Total (Rs)"]
        st.dataframe(df_items, use_container_width=True, hide_index=True)

    shipping = run_select("SELECT * FROM Shipping WHERE order_id = %s", (order_id,))
    if shipping:
        s = shipping[0]
        st.caption(
            f"Shipping: {s['shipping_status']} via {s['courier_company']}"
            + (f" — Tracking: {s['tracking_number']}" if s["tracking_number"] else "")
        )

st.divider()

# ---------------- Create new order (Admin & Sales only) ----------------
can_create = st.session_state["role"] in ("Admin", "Sales")

st.subheader("Create New Order")
if not can_create:
    st.caption("Only Admin and Sales roles can create new orders.")
else:
    customers = run_select("SELECT customer_id, name FROM Customers ORDER BY name")
    products = run_select("SELECT product_id, name, price, stock_quantity FROM Products WHERE stock_quantity > 0 ORDER BY name")

    if not customers or not products:
        st.info("Need at least one customer and one in-stock product to create an order.")
    else:
        customer_options = {c["name"]: c["customer_id"] for c in customers}
        product_options = {
            f"{p['name']} — Rs {p['price']:,.0f} ({p['stock_quantity']} in stock)": p
            for p in products
        }

        if "order_flash" in st.session_state:
            st.success(st.session_state.pop("order_flash"))

        # Not inside st.form on purpose: widgets in a form don't refresh until
        # submit, which made the total and max quantity go stale when the
        # product was changed. Outside a form, the total updates instantly.
        with st.container(border=True):
            colA, colB = st.columns(2)
            with colA:
                chosen_customer = st.selectbox("Customer", list(customer_options.keys()))
            with colB:
                chosen_product_label = st.selectbox("Product", list(product_options.keys()))

            chosen_product = product_options[chosen_product_label]
            max_qty = int(chosen_product["stock_quantity"])
            qty_key = f"qty_{chosen_product['product_id']}"
            quantity = st.number_input(
                "Quantity", min_value=1, max_value=max_qty, step=1, key=qty_key
            )

            unit_price = chosen_product["price"]
            total_amount = unit_price * quantity
            st.write(f"**Total: Rs {total_amount:,.2f}**")

            if st.button("Place Order"):
                success, err = call_procedure(
                    "sp_process_secure_checkout",
                    (
                        customer_options[chosen_customer],
                        total_amount,
                        chosen_product["product_id"],
                        quantity,
                        unit_price,
                    ),
                )
                if success:
                    st.session_state["order_flash"] = (
                        "Order placed successfully. Stock was updated automatically."
                    )
                    del st.session_state[qty_key]
                    st.rerun()
                else:
                    st.error(f"Order failed: {err}")