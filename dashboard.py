import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import subprocess

# Cek apakah matplotlib sudah terinstall, jika tidak maka install dulu
try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    subprocess.check_call(["pip", "install", "matplotlib"])
    import matplotlib.pyplot as plt

# Konfigurasi tema
st.set_page_config(
    page_title="Air Quality Dashboard",
    layout="wide"
)
sns.set(style='dark')

# Menambahkan background
background_style = """
    <style>
        .stApp {
            background: linear-gradient(to bottom, #191d26, #000000);
            color: white;
        }
    </style>
"""
st.markdown(background_style, unsafe_allow_html=True)

# Load dataset
file_path = "main_data.csv"  # Sesuaikan dengan file dataset
df = pd.read_csv(file_path)

# Konversi tanggal dan waktu
df["date"] = pd.to_datetime(df[["year", "month", "day"]])
df["hour"] = df["hour"].astype(int)

# Sidebar untuk filter
st.sidebar.header("Filter Data")
selected_location = st.sidebar.selectbox("Pilih Wilayah", df["station"].unique())
start_year, end_year = st.sidebar.slider("Pilih Rentang Tahun", int(df["year"].min()), int(df["year"].max()), (2013, 2017))

# Filter dataset
df_filtered = df[(df["station"] == selected_location) & (df["year"].between(start_year, end_year))]

# Judul utama
st.title("📊 Air Quality Dashboard")
st.subheader(f"Wilayah: {selected_location} ({start_year} - {end_year})")

# 1️⃣ **Tren Kualitas Udara Tiap Tahun**
st.subheader("📈 Tren Kualitas Udara")
fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(x="date", y="PM2.5", data=df_filtered, ax=ax, color="red")
ax.set_title("Tren Polusi PM2.5 dari Tahun ke Tahun", fontsize=14)
ax.set_ylabel("Konsentrasi PM2.5 (µg/m³)")
ax.set_xlabel("Tanggal")
st.pyplot(fig)

# 2️⃣ **Hubungan Kondisi Cuaca dengan Polusi**
st.subheader("🌦️ Pengaruh Kondisi Cuaca terhadap Polusi")
fig, ax = plt.subplots(figsize=(12, 6))
sns.scatterplot(x="TEMP", y="PM2.5", data=df_filtered, ax=ax, alpha=0.5, color="blue")
ax.set_title("Hubungan Suhu dengan PM2.5", fontsize=14)
ax.set_ylabel("PM2.5 (µg/m³)")
ax.set_xlabel("Suhu (°C)")
st.pyplot(fig)

# 3️⃣ **Perbandingan Kualitas Udara antar Wilayah**
st.subheader("📊 Perbandingan Polusi antar Wilayah")
df_avg_pm25 = df.groupby("station")["PM2.5"].mean().reset_index()
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x="station", y="PM2.5", data=df_avg_pm25, ax=ax, palette="Reds")
ax.set_title("Rata-rata PM2.5 per Wilayah", fontsize=14)
ax.set_ylabel("Rata-rata PM2.5 (µg/m³)")
ax.set_xlabel("Wilayah")
st.pyplot(fig)

# 4️⃣ **Jam dengan Kualitas Udara Terburuk**
st.subheader("⏰ Jam dengan Polusi Tertinggi")
fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(x="hour", y="PM2.5", data=df_filtered.groupby("hour").mean().reset_index(), ax=ax, color="darkred")
ax.set_title("Rata-rata PM2.5 per Jam", fontsize=14)
ax.set_ylabel("PM2.5 (µg/m³)")
ax.set_xlabel("Jam")
st.pyplot(fig)

# Footer
st.caption("📌 Data diambil dari PRSA Dataset Air Quality | Dashboard dibuat oleh Radya Ardi")
