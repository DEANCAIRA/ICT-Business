# 📊 Financial Metrics Comparison App

This is a **Streamlit web app** that allows you to upload Excel files of financial statements from multiple companies and compare key metrics like **EBITDA**, **Revenue**, or **Net Profit**.

---

## 🚀 Features
- Upload financial Excel files
- Automatically extract and list available financial metrics
- Search and select a specific metric
- View side-by-side comparison charts and tables for multiple companies
- Export comparison tables to CSV

---

## 🧾 Excel File Format
Each Excel file should follow this structure:

- **Sheet name:** `Sheet1`
- **Column 1 (B):** Metric names (e.g., EBITDA, Revenue)
- **Row 2 (from Column C onward):** Years (e.g., 2020, 2021, 2022...)
- **Each row:** Values of a single metric across years

|     | A     | B           | C     | D     | E     |
|-----|-------|-------------|-------|-------|-------|
| 1   |       |             | 2020  | 2021  | 2022  |
| 2   |       | EBITDA      | 100   | 120   | 140   |
| 3   |       | Revenue     | 500   | 550   | 600   |
| ... | ...   | ...         | ...   | ...   | ...   |

---

## 📁 Repository Contents
```
├── app.py                # Streamlit application file
├── requirements.txt      # Python package dependencies
├── ALPHA.xlsx            # Example company file (optional)
├── OMEGA.xlsx            # Example company file (optional)
└── README.md             # Project documentation
```

---

## 💻 Local Setup
```bash
# 1. Clone the repo
https://github.com/yourusername/financial-metrics-app.git

# 2. Navigate to the project folder
cd financial-metrics-app

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

---

## ☁️ Deploy on Streamlit Cloud
1. Push this code to a public GitHub repository
2. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
3. Log in and click **New App**
4. Select your repo and set `app.py` as the entry point
5. Click **Deploy**

---

## 📦 Requirements
Contents of `requirements.txt`:
```
streamlit
pandas
openpyxl
plotly
```

---

## 📬 Contact
If you encounter issues or have suggestions, please feel free to open an issue or contact the maintainer.

---

Created with ❤️ using Streamlit.
