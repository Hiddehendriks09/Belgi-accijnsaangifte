import streamlit as st
import pandas as pd

def process_files(main_file, reference_file, start_date, end_date):
    # Load main data file
    data = pd.read_csv(main_file)
    
    # Renaming columns and preparing the data
    data = data.rename(columns={"Lineitem sku": "SKU"})
    data['SKU'] = data['SKU'].str.replace(r"(-\d+|[A-Z])$", "", regex=True)
    
    # Load reference data file
    check = pd.read_csv(reference_file)
    
    # Merging data with reference data
    data = pd.merge(data, check[['SKU', 'Alcohol Percentage', 'Excise code']], on='SKU', how='left')
    
    # Filling missing data
    data['Fulfilled at'] = data['Fulfilled at'].fillna(method='ffill')
    data['Billing Name'] = data['Billing Name'].fillna(method='ffill')
    data['Billing Street'] = data['Billing Street'].fillna(method='ffill')
    
    # Filtering data for specific conditions
    df = data[data['Billing Country'] == 'BE']
    selected_columns = ["Name", "Created at", "Fulfilled at", "Lineitem quantity", "Lineitem name", "Billing Name", "Billing Street", "Alcohol Percentage", "Excise code"]
    new_df = df[selected_columns]
    new_df = new_df.rename(columns={"Name": "Invoice/order", "Created at": "Invoice date", "Fulfilled at": "Delivery date","Lineitem name": "Product name", "Lineitem quantity": "Number of sold items", "Billing Name": "Name of client", "Billing Street": "Address details"  })
    new_df['Invoice date'] = pd.to_datetime(new_df['Invoice date']).dt.tz_localize(None)
# Format the 'Invoice date' column with the desired format
    #new_df['Invoice date'] = new_df['Invoice date'].dt.strftime('%Y-%m-%d %H:%M')
# Repeat the same process for 'Delivery date' column if needed
    new_df['Delivery date'] = pd.to_datetime(new_df['Delivery date']).dt.tz_localize(None)
    #new_df['Delivery date'] = new_df['Delivery date'].dt.strftime('%Y-%m-%d %H:%M')
    new_df["Plato percentage"] = 0
#new_df['Last Part'] = new_df['Product name'].str.split().str[-2:].str.join(' ')
    new_df['Content'] = new_df['Product name'].str.extract(r'(\d+)(?!.*\d)').astype(float).astype('Int64')
    new_df["Total content"] = new_df["Content"]*new_df["Number of sold items"]

    filtered_df = new_df[(new_df['Delivery date'] >= start_date) & (new_df['Delivery date'] <= end_date)]
    final_data = filtered_df[['Invoice/order', 'Invoice date', 'Delivery date', 'Name of client', 'Address details', 'Product name', 'Excise code', 'Number of sold items', 'Content', 'Total content', 'Alcohol Percentage', 'Plato percentage']]
    final_data = final_data.drop_duplicates()
    return final_data

st.title('Accijnsaangifte België')

# File uploaders
uploaded_file = st.file_uploader("Importeer de csv file van shopify", type=['csv'])
reference_file = st.file_uploader("Importeer de referentie csv file", type=['csv'])
start_time = st.text_input("Start datum in format: (YYYY-MM-DD HH:MM:SS)")
end_time = st.text_input("Eind datum in format: (YYYY-MM-DD HH:MM:SS)")


if st.button('Download bestand'):
    if uploaded_file is not None and reference_file is not None and start_time and end_time:
        try:
            # Convert string dates to datetime objects
            start_time = pd.to_datetime(start_time)
            end_time = pd.to_datetime(end_time)
            
            # Process files with the specified date and time
            result_df = process_files(uploaded_file, reference_file, start_time, end_time)
            st.write(result_df)
            csv = result_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download processed CSV", csv, "processed_data.csv", "text/csv", key='download-csv')
        except ValueError as e:
            st.error(f"Error in date format: {e}")
    else:
        st.error("Please upload both files and specify the date range to continue.")
