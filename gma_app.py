import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import io

# Konfigurasi Halaman
# st.set_page_config(page_title="GMAT", layout="wide")

st.title("GMAT: Ground Motion Analysis Tools")

# ==========================================
# 1. PANEL INPUT DATA
# ==========================================
st.sidebar.header("1. Input Data")
uploaded_file = st.sidebar.file_uploader("Upload the Ground Motion Data (Excel/CSV)", type=['xlsx', 'xls', 'csv'])
st.sidebar.caption("Column 1 = time series, Column 2 = x-component (E-W), Column 3 = y-component (N-S), Column 4 = z-component (Z)")

st.sidebar.markdown("---")
st.sidebar.header("2. Analysis Option")
apply_fft = st.sidebar.button("Apply FFT")

# Warna default untuk plot
warna_list = ['brown', 'cyan', 'magenta']

# Default Parameters
height_figure = 500

# ==========================================
# PROSES UTAMA
# ==========================================
if uploaded_file is not None:
    try:
        # Membaca file input
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, sep=';')
        else:
            df = pd.read_excel(uploaded_file)

        # Standarisasi kolom (Dinamis)
        kolom_asli = df.columns.tolist()
        if len(kolom_asli) < 2:
            # st.error("Data harus memiliki minimal 2 kolom (1 kolom Waktu dan minimal 1 kolom Komponen).")
            st.error("Data should has at least 2 columns, the first column is time series and the second column is the ground motion amplitude of certain component.")
            st.stop()

        # Rename kolom pertama menjadi 'Waktu', sisanya menyesuaikan nama asli
        df.rename(columns={kolom_asli[0]: 'Time'}, inplace=True)
        komponen_list = df.columns[1:].tolist()

        # ==========================================
        # 3. PENGATURAN TAMPILAN (DINAMIS)
        # ==========================================
        st.sidebar.markdown("---")
        st.sidebar.header("3. Visualization")
        st.sidebar.write("Check for hiding the graph:")
        
        visible_comps = []
        warna_dict = {}
        
        # Checkbox sesuai jumlah komponen
        for i, comp in enumerate(komponen_list):
            is_hidden = st.sidebar.checkbox(f"Hiding {comp}", value=False)
            if not is_hidden:
                visible_comps.append(comp)
            warna_dict[comp] = warna_list[i % len(warna_list)]

        # ==========================================
        # KALKULASI PGA
        # ==========================================
        pga_results = []
        for comp in komponen_list:
            max_abs_idx = df[comp].abs().idxmax()
            pga_val = df.loc[max_abs_idx, comp]
            t_pga = df.loc[max_abs_idx, 'Time']
            
            pga_results.append({
                'Component': comp,
                'PGA (g)': round(abs(pga_val), 6),
                'Time PGA (s)': round(t_pga, 4),
                'Actual Value (g)': round(pga_val, 6)
            })

        st.write("### Peak Ground Acceleration (PGA)")
        df_pga = pd.DataFrame(pga_results)
        st.table(df_pga[['Component', 'PGA (g)', 'Time PGA (s)']])

        # ==========================================
        # PLOT GROUND MOTION
        # ==========================================
        num_visible = len(visible_comps)
        
        if num_visible > 0:
            gm_titles = [f"{comp} (g)" for comp in visible_comps]
            fig_gm = make_subplots(rows=num_visible, cols=1, shared_xaxes=True, vertical_spacing=0.05, subplot_titles=gm_titles)

            for i, comp in enumerate(visible_comps):
                color = warna_dict[comp]
                fig_gm.add_trace(go.Scatter(x=df['Time'], y=df[comp], mode='lines', name=comp, line=dict(color=color)), row=i+1, col=1)
                
                idx_pga = komponen_list.index(comp)
                t_pga = pga_results[idx_pga]['Time PGA (s)']
                pga_val_asli = pga_results[idx_pga]['Actual Value (g)']
                
                fig_gm.add_vline(x=t_pga, line_width=2, line_dash="dash", line_color="black", row=i+1, col=1)
                fig_gm.add_annotation(
                    x=t_pga, y=pga_val_asli,
                    text=f"PGA: {abs(pga_val_asli):.4f} g",
                    showarrow=True, arrowhead=2, ax=40, ay=-30,
                    font=dict(size=12, color="black"),
                    row=i+1, col=1
                )

            fig_gm.update_layout(height=500 * num_visible, title_text="Time Series of Ground Motion", showlegend=False)

            if not apply_fft:
                st.plotly_chart(fig_gm, use_container_width=True)
        else:
            # st.warning("Semua grafik disembunyikan. Hapus centang pada panel samping untuk menampilkannya kembali.")
            st.warning("All charts are hidden. Uncheck the boxes in the side panel to show them again.")

        # ==========================================
        # JIKA TOMBOL "APPLY FFT" DIKLIK
        # ==========================================
        if apply_fft:
            st.markdown("---")
            st.subheader("Result of Fast Fourier Transform (FFT)")

            n = len(df)
            dt = df['Time'].iloc[1] - df['Time'].iloc[0]
            freq = np.fft.fftfreq(n, d=dt)

            half_n = n // 2
            freq_pos = freq[:half_n]

            fft_results = []
            fft_plot_data = {}

            for comp in komponen_list:
                fft_vals = np.fft.fft(df[comp].values)
                amp = (2.0 / n) * np.abs(fft_vals[:half_n])
                fft_plot_data[comp] = amp

                max_amp_idx = np.argmax(amp)
                dom_freq = freq_pos[max_amp_idx]
                max_amp = amp[max_amp_idx]

                fft_results.append({
                    'Component': comp,
                    'Dominant Frequency (Hz)': round(dom_freq, 4),
                    'Max Amplitude': round(max_amp, 6)
                })

            st.write("### Dominant Frequency Information")
            df_fft_res = pd.DataFrame(fft_results)
            st.table(df_fft_res)

            if num_visible > 0:
                fft_titles = [f"Spectrum - {comp}" for comp in visible_comps]
                fig_fft = make_subplots(rows=num_visible, cols=1, shared_xaxes=True, vertical_spacing=0.05, subplot_titles=fft_titles)

                for i, comp in enumerate(visible_comps):
                    color = warna_dict[comp]
                    valid_idx = freq_pos > 0
                    fig_fft.add_trace(go.Scatter(x=freq_pos[valid_idx], y=fft_plot_data[comp][valid_idx], mode='lines', line=dict(color=color)), row=i+1, col=1)
                    
                    fig_fft.update_xaxes(type="log", row=i+1, col=1, title_text="Frequency (Hz)" if i == num_visible-1 else "")

                fig_fft.update_layout(height=500 * num_visible, title_text="Spectrum", showlegend=False)

                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(fig_gm, use_container_width=True)
                with col2:
                    st.plotly_chart(fig_fft, use_container_width=True)

            # ==========================================
            # PILIHAN MENYIMPAN HASIL (NAMA FILE BEBAS)
            # ==========================================
            st.markdown("---")
            st.subheader("Download the Result")

            down_col1, down_col2 = st.columns(2)

            # Field Input & Unduh Tabel CSV
            with down_col1:
                custom_csv_name = st.text_input("Filename (CSV):", value="table_fft")
                if not custom_csv_name.strip().endswith(".csv"):
                    file_csv_final = f"{custom_csv_name.strip()}.csv"
                else:
                    file_csv_final = custom_csv_name.strip()

                csv_fft = df_fft_res.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download the FFT Data (CSV)",
                    data=csv_fft,
                    file_name=file_csv_final,
                    mime="text/csv"
                )

            # Field Input & Unduh Gambar PNG
            with down_col2:
                if num_visible > 0:
                    custom_png_name = st.text_input("Image Filename (PNG):", value="grafik_GMAtools")
                    if not custom_png_name.strip().endswith(".png"):
                        file_png_final = f"{custom_png_name.strip()}.png"
                    else:
                        file_png_final = custom_png_name.strip()

                    fig_plt, axes = plt.subplots(num_visible, 2, figsize=(16, 4 * num_visible), squeeze=False)
                    for i, comp in enumerate(visible_comps):
                        color = warna_dict[comp]
                        idx_pga = komponen_list.index(comp)
                        
                        t_pga = pga_results[idx_pga]['Time PGA (s)']
                        pga_val = pga_results[idx_pga]['Actual Value (g)']
                        axes[i, 0].plot(df['Time'], df[comp], color=color)
                        axes[i, 0].axvline(x=t_pga, color='red', linestyle='--', linewidth=2)
                        axes[i, 0].annotate(f'PGA: {abs(pga_val):.4f} g', xy=(t_pga, pga_val), 
                                            xytext=(t_pga + (df['Time'].max()*0.05), pga_val),
                                            arrowprops=dict(facecolor='red', shrink=0.05, width=1, headwidth=5))
                        axes[i, 0].set_ylabel(f'Amp {comp} (g)')
                        axes[i, 0].grid(True, linestyle='--', alpha=0.6)
                        if i == num_visible - 1: axes[i, 0].set_xlabel('Time (s)')
                        if i == 0: axes[i, 0].set_title("Ground Motion")

                        valid_idx = freq_pos > 0
                        axes[i, 1].plot(freq_pos[valid_idx], fft_plot_data[comp][valid_idx], color=color)
                        axes[i, 1].set_xscale('log')
                        axes[i, 1].set_ylabel('Amplitudo')
                        axes[i, 1].grid(True, which="both", linestyle='--', alpha=0.6)
                        if i == num_visible - 1: axes[i, 1].set_xlabel('Frequency (Hz)')
                        if i == 0: axes[i, 1].set_title("Spectrum")

                    plt.tight_layout()
                    buf = io.BytesIO()
                    plt.savefig(buf, format="png", dpi=300)
                    buf.seek(0)

                    st.download_button(
                        label="🖼️ Download the Image (PNG)",
                        data=buf,
                        file_name=file_png_final,
                        mime="image/png"
                    )

    except Exception as e:
        # st.error(f"Terjadi kesalahan. Pastikan file sesuai format. Detail: {e}")
        st.error(f"An error occurred. Ensure the file is in the correct format. Details: {e}")