import streamlit as st
import pandas as pd
import plotly.express as px
import io

def load_data(file):
    data = pd.read_excel(file)
    data['tgl_hasil_diagnosis'] = pd.to_datetime(data['tgl_hasil_diagnosis'])
    data['nama_bulan'] = data['tgl_hasil_diagnosis'].dt.strftime('%B')
    # Menentukan minggu dalam bulan
    bins = [0, 7, 14, 21, 32]  # Rentang tanggal untuk setiap minggu
    labels = [1, 2, 3, 4] 
    data['Week of Month'] = pd.cut(data['tgl_hasil_diagnosis'].dt.day, bins=bins, labels=labels, right=False)
    data['IK_status'] = data['SITK'].apply(lambda x: 'Sudah IK' if pd.notna(x) else 'Belum IK')
    return data

def age_distribution(data):
    max_age = data['umur'].max()
    bins = list(range(0, max_age + 11, 10))
    labels = [f'{i}-{i+9}' for i in range(0, max_age, 10)]  # label rentang usia 10 tahun
    data['age_group'] = pd.cut(data['umur'], bins=bins, labels=labels, right=False)

    fig = px.histogram(data, x='age_group', title='Distribusi Umur Pasien',
                        category_orders={'age_group': labels}) 
    fig.update_traces(marker_color='skyblue', marker_line_color='navy', marker_line_width=1.5, opacity=0.6)
    fig.update_layout(xaxis_title='Kelompok Umur', yaxis_title='Jumlah Pasien',
                    xaxis={'categoryorder':'array'})
    return fig

def cases_by_kecamatan(data):
    case_count = data['person_kecamatan'].value_counts().reset_index()
    case_count.columns = ['Kecamatan', 'Jumlah Kasus']
    # Menggunakan 'Kecamatan' sebagai kategori
    fig = px.bar(case_count, x='Kecamatan', y='Jumlah Kasus', title='Jumlah Kasus per Kecamatan', color='Kecamatan')
    fig.update_layout(xaxis_title='Kecamatan', yaxis_title='Jumlah Kasus', xaxis={'categoryorder':'total descending'})
    fig.update_layout(legend_title_text='Kecamatan')
    return fig

def gender_distribution(data):
    gender_distribution = data['jenis_kelamin_id'].value_counts().reset_index()
    gender_distribution.columns = ['Jenis Kelamin', 'Jumlah']
    fig = px.pie(gender_distribution, values='Jumlah', names='Jenis Kelamin', title='Distribusi Jenis Kelamin Pasien')
    return fig

def plot_data(data):
    weekly_ik_status = data.groupby(['Week of Month', 'IK_status']).size().reset_index(name='count')
    
    # bulan_translate = {
    # 'January': 'Januari',
    # 'February': 'Februari',
    # 'March': 'Maret',
    # 'April': 'April',
    # 'May': 'Mei',
    # 'June': 'Juni',
    # 'July': 'Juli',
    # 'August': 'Agustus',
    # 'September': 'September',
    # 'October': 'Oktober',
    # 'November': 'November',
    # 'December': 'Desember'
    # }

    # Mengganti nama bulan Inggris menjadi Indonesia
    # data['nama_bulan'] = data['nama_bulan'].map(bulan_translate)
    
    # Membuat grafik menggunakan Plotly
    fig = px.bar(weekly_ik_status, x='Week of Month', y='count', color='IK_status', 
                title='Trafik Data Hasil Bridging Bulan ' + data['nama_bulan'].iloc[0],
                labels={'count': 'Jumlah Kasus', 'Week of Month': 'Minggu Ke-', 'IK_status': 'Status IK'},
                barmode='group')
    
    fig.update_layout(xaxis=dict(tickmode='array', tickvals=[1, 2, 3, 4], ticktext=['1', '2', '3', '4']),
                    yaxis_title='Jumlah Kasus',
                    xaxis_title='Minggu Ke-',
                    legend_title_text='Status IK')
    
    return fig

def main():
    st.title("Analisis Data Bridging IK dan Non-IK")
    
    uploaded_file = st.file_uploader("Upload file Excel Anda", type=['xlsx'])
    
    if uploaded_file is not None:
        data = load_data(uploaded_file)
        st.success('Data loaded successfully!')
        
        st.plotly_chart(plot_data(data))
        
        # Check for duplicates
        duplicates = data[data.duplicated(keep=False)]
        if not duplicates.empty:
            st.write("Data Duplikat:")
            st.dataframe(duplicates)
            
        data_belum_ik = data[data['IK_status'] == 'Belum IK']
        if not data_belum_ik.empty:
            st.write("Data yang Belum Melakukan IK:")
            st.dataframe(data_belum_ik)
            
            # Prepare Excel file for download
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                data_belum_ik.to_excel(writer, index=False, sheet_name='Data Belum IK')
                writer.save()
            val = output.getvalue()
            file_name = f"data_belum_ik_{data['nama_bulan'].iloc[0]}.xlsx"
            st.download_button(
                label="Download",
                data=val,
                file_name= file_name,
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
        # if st.button('Tampilkan Analisis'):
        st.plotly_chart(age_distribution(data))
        st.plotly_chart(cases_by_kecamatan(data))
        st.plotly_chart(gender_distribution(data))
            
if __name__ == "__main__":
    main()
