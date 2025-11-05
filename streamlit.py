import streamlit as st
import pandas as pd
import os
import plotly.express as px

OUTLET_FILES = {
    "Hilal": "hilal.Xlsx",
    "Safa Super": "safa super market.Xlsx",
    "Azhar HP": "azhar hp.Xlsx",
    "Azhar": "Azhar GT.Xlsx",
    "Blue Pearl": "blue pearl.Xlsx",
    "Fida": "fida al madina.Xlsx",
    "Hadeqat": "hadeqat.Xlsx",
    "Jais": "jais.Xlsx",
    "Sabah": "sabah.Xlsx",
    "Sahat": "sahat.Xlsx",
    "Shams salem": "shams.Xlsx",
    "Shams Liwan": "liwan.Xlsx",
    "Superstore": "superstore.Xlsx",
    "Tay Tay": "taytay.Xlsx",
    "Safa oudmehta": "safa oud metha.Xlsx",
    "Port saeed": "port saeed.Xlsx"
}

st.set_page_config("Outlet Return Dashboard", layout="wide")
st.title("📦 Outlet Return Analysis Dashboard (October)")

# ---- LOAD ALL FILES ----
@st.cache_data
def load_all_data():
    frames = []
    for outlet, file in OUTLET_FILES.items():
        if os.path.exists(file):
            df = pd.read_excel(file)
            df.columns = df.columns.str.strip()  # Clean column names
            df["Outlet"] = outlet
            frames.append(df)
        else:
            st.warning(f"⚠️ File not found: {file}")
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)

df_all = load_all_data()
if df_all.empty:
    st.stop()

# ---- FILTER ----
outlet_selected = st.selectbox("Select Outlet", ["All"] + list(OUTLET_FILES.keys()))
if outlet_selected != "All":
    df = df_all[df_all["Outlet"] == outlet_selected].copy()
else:
    df = df_all.copy()

# ---- CLEAN & PREP ----
for col in ["Total Before Tax", "Total After Tax"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).abs()
    df_all[col] = pd.to_numeric(df_all[col], errors="coerce").fillna(0).abs()

# ---- METRICS ----
total_returns_after = df["Total After Tax"].sum()
total_returns_before = df["Total Before Tax"].sum()
col1, col2 = st.columns(2)
col1.metric("📦 Total Return Value (After Tax)", f"{total_returns_after:,.2f}")
col2.metric("🏷️ Total Return Value (Before Tax)", f"{total_returns_before:,.2f}")

# ---- TOP 30 RETURNED ITEMS (with outlet info) ----
st.subheader("🏆 Top 30 Returned Items by Value (After Tax)")

top_n = 30
top_items = (
    df.groupby(["Description", "Outlet"], dropna=False)["Total After Tax"]
    .sum()
    .reset_index()
)

# Get overall top 30 items by total return value
top_item_list = (
    top_items.groupby("Description")["Total After Tax"]
    .sum()
    .sort_values(ascending=False)
    .head(top_n)
    .index
)
top_items = top_items[top_items["Description"].isin(top_item_list)]

top_items["Description"] = top_items["Description"].astype(str)
top_items["Outlet"] = top_items["Outlet"].astype(str)

fig_items = px.bar(
    top_items,
    y="Description",
    x="Total After Tax",
    color="Outlet",  # color by outlet
    orientation="h",
    title=f"Top {top_n} Returned Items by Outlet",
    labels={"Total After Tax": "Return Value (After Tax)", "Description": "Item Description"},
    hover_data={"Outlet": True, "Total After Tax": ":,.2f"},
)

fig_items.update_traces(
    hovertemplate="<b>%{y}</b><br>Outlet: %{customdata[0]}<br>Return: %{x:,.2f}<extra></extra>",
    marker_line_width=0
)
fig_items.update_layout(
    height=1000,
    margin=dict(l=200, r=50, t=60, b=40),
    yaxis=dict(categoryorder="total ascending"),
    legend_title_text="Outlet"
)
st.plotly_chart(fig_items, use_container_width=True)

# ---- OUTLET-WISE RETURNS ----
if outlet_selected == "All":
    st.subheader("🏬 Outlet-wise Total Return Value (After Tax)")

    outlet_summary = (
        df_all.groupby("Outlet")[["Total After Tax", "Total Before Tax"]]
        .sum()
        .reset_index()
        .sort_values("Total After Tax", ascending=False)
    )

    fig_outlets = px.bar(
        outlet_summary,
        y="Outlet",
        x="Total After Tax",
        orientation="h",
        title="Outlet-wise Total Return Value (After Tax)",
        labels={"Total After Tax": "Return Value (After Tax)", "Outlet": "Outlet"},
        hover_data={"Outlet": True, "Total After Tax": ":,.2f"},
        color="Outlet",
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    fig_outlets.update_traces(
        hovertemplate="<b>%{y}</b><br>Return: %{x:,.2f}<extra></extra>",
        marker_line_width=0
    )
    fig_outlets.update_layout(
        height=800,
        margin=dict(l=200, r=50, t=60, b=40),
        showlegend=False
    )
    st.plotly_chart(fig_outlets, use_container_width=True)

    st.dataframe(outlet_summary.style.format({"Total After Tax": "{:,.2f}", "Total Before Tax": "{:,.2f}"}))

# ---- DETAILS ----
with st.expander("📋 View Detailed Return Data"):
    st.dataframe(df)
