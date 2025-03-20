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
file_path = "main_data.csv"
df = pd.read_csv(file_path)

# Konversi tanggal dan waktu
df["date"] = pd.to_datetime(df[["year", "month", "day"]])
df["hour"] = df["hour"].astype(int)

# Judul utama
st.title("📊 Air Quality Dashboard")
st.subheader(f"Beijing 2013-2017")

# **Tren Kualitas Udara Tiap Tahun**
st.header("Kualitas Udara Berdasarkan PM2.5")

# Fungsi untuk mengkategorikan kualitas udara
def categorize_pm25(pm25):
    if pm25 <= 15.5:
        return "Baik"
    elif 15.6 <= pm25 <= 55.4:
        return "Sedang"
    elif 55.5 <= pm25 <= 150.4:
        return "Tidak Sehat"
    elif 150.5 <= pm25 <= 250.4:
        return "Sangat Tidak Sehat"
    else:
        return "Berbahaya"

df["air_quality_category"] = df["PM2.5"].apply(categorize_pm25)

col1, col2 = st.columns(2)  # Membagi tampilan menjadi dua kolom

#Tabel Keterangan Pembagian Kualitas Udara
with col1:
    st.subheader("Kategori Kualitas Udara")
    st.markdown("""
    | PM2.5 (µg/m³) | Kategori |
    |--------------|----------|
    | 0 - 15.5    | Baik |
    | 15.6 - 55.4  | Sedang |
    | 55.5 - 150.4 | Tidak Sehat |
    | 150.5 - 250.4 | Sangat Tidak Sehat |
    | > 250.5      | Berbahaya |
    """)
    
#1. Tabel Distribusi Kualitas Udara per Wilayah 
with col2:
    st.subheader("Distribusi Kualitas Udara per Wilayah")
    region_quality_df = df.groupby(["station", "air_quality_category"]).size().reset_index(name="count")
    st.dataframe(region_quality_df)

#Line Plot Tren Rata-Rata Tiap Parameter per Tahun dan Wilayah
st.subheader("Tren Kualitas Udara per Tahun dan Wilayah")

# Pilihan wilayah
regions = df["station"].unique()
selected_region = st.selectbox("Pilih Wilayah", regions)

# Filter data berdasarkan wilayah yang dipilih
df_region = df[df["station"] == selected_region]

# Agregasi data: menghitung rata-rata per tahun untuk tiap parameter
df_trend = df_region.groupby("year")[["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"]].mean().reset_index()

# Plot
fig, ax = plt.subplots(figsize=(10, 5))
for column in ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"]:
    ax.plot(df_trend["year"], df_trend[column], marker='o', label=column)

ax.set_xlabel("Tahun")
ax.set_ylabel("Konsentrasi Polutan")
ax.set_title(f"Tren Polutan Udara di {selected_region}")
ax.legend()
st.pyplot(fig)

# 2. Hubungan Kondisi Cuaca dengan Polusi**
st.subheader("🌦️ Korelasi antara Kondisi Cuaca dan Tingkat Polusi")
weather_factors = ["PM2.5", "TEMP", "PRES", "DEWP", "RAIN"]
df_corr = df[weather_factors].corr()
fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(df_corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
ax.set_title("Heatmap Korelasi PM2.5 dengan Faktor Cuaca", fontsize=14)
st.pyplot(fig)

st.info("💡 note: nilai yang mendekati 0 berarti tidak memiliki korelasi, sedangkan nilai yang mendekati angka 1 berarti memiliki korelasi.")


#3. Perbandingan Kualitas Udara antar Wilayah
st.subheader("🌍 Perbedaan Tingkat Polusi antara Wilayah")
pollutants = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"]
df_region_avg = df.groupby("station")[pollutants].mean().reset_index()
st.dataframe(df_region_avg.style.format("{:.2f}"))

# Visualisasi Bar Plot
fig, ax = plt.subplots(figsize=(10, 6))
df_region_avg.set_index("region")[pollutants].plot(kind="bar", ax=ax, colormap="viridis")
ax.set_title("Rata-rata Polutan per Wilayah", fontsize=14)
ax.set_ylabel("Konsentrasi Polutan (µg/m³)")
ax.set_xlabel("Wilayah")
plt.xticks(rotation=45)
st.pyplot(fig)

# 4. Jam dengan Kualitas Udara Terburuk**
st.subheader("⏰ Jam dengan Kualitas Udara Paling Buruk")
df_hourly = df.groupby(["hour", "station"])["PM2.5"].mean().reset_index()

# Plot data
fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(data=df_hourly, x="hour", y="PM2.5", hue="region", marker="o", ax=ax)
ax.set_title("Rata-rata PM2.5 Berdasarkan Jam untuk Setiap Wilayah", fontsize=14)
ax.set_ylabel("PM2.5 (µg/m³)")
ax.set_xlabel("Jam")
ax.legend(title="Wilayah")
st.pyplot(fig)

# Footer
st.caption("📌 Data diambil dari PRSA Dataset Air Quality | Dashboard dibuat oleh Radya Ardi")
