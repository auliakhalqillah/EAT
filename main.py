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
    st.title("🌋 EATbox: Earthquake Analysis Toolbox")
    st.caption("An integrated platform for earthquake ground motion data processing")
    
    st.markdown("---")

    # Section Card / Informasi Fitur
    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.subheader("📈 Ground Motion Analysis Tools (GMAT)")
            st.write(
                "An interactive toolbox for processing and analyzing ground motion signals. "
                "Features include time-history analysis and calculations of Peak Ground Amplitude (PGA, PGV, PGD), "
                "as well as the implementation of the Fast Fourier Transform (FFT) to estimate the dominant frequency."
            )
            
            # Tombol navigasi langsung ke gma_app
            if st.button("Open GMAT Toolbox ➔", type="primary", key="btn_gma"):
                st.switch_page(gma_page)

        with st.container(border=True):
            st.subheader("📈 Motion Capture Analysis Tools (MCAT)")
            st.write(
                "An interactive toolbox for processing and analyzing the displacement motion data from motion capture instrument. "
                "Conduct the baseline correction to get the proper displacement data"
            )
            
            # Tombol navigasi langsung ke gma_app
            if st.button("Open MCAT Toolbox ➔", type="primary", key="btn_mca"):
                st.switch_page(mca_page)

    with col2:
        with st.container(border=True):
            st.subheader("🔬 Other Modules (Coming Soon)")
            st.write(
                """
                Additional modules such as *Response Spectrum Analysis*, *Probabilistic and Rates Calculation*, and
                *Filter Signal Processing* are currently under development.
                """
            )
            # st.button("Segera Hadir", disabled=True, key="btn_future")

    st.markdown("---")

    # Informasi Tambahan / Panduan Singkat
    st.subheader("ℹ️ How to Use")
    
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        st.markdown("#### 1. Select the Tool")
        st.write("Use the navigation menu in the left sidebar or the buttons at the top to select an application.")

    with col_info2:
        st.markdown("#### 2. Import the Data")
        st.write("Prepare the seismic data file in `.csv` or `.xlsx` format, in accordance with the specified standard format.")

    with col_info3:
        st.markdown("#### 3. Analysis and Export")
        st.write("Perform signal processing and download the data recapitulation results as well as high-resolution graphs.")

    st.markdown("---")

    # Contact Information
    st.subheader("ℹ️ More Information")
    st.caption("email: auliakhalqillah@usk.ac.id or auliakhalqillah.mail@gmail.com")

# Deklarasi Halaman Navigasi
home = st.Page(home_page, title="Home Page", icon="🏠", default=True)
gma_page = st.Page("gma_app.py", title="Ground Motion Analysis Tool (GMAT)", icon="📈")
mca_page = st.Page("mca_app.py", title="Motion Capture Analysis Tool (MCAT)", icon="\U0001F4F7")

# ==========================================
# SETUP NAVIGASI STREAMLIT
# ==========================================
pg = st.navigation(
    {
        "Main Page": [home],
        "Toolbox": [gma_page, mca_page],
    }
)

# Menjalankan Navigasi
pg.run()