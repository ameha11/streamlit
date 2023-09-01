import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
import altair as alt

import matplotlib.pyplot as plt
from matplotlib import style
import altair as alt
import plost

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Agp II Dashboard", page_icon=":bar_chart:", layout="wide"
)
st.title("AGP II Dashboard")
# :bar_chart:
st.markdown(
    "<style>div.block-container{padding-top:1rem;}</style>", unsafe_allow_html=True
)

df = pd.read_excel("C:\Survey AGP II\Data\Head_and_Spouse.xls")

col1, col2 = st.columns((2))
df["ID15"] = pd.to_datetime(df["ID15"])

# Getting the min and max date
startDate = pd.to_datetime(df["ID15"]).min()
endDate = pd.to_datetime(df["ID15"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["ID15"] >= date1) & (df["ID15"] <= date2)].copy()

# Location selection sidebar
st.sidebar.header("Filter by Location: ")

# Region
region = st.sidebar.multiselect("Region", df["Region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

# Woreda
woreda = st.sidebar.multiselect("Woreda", df2["Woreda"].unique())
if not woreda:
    df3 = df2.copy()
else:
    df3 = df2[df2["Woreda"].isin(woreda)]

# Kebele
kebele = st.sidebar.multiselect("kebele", df3["Kebele"].unique())

# Filter by location

if not region and not woreda and not kebele:
    filtered_df = df
elif not woreda and not kebele:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not kebele:
    filtered_df = df[df["Woreda"].isin(woreda)]
elif woreda and kebele:
    filtered_df = df3[df["Woreda"].isin(woreda) & df3["Kebele"].isin(kebele)]
elif region and kebele:
    filtered_df = df3[df["Region"].isin(region) & df3["Kebele"].isin(kebele)]
elif region and woreda:
    filtered_df = df3[df["Region"].isin(region) & df3["Woreda"].isin(woreda)]
elif kebele:
    filtered_df = df3[df3["Kebele"].isin(kebele)]
else:
    filtered_df = df3[
        df3["Region"].isin(region)
        & df3["Woreda"].isin(woreda)
        & df3["Kebele"].isin(kebele)
    ]

# -----------------------------------------------------------------------------------#
woreda_exp_dic = {
    "Bita": 240,
    "East Demibia": 240,
    "Ejere": 240,
    "Enarji Enawuga": 280,
    "Estie": 280,
    "Geta": 240,
    "Gewata": 240,
    "Gimbo": 240,
    "Ginir": 280,
    "Gondar Zuriya": 280,
    "Kersa Malima": 240,
    "Minjar Shenkora": 240,
    "Omo Beyam": 240,
    "Yilmana Densa": 240,
}
category_df = filtered_df.groupby(by=["Woreda"], as_index=False)["COLLECTED"].sum()

category_df["EXPECTED"] = category_df["Woreda"].map(woreda_exp_dic)


# print(category_df)
with col1:
    st.subheader("Interviews by woreda")
    plost.bar_chart(
        data=category_df,
        bar="Woreda",
        value=["COLLECTED", "EXPECTED"],
        group=True,
        width=75,
    )


with col2:
    st.subheader("Interview by sample type")
    fig = px.pie(filtered_df, values="COLLECTED", names="ID0", hole=0.5)
    fig.update_traces(text=filtered_df["Region"], textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

filtered_df["Day"] = filtered_df["ID15"].dt.to_period("D")
linechart = pd.DataFrame(
    filtered_df.groupby(filtered_df["Day"].dt.strftime("%D : %b"))["COLLECTED"].sum()
).reset_index()

col3, col4 = st.columns((2))
with col3:
    st.subheader("Daily Progress")
    fig2 = px.line(
        linechart,
        x="Day",
        y="COLLECTED",
        # labels={"Sales": "Amount"},
        # height=500,
        # width=500,
        template="gridon",
    )
    st.plotly_chart(fig2, use_container_width=True)

with col4:
    payout_df = filtered_df.groupby(by=["Supervisor"], as_index=False)["Payout"].mean()
    st.subheader("Average Payout by Team")
    fig = px.bar(
        payout_df,
        x="Supervisor",
        y="Payout",
        text=["{:,.0f}".format(x) for x in payout_df["Payout"]],
        template="seaborn",
    )
    st.plotly_chart(fig, use_container_width=True)
