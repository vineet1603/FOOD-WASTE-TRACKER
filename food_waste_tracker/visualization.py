import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# 📈 1. Daily waste line chart
def create_daily_chart(df):
    if df.empty or "date" not in df.columns or "quantity_kg" not in df.columns:
        return go.Figure().update_layout(title="No data available for daily trend")

    daily_data = df.groupby(df['date'].dt.date)["quantity_kg"].sum().reset_index()
    fig = px.line(daily_data, x="date", y="quantity_kg", title="Daily Food Waste (kg)")
    fig.update_traces(mode="lines+markers")
    fig.update_layout(xaxis_title="Date", yaxis_title="Kg Wasted")
    return fig

# 📊 2. Category-wise bar chart
def create_category_chart(df):
    if df.empty or "category" not in df.columns or "quantity_kg" not in df.columns:
        return go.Figure().update_layout(title="No data available for category trend")

    category_data = df.groupby("category")["quantity_kg"].sum().reset_index()
    fig = px.bar(category_data, x="category", y="quantity_kg", title="Waste by Category (kg)", text_auto=True)
    fig.update_layout(xaxis_title="Category", yaxis_title="Kg Wasted")
    return fig

# 📉 3. Monthly waste trend area chart
def create_monthly_trend(df):
    if df.empty or "date" not in df.columns or "quantity_kg" not in df.columns:
        return go.Figure().update_layout(title="No data available for monthly trend")

    df["month"] = df["date"].dt.to_period("M").astype(str)
    monthly_data = df.groupby("month")["quantity_kg"].sum().reset_index()
    fig = px.area(monthly_data, x="month", y="quantity_kg", title="Monthly Food Waste Trend (kg)")
    fig.update_layout(xaxis_title="Month", yaxis_title="Kg Wasted")
    return fig
