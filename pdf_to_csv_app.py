import PyPDF2
import pandas as pd
import os
import re
import streamlit as st
from io import StringIO

st.set_page_config(
    page_title="pdf to csv")

uploaded_file = st.file_uploader("Choose file", type = ["pdf"])

st.spinner("extracting")

def extract_pdf(pdf):
    with pdf as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        
        all_lines = []
        #get first page
        page = reader.pages[0]
        text = page.extract_text()
        
        #date
        date_text = text.split('\n')[0]
        date_pattern = re.search(r'month\s*:\s*\w+\s*\d{4}', date_text)
        if date_pattern:
            try:
                date_extract = date_pattern.group()[7:]
                year = date_extract.split(" ")[1]
                month = date_extract.split(" ")[0]
                date_str = (str(year) + "_" + str(month) + str("_"))
            except:
                pass
        else:
            year = st.text_input("enter year (example: 2023): ")
            month = st.text_input("Enter month (example: February): ")
            date_str = (str(year) + "_" + str(month) + str("_"))
        
        
        #data
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
        
        # Assuming each line is a row and columns are separated by spaces (customize this part)
        row = line.split(' ')

        if len(row) == 16:
            row.insert(2, '')
        
        extracted_data.append(row)
    return(date_str, pd.DataFrame(extracted_data))


if uploaded_file is not None:
    with st.spinner('Reading PDF...'):
        pdf_date, df = extract_pdf(uploaded_file)


    df.columns = ["base", "rank", "no_name", "crew code", "a/c type", "group", "Real BH", "Flight Duty Time", "No. Night stops", "No. Flight Procs", 
                "No. Ground Procs", "No. standby duties", "OFF this month", "Vacation", "Sickness", "Sick this year", "Duty Time"]

    #column types
    string_cols = ["base", "rank", "a/c type", "group"]
    alpha_num_cols = ["crew code"]
    has_empty = ["no_name"]
    integer_cols = ["No. Night stops", "No. Flight Procs", "No. Ground Procs", "No. standby duties", "OFF this month", "Vacation", "Sickness", "Sick this year"]
    time_cols = ["Real BH", "Flight Duty Time", "Duty Time"]

    #assign data types
    df[string_cols + alpha_num_cols + has_empty] = df[string_cols + alpha_num_cols + has_empty].astype("string")
    try:
        for col in integer_cols:
            df[col] = df[col].astype(int)
    except:
        print(f"non integer types present in column {col}")
        df[col] = df[col].astype(str)
    df[time_cols] = df[time_cols].astype("string")

    #check string columns
    for col in string_cols:
        if col == "group":
            continue
        if all(df[col].astype(str).apply(str.isalpha)):
            continue
        else:
            print(f"Warning: Non alphabetical entry in column [{col}]")

    #check on group colum
    if df["group"].str.contains(r"\*[a-zA-Z]", regex = True).all():
        pass
    else:
        print(f"Warning: column [group] does not follow pattern * followed by a character, eg: *F")

    #check numeric column have integers
    for col in integer_cols:
        if all(df[col].astype(str).apply(str.isnumeric)):
            continue
        else:
            print(f"Warning: Non integer entry in column {col}")

    #check time columns
    for col in time_cols:
        if df[col].str.contains(r":", regex = True).all():
            continue
        else:
            print("Warning: Column {col} appears to have values(s) not in time format")

    st.dataframe(df)



    # #set output file name
    # file_name = os.path.splitext(os.path.basename(input_path))[0]
    # output_filename = pdf_date + file_name + "_csv.csv"

    csv = df.to_csv(index=False)
    st.success("Conversion from pdf to csv complete", icon="✅")


    out_file_name = (pdf_date + uploaded_file.name[:-4])
    st.download_button('Download CSV File', csv, 
                    file_name=f'{out_file_name}.csv', mime='text/csv')



