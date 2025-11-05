import streamlit as st
import pandas as pd
import os
import plotly.express as px

# ---- FILES ----
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

# ---- APP SETTINGS ----
st.set_page_config("Outlet Return Dashboard", layout="wide")
st.title("📦 Outlet Return Analysis Dashboard (October)")

# ---- LOAD DATA ----
@st.cache_data
def load_all_data():
    all_data = []
    for outlet, file in OUTLET_FILES.items():
        if os.path.exists(file):
            df = pd.read_excel(file)
            df["Outlet"] = outlet
            all_data.append(df)
        else:
            st.warning(f"⚠️ File not found: {file}")
    return pd.concat(all_data, ignore_index=True)

df_all = load_all_data()

# ---- FILTER ----
outlet_selected = st.selectbox("Select Outlet", ["All"] + list(OUTLET_FILES.keys()))

if outlet_selected != "All":
    df = df_all[df_all["Outlet"] == outlet_selected]
else:
    df = df_all

# ---- CLEAN & PREP DATA ----
for col in ["Total Before Tax", "Total After Tax"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df[col] = df[col].abs()  # convert negatives to positive (return value)

# ---- KEY METRICS ----
total_returns_after = df["Total After Tax"].sum()
total_returns_before = df["Total Before Tax"].sum()
top_returned_items = (
    df.groupby("Description")["Total After Tax"].sum().nlargest(10).reset_index()
)

col1, col2 = st.columns(2)
col1.metric("📦 Total Return Value (After Tax)", f"{total_returns_after:,.2f}")
col2.metric("🏷️ Total Return Value (Before Tax)", f"{total_returns_before:,.2f}")

# ---- TOP RETURNED ITEMS ----
st.subheader("🏆 Top 10 Returned Items by Value")
fig_items = px.bar(
    top_returned_items,
    x="Description",
    y="Total After Tax",
    hover_data={"Description": True, "Total After Tax": ":,.2f"},
    text_auto=".2s",
    color="Total After Tax",
    color_continuous_scale="Blues",
    title="Top Returned Items",
)
fig_items.update_layout(xaxis_title="", yaxis_title="Return Value (After Tax)")
st.plotly_chart(fig_items, use_container_width=True)

# ---- OUTLET SUMMARY ----
if outlet_selected == "All":
    st.subheader("🏬 Outlet-wise Return Summary")

    outlet_summary = (
        df_all.groupby("Outlet")[["Total Before Tax", "Total After Tax"]]
        .sum()
        .abs()
        .sort_values("Total After Tax", ascending=False)
        .reset_index()
    )

    # ---- INTERACTIVE BAR CHART ----
    fig_outlets = px.bar(
        outlet_summary,
        x="Outlet",
        y="Total After Tax",
        hover_data={"Outlet": True, "Total After Tax": ":,.2f"},
        text_auto=".2s",
        color="Total After Tax",
        color_continuous_scale="Tealgrn",
        title="💹 Outlet-wise Total Return Value (After Tax)",
    )
    fig_outlets.update_layout(
        xaxis_title="Outlet",
        yaxis_title="Return Value (After Tax)",
        hoverlabel=dict(bgcolor="white", font_size=13, font_family="Arial"),
    )
    st.plotly_chart(fig_outlets, use_container_width=True)

    # Table
    st.dataframe(outlet_summary)

# ---- DETAILED VIEW ----
with st.expander("📋 View Detailed Return Data"):
    st.dataframe(df)
