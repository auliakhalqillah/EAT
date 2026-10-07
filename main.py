import streamlit as st

# Konfigurasi Tampilan Halaman Utama
st.set_page_config(
    page_title="Seismic & Geophysics Toolbox",
    page_icon="🌋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# DEFINISI HALAMAN
# ==========================================

def home_page():
    # Banner / Hero Section
    st.title("🌋 Geophysics & Seismic Analysis Portal")
    st.caption("Platform terpadu untuk analisis sinyal seismik, pengolahan data ground motion, dan geofisika.")
    
    st.markdown("---")

    # Section Card / Informasi Fitur
    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.subheader("📈 Ground Motion Analysis Tools (GMAT)")
            st.write(
                "Toolbox interaktif untuk mengolah dan menganalisis sinyal getaran tanah (Ground Motion). "
                "Fitur mencakup analisis riwayat waktu (*Time-History*), perhitungan *Peak Ground Acceleration* (PGA), "
                "serta *Fast Fourier Transform* (FFT) spektrum frekuensi dominan."
            )
            
            # Tombol navigasi langsung ke gma_app
            if st.button("Buka GMAT Toolbox ➔", type="primary", key="btn_gma"):
                st.switch_page(gma_page)

    with col2:
        with st.container(border=True):
            st.subheader("🔬 Module Lainnya (Segera Hadir)")
            st.write(
                "Modul tambahan seperti *Response Spectrum Analysis*, *Seismic Hazard Analysis (PSHA/DSHA)*, "
                "dan *Filter Signal Processing* sedang dalam tahap pengembangan."
            )
            st.button("Segera Hadir", disabled=True, key="btn_future")

    st.markdown("---")

    # Informasi Tambahan / Panduan Singkat
    st.subheader("ℹ️ Petunjuk Penggunaan Portal")
    
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        st.markdown("#### 1. Pilih Tool")
        st.write("Gunakan menu navigasi di *sidebar* sebelah kiri atau tombol di atas untuk memilih aplikasi.")

    with col_info2:
        st.markdown("#### 2. Unggah Data")
        st.write("Siapkan file data seismik dalam format `.csv` atau `.xlsx` sesuai format standar yang ditentukan.")

    with col_info3:
        st.markdown("#### 3. Analisis & Ekspor")
        st.write("Jalankan pemrosesan sinyal dan unduh hasil rekapitulasi data (CSV) maupun grafik resolusi tinggi (PNG).")

# Deklarasi Halaman Navigasi
home = st.Page(home_page, title="Halaman Utama", icon="🏠", default=True)
gma_page = st.Page("gma_app.py", title="Ground Motion Analysis Tool (GMAT)", icon="📈")

# ==========================================
# SETUP NAVIGASI STREAMLIT
# ==========================================
pg = st.navigation(
    {
        "Menu Utama": [home],
        "Toolbox Seismik": [gma_page],
    }
)

# Menjalankan Navigasi
pg.run()