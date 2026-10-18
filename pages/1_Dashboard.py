import streamlit as st
import pandas as pd
from auth import require_login, logout
from style import apply_theme, status_badge
from db import run_select

st.set_page_config(page_title="Dashboard | Noor Collections", layout="wide")
apply_theme()
require_login()

# ---------------- Sidebar ----------------
with st.sidebar:
    st.markdown(f"**{st.session_state['name']}**")
    st.caption(st.session_state["role"])
    if st.button("Log out"):
        logout()
        st.switch_page("app.py")

st.title("Dashboard")
st.caption("Overview of revenue, orders and inventory health.")

# ---------------- Top summary cards ----------------
summary_rows = run_select("SELECT * FROM v_revenue_summary")
summary = summary_rows[0] if summary_rows else {}

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Revenue", f"Rs {summary.get('total_revenue') or 0:,.0f}")
col2.metric("Total Orders", summary.get("total_orders") or 0)
col3.metric("Pending Orders", summary.get("pending_orders") or 0)
col4.metric("Sold Out Products", summary.get("sold_out_products") or 0)
col5.metric("Low Stock Products", summary.get("low_stock_products") or 0)

st.divider()

left, right = st.columns([1.3, 1])

# ---------------- Monthly revenue chart ----------------
with left:
    st.subheader("Monthly Revenue")
    monthly = run_select("SELECT * FROM v_monthly_revenue")
    if monthly:
        df = pd.DataFrame(monthly)
        df = df.set_index("month")
        st.bar_chart(df["revenue"], color="#7B1E3A")
    else:
        st.info("No payment data yet.")

# ---------------- Top products ----------------
with right:
    st.subheader("Top Selling Products")
    top_products = run_select("SELECT * FROM v_top_products LIMIT 5")
    if top_products:
        df = pd.DataFrame(top_products)[["name", "units_sold", "revenue_generated"]]
        df.columns = ["Product", "Units Sold", "Revenue (Rs)"]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No sales data yet.")

st.divider()

# ---------------- Low stock alerts ----------------
st.subheader("Low Stock & Sold Out Alerts")
alerts = run_select("SELECT * FROM v_low_stock_alerts")
if alerts:
    df = pd.DataFrame(alerts)
    df["Status"] = df["operational_status"].apply(status_badge)
    display_df = df[["product_id", "name", "material", "stock_quantity", "Status"]]
    display_df.columns = ["ID", "Product", "Material", "Stock", "Status"]
    st.markdown(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)
else:
    st.success("All products are healthily stocked. ")

st.divider()

# ---------------- Recent orders ----------------
st.subheader("Recent Orders")
recent_orders = run_select(
    """
    SELECT o.order_id, c.name AS customer, o.order_date, o.total_amount, o.status
    FROM Orders o
    JOIN Customers c ON c.customer_id = o.customer_id
    ORDER BY o.order_date DESC, o.order_id DESC
    LIMIT 8
    """
)
if recent_orders:
    df = pd.DataFrame(recent_orders)
    df["Status"] = df["status"].apply(status_badge)
    display_df = df[["order_id", "customer", "order_date", "total_amount", "Status"]]
    display_df.columns = ["Order ID", "Customer", "Date", "Total (Rs)", "Status"]
    st.markdown(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)
else:
    st.info("No orders yet.")
