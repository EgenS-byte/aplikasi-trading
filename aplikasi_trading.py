import streamlit as st
import pandas as pd
import numpy as np

# Judul Aplikasi
st.title("✅ UJI COBA APLIKASI — Jalan dengan Baik!")
st.write("Jika tulisan ini muncul, berarti aplikasi berjalan lancar ✅")

# --- 1. CONTOH DATA SENDIRI ---
st.subheader("📊 Contoh Data")
data = {
    "Bulan": ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun"],
    "Penjualan": [120, 150, 180, 160, 210, 240],
    "Pengeluaran": [80, 90, 100, 110, 95, 120]
}
df = pd.DataFrame(data)
st.dataframe(df)  # Tampilkan tabel

# --- 2. GRAFIK SEDERHANA ---
st.subheader("📈 Grafik Penjualan vs Pengeluaran")
st.line_chart(df, x="Bulan", y=["Penjualan", "Pengeluaran"])

# --- 3. Teks Konfirmasi ---
st.success("🎉 Selamat! Semua komponen berjalan dengan sempurna!")
st.write("Jika Anda bisa melihat tulisan ini beserta tabel dan grafik di atas, berarti:")
st.write("✅ Python berjalan")
st.write("✅ Pustaka pandas & numpy terpasang")
st.write("✅ Streamlit berfungsi dengan baik")
