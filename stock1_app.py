import pandas as pd #pip install pandas openpyxl
import plotly.express as px #pip install plotly-express
import streamlit as st #pip install streamlit

st.set_page_config(page_title="Retail Analysis",
                   page_icon= ":p_button:", 
                   layout="wide"
)

df = pd.read_csv("retail_sales_data.csv", parse_dates=["Date"])
df["Month"] = df["Date"].dt.month_name()
df["Year"] = df["Date"].dt.year
df["Month_Year"] = df["Date"].dt.to_period("M").astype(str)

print(df)

#sidebar
st.sidebar.header("Please filter here:")
Month = st.sidebar.multiselect(
    "Select the month:",
    options=df["Month"].unique(),
    default=df["Month"].unique()
)

Year = st.sidebar.multiselect(
    "Select the year:",
    options=df["Year"].unique(),
    default=df["Year"].unique()
)   
df_selection = df.query(
    "Month == @Month and Year == @Year"
)

#mainpage
st.title(":bar_chart: Retail Sales & Stock Dashboard")
st.markdown("##")

# KPI Section
total_revenue = int(df_selection["Revenue"].sum())
total_units = int(df_selection["Units_Sold"].sum())
avg_stock = int(df_selection["Stock_Level"].mean())

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Revenue", f"${total_revenue:,.0f}")
col2.metric("📦 Total Units Sold", f"{total_units:,}")
col3.metric("📉 Avg. Stock Level", f"{avg_stock:,}")
st.markdown("---")

#monthly revenue trend(line chart)
st.subheader("📈 Monthly Revenue Trend")
monthly_rev = df_selection.groupby("Month_Year")["Revenue"].sum().reset_index()

fig_line = px.line(
    monthly_rev,
    x="Month_Year",
    y="Revenue",
    markers=True,
    title="Monthly Revenue Over Time",
    template="plotly_white"
)
fig_line.update_traces(line_color="#6A5ACD")
fig_line.update_layout(xaxis_title="Month", yaxis_title="Revenue", title_x=0.5)
st.plotly_chart(fig_line, use_container_width=True)
st.markdown("---")

#top 10 best selling products
st.subheader("🏆 Top 10 Best-Selling Products")

top_products = df_selection.groupby("Product_Name")["Units_Sold"].sum().sort_values(ascending=True).head(10).reset_index()

fig_bar = px.bar(
    top_products,
    x="Units_Sold",
    y="Product_Name",
    orientation="h",
    title="Top 10 Products by Units Sold",
    template="plotly_white",
    color="Units_Sold",
    color_continuous_scale="viridis"
)
fig_bar.update_layout(xaxis_title="Units Sold", yaxis_title="Product", title_x=0.5)
fig_bar.update_traces(marker_line_color="black", marker_line_width=1.2)
st.plotly_chart(fig_bar, use_container_width=True)
st.markdown("---")

#pie chart for category contribution
st.subheader("📊 Revenue Contribution by Category")

category_revenue = df_selection.groupby("Category")["Revenue"].sum().reset_index()

fig_pie = px.pie(
    category_revenue,
    values="Revenue",
    names="Category",
    title="Revenue Share by Product Category",
    hole=0.4,  # for donut chart feel
    color_discrete_sequence=px.colors.qualitative.Pastel
)
fig_pie.update_traces(textposition="inside", textinfo="percent+label")
fig_pie.update_layout(title_x=0.5)
st.plotly_chart(fig_pie, use_container_width=True)
st.markdown("---")

#restock suggestion table
st.subheader("🔁 Restock Suggestions")

# Calculate average demand and stock per product
avg_demand = df_selection.groupby("Product_Name")["Units_Sold"].mean()
avg_stock = df_selection.groupby("Product_Name")["Stock_Level"].mean()

stock_df = pd.DataFrame({
    "Avg_Units_Sold": avg_demand,
    "Avg_Stock_Level": avg_stock
})

def stock_status(row):
    if row["Avg_Units_Sold"] > row["Avg_Stock_Level"] * 0.8:
        return "⚠️ Urgent Restock"
    elif row["Avg_Units_Sold"] > row["Avg_Stock_Level"] * 0.5:
        return "🟠 Monitor"
    else:
        return "✅ Stable"

stock_df["Restock_Status"] = stock_df.apply(stock_status, axis=1)
stock_df = stock_df.reset_index().sort_values(by="Avg_Units_Sold", ascending=False)

st.dataframe(
    stock_df.style.format({
        "Avg_Units_Sold": "{:.1f}",
        "Avg_Stock_Level": "{:.1f}"
    }),
    use_container_width=True
)
st.markdown("---")