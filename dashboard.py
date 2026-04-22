import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ================================
# LOAD DATA
# ================================
df = pd.read_csv("clean_sales_Q1_2026.csv")
prod = pd.read_excel("clean_production_data.xlsx")

# Clean dates
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date"])

prod["Date"] = pd.to_datetime(prod["Date"], errors="coerce")
prod = prod.dropna(subset=["Date"])

# Create YearMonth
df["YearMonth"] = df["Date"].dt.to_period("M").astype(str)
prod["YearMonth"] = prod["Date"].dt.to_period("M").astype(str)

# ================================
# SIDEBAR FILTERS
# ================================
st.sidebar.title("Filters")

customers = st.sidebar.multiselect(
    "Select Customer",
    options=sorted(df["Customer"].dropna().unique()),
    default=sorted(df["Customer"].dropna().unique())
)

drop_points = st.sidebar.multiselect(
    "Select Drop-Off Point",
    options=sorted(df["Drop_Off_Point"].dropna().unique()),
    default=sorted(df["Drop_Off_Point"].dropna().unique())
)

df = df[
    df["Customer"].isin(customers) &
    df["Drop_Off_Point"].isin(drop_points)
]

# Match production to filtered months
prod = prod[prod["YearMonth"].isin(df["YearMonth"].unique())]

# ================================
# TABS
# ================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "📦 Logistics",
    "🏆 Customers",
    "📊 Performance",
    "🌱 Production vs Sales"
])

# =========================================================
# 📊 TAB 1: OVERVIEW
# =========================================================
with tab1:
    st.title("🌹 Flower Sales Dashboard (Q1 2026)")

    # KPIs
    total_revenue = df["Total_Sales_KES"].sum()
    total_stems = df["Quantity_Sold"].sum()
    avg_price = df["Unit_Price"].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue (KES)", f"{total_revenue:,.0f}")
    col2.metric("Total Stems Sold", f"{total_stems:,.0f}")
    col3.metric("Avg Price per Stem", f"{avg_price:.2f}")

    # DAILY TREND
    daily = df.groupby("Date")["Total_Sales_KES"].sum().reset_index()

    st.subheader("📈 Daily Revenue Trend")
    fig1, ax1 = plt.subplots()
    ax1.plot(daily["Date"], daily["Total_Sales_KES"])
    ax1.grid()
    st.pyplot(fig1)

    # MONTHLY SALES
    st.subheader("📊 Monthly Sales Comparison")
    monthly_sales = (
        df.groupby("YearMonth")["Total_Sales_KES"]
        .sum()
        .reset_index()
        .sort_values("YearMonth")
    )

    fig_bar, ax_bar = plt.subplots()
    ax_bar.bar(monthly_sales["YearMonth"], monthly_sales["Total_Sales_KES"])
    ax_bar.grid(axis="y")

    for i, v in enumerate(monthly_sales["Total_Sales_KES"]):
        ax_bar.text(i, v, f"{v:,.0f}", ha='center')

    st.pyplot(fig_bar)

    # MONTHLY TREND
    monthly = df.resample("ME", on="Date")["Total_Sales_KES"].sum()

    st.subheader("📅 Monthly Revenue Trend")
    fig3, ax3 = plt.subplots()
    ax3.plot(monthly.index, monthly.values, marker='o')
    ax3.grid()
    st.pyplot(fig3)

    # CUMULATIVE
    st.subheader("📈 Cumulative Revenue (Q1)")
    cumulative = monthly.cumsum()

    fig5, ax5 = plt.subplots()
    ax5.plot(cumulative.index, cumulative.values, marker='o')
    ax5.grid()
    st.pyplot(fig5)

    # TOP CUSTOMERS (FIXED)
    st.subheader("🏆 Top Customers by Revenue")

    top_customers = (
        df.groupby("Customer")["Total_Sales_KES"]
        .sum()
        .nlargest(10)
    )

    fig_cust, ax_cust = plt.subplots()
    ax_cust.barh(top_customers.index, top_customers.values)
    ax_cust.invert_yaxis()
    ax_cust.grid()

    st.pyplot(fig_cust)

# =========================================================
# 📦 TAB 2: LOGISTICS
# =========================================================
with tab2:
    st.subheader("📦 Monthly Sales by Drop-Off Point")

    logistics_data = (
        df.groupby(["YearMonth", "Drop_Off_Point"])["Total_Sales_KES"]
        .sum()
        .reset_index()
    )

    pivot_logistics = logistics_data.pivot(
        index="YearMonth",
        columns="Drop_Off_Point",
        values="Total_Sales_KES"
    ).fillna(0)

    st.bar_chart(pivot_logistics)

    # MARKET BREAKDOWN
    st.subheader("🌍 Market Breakdown")

    market_data = (
        df.groupby(["YearMonth", "Market"])["Total_Sales_KES"]
        .sum()
        .reset_index()
    )

    pivot_market = market_data.pivot(
        index="YearMonth",
        columns="Market",
        values="Total_Sales_KES"
    ).fillna(0)

    st.bar_chart(pivot_market)

# =========================================================
# 🏆 TAB 3: CUSTOMERS
# =========================================================
with tab3:
    st.subheader("🏆 Monthly Sales by Customer")

    customer_data = (
        df.groupby(["YearMonth", "Customer"])["Total_Sales_KES"]
        .sum()
        .reset_index()
    )

    top_customers = (
        df.groupby("Customer")["Total_Sales_KES"]
        .sum()
        .nlargest(5)
        .index
    )

    customer_data = customer_data[
        customer_data["Customer"].isin(top_customers)
    ]

    pivot_customer = customer_data.pivot(
        index="YearMonth",
        columns="Customer",
        values="Total_Sales_KES"
    ).fillna(0)

    st.bar_chart(pivot_customer)

# =========================================================
# 📊 TAB 4: PERFORMANCE
# =========================================================
with tab4:
    st.subheader("📊 Performance Summary")

    summary = df.groupby("Customer").agg({
        "Total_Sales_KES": "sum",
        "Quantity_Sold": "sum",
        "No_Boxes": "sum"
    }).sort_values("Total_Sales_KES", ascending=False)

    st.dataframe(summary)

# =========================================================
# 🌱 TAB 5: PRODUCTION VS SALES
# =========================================================
with tab5:
    st.subheader("🌱 Production vs Sales")

    prod_monthly = prod.groupby("YearMonth")["Production_Qty"].sum()
    sales_monthly = df.groupby("YearMonth")["Quantity_Sold"].sum()

    combined = pd.DataFrame({
        "Production": prod_monthly,
        "Sales": sales_monthly
    }).fillna(0)

    st.line_chart(combined)

    # GAP
    combined["Gap"] = combined["Production"] - combined["Sales"]

    st.subheader("📉 Production Gap (Unsold Stock)")

    fig_gap, ax_gap = plt.subplots()
    ax_gap.bar(combined.index, combined["Gap"])
    ax_gap.grid(axis="y")

    st.pyplot(fig_gap)