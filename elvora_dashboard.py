import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

# page
st.set_page_config(page_title="Elvora Dashboard", layout="wide")

st.markdown("""
<style>

/* الصفحة */
[data-testid="stAppViewContainer"] {
    background-color: #f4f6f8;
}

/* المحتوى */
[data-testid="stHeader"] {
    background: transparent;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #334155;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* KPI Cards */
div[data-testid="metric-container"] {
    background-color: white;
    border: 1px solid #e5e7eb;
    padding: 18px;
    border-radius: 16px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.08);
}

/* عنوان */
h1 {
    color: #334155;
    font-size: 38px;
    font-weight: bold;
}
div.stDownloadButton {
    text-align: center;
}

div.stDownloadButton > button {
    background-color: #334155;
    color: white;
    border-radius: 12px;
    padding: 10px 25px;
    font-weight: bold;
    border: none;
}

</style>
""", unsafe_allow_html=True)

st.markdown("<h1>📊 ELVORA Business Dashboard</h1>", unsafe_allow_html=True)

st.sidebar.header("Filters")
selected_city = st.sidebar.selectbox(
    "choose City",["All","Dubai","Riyadh","Doha","Kuwait City","Manama"]
)

# database
conn = sqlite3.connect("elvora.db")

# ---------------- KPI ----------------
query = """
SELECT 
SUM(o.quantity * p.price) AS total_revenue
FROM orders o
JOIN products p
ON o.product_id = p.product_id
"""

revenue = pd.read_sql(query, conn)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Revenue", f"${revenue['total_revenue'][0]:,.0f}")

with col2:
    total_products = pd.read_sql("SELECT COUNT(*) AS count FROM products", conn)
    st.metric("Total Products", total_products["count"][0])

with col3:
    total_cities = pd.read_sql("SELECT COUNT(DISTINCT city) AS count FROM customers", conn)
    st.metric("Cities", total_cities["count"][0])

# ---------------- Top Products ----------------
st.markdown("## 📦 Top Selling Products")

query = """
SELECT 
p.product_name,
SUM(o.quantity) AS total_sold
FROM orders o
JOIN products p
ON o.product_id = p.product_id
GROUP BY p.product_name
ORDER BY total_sold DESC
"""

df = pd.read_sql(query, conn)

fig, ax = plt.subplots()
ax.bar(df["product_name"], df["total_sold"], color="#3b82f6")
plt.xticks(rotation=45)
st.pyplot(fig)

# ---------------- City Sales ----------------
st.markdown("## 🌍 Sales by City")

if selected_city == "All":
    query = """
    SELECT 
    c.city,
    SUM(o.quantity) AS total_orders
    FROM orders o
    JOIN customers c
    ON o.customer_id = c.customer_id
    GROUP BY c.city
    ORDER BY total_orders DESC
    """
else:
    query = f"""
    SELECT 
    c.city,
    SUM(o.quantity) AS total_orders
    FROM orders o
    JOIN customers c
    ON o.customer_id = c.customer_id
    where c.city = '{selected_city}'
    GROUP BY c.city
    """

city_df = pd.read_sql(query, conn)

fig2, ax2 = plt.subplots()
ax2.bar(city_df["city"], city_df["total_orders"], color="#1d4ed8")
plt.xticks(rotation=45)
st.pyplot(fig2)

st.markdown("## 💳 Payment Methods")

query = """
SELECT payment_method, COUNT(*) AS total
FROM payments
GROUP BY payment_method
"""

pay_df = pd.read_sql(query, conn)

fig3, ax3 = plt.subplots()
colors = ["#3b82f6", "#1e3a8a", "#1d4ed8"]

ax3.pie(
    pay_df["total"],
    labels=pay_df["payment_method"],
    autopct="%1.1f%%",
    startangle=90,
    colors=colors
)

st.pyplot(fig3)


orders_df = pd.read_sql("SELECT * FROM orders", conn)

csv = orders_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Orders CSV",
    data=csv,
    file_name="orders_data.csv",
    mime="text/csv"
)

st.markdown("---")
st.caption("Built by Maria  | Powered by Python & Streamlit")
