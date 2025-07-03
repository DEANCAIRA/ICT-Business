# 📊 Financial Metrics Comparison App

This is a **Streamlit web app** that allows you to upload Excel files of financial statements from multiple companies and compare key metrics like **EBITDA**, **Revenue**, or **Net Profit**.

## 🚀 Features
- Upload financial Excel files
- Automatically extract and list available financial metrics
- Search and select a specific metric
- View side-by-side comparison charts and tables for multiple companies
- Export comparison tables to CSV

## 🧾 Excel File Format
Each Excel file should follow this structure:

- **Sheet name:** `Sheet1`
- **Column 1 (B):** Metric names (e.g., EBITDA, Revenue)
- **Row 2 (from Column C onward):** Years (e.g., 2020, 2021, 2022...)
- **Each row:** Values of a single metric across years

## 📁 Repository Contents
├── app.py                # Streamlit application file
├── requirements.txt      # Python package dependencies
├── ALPHA.xlsx            # Example company file (optional)
├── OMEGA.xlsx            # Example company file (optional)
└── README.md             # Project documentation

## 💻 Local Setup
```bash
git clone https://github.com/yourusername/financial-metrics-app.git
cd financial-metrics-app
pip install -r requirements.txt
streamlit run app.py
```

## ☁️ Deploy on Streamlit Cloud
1. Push this code to a public GitHub repository
2. Go to https://streamlit.io/cloud
3. Log in and click **New App**
4. Select your repo and set `app.py` as the entry point
5. Click **Deploy**

## 📦 Requirements
streamlit  
pandas  
openpyxl  
plotly
