import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ================================
# LOAD DATA (CLOUD SAFE)
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

sales["Revenue_per_Stem"] = (
    sales["Total_Sales_KES"] / sales["Quantity_Sold"]
)

# Daily aggregation (IMPORTANT)
sales_daily = (
    sales.groupby("Date")
    .agg({
        "Quantity_Sold": "sum",
        "Total_Sales_KES": "sum"
    })
    .reset_index()
)

sales_daily["Revenue_per_Stem"] = (
    sales_daily["Total_Sales_KES"] / sales_daily["Quantity_Sold"]
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
# MERGE (DATE LEVEL)
# ================================
df = pd.merge(
    production,
    sales_daily,
    on="Date",
    how="left"
)

# Fill missing values
df["Quantity_Sold"] = df["Quantity_Sold"].fillna(0)
df["Total_Sales_KES"] = df["Total_Sales_KES"].fillna(0)
df["Revenue_per_Stem"] = df["Revenue_per_Stem"].fillna(0)

# ================================
# DERIVED METRICS
# ================================
df["Estimated_Revenue"] = df["Production_Qty"] * df["Revenue_per_Stem"]

# Allocate sales proportionally across varieties
total_daily_production = df.groupby("Date")["Production_Qty"].transform("sum")

df["Allocated_Sales"] = (
    df["Production_Qty"] / total_daily_production
) * df["Quantity_Sold"]

df["Allocated_Sales"] = df["Allocated_Sales"].fillna(0)

# Inventory logic
df["Remaining_Stock"] = df["Production_Qty"] - df["Allocated_Sales"]

# ================================
# SIDEBAR FILTER
# ================================
st.sidebar.title("Filters")

varieties = st.sidebar.multiselect(
    "Select Variety",
    options=sorted(df["Variety"].unique()),
    default=sorted(df["Variety"].unique())
)

df = df[df["Variety"].isin(varieties)]

# ================================
# TABS
# ================================
tab1, tab2, tab3 = st.tabs([
    "🌹 Revenue",
    "📦 Inventory",
    "📉 Production Gap"
])

# =========================================================
# 🌹 TAB 1: REVENUE PER VARIETY
# =========================================================
with tab1:
    st.subheader("🌹 Revenue per Variety")

    variety_rev = (
        df.groupby("Variety")["Estimated_Revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    st.bar_chart(variety_rev)

# =========================================================
# 📦 TAB 2: INVENTORY TRACKING
# =========================================================
with tab2:
    st.subheader("📦 Inventory Tracking")

    inventory = df.groupby("Variety").agg({
        "Production_Qty": "sum",
        "Allocated_Sales": "sum"
    })

    inventory["Remaining_Stock"] = (
        inventory["Production_Qty"] - inventory["Allocated_Sales"]
    )

    inventory = inventory.sort_values("Remaining_Stock", ascending=False)

    st.dataframe(inventory)

# =========================================================
# 📉 TAB 3: PRODUCTION VS SALES GAP
# =========================================================
with tab3:
    st.subheader("📉 Production vs Sales Gap")

    gap = (
        df.groupby("Variety")
        .apply(lambda x: x["Production_Qty"].sum() - x["Allocated_Sales"].sum())
        .sort_values(ascending=False)
    )

    fig, ax = plt.subplots()
    ax.bar(gap.index, gap.values)
    ax.set_xticklabels(gap.index, rotation=90)
    ax.set_title("Production - Sales Gap")

    st.pyplot(fig)