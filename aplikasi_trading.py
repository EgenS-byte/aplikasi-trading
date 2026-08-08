import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st

st.title("⏱️ Analisis Trader Harian — Interval 30 Menit")
st.caption("⚠️ Data tertunda ±15–20 menit | Gunakan kode berakhiran .JK (contoh: BBRI.JK)")

# Input kode saham
ticker = st.text_input("Masukkan Kode Saham:", "BBRI.JK")
st.info("⚙️ Pengaturan: Interval 30 menit | Data 30 hari ke belakang | Indikator: SMA10, MACD, Volume")

if st.button("🚀 AMBIL DATA & ANALISIS"):
    # === AMBIL DATA: 30 HARI, INTERVAL 30 MENIT ===
    # 30 hari = ±240 batang → SANGAT CUKUP untuk MACD lengkap
    data = yf.download(ticker, period="30d", interval="30m", progress=False)
    
    # === PERBAIKAN STRUKTUR KOLOM ===
    # Hapus nama saham dari judul kolom agar mudah dipakai
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)
    
    # === TAMPILKAN DATA MENTAH DULU ===
    st.subheader("📋 Data Mentah dari Yahoo Finance")
    if data.empty:
        st.error("❌ Data KOSONG! Periksa:")
        st.write("• Apakah kode berakhiran .JK? (contoh: BBRI.JK)")
        st.write("• Apakah saham tersebut ada di Yahoo Finance?")
    else:
        st.success(f"✅ BERHASIL! Diterima {len(data)} batang data (30 menit/batang)")
        st.dataframe(data)  # TAMPILKAN SEMUA DATA
        
        # === LANJUTKAN HANYA JIKA DATA CUKUP ===
        if len(data) < 40:
            st.warning(f"⚠️ Data masih kurang ({len(data)} batang), sinyal mungkin belum lengkap")
        else:
            # === 1. Harga Rata-rata (SMA10 = ±5 hari) ===
            data['SMA10'] = data['Close'].rolling(window=10).mean()
            
            # === 2. MACD Standar (12, 26, 9) ===
            data['EMA12'] = data['Close'].ewm(span=12, adjust=False).mean()
            data['EMA26'] = data['Close'].ewm(span=26, adjust=False).mean()
            data['MACD'] = data['EMA12'] - data['EMA26']
            data['Sinyal'] = data['MACD'].ewm(span=9, adjust=False).mean()
            
            # === 3. Volume Rata-rata ===
            data['Vol_Rata'] = data['Volume'].rolling(window=10).mean()

            # Hapus baris yang belum lengkap datanya
            data_valid = data.dropna(subset=['SMA10', 'MACD', 'Vol_Rata'])
            
            if len(data_valid) < 3:
                st.warning("⚠️ Belum cukup data lengkap untuk analisis sinyal")
            else:
                # Ambil 3 batang terakhir
                terakhir = data_valid.iloc[-1]
                sebelumnya = data_valid.iloc[-2]
                tiga_batang_lalu = data_valid.iloc[-3]

                harga = terakhir['Close'].item()
                sma = terakhir['SMA10'].item()
                macd = terakhir['MACD'].item()
                sinyal = terakhir['Sinyal'].item()
                vol = terakhir['Volume'].item()
                vol_rata = terakhir['Vol_Rata'].item()

                # === Ringkasan 3 batang terakhir ===
                st.subheader("📊 3 Batang Terakhir")
                ringkas = pd.DataFrame({
                    'Waktu': [str(tiga_batang_lalu.name)[:16], 
                              str(sebelumnya.name)[:16], 
                              str(terakhir.name)[:16]],
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
                }, index=['-2', '-1', '🔴 SEKARANG'])
                st.table(ringkas)

                # === Analisis Sinyal ===
                st.subheader("🎯 Kondisi Indikator")
                poin = []
                poin.append("✅ Harga DI ATAS rata-rata (Uptrend)" if harga > sma 
                           else "❌ Harga DI BAWAH rata-rata (Downtrend)")
                poin.append("✅ MACD DI ATAS garis sinyal (Beli)" if macd > sinyal 
                           else "❌ MACD DI BAWAH garis sinyal (Tahan/Jual)")
                poin.append("✅ Volume membesar di atas rata-rata" if vol > vol_rata * 1.1 
                           else "⚠️ Volume biasa/kecil")

                for p in poin:
                    st.write(p)

                # === Keputusan ===
                skor = sum(1 for p in poin if "✅" in p)
                macd_naik = macd > sebelumnya['MACD'].item() > tiga_batang_lalu['MACD'].item()

                st.subheader("🔔 Saran Keputusan")
                if skor >= 2 and macd_naik:
                    st.success("🟢 BELI — Semua searah naik & terkonfirmasi")
                elif skor >= 2:
                    st.warning("🟡 LIHAT DULU — Kondisi baik, tunggu konfirmasi MACD naik")
                elif skor == 1:
                    st.info("⚪ NETRAL — Belum ada sinyal kuat")
                else:
                    st.error("🔴 JANGAN BELI — Mayoritas lemah")

                # === Grafik ===
                st.subheader("📈 Grafik Harga & SMA10")
                st.line_chart(data_valid[['Close', 'SMA10']])
                st.subheader("📊 Grafik MACD & Sinyal")
                st.line_chart(data_valid[['MACD', 'Sinyal']])
