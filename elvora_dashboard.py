import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

# page
st.set_page_config(page_title="Elvora Dashboard", layout="wide")

st.markdown("""
<style>

/* page background */
[data-testid="stAppViewContainer"] {
    background-color: #f8fafc;
}

/* sidebar */
section[data-testid="stSidebar"] {
    background-color: #1e293b;
}

/* sidebar text only */
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span {
    color: white !important;
}

/* dropdown text */
section[data-testid="stSidebar"] div[data-baseweb="select"] * {
    color: black !important;
}

/* titles in main page */
h1, h2, h3 {
    color: #1e293b !important;
}


/* KPI card */
div[data-testid="metric-container"] {
    background: white;
    border-left: 5px solid #1d4ed8;
    padding: 16px;
    border-radius: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

/* label */
div[data-testid="metric-container"] label {
    color: #475569 !important;
    font-size: 14px !important;
    font-weight: 600 !important;
}

/* value */
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #1e293b !important;
    font-size: 26px !important;
    font-weight: bold !important;
}

/* mobile */
@media (max-width: 768px) {
    div[data-testid="metric-container"] {
        padding: 12px;
    }

    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 22px !important;
    }

    div[data-testid="metric-container"] label {
        font-size: 13px !important;
    }
}


/* button */
div.stDownloadButton {
    text-align: center;
}

div.stDownloadButton > button {
    background-color: #1d4ed8;
    color: white;
    border-radius: 12px;
    padding: 10px 24px;
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
