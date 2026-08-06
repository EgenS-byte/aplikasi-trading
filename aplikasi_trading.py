import pandas as pd
import streamlit as st

def ema(seri, periode):
    return seri.ewm(span=periode, adjust=False).mean()

def macd(seri):
    garis = ema(seri, 12) - ema(seri, 26)
    sinyal = ema(garis, 9)
    return garis, sinyal

def rsi(seri, periode=14):
    ubah = seri.diff(1)
    naik = ubah.where(ubah > 0, 0)
    turun = -ubah.where(ubah < 0, 0)
    rs = naik.rolling(periode).mean() / turun.rolling(periode).mean()
    return 100 - (100 / (1 + rs))

def atr(data, periode=14):
    t = data['Tertinggi']
    r = data['Terendah']
    tutup = data['Tutup']
    r1 = t - r
    r2 = abs(t - tutup.shift(1))
    r3 = abs(r - tutup.shift(1))
    tr = pd.concat([r1, r2, r3], axis=1).max(axis=1)
    return tr.rolling(periode).mean()

st.set_page_config(page_title="Sinyal Trading Harian", page_icon="📈", layout="wide")
st.title("📊 SISTEM KEPUTUSAN TRADING — VERSI HARIAN")
st.markdown("---")

file_unggah = st.file_uploader("📂 Unggah File CSV (Investing.com / Yahoo Finance)", type="csv")

if file_unggah:
    data = pd.read_csv(file_unggah)

    kolom = {
        'Tanggal':'Tanggal', 'Date':'Tanggal',
        'Terakhir':'Tutup', 'Harga':'Tutup', 'Close':'Tutup',
        'Pembukaan':'Buka', 'Open':'Buka',
        'Tertinggi':'Tertinggi', 'High':'Tertinggi',
        'Terendah':'Terendah', 'Low':'Terendah',
        'Vol.':'Volume', 'Volume':'Volume'
    }
    for lama, baru in kolom.items():
        if lama in data.columns:
            data[baru] = data[lama]

    def bersihkan_angka(x):
        if isinstance(x, str):
            return float(x.replace('%','').replace(',','.'))
        return float(x)

    data['Tutup'] = data['Tutup'].apply(bersihkan_angka)
    data['Tertinggi'] = data['Tertinggi'].apply(bersihkan_angka)
    data['Terendah'] = data['Terendah'].apply(bersihkan_angka)

    data = data.sort_values('Tanggal').reset_index(drop=True)

    e12 = ema(data['Tutup'], 12)
    e26 = ema(data['Tutup'], 26)
    garis_macd, garis_sinyal = macd(data['Tutup'])
    nilai_rsi = rsi(data['Tutup'])
    atr_val = atr(data).iloc[-1]

    harga = round(data['Tutup'].iloc[-1], 2)
    tren = "NAIK" if e12.iloc[-1] > e26.iloc[-1] else "TURUN"
    arah_macd = "NAIK" if garis_macd.iloc[-1] > garis_sinyal.iloc[-1] else "TURUN"
    rsi_terakhir = round(nilai_rsi.iloc[-1], 1)

    stop_loss = round(harga - (atr_val * 1.5), 2)
    target_profit = round(harga + (atr_val * 3), 2)
    risiko = round(harga - stop_loss, 2)
    untung = round(target_profit - harga, 2)
    rasio = round(untung/risiko, 1) if risiko != 0 else 0

    st.markdown("---")
    st.subheader(f"💵 Harga Terakhir: {harga:,}")
    st.info(f"📊 Tren: **{tren}** | MACD: **{arah_macd}** | RSI: **{rsi_terakhir}**")
    st.markdown("---")

    if tren == "NAIK" and arah_macd == "NAIK" and 30 < rsi_terakhir < 70:
        st.success("### 🟢🟢🟢  BELI — Tren Naik & Momentum Positif")
        col1, col2, col3 = st.columns(3)
        col1.metric("🔴 Stop Loss", f"{stop_loss:,}", f"-{risiko:,}")
        col2.metric("🟢 Target Profit", f"{target_profit:,}", f"+{untung:,}")
        col3.metric("⚖️ Risiko:Untung", f"1 : {rasio}")
    elif tren == "TURUN" and arah_macd == "TURUN":
        st.error("### 🔴🔴🔴  JANGAN BELI — Tren Sedang Turun")
    else:
        st.warning("### 🟡🟡🟡  TAHAN — Tunggu Konfirmasi Lebih Jelas")

    st.markdown("---")
    st.caption("✅ Data dari Investing.com / Yahoo Finance | SL & TP = ATR × 1.5 / × 3")

else:
    st.info("👆 Unduh CSV dari Investing.com → Data Historis → 3 Bulan → Unduh Data → Unggah di sini")
