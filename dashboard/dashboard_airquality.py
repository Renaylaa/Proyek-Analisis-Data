import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import calendar

sns.set(style='dark')

def create_daily_pollution_df(df):
    daily_pollution_df = df.resample(rule='D', on='datetime').agg({
        "PM2.5": "mean"
    })
    
    daily_pollution_df = daily_pollution_df.reset_index()
    daily_pollution_df.rename(columns={
        "PM2.5": "avg_pm25"
    }, inplace=True)
    
    return daily_pollution_df


def create_pollution_comparison_df(df):
    pollution_cols = ["PM2.5","PM10","SO2","NO2","CO","O3"]
    pollution_df = df[pollution_cols].mean().sort_values(ascending=False).reset_index()
    pollution_df.columns = ["Pollutant","Average Value"]
    
    return pollution_df


def create_weather_relation_df(df):
    weather_df = df.groupby("wd")["PM2.5"].mean().reset_index()
    weather_df.rename(columns={
        "wd": "Wind Direction",
        "PM2.5": "Avg_PM25"
    }, inplace=True)
    
    return weather_df

def create_station_pm25(df):
    return df.groupby("station")["PM2.5"].mean().sort_values(ascending=False).reset_index()


def create_monthly_trend(df):
    monthly = df.groupby("month")["PM2.5"].mean().reset_index()
    monthly["Bulan"] = monthly["month"].apply(lambda x: calendar.month_name[x])
    
    order = ["January","February","March","April","May","June",
             "July","August","September","October","November","December"]
    
    monthly["Bulan"] = pd.Categorical(monthly["Bulan"], categories=order, ordered=True)
    monthly = monthly.sort_values("Bulan")
    
    return monthly

df = pd.read_csv("all_data.csv")

df["datetime"] = pd.to_datetime(df[["year","month","day","hour"]])
df.sort_values(by="datetime", inplace=True)

min_date = df["datetime"].min()
max_date = df["datetime"].max()

with st.sidebar:
    
    st.image("air_quality.webp")

    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = df[(df["datetime"] >= str(start_date)) &
             (df["datetime"] <= str(end_date))]


daily_pollution_df = create_daily_pollution_df(main_df)
pollution_df = create_pollution_comparison_df(main_df)
weather_df = create_weather_relation_df(main_df)

station_df = create_station_pm25(main_df)
monthly_df = create_monthly_trend(main_df)


st.header('Air Quality Dashboard :sparkles:')

st.subheader("Perbandingan PM2.5 antar Stasiun")

fig, ax = plt.subplots(figsize=(10,5))

sns.barplot(
    x="PM2.5",
    y="station",
    data=station_df,
    palette="Blues_r",
    ax=ax
)

st.pyplot(fig)

st.write(f"📌 Stasiun dengan PM2.5 tertinggi: **{station_df.iloc[0]['station']}**")
st.write(f"📌 Stasiun dengan PM2.5 terendah: **{station_df.iloc[-1]['station']}**")

st.subheader("Tren Bulanan PM2.5")

fig, ax = plt.subplots(figsize=(12,5))

sns.lineplot(
    data=monthly_df,
    x="Bulan",
    y="PM2.5",
    marker="o",
    ax=ax
)

plt.xticks(rotation=45)
st.pyplot(fig)

worst = monthly_df.sort_values(by="PM2.5", ascending=False).iloc[0]
best = monthly_df.sort_values(by="PM2.5", ascending=True).iloc[0]

st.write(f"📌 Bulan terburuk: **{worst['Bulan']}** ({round(worst['PM2.5'],2)})")
st.write(f"📌 Bulan terbaik: **{best['Bulan']}** ({round(best['PM2.5'],2)})")

st.subheader("Daily PM2.5 Trend")

col1, col2 = st.columns(2)

with col1:
    avg_pm25 = round(daily_pollution_df.avg_pm25.mean(),2)
    st.metric("Average PM2.5", avg_pm25)

with col2:
    max_pm25 = round(daily_pollution_df.avg_pm25.max(),2)
    st.metric("Max PM2.5", max_pm25)

fig, ax = plt.subplots(figsize=(16,8))

ax.plot(
    daily_pollution_df["datetime"],
    daily_pollution_df["avg_pm25"],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)

ax.set_xlabel("Date")
ax.set_ylabel("PM2.5")

st.pyplot(fig)

st.subheader("Pollutant Comparison")

fig, ax = plt.subplots(figsize=(12,7))

sns.barplot(
    x="Average Value",
    y="Pollutant",
    data=pollution_df,
    palette="Blues_r",
    ax=ax
)

st.pyplot(fig)

st.subheader("PM2.5 Based on Wind Direction")

fig, ax = plt.subplots(figsize=(12,7))

sns.barplot(
    x="Wind Direction",
    y="Avg_PM25",
    data=weather_df,
    palette="coolwarm",
    ax=ax
)

st.pyplot(fig)

st.subheader("Correlation Between Variables")

numeric_df = main_df.select_dtypes(include=['float64','int64'])

fig, ax = plt.subplots(figsize=(10,6))

sns.heatmap(
    numeric_df.corr(),
    annot=True,
    cmap="coolwarm",
    ax=ax
)

st.pyplot(fig)

st.caption('Copyright © 2026 Air Quality Analysis')