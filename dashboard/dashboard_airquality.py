import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import calendar

sns.set(style="whitegrid")
PRIMARY = "#4C72B0"
SECONDARY = "#DD8452"

url = "https://raw.githubusercontent.com/Renaylaa/Proyek-Analisis-Data/refs/heads/main/dashboard/all_data.csv"
df = pd.read_csv(url)

df["datetime"] = pd.to_datetime(df[["year","month","day","hour"]])
df.sort_values("datetime", inplace=True)

st.sidebar.title("Filter Data")

min_date = df["datetime"].min()
max_date = df["datetime"].max()

start_date, end_date = st.sidebar.date_input(
    "Pilih Rentang Waktu",
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

main_df = df[(df["datetime"] >= str(start_date)) &
             (df["datetime"] <= str(end_date))]

stations = ["Aotizhongxin", "Changping"]
df_filtered = main_df[main_df["station"].isin(stations)].copy()

def create_monthly_station(df):
    monthly = df.groupby(["station","month"])["PM2.5"].mean().reset_index()

    monthly["Bulan"] = monthly["month"].apply(lambda x: calendar.month_name[x])

    order = ["January","February","March","April","May","June",
             "July","August","September","October","November","December"]

    monthly["Bulan"] = pd.Categorical(monthly["Bulan"], categories=order, ordered=True)

    return monthly.sort_values("Bulan")


def get_season(month):
    if month in [12,1,2]:
        return "Winter"
    elif month in [3,4,5]:
        return "Spring"
    elif month in [6,7,8]:
        return "Summer"
    else:
        return "Autumn"

df_filtered["season"] = df_filtered["month"].apply(get_season)

monthly_df = create_monthly_station(df_filtered)
season_df = df_filtered.groupby(["station","season"])["PM2.5"].mean().reset_index()

st.title("Air Quality Dashboard :sparkles:")
st.caption("Fokus Analisis: Aotizhongxin vs Changping (2013–2017)")

st.header("Tren Bulanan PM2.5")

st.write("Bagaimana tren perubahan konsentrasi PM2.5 bulanan di wilayah Aotizhongxin dan Changping?")

fig, ax = plt.subplots(figsize=(12,5))

sns.lineplot(
    data=monthly_df,
    x="Bulan",
    y="PM2.5",
    hue="station",
    marker="o",
    palette=[PRIMARY, SECONDARY],
    ax=ax
)

plt.xticks(rotation=45)
ax.set_title("Perbandingan Tren Bulanan PM2.5")
st.pyplot(fig)


worst_month = monthly_df.groupby("Bulan")["PM2.5"].mean().idxmax()
st.info(f" Secara umum, PM2.5 tertinggi terjadi pada bulan **{worst_month}**.")

st.header("Analisis Berdasarkan Musim")

st.write("Bagaimana perbedaan rata-rata konsentrasi PM2.5 berdasarkan musim?")

fig, ax = plt.subplots(figsize=(10,5))

sns.barplot(
    data=season_df,
    x="season",
    y="PM2.5",
    hue="station",
    palette=[PRIMARY, SECONDARY],
    ax=ax
)

ax.set_title("Perbandingan PM2.5 Berdasarkan Musim")
st.pyplot(fig)

worst_season = season_df.groupby("season")["PM2.5"].mean().idxmax()
st.warning(f"Musim dengan polusi tertinggi adalah **{worst_season}**.")

st.header("Ringkasan")

col1, col2 = st.columns(2)

aot_avg = df_filtered[df_filtered["station"]=="Aotizhongxin"]["PM2.5"].mean()
cha_avg = df_filtered[df_filtered["station"]=="Changping"]["PM2.5"].mean()

col1.metric("Rata-rata PM2.5 Aotizhongxin", round(aot_avg,2))
col2.metric("Rata-rata PM2.5 Changping", round(cha_avg,2))


#edef


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

daily_pollution_df = create_daily_pollution_df(main_df)
pollution_df = create_pollution_comparison_df(main_df)
weather_df = create_weather_relation_df(main_df)

station_df = create_station_pm25(main_df)
monthly_df = create_monthly_trend(main_df)


st.header("Perbandingan PM2.5 antar Stasiun")

fig, ax = plt.subplots(figsize=(10,5))

colors = ["#4C72B0" if i != 0 else "#DD8452" for i in range(len(station_df))]

sns.barplot(
    x="PM2.5",
    y="station",
    data=station_df,
    palette=colors,
    ax=ax
)
st.pyplot(fig)

st.write(f" Stasiun dengan PM2.5 tertinggi: **{station_df.iloc[0]['station']}**")
st.write(f" Stasiun dengan PM2.5 terendah: **{station_df.iloc[-1]['station']}**")


st.header("Tren Harian PM2.5")

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
    linewidth=2,
    color="#4C72B0"
)
ax.set_xlabel("Date")
ax.set_ylabel("PM2.5")

st.pyplot(fig)

st.header("Perbandingan Polusi")

fig, ax = plt.subplots(figsize=(12,7))

colors = ["#DD8452" if i == 0 else "#4C72B0" for i in range(len(pollution_df))]

sns.barplot(
    x="Average Value",
    y="Pollutant",
    data=pollution_df,
    palette=colors,
    ax=ax
)

st.pyplot(fig)

st.header("PM2.5 Berdasarkan Arah Angin")

fig, ax = plt.subplots(figsize=(12,7))

sns.barplot(
    x="Wind Direction",
    y="Avg_PM25",
    data=weather_df,
    color="#4C72B0",
    ax=ax
)

st.pyplot(fig)

st.header("Korelasi Antar Variabel")

numeric_df = main_df.select_dtypes(include=['float64','int64'])

fig, ax = plt.subplots(figsize=(10,6))

sns.heatmap(
    numeric_df.corr(),
    cmap="Blues",
    ax=ax
)

st.pyplot(fig)

st.caption('Copyright © 2026 Air Quality Analysis')