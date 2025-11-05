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

st.set_page_config("Outlet Return Dashboard", layout="wide")
st.title("📦 Outlet Return Analysis Dashboard (October)")

# ---- LOAD ALL FILES ----
@st.cache_data
def load_all_data():
    frames = []
    for outlet, file in OUTLET_FILES.items():
        if os.path.exists(file):
            df = pd.read_excel(file)
            df["Outlet"] = outlet
            frames.append(df)
        else:
            st.warning(f"⚠️ File not found: {file}")
    if not frames:
        return pd.DataFrame()  # empty
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

# ---- CLEAN & PREP: ignore Tax, convert columns, use absolute (returns) ----
for col in ["Total Before Tax", "Total After Tax"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).abs()
    else:
        df[col] = 0.0

# Make sure df_all has numeric/abs too (used for outlet summary)
df_all_prep = df_all.copy()
for col in ["Total Before Tax", "Total After Tax"]:
    if col in df_all_prep.columns:
        df_all_prep[col] = pd.to_numeric(df_all_prep[col], errors="coerce").fillna(0).abs()
    else:
        df_all_prep[col] = 0.0

# ---- METRICS ----
total_returns_after = df["Total After Tax"].sum()
total_returns_before = df["Total Before Tax"].sum()
col1, col2 = st.columns(2)
col1.metric("📦 Total Return Value (After Tax)", f"{total_returns_after:,.2f}")
col2.metric("🏷️ Total Return Value (Before Tax)", f"{total_returns_before:,.2f}")

# ---- TOP 30 RETURNED ITEMS (vertical) ----
st.subheader("🏆 Top 30 Returned Items by Value (After Tax)")

top_n = 30
top_items = (
    df.groupby("Description", dropna=False)["Total After Tax"]
    .sum()
    .sort_values(ascending=False)
    .head(top_n)
    .reset_index()
)

# If Description is numeric or has NaNs, coerce to string for plotting
top_items["Description"] = top_items["Description"].astype(str)

fig_items = px.bar(
    top_items,
    x="Description",
    y="Total After Tax",
    title=f"Top {top_n} Returned Items (by Return Value)",
    labels={"Total After Tax": "Return Value (After Tax)", "Description": "Item Description"},
    hover_data={"Description": True, "Total After Tax": ":,.2f"},
)
# Force vertical bars, rotate x ticks for readability and set height
fig_items.update_traces(
    hovertemplate="<b>%{x}</b><br>Return: %{y:,.2f}<extra></extra>",
    marker_line_width=0
)
fig_items.update_layout(
    xaxis_tickangle=-45,
    xaxis_tickfont=dict(size=9),
    height=700,
    margin=dict(l=40, r=20, t=60, b=200),
)
st.plotly_chart(fig_items, use_container_width=True)

# ---- OUTLET-WISE BAR (vertical) ----
if outlet_selected == "All":
    st.subheader("🏬 Outlet-wise Total Return Value (After Tax)")

    outlet_summary = (
        df_all_prep.groupby("Outlet", dropna=False)[["Total After Tax", "Total Before Tax"]]
        .sum()
        .reset_index()
        .sort_values("Total After Tax", ascending=False)
    )

    # Ensure Outlet is string
    outlet_summary["Outlet"] = outlet_summary["Outlet"].astype(str)

    fig_outlets = px.bar(
        outlet_summary,
        x="Outlet",
        y="Total After Tax",
        title="Outlet-wise Total Return Value (After Tax)",
        labels={"Total After Tax": "Return Value (After Tax)", "Outlet": "Outlet"},
        hover_data={"Outlet": True, "Total After Tax": ":,.2f"},
    )

    fig_outlets.update_traces(
        hovertemplate="<b>%{x}</b><br>Return: %{y:,.2f}<extra></extra>",
        marker_line_width=0
    )
    fig_outlets.update_layout(
        xaxis_tickangle=-45,
        xaxis_tickfont=dict(size=10),
        height=600,
        margin=dict(l=40, r=20, t=60, b=120),
    )
    st.plotly_chart(fig_outlets, use_container_width=True)

    st.dataframe(outlet_summary.style.format({"Total After Tax": "{:,.2f}", "Total Before Tax": "{:,.2f}"}))

# ---- DETAILED VIEW ----
with st.expander("📋 View Detailed Return Data"):
    st.dataframe(df)
