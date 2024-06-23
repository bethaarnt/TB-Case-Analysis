import streamlit as st
import pandas as pd
import plotly.express as px

def load_data(file):
    data = pd.read_excel(file, skiprows=6)
    data['Tanggal Hasil Pemeriksaan Dahak'] = pd.to_datetime(data['Tanggal Hasil Pemeriksaan Dahak'], errors='coerce')
    return data

def temuan_kasus_kader(data):
    patient_type_distribution = data['Tipe Pasien'].value_counts()
    # Jumlah kasus berdasarkan kader untuk masing-masing tipe pasien
    kader_patient_type = data.groupby(['Kader', 'Tipe Pasien']).size().unstack(fill_value=0)
    kader_patient_type['Total Kasus'] = kader_patient_type.sum(axis=1)
    return patient_type_distribution, kader_patient_type

def kader_performance_analysis(data):
    kader_cases = data.groupby('Kader').size()
    fig = px.bar(kader_cases, labels={'value': 'Jumlah Kasus', 'index': 'Kader'}, title='Performance by Kader')
    st.plotly_chart(fig)
    
def monthly_analysis(data):
    data['Bulan'] = data['Tanggal Hasil Pemeriksaan Dahak'].dt.to_period('M')
    monthly_cases = data.groupby('Bulan').size().reset_index(name='Cases')
    fig = px.line(monthly_cases, x=monthly_cases['Bulan'].dt.to_timestamp(),
                y='Cases', labels={'x': 'Bulan', 'Cases': 'Jumlah Kasus'}, title='Monthly TB Case Trends')

    st.plotly_chart(fig)

def demographic_analysis(data):
    data['Usia'] = data['Usia'].apply(lambda x: int(x.replace(' Thn', '')))
    max_age = data['Usia'].max()
    bins = list(range(0, max_age + 10, 10))
    labels = [f'{i}-{i+9}' for i in range(0, max_age, 10)]  # label rentang usia 10 tahun
    data['Usia'] = pd.cut(data['Usia'], bins=bins, labels=labels, right=False)

    fig = px.histogram(data, x='Usia', title='Distribusi Usia Pasien',
                        category_orders={'Usia': labels}) 
    fig.update_traces(marker_color='skyblue', marker_line_color='navy', marker_line_width=1.5, opacity=0.6)
    fig.update_layout(xaxis_title='Kelompok Usia', yaxis_title='Jumlah Pasien',
                    xaxis={'categoryorder':'array'})

    st.plotly_chart(fig)

    gender_counts = data['Jenis Kelamin'].value_counts().reset_index()
    gender_counts.columns = ['Gender', 'Jumlah']
    fig = px.pie(gender_counts, names='Gender', values='Jumlah', title='Distribusi Pasien TB Berdasarkan Gender')
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

def geographical_analysis(data):
    case_distribution = data['Kecamatan'].value_counts()
    fig = px.bar(case_distribution, labels={'value': 'Jumlah Kasus', 'index': 'Kecamatan'}, title='Distribusi Kasus Per Kecamatan')
    st.plotly_chart(fig)

def treatment_outcomes(data):
    outcome_counts = data['Hasil Pengobatan'].value_counts()
    fig = px.pie(values=outcome_counts.values, names=outcome_counts.index, labels={'values': 'Jumlah Kasus', 'names': 'Hasil Pengobatan'}, title='Hasil Pengobatan')
    st.plotly_chart(fig)

def main():
    st.title('Analisis Data Temuan Kasus TB oleh Kader')
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

    if uploaded_file is not None:
        data = load_data(uploaded_file)
        data['Tanggal Hasil Pemeriksaan Dahak'] = pd.to_datetime(data['Tanggal Hasil Pemeriksaan Dahak'])
        
        patient_type_distribution, kader_patient_type = temuan_kasus_kader(data)
        st.write("### Distribusi Tipe Pasien:", patient_type_distribution)
        st.write("### Jumlah Kasus per Kader berdasarkan Tipe Pasien:")
        st.dataframe(kader_patient_type)
        kader_performance_analysis(data)

        st.write("### Temuan Kasus TB Bulanan")
        monthly_analysis(data)
        
        demographic_analysis(data)
        
        geographical_analysis(data)

        st.write("### Outcomes Analysis")
        treatment_outcomes(data)
        
if __name__ == "__main__":
    main()
