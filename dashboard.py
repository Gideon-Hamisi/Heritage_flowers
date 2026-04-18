import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# ================================
# LOAD DATA
# ================================
file_path = r"C:\Users\G_BOOTS\OneDrive\Desktop\heritage flowers\clean_sales_Q1_2026.csv"
df = pd.read_csv(file_path)

# Clean date
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date"])

# Create YearMonth
df["YearMonth"] = df["Date"].dt.to_period("M").astype(str)

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

# ================================
# CREATE TABS
# ================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview",
    "📦 Logistics",
    "🏆 Customers",
    "📊 Performance"
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

    # MONTHLY BAR CHART
    st.subheader("📊 Monthly Sales Comparison")

    monthly_sales = (
        df.groupby("YearMonth")["Total_Sales_KES"]
        .sum()
        .reset_index()
        .sort_values("YearMonth")
    )

    fig_bar, ax_bar = plt.subplots()
    ax_bar.bar(monthly_sales["YearMonth"], monthly_sales["Total_Sales_KES"])
    ax_bar.tick_params(axis='x', rotation=45)
    ax_bar.grid(axis="y")

    for i, v in enumerate(monthly_sales["Total_Sales_KES"]):
        ax_bar.text(i, v, f"{v:,.0f}", ha='center', va='bottom')

    st.pyplot(fig_bar)

    # MONTHLY TREND LINE
    monthly = df.resample("ME", on="Date")["Total_Sales_KES"].sum()

    st.subheader("📅 Monthly Revenue Trend")
    fig3, ax3 = plt.subplots()
    ax3.plot(monthly.index, monthly.values, marker='o')
    ax3.grid()
    st.pyplot(fig3)

    # FORECAST
    st.subheader("🔮 30-Day Revenue Forecast")

    df_ts = daily.copy()
    df_ts["t"] = np.arange(len(df_ts))

    model = LinearRegression()
    model.fit(df_ts[["t"]], df_ts["Total_Sales_KES"])

    future_days = 30
    future_t = np.arange(len(df_ts), len(df_ts) + future_days)

    future_preds = model.predict(pd.DataFrame(future_t, columns=["t"]))

    future_dates = pd.date_range(
        start=df_ts["Date"].max(),
        periods=future_days + 1,
        freq="D"
    )[1:]

    fig4, ax4 = plt.subplots()
    ax4.plot(df_ts["Date"], df_ts["Total_Sales_KES"], label="Actual")
    ax4.plot(future_dates, future_preds, label="Forecast")
    ax4.legend()
    ax4.grid()

    st.pyplot(fig4)

# =========================================================
# 📦 TAB 2: LOGISTICS ANALYSIS
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

# =========================================================
# 🏆 TAB 3: CUSTOMER ANALYSIS
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
# 📊 TAB 4: PERFORMANCE SUMMARY
# =========================================================
with tab4:
    st.subheader("📊 Performance Summary")

    summary = df.groupby("Customer").agg({
        "Total_Sales_KES": "sum",
        "Quantity_Sold": "sum",
        "No_Boxes": "sum"
    }).sort_values("Total_Sales_KES", ascending=False)

    st.dataframe(summary)