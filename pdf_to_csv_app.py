import PyPDF2
import pandas as pd
import re
import streamlit as st

st.set_page_config(page_title="pdf to csv")
st.title("EWL Fair Distribution Converter")

uploaded_files = st.file_uploader("Choose files", type=["pdf"], accept_multiple_files=True)

def extract_pdf(pdf):
    with pdf as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        all_lines = []
        
        page = reader.pages[0]
        text = page.extract_text()
        
        date_text = text.split('\n')[0]
        date_pattern = re.search(r'month\s*:\s*\w+\s*\d{4}', date_text)
        
        if date_pattern:
            date_extract = date_pattern.group()[7:]
            year, month = date_extract.split()
            date_str = f"{year}_{month}_"
        else:
            year = st.text_input("enter year (example: 2023): ")
            month = st.text_input("Enter month (example: February): ")
            date_str = f"{year}_{month}_"
        
        first_page_lines = text.split('\n')[5:]
        all_lines += first_page_lines
        
        for i in range(1, num_pages):
            page = reader.pages[i]
            text = page.extract_text()
            lines = text.split('\n')[4:]
            all_lines += lines
            
    extracted_data = []
    
    for line in all_lines:
        if ", " in line:
            line = line.replace(", ", " ")
        
        row = line.split(' ')
        
        if len(row) == 16:
            row.insert(2, '')
        
        extracted_data.append(row)
    
    return date_str, pd.DataFrame(extracted_data)

all_dfs = []

if uploaded_files:
    for uploaded_file in uploaded_files:
        pdf_date, df = extract_pdf(uploaded_file)
        all_dfs.append(df)
        
    final_df = pd.concat(all_dfs, ignore_index=True)
    final_df.columns = ["base", "rank", "no_name", "crew code", "a/c type", "group", "Real BH", "Flight Duty Time", "No. Night stops", "No. Flight Procs", "No. Ground Procs", "No. standby duties", "OFF this month", "Vacation", "Sickness", "Sick this year", "Duty Time"]
    
    # Hier setzt du deine Datentyp-Konvertierungen ein...
    
    st.dataframe(final_df)
    
    csv = final_df.to_csv(index=False)
    st.success("Conversion from pdf to csv complete")
    st.download_button('Download Combined CSV File', csv, file_name='multiple_pdfs_converted.csv', mime='text/csv')
