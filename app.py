"""
Global Superstore — Regional Sales Manager Dashboard
Team: <你的组号/名字>
"""
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Global Superstore — Profit Dashboard", layout="wide")


# ---------- 1. 读数据 ----------
@st.cache_data
def load_data():
    df = pd.read_csv("superstore.csv", encoding="latin-1")
    df["Order.Date"] = pd.to_datetime(df["Order.Date"])
    df["Year"] = df["Order.Date"].dt.year
    return df


df = load_data()

# ---------- 2. 标题 + 一句话说明 ----------
st.title("Global Superstore · Sales & Profit Dashboard")
st.caption(
    "For the Regional Sales Manager — spot high-sales, low-margin product lines "
    "and decide which discounts to cut.  Data: Jan 2011 – Dec 2014, Kaggle snapshot.  "
    "In production: refresh nightly, reviewed every Monday."
)

# ---------- 3. 筛选器 ----------
with st.sidebar:
    st.header("Filters")
    years = sorted(df["Year"].unique().tolist())
    chosen_years = st.multiselect("Year", years, default=years)

    categories = sorted(df["Category"].unique().tolist())
    chosen_cats = st.multiselect("Category", categories, default=categories)

    regions = sorted(df["Region"].unique().tolist())
    chosen_region = st.selectbox("Region", ["All"] + regions)

d = df[
    df["Year"].isin(chosen_years)
    & df["Category"].isin(chosen_cats)
]
if chosen_region != "All":
    d = d[d["Region"] == chosen_region]

# ---------- 4. 顶部三个 KPI（5 秒内能看完）----------
total_sales = d["Sales"].sum()
total_profit = d["Profit"].sum()
margin = total_profit / total_sales * 100 if total_sales else 0
loss_orders = (d["Profit"] < 0).sum()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Sales", f"${total_sales:,.0f}")
k2.metric("Total Profit", f"${total_profit:,.0f}")
k3.metric("Profit Margin", f"{margin:.1f}%")
k4.metric("Loss-making orders", f"{loss_orders:,}")

st.divider()

# ---------- 5. 中间图表 1：按子品类看利润（找出"卖得多却亏钱"的）----------
st.subheader("Profit by Sub-Category — which lines drag us down?")
sub = (
    d.groupby("Sub-Category")
    .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
    .reset_index()
)
sub["Margin%"] = sub["Profit"] / sub["Sales"] * 100
sub = sub.sort_values("Profit")

fig1 = px.bar(
    sub,
    x="Profit",
    y="Sub-Category",
    orientation="h",
    color="Profit",
    color_continuous_scale="RdYlGn",
    hover_data={"Sales": ":$,", "Margin%": ":.1f"},
)
fig1.update_layout(height=460, margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig1, use_container_width=True)

# ---------- 6. 中间图表 2：折扣 vs 利润（验证"高折扣=亏钱"）----------
st.subheader("Discount level vs Profit — where do discounts turn into losses?")
d2 = d.copy()
d2["Discount_band"] = pd.cut(
    d2["Discount"],
    bins=[-0.001, 0, 0.1, 0.2, 0.3, 1.0],
    labels=["0%", "0–10%", "10–20%", "20–30%", ">30%"],
)
band = (
    d2.groupby("Discount_band", observed=True)
    .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Row.ID", "count"))
    .reset_index()
)
fig2 = px.bar(
    band,
    x="Discount_band",
    y="Profit",
    color="Profit",
    color_continuous_scale="RdYlGn",
    hover_data={"Sales": ":$,", "Orders": ":,"},
    labels={"Discount_band": "Discount band"},
)
fig2.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig2, use_container_width=True)

# ---------- 7. 底部：明细表格（想钻进去的人看）----------
with st.expander("Show underlying orders (last 200)"):
    cols = ["Order.Date", "Order.ID", "Region", "Category", "Sub-Category",
            "Customer.Name", "Sales", "Discount", "Profit"]
    st.dataframe(d[cols].sort_values("Order.Date", ascending=False).head(200),
                 use_container_width=True, height=300)

st.caption("Built with Streamlit · Data source: Kaggle Global Superstore (2011–2014)")
