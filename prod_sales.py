import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ================================
# CONFIG
# ================================
st.set_page_config(page_title="Heritage Flowers BI", layout="wide")

# ================================
# LOAD DATA
# ================================
@st.cache_data
def load_data():
    sales = pd.read_csv("clean_sales_Q1_2026.csv")
    production = pd.read_excel("clean_production_data.xlsx")
    return sales, production

sales, production = load_data()

# ================================
# CLEAN SALES
# ================================
sales["Date"] = pd.to_datetime(sales["Date"], errors="coerce")
sales = sales.dropna(subset=["Date"])

sales["Revenue_per_Stem"] = np.where(
    sales["Quantity_Sold"] > 0,
    sales["Total_Sales_KES"] / sales["Quantity_Sold"],
    0
)

# DAILY SALES AGGREGATION
sales_daily = (
    sales.groupby("Date")
    .agg({
        "Quantity_Sold": "sum",
        "Total_Sales_KES": "sum"
    })
    .reset_index()
)

sales_daily["Revenue_per_Stem"] = np.where(
    sales_daily["Quantity_Sold"] > 0,
    sales_daily["Total_Sales_KES"] / sales_daily["Quantity_Sold"],
    0
)

# ================================
# CLEAN PRODUCTION
# ================================
production["Date"] = pd.to_datetime(production["Date"], errors="coerce")
production = production.dropna(subset=["Date"])

production["Variety"] = (
    production["Variety"]
    .astype(str)
    .str.strip()
    .str.upper()
)

# ================================
# MERGE DATA
# ================================
df = pd.merge(
    production,
    sales_daily,
    on="Date",
    how="left"
)

df["Quantity_Sold"] = df["Quantity_Sold"].fillna(0)
df["Total_Sales_KES"] = df["Total_Sales_KES"].fillna(0)
df["Revenue_per_Stem"] = df["Revenue_per_Stem"].fillna(0)

# ================================
# DERIVED METRICS
# ================================
# Estimated Revenue
df["Estimated_Revenue"] = df["Production_Qty"] * df["Revenue_per_Stem"]

# Safe allocation
total_daily_production = df.groupby("Date")["Production_Qty"].transform("sum")

df["Allocated_Sales"] = np.where(
    total_daily_production > 0,
    (df["Production_Qty"] / total_daily_production) * df["Quantity_Sold"],
    0
)

# Inventory
df["Remaining_Stock"] = df["Production_Qty"] - df["Allocated_Sales"]

# ================================
# DATE FEATURES
# ================================
df["YearMonth"] = df["Date"].dt.to_period("M").astype(str)

# ================================
# SIDEBAR FILTERS
# ================================
st.sidebar.title("Filters")

# Date filter
min_date = df["Date"].min()
max_date = df["Date"].max()

date_range = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date]
)

if len(date_range) == 2:
    start_date, end_date = date_range
    df = df[(df["Date"] >= pd.to_datetime(start_date)) &
            (df["Date"] <= pd.to_datetime(end_date))]

# Variety filter
varieties = st.sidebar.multiselect(
    "Select Variety",
    options=sorted(df["Variety"].unique()),
    default=sorted(df["Variety"].unique())
)

df = df[df["Variety"].isin(varieties)]

# ================================
# HEADER
# ================================
st.title("🌹 Heritage Flowers Business Intelligence Dashboard")

st.info("⚠️ Note: Variety-level sales are estimated using proportional allocation.")

# ================================
# KPI SECTION
# ================================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Revenue (KES)", f"{df['Total_Sales_KES'].sum():,.0f}")
col2.metric("Total Production", f"{df['Production_Qty'].sum():,.0f}")
col3.metric("Total Allocated Sales", f"{df['Allocated_Sales'].sum():,.0f}")
col4.metric("Remaining Stock", f"{df['Remaining_Stock'].sum():,.0f}")

# ================================
# TABS
# ================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Revenue",
    "📦 Inventory",
    "📉 Production Gap",
    "📈 Trends"
])

# =========================================================
# 📊 TAB 1: REVENUE
# =========================================================
with tab1:
    st.subheader("🌹 Top Varieties (Estimated Revenue)")

    variety_rev = (
        df.groupby("Variety")["Estimated_Revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    st.bar_chart(variety_rev)

    # Monthly revenue
    st.subheader("📊 Monthly Revenue")

    monthly_rev = (
        df.groupby("YearMonth")["Estimated_Revenue"]
        .sum()
    )

    st.bar_chart(monthly_rev)

# =========================================================
# 📦 TAB 2: INVENTORY
# =========================================================
with tab2:
    st.subheader("📦 Inventory Summary")

    inventory = df.groupby("Variety").agg({
        "Production_Qty": "sum",
        "Allocated_Sales": "sum",
        "Remaining_Stock": "sum"
    }).sort_values("Remaining_Stock", ascending=False)

    st.dataframe(inventory)

    # Low stock alert
    st.subheader("⚠️ Low Stock Varieties")

    low_stock = inventory[inventory["Remaining_Stock"] < 1000]

    st.dataframe(low_stock)

# =========================================================
# 📉 TAB 3: GAP ANALYSIS
# =========================================================
with tab3:
    st.subheader("📉 Production vs Sales Gap")

    gap = (
        df.groupby("Variety")["Remaining_Stock"]
        .sum()
        .sort_values(ascending=False)
    )

    fig, ax = plt.subplots()
    ax.bar(gap.index, gap.values)
    plt.xticks(rotation=90)

    st.pyplot(fig)

# =========================================================
# 📈 TAB 4: TRENDS
# =========================================================
with tab4:
    st.subheader("📈 Daily Production vs Sales")

    daily_trend = df.groupby("Date").agg({
        "Production_Qty": "sum",
        "Allocated_Sales": "sum"
    })

    st.line_chart(daily_trend)

    st.subheader("📊 Cumulative Performance")

    cumulative = daily_trend.cumsum()

    st.line_chart(cumulative)