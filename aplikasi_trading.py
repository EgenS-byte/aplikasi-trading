import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st

# Judul Aplikasi
st.title("📈 Aplikasi Sinyal Trading (MACD, Volume & Harga Rata-rata)")

# Masukkan kode saham
ticker = st.text_input("Masukkan Kode Saham (contoh: BBRI.JK untuk Indonesia):", "BBRI.JK")
periode = st.selectbox("Pilih Periode Data", ["1mo", "3mo", "6mo", "1y"], index=2)

if st.button("Ambil Data & Analisis"):
    # Ambil data dari Yahoo Finance
    data = yf.download(ticker, period=periode)
    
    # === PERBAIKAN: Sederhanakan nama kolom agar mudah dipakai ===
    data.columns = data.columns.droplevel(1)  # Hapus nama saham dari judul kolom
    
    if data.empty:
        st.error("❌ Data tidak ditemukan! Periksa kode saham.")
    else:
        # Hitung Harga Rata-rata (Periode 20 hari)
        data['SMA20'] = data['Close'].rolling(window=20).mean()
        # Hitung MACD
        data['EMA12'] = data['Close'].ewm(span=12, adjust=False).mean()
        data['EMA26'] = data['Close'].ewm(span=26, adjust=False).mean()
        data['MACD'] = data['EMA12'] - data['EMA26']
        data['Sinyal'] = data['MACD'].ewm(span=9, adjust=False).mean()
        data['Histogram'] = data['MACD'] - data['Sinyal']

        # Tampilkan data terbaru
        st.subheader("📊 Data Terbaru")
        st.dataframe(data.tail(10))

        # Ambil nilai terakhir — .item() agar menjadi angka biasa
        terakhir = data.iloc[-1]
        harga = terakhir['Close'].item()
        sma20 = terakhir['SMA20'].item()
        macd = terakhir['MACD'].item()
        sinyal = terakhir['Sinyal'].item()
        vol = terakhir['Volume'].item()
        vol_rata = data['Volume'].rolling(20).mean().iloc[-1].item()

        # Saran Sinyal
        st.subheader("📌 Hasil Analisis Saat Ini")
        kondisi = []
        if harga > sma20:
            kondisi.append("✅ Harga > Rata-rata (Uptrend)")
        else:
            kondisi.append("❌ Harga < Rata-rata (Downtrend)")

        if macd > sinyal:
            kondisi.append("✅ MACD di Atas Garis Sinyal (Beli)")
        else:
            kondisi.append("❌ MACD di Bawah Garis Sinyal (Jual/Tahan)")

        if vol > vol_rata:
            kondisi.append("✅ Volume Tinggi (Minat Kuat)")
        else:
            kondisi.append("⚠️ Volume Biasa")

        for k in kondisi:
            st.write(k)

        # Kesimpulan
        st.subheader("🔔 Saran Trading")
        skor = sum(1 for k in kondisi if "✅" in k)
        if skor == 3:
            st.success("🟢 DISARANKAN BELI")
        elif skor >= 2:
            st.warning("🟡 TAHAN / Perhatikan Lebih Lanjut")
        else:
            st.error("🔴 DISARANKAN JANGAN BELI / Jual")

        # Tampilkan Grafik
        st.subheader("📉 Grafik Harga & Rata-rata")
        st.line_chart(data[['Close', 'SMA20']])

        st.subheader("📊 Grafik MACD")
        st.line_chart(data[['MACD', 'Sinyal']])
