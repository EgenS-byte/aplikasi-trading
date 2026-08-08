import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st

st.title("⏱️ Analisis Trader Harian — Interval 30 Menit")
st.caption("⚠️ Data tertunda ±15–20 menit → untuk konfirmasi tren, bukan keputusan detik-ke-detik")

# Input kode saham
ticker = st.text_input("Masukkan Kode Saham (tambah .JK → contoh: BBRI.JK):", "BBRI.JK")
st.info("⚙️ Pengaturan: Interval 30 menit | Data 7 hari perdagangan | Indikator: SMA8, MACD, Volume")

if st.button("🚀 ANALISIS SEKARANG"):
    # === Ambil data: Interval 30 menit, ambil 7 hari agar cukup batang ===
    data = yf.download(ticker, period="7d", interval="30m")
    
    # Sederhanakan nama kolom
    data.columns = data.columns.droplevel(1)
    
    if data.empty:
        st.error("❌ Data tidak ditemukan! Pastikan kode saham berakhiran .JK")
    else:
        st.success(f"✅ {len(data)} batang data berhasil diterima")
        
        # === 1. Harga Rata-rata (SMA8 ≈ 2 hari perdagangan) ===
        data['SMA8'] = data['Close'].rolling(window=8).mean()
        
        # === 2. MACD Standar (12, 26, 9) ===
        data['EMA12'] = data['Close'].ewm(span=12, adjust=False).mean()
        data['EMA26'] = data['Close'].ewm(span=26, adjust=False).mean()
        data['MACD'] = data['EMA12'] - data['EMA26']
        data['Sinyal'] = data['MACD'].ewm(span=9, adjust=False).mean()
        
        # === 3. Analisis Volume ===
        data['Vol_Rata'] = data['Volume'].rolling(window=8).mean()

        # Hapus baris yang datanya belum lengkap
        data_valid = data.dropna(subset=['SMA8', 'MACD', 'Vol_Rata'])
        
        if len(data_valid) < 3:
            st.warning("⚠️ Masih menunggu cukup data untuk perhitungan lengkap...")
        else:
            # Ambil 3 batang terakhir untuk melihat tren
            terakhir = data_valid.iloc[-1]
            sebelumnya = data_valid.iloc[-2]
            tiga_batang_lalu = data_valid.iloc[-3]

            # Konversi ke angka murni
            harga = terakhir['Close'].item()
            sma = terakhir['SMA8'].item()
            macd = terakhir['MACD'].item()
            sinyal = terakhir['Sinyal'].item()
            vol = terakhir['Volume'].item()
            vol_rata = terakhir['Vol_Rata'].item()

            # === Tampilkan ringkasan 3 batang terakhir ===
            st.subheader("📊 3 Batang Terakhir — Lihat Arah Pergerakan")
            ringkas = pd.DataFrame({
                'Harga': [round(tiga_batang_lalu['Close'].item(), 2),
                          round(sebelumnya['Close'].item(), 2),
                          round(harga, 2)],
                'MACD': [round(tiga_batang_lalu['MACD'].item(), 3),
                         round(sebelumnya['MACD'].item(), 3),
                         round(macd, 3)],
                'Garis Sinyal': [round(tiga_batang_lalu['Sinyal'].item(), 3),
                                 round(sebelumnya['Sinyal'].item(), 3),
                                 round(sinyal, 3)],
                'Volume': [int(tiga_batang_lalu['Volume'].item()),
                           int(sebelumnya['Volume'].item()),
                           int(vol)]
            }, index=['-2 Batang', '-1 Batang', '🔴 SEKARANG'])
            st.table(ringkas)

            # === Analisis Sinyal Saat Ini ===
            st.subheader("🎯 Kondisi Indikator Saat Ini")
            poin = []
            poin.append("✅ Harga DI ATAS garis rata-rata (Uptrend)" if harga > sma else "❌ Harga DI BAWAH garis rata-rata (Downtrend)")
            poin.append("✅ MACD DI ATAS garis sinyal (Potensi Beli)" if macd > sinyal else "❌ MACD DI BAWAH garis sinyal (Tahan/Jual)")
            poin.append("✅ Volume membesar di atas rata-rata" if vol > vol_rata * 1.1 else "⚠️ Volume biasa / di bawah rata-rata")

            for p in poin:
                st.write(p)

            # === Aturan Keputusan dengan Konfirmasi ===
            skor = sum(1 for p in poin if "✅" in p)
            macd_naik = macd > sebelumnya['MACD'].item() > tiga_batang_lalu['MACD'].item()

            st.subheader("🔔 Saran Keputusan")
            if skor >= 2 and macd_naik:
                st.success("🟢 BELI — Semua indikator searah naik & sudah terkonfirmasi 2 batang berturut-turut")
            elif skor >= 2:
                st.warning("🟡 LIHAT DULU — Kondisi mendukung, namun belum ada konfirmasi kenaikan MACD")
            elif skor == 1:
                st.info("⚪ NETRAL — Belum ada sinyal yang cukup kuat")
            else:
                st.error("🔴 JANGAN BELI — Mayoritas indikator masih lemah")

            # === Tampilkan Grafik ===
            st.subheader("📈 Grafik Harga & Rata-rata")
            st.line_chart(data_valid[['Close', 'SMA8']])

            st.subheader("📊 Grafik MACD & Garis Sinyal")
            st.line_chart(data_valid[['MACD', 'Sinyal']])
