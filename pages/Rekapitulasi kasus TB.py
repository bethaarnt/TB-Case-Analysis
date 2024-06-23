import streamlit as st
import pandas as pd
import plotly.express as px

def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file, header=9)
    df['Nama Kecamatan & Fasyankes'] = df['KATEGORI'].astype(str) + " (" + df['Unnamed: 3'].astype(str) + ")"
    df = df[['Nama Kecamatan & Fasyankes', 'Terduga TB', 'Anak yang Mendapatkan TPT', 'Unnamed: 11']]
    df = df.rename(columns={'Unnamed: 11': 'Total Kasus TB Ternotifikasi'})
    df = df.dropna(subset=['Terduga TB', 'Anak yang Mendapatkan TPT', 'Total Kasus TB Ternotifikasi'])
    df['Total Kasus TB Ternotifikasi'] = pd.to_numeric(df['Total Kasus TB Ternotifikasi'], errors='coerce')
    
    total_index = df[df['Nama Kecamatan & Fasyankes'].str.contains('TOTAL')].index.min()
    df_corrected = df.loc[:total_index-1] if total_index is not None else df

    # Calculate and append the total row
    # total_row = pd.DataFrame({
    #     'Nama Kecamatan & Fasyankes': ['Jumlah Kasus'],
    #     'Terduga TB': [df_corrected['Terduga TB'].sum()],
    #     'Anak yang Mendapatkan TPT': [df_corrected['Anak yang Mendapatkan TPT'].sum()],
    #     'Total Kasus TB Ternotifikasi': [df_corrected['Total Kasus TB Ternotifikasi'].sum()]
    # })
    # df_corrected = pd.concat([df_corrected, total_row], ignore_index=True)
    
    return df_corrected

def plot_data(df_corrected, column, title):
    fig = px.bar(df_corrected, y=column, title=title,
                color='Nama Kecamatan & Fasyankes', labels={'Nama Kecamatan & Fasyankes': 'Kecamatan & Fasyankes'})
    
    fig.update_layout(
        xaxis_title='Kecamatan & Fasyankes',
        # xaxis=dict(
        #     showticklabels=False  # Menyembunyikan tick labels pada sumbu x
        # )
    )

    return fig

def main():
    st.title('Analisis Data TB')
    uploaded_file = st.file_uploader("Upload file Excel Anda", type="xlsx")
    if uploaded_file is not None:
        data = load_data(uploaded_file)
        st.success('Data loaded successfully!')
        
        st.write("### Data Terduga TB")
        st.dataframe(data[['Nama Kecamatan & Fasyankes', 'Terduga TB']], width=1000)
        fig_tb = plot_data(data, 'Terduga TB', 'Visualisasi Terduga TB per Kecamatan & Fasyankes')
        st.plotly_chart(fig_tb, use_container_width=True)
        
        st.write("### Data Anak yang Mendapatkan TPT")
        st.dataframe(data[['Nama Kecamatan & Fasyankes', 'Anak yang Mendapatkan TPT']], width=1000)
        fig_tpt = plot_data(data, 'Anak yang Mendapatkan TPT', 'Visualisasi Anak yang Mendapatkan TPT per Kecamatan & Fasyankes')
        st.plotly_chart(fig_tpt, use_container_width=True)

        st.write("### Data Total Kasus TB Ternotifikasi")
        st.dataframe(data[['Nama Kecamatan & Fasyankes', 'Total Kasus TB Ternotifikasi']], width=1000)
        fig_total = plot_data(data, 'Total Kasus TB Ternotifikasi', 'Visualisasi Total Kasus TB Ternotifikasi per Kecamatan & Fasyankes')
        st.plotly_chart(fig_total, use_container_width=True)

if __name__ == "__main__":
    main()