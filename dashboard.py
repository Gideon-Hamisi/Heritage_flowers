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

# Convert Date
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# Drop bad rows
df = df.dropna(subset=["Date"])

# ================================
# SIDEBAR FILTERS
# ================================
st.sidebar.title("Filters")

customers = st.sidebar.multiselect(
    "Select Customer",
    options=df["Customer"].dropna().unique(),
    default=df["Customer"].dropna().unique()
)

df = df[df["Customer"].isin(customers)]

# ================================
# KPI METRICS
# ================================
total_revenue = df["Total_Sales_KES"].sum()
total_stems = df["Quantity_Sold"].sum()
avg_price = df["Unit_Price"].mean()

st.title("🌹 Flower Sales Dashboard (Q1 2026)")

col1, col2, col3 = st.columns(3)

col1.metric("Total Revenue (KES)", f"{total_revenue:,.0f}")
col2.metric("Total Stems Sold", f"{total_stems:,.0f}")
col3.metric("Avg Price per Stem", f"{avg_price:.2f}")

# ================================
# DAILY REVENUE
# ================================
daily = df.groupby("Date")["Total_Sales_KES"].sum().reset_index()

st.subheader("📈 Daily Revenue Trend")

fig1, ax1 = plt.subplots()
ax1.plot(daily["Date"], daily["Total_Sales_KES"])
ax1.set_title("Daily Revenue")
ax1.set_xlabel("Date")
ax1.set_ylabel("KES")
ax1.grid()

st.pyplot(fig1)

# ================================
# MOVING AVERAGE
# ================================
daily["MA_7"] = daily["Total_Sales_KES"].rolling(7).mean()

st.subheader("📊 Revenue with 7-Day Moving Average")

fig2, ax2 = plt.subplots()
ax2.plot(daily["Date"], daily["Total_Sales_KES"], label="Actual")
ax2.plot(daily["Date"], daily["MA_7"], label="7-Day MA")
ax2.legend()
ax2.grid()

st.pyplot(fig2)

# ================================
# MONTHLY REVENUE
# ================================
monthly = df.resample("M", on="Date")["Total_Sales_KES"].sum()

st.subheader("📅 Monthly Revenue")

fig3, ax3 = plt.subplots()
ax3.plot(monthly.index, monthly.values, marker='o')
ax3.grid()

st.pyplot(fig3)

# ================================
# FORECASTING (LINEAR MODEL)
# ================================
st.subheader("🔮 30-Day Revenue Forecast")

df_ts = daily.copy()
df_ts["t"] = np.arange(len(df_ts))

X = df_ts[["t"]]
y = df_ts["Total_Sales_KES"]

model = LinearRegression()
model.fit(X, y)

# Future prediction
future_days = 30
future_t = np.arange(len(df_ts), len(df_ts) + future_days).reshape(-1, 1)
future_preds = model.predict(future_t)

future_dates = pd.date_range(
    start=df_ts["Date"].max(),
    periods=future_days + 1,
    freq="D"
)[1:]

# Plot forecast
fig4, ax4 = plt.subplots()
ax4.plot(df_ts["Date"], y, label="Actual")
ax4.plot(future_dates, future_preds, label="Forecast")
ax4.legend()
ax4.grid()

st.pyplot(fig4)

# ================================
# TOP CUSTOMERS
# ================================
st.subheader("🏆 Top Customers")

top_customers = (
    df.groupby("Customer")["Total_Sales_KES"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

st.bar_chart(top_customers)