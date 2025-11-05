import streamlit as st
import pandas as pd
import os

# ---- FILES ----
OUTLET_FILES = {
    "Hilal": "hilal.Xlsx",
    #"Safa Super": "Safa super oct.Xlsx",
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

# ---- APP ----
st.set_page_config("Outlet Sales Dashboard", layout="wide")
st.title("📊 Outlet Refund")

# ---- READ ALL DATA ----
@st.cache_data
def load_all_data():
    all_data = []
    for outlet, file in OUTLET_FILES.items():
        if os.path.exists(file):
            df = pd.read_excel(file)
            df["Outlet"] = outlet
            all_data.append(df)
    return pd.concat(all_data, ignore_index=True)

df_all = load_all_data()

# ---- FILTER ----
outlet_selected = st.selectbox("Select Outlet", ["All"] + list(OUTLET_FILES.keys()))

if outlet_selected != "All":
    df = df_all[df_all["Outlet"] == outlet_selected]
else:
    df = df_all

# ---- CLEAN DATA ----
for col in ["Total Before Tax", "Tax", "Total After Tax"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# ---- KEY INSIGHTS ----
total_sales = df["Total After Tax"].sum()
total_tax = df["Tax"].sum()
total_before_tax = df["Total Before Tax"].sum()
top_items = df.groupby("Description")["Total After Tax"].sum().nlargest(10)

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Sales (After Tax)", f"{total_sales:,.2f}")
col2.metric("🏷️ Total Before Tax", f"{total_before_tax:,.2f}")
col3.metric("📈 Total Tax Collected", f"{total_tax:,.2f}")

# ---- TOP ITEMS ----
st.subheader("🏆 Top 10 Items by Total Sales")
st.bar_chart(top_items)

# ---- OUTLET SUMMARY & CHART ----
if outlet_selected == "All":
    st.subheader("🏬 Outlet-wise Summary")

    outlet_summary = (
        df_all.groupby("Outlet")[["Total Before Tax", "Tax", "Total After Tax"]]
        .sum()
        .sort_values("Total After Tax", ascending=False)
    )

    # Bar chart for outlet-wise total after tax
    st.write("### 💹 Outlet-wise Total Sales (After Tax)")
    st.bar_chart(outlet_summary["Total After Tax"])

    # Detailed summary table
    st.dataframe(outlet_summary)

# ---- DETAILED VIEW ----
with st.expander("📋 View Detailed Data"):
    st.dataframe(df)
