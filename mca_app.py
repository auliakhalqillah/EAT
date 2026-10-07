import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import io

# Konfigurasi Halaman
# st.set_page_config(page_title="MoCap Displacement Analysis", layout="wide")
st.title("MCAT: Motion Capture Analysis Tool")

# 1. Import Data & Tampilkan Metadata
st.header("1. Import Data")
uploaded_file = st.file_uploader("Import Motion Capture Data (CSV)", type=['csv'])

if uploaded_file is not None:
    try:
        # Membaca baris header (format umum OptiTrack)
        # Baris 2: Name, Baris 4: Type (Position/Rotation), Baris 5: Component (X, Y, Z, W)
        df_raw = pd.read_csv(uploaded_file, header=[2,4,5])
        
        st.success("Data has been loaded properly")
        
        st.subheader("Data Overview")
        st.dataframe(df_raw.head())
        
        # Mengambil daftar kolom (menghilangkan kolom Time/Frame jika ada)
        available_columns = [col for col in df_raw.columns if 'Time' not in str(col) and 'Frame' not in str(col)]
        
        # Ekstrak nilai unik untuk dropdown
        names = sorted(list(set([col[0] for col in available_columns if isinstance(col, tuple)])))
        
        # Pemilihan Jumlah Set Data
        st.header("2. Selecting the Data Preference")
        jumlah_set = st.radio("How many datasets do you want to analyze?", (1, 2))
        
        target_cols = []
        
        for i in range(jumlah_set):
            st.subheader(f"Set Data {i+1}")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                selected_name = st.selectbox(f"Select the Object/Marker {i+1}:", names, key=f"name_{i}")
            
            # Filter tipe berdasarkan nama yang dipilih
            types = sorted(list(set([col[1] for col in available_columns if col[0] == selected_name])))
            with col2:
                selected_type = st.selectbox(f"Select Data Type {i+1}:", types, key=f"type_{i}") # Position atau Rotation
                
            # Filter komponen berdasarkan tipe & nama
            components = sorted(list(set([col[2] for col in available_columns if col[0] == selected_name and col[1] == selected_type])))
            with col3:
                selected_component = st.selectbox(f"Select Component {i+1}:", components, key=f"comp_{i}") # X, Y, Z, W
                
            target_cols.append((selected_name, selected_type, selected_component))
        
        # 3. Analisis Baseline
        st.header("3. Baseline Processing")
        for i, col in enumerate(target_cols):
            st.write(f"Selected Column {i+1}: **{col[0]} -> {col[1]} -> {col[2]}**")
        
        if st.button("Apply Baseline"):
            # Proses setiap set data yang dipilih
            for i, target_col in enumerate(target_cols):
                awal = df_raw[target_col].iloc[0]
                df_raw[f'Baseline_Result_{i+1}'] = df_raw[target_col] - awal
                st.success(f"Analisis Set {i+1} if complete! The initial value of {awal:.3f} has been changed to 0.")
            
            # Jika 2 set dipilih, hitung selisihnya
            if jumlah_set == 2:
                df_raw['Selisih_Baseline'] = df_raw['Baseline_Result_1'] - df_raw['Baseline_Result_2']
                st.success("The residual baseline calculation (Set 1 - Set 2) is complete.")
                
            st.session_state['data_ready'] = True
            st.session_state['plot_data'] = df_raw
            st.session_state['jumlah_set'] = jumlah_set
            st.session_state['target_cols'] = target_cols

        # 4 & 5. Visualisasi & Export
        if st.session_state.get('data_ready'):
            df_plot = st.session_state['plot_data']
            jm_set = st.session_state['jumlah_set']
            t_cols = st.session_state['target_cols']
            
            st.header("4. Visualization")
            plot_col1, plot_col2 = st.columns(2)
            
            # Asumsi index DataFrame atau kolom pertama adalah waktu/frame
            x_axis = df_plot.index / 120
            
            with plot_col1:
                st.subheader("Matplotlib")
                fig, ax = plt.subplots(figsize=(8, 4))
                
                # Plot set 1
                ax.plot(x_axis, df_plot['Baseline_Result_1'], label=f"Set 1: {t_cols[0][0]}", linewidth=1.5)
                
                # Plot set 2 dan selisih jika ada
                if jm_set == 2:
                    ax.plot(x_axis, df_plot['Baseline_Result_2'], label=f"Set 2: {t_cols[1][0]}", linewidth=1.5)
                    ax.plot(x_axis, df_plot['Selisih_Baseline'], label="Selisih (Set1 - Set2)", linestyle='--', linewidth=1.5)
                    
                ax.set_title("Displacement Analysis")
                ax.set_ylabel("Displacement (mm)")
                ax.set_xlabel("Time (s)")
                ax.legend()
                ax.grid(True, linestyle='--', alpha=0.6)
                st.pyplot(fig)
                
                # Export Grafik Matplotlib
                buf_fig = io.BytesIO()
                fig.savefig(buf_fig, format='png', bbox_inches='tight')
                st.download_button(
                    label="Download (PNG)",
                    data=buf_fig.getvalue(),
                    file_name="Grafik_Displacement.png",
                    mime="image/png"
                )
                
            with plot_col2:
                st.subheader("Plotly (Interaktif)")
                
                fig_plotly = go.Figure()
                fig_plotly.add_trace(go.Scatter(x=x_axis, y=df_plot['Baseline_Result_1'], mode='lines', name=f"Set 1: {t_cols[0][0]}"))
                
                if jm_set == 2:
                    fig_plotly.add_trace(go.Scatter(x=x_axis, y=df_plot['Baseline_Result_2'], mode='lines', name=f"Set 2: {t_cols[1][0]}"))
                    fig_plotly.add_trace(go.Scatter(x=x_axis, y=df_plot['Selisih_Baseline'], mode='lines', name="Selisih", line=dict(dash='dash')))
                
                fig_plotly.update_layout(title='Displacement Analysis', xaxis_title='Time (s)', yaxis_title='Displacment (mm)')
                
                st.plotly_chart(fig_plotly, use_container_width=True)
                st.info("Use the built-in menu (camera icon) at the top right of the Plotly chart to download the interactive version.")
            
            # 5. Export Data Excel
            st.header("5. Export Data")
            
            # Buat DataFrame untuk diekspor
            export_dict = {'Waktu (detik)': x_axis}
            export_dict[f'Raw_Set_1 ({t_cols[0][0]}_{t_cols[0][2]})'] = df_plot[t_cols[0]]
            export_dict['Baseline_Set_1_mm'] = df_plot['Baseline_Result_1']
            
            if jm_set == 2:
                 export_dict[f'Raw_Set_2 ({t_cols[1][0]}_{t_cols[1][2]})'] = df_plot[t_cols[1]]
                 export_dict['Baseline_Set_2_mm'] = df_plot['Baseline_Result_2']
                 export_dict['Selisih_Baseline_mm'] = df_plot['Selisih_Baseline']
                 
            export_df = pd.DataFrame(export_dict)
            
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                export_df.to_excel(writer, index=False, sheet_name='Displacement Data')
                
            st.download_button(
                label="Download Data (Excel / XLSX)",
                data=excel_buffer.getvalue(),
                file_name="Displacement_Data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"An error occurred while processing the data. Ensure the CSV format is correct. Error details: {e}")