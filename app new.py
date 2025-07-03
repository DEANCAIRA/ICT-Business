import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Financial Metrics Comparison", layout="wide")

# Function to load financial data from Excel files
@st.cache_data
def load_financial_data(file_path):
    try:
        df = pd.read_excel(file_path, sheet_name="Sheet1", header=None)
        return df
    except Exception as e:
        st.error(f"Error loading {file_path}: {e}")
        return None

# Function to extract available metrics from dataframes
def get_available_metrics(dataframes):
    all_metrics = set()
    for df in dataframes.values():
        if df is not None:
            # Assuming metrics are in column 1
            metrics = df[1].astype(str).str.lower().str.strip().tolist()
            all_metrics.update(metrics)
    
    # Remove empty strings and non-meaningful values
    all_metrics = [m for m in all_metrics if m and m not in ['', 'nan', 'year', 'none']]
    return sorted(all_metrics)

# Function to extract specific financial metric
def extract_metric(df, metric_name):
    if df is None:
        return pd.DataFrame({"Year": [], "Value": []})
    
    # Extract years from header row (assuming they start from column 2)
    years = df.iloc[1, 2:].tolist()
    
    # Find the row with the metric
    df[1] = df[1].astype(str)
    match_row = df[df[1].str.lower().str.strip() == metric_name.lower().strip()]
    
    if not match_row.empty:
        values = match_row.iloc[0, 2:].tolist()
        return pd.DataFrame({"Year": years, "Value": values})
    else:
        return pd.DataFrame({"Year": years, "Value": [None] * len(years)})

# Main app
def main():
    st.title("📊 Financial Metrics Comparison Tool")
    
    st.markdown("""
    This app allows you to compare financial metrics across multiple companies.
    Upload Excel files containing financial data and select metrics to compare.
    """)
    
    # File upload section
    st.header("1. Upload Financial Data")
    
    uploaded_files = st.file_uploader("Upload Excel files containing financial data", 
                                     type=["xlsx", "xls"], 
                                     accept_multiple_files=True)
    
    # Process uploaded files
    company_data = {}
    
    if uploaded_files:
        for file in uploaded_files:
            company_name = file.name.split('.')[0]  # Use filename as company name
            df = load_financial_data(file)
            if df is not None:
                company_data[company_name] = df
    else:
        # Use sample data for demonstration if no files are uploaded
        st.info("No files uploaded. Using sample data for demonstration.")
        
        # Create sample dataframes
        alpha_data = pd.DataFrame({
            0: [0, "Year", "EBITDA", "Revenue", "Net Income", "Gross Profit"],
            1: [0, "", "EBITDA", "Revenue", "Net Income", "Gross Profit"],
            2: [0, 2020, 100, 500, 50, 200],
            3: [0, 2021, 120, 550, 60, 220],
            4: [0, 2022, 140, 600, 70, 240]
        })
        
        omega_data = pd.DataFrame({
            0: [0, "Year", "EBITDA", "Revenue", "Net Income", "Gross Profit"],
            1: [0, "", "EBITDA", "Revenue", "Net Income", "Gross Profit"],
            2: [0, 2020, 80, 400, 40, 180],
            3: [0, 2021, 90, 450, 45, 190],
            4: [0, 2022, 100, 480, 50, 200]
        })
        
        company_data = {
            "ALPHA": alpha_data,
            "OMEGA": omega_data
        }
    
    # Get available metrics
    available_metrics = get_available_metrics(company_data)
    
    # Metric selection
    st.header("2. Select Metrics to Compare")
    
    # Allow user to search for metrics
    metric_search = st.text_input("Search for a metric (e.g., EBITDA, Revenue, Profit)").lower()
    
    # Filter metrics based on search
    filtered_metrics = [m for m in available_metrics if metric_search in m]
    
    if metric_search and not filtered_metrics:
        st.warning(f"No metrics found containing '{metric_search}'")
    
    selected_metric = st.selectbox("Select a metric to compare", 
                                  options=filtered_metrics if filtered_metrics else available_metrics)
    
    # Extract and display data
    if selected_metric:
        st.header(f"3. Comparison of {selected_metric.upper()}")
        
        # Create tabs for table and chart views
        tab1, tab2 = st.tabs(["Chart View", "Table View"])
        
        # Extract data for all companies
        comparison_data = {}
        for company, df in company_data.items():
            metric_data = extract_metric(df, selected_metric)
            if not metric_data.empty and not metric_data["Value"].isna().all():
                comparison_data[company] = metric_data
        
        if comparison_data:
            # Prepare data for visualization
            plot_data = pd.DataFrame()
            for company, data in comparison_data.items():
                temp_df = data.copy()
                temp_df["Company"] = company
                plot_data = pd.concat([plot_data, temp_df])
            
            # Convert Year to string for better display
            plot_data["Year"] = plot_data["Year"].astype(str)
            
            with tab1:
                # Create interactive chart with Plotly
                fig = px.line(plot_data, x="Year", y="Value", color="Company", 
                             markers=True, title=f"{selected_metric.upper()} Comparison")
                fig.update_layout(
                    xaxis_title="Year",
                    yaxis_title=f"{selected_metric.upper()} Value",
                    legend_title="Company",
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                # Create comparison table
                st.subheader("Data Table")
                
                # Pivot the data for better table display
                pivot_table = plot_data.pivot(index="Year", columns="Company", values="Value")
                st.dataframe(pivot_table, use_container_width=True)
                
                # Download option
                csv = pivot_table.to_csv()
                st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name=f'{selected_metric}_comparison.csv',
                    mime='text/csv',
                )
        else:
            st.warning(f"No data available for {selected_metric}")
    
    # Add information about deployment
    st.sidebar.header("About")
    st.sidebar.info("""
    This app allows you to compare financial metrics across multiple companies.
    
    **How to use:**
    1. Upload Excel files containing financial data
    2. Search for and select a metric to compare
    3. View the comparison in chart or table format
    
    **Data Format Requirements:**
    - Excel files with metrics in column 1
    - Years in row 1 starting from column 2
    - Values in corresponding cells
    """)

if __name__ == "__main__":
    main()