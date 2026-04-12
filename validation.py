import pandas as pd

# Load cleaned production data
file_path = r"C:\Users\G_BOOTS\OneDrive\Desktop\heritage flowers\clean_production_data.xlsx"
df = pd.read_excel(file_path)

print("🔍 BASIC INFO")
print(df.info())

print("\n📊 SAMPLE DATA")
print(df.head())

# -------------------------------
# 1. Missing Values Check
# -------------------------------
print("\n❌ Missing Values:")
print(df.isnull().sum())

# -------------------------------
# 2. Date Validation
# -------------------------------
print("\n📅 Date Range:")
print("Min Date:", df['Date'].min())
print("Max Date:", df['Date'].max())

# Check invalid dates
invalid_dates = df[df['Date'].isna()]
print("Invalid date rows:", len(invalid_dates))

# -------------------------------
# 3. Duplicate Check
# -------------------------------
duplicates = df.duplicated(subset=['Date', 'Variety'])
print("\n🔁 Duplicate Records:", duplicates.sum())

# -------------------------------
# 4. Quantity Validation
# -------------------------------
print("\n📦 Production Quantity Stats:")
print(df['Production_Qty'].describe())

# Check negative or zero values
bad_qty = df[df['Production_Qty'] <= 0]
print("⚠️ Zero or Negative Quantities:", len(bad_qty))

# -------------------------------
# 5. Category Validation
# -------------------------------
print("\n🌹 Category Distribution:")
print(df['Category'].value_counts())

unknowns = df[df['Category'] == 'Unknown']['Variety'].unique()
print("\n⚠️ Unknown Varieties:", unknowns)

# -------------------------------
# 6. Grade Validation
# -------------------------------
#print("\n🏷️ Unique Grades:")
#print(df['Grade'].unique())

# -------------------------------
# 7. Logical Check (Daily totals)
# -------------------------------
daily_totals = df.groupby('Date')['Production_Qty'].sum()

print("\n📊 Daily Production Summary:")
print(daily_totals.describe())

# -------------------------------
# 8. Outlier Detection
# -------------------------------
q1 = df['Production_Qty'].quantile(0.25)
q3 = df['Production_Qty'].quantile(0.75)
iqr = q3 - q1

outliers = df[
    (df['Production_Qty'] < (q1 - 1.5 * iqr)) |
    (df['Production_Qty'] > (q3 + 1.5 * iqr))
]

print("\n🚨 Outliers detected:", len(outliers))
print(outliers.head())

pivot_check = df.pivot_table(
    index='Date',
    columns='Variety',
    values='Production_Qty',
    aggfunc='sum'
)

print(pivot_check.head())