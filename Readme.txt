# 🎯 Customer Persona Generator

A powerful Streamlit application that automatically generates detailed customer personas from uploaded customer data. Transform your customer data into actionable insights with intelligent analysis and beautiful visualizations.

## ✨ Features

### 🔧 Core Functionality
- **Smart File Upload**: Support for CSV and Excel files (.csv, .xlsx, .xls)
- **Automatic Analysis**: Intelligently extracts customer interests, behaviors, and preferences
- **Persona Generation**: Creates detailed, narrative customer personas
- **Smart Categorization**: Groups customers into meaningful segments
- **Real-time Processing**: Instant persona generation upon data upload

### 📊 Analytics & Visualization
- **Interactive Dashboard**: Four comprehensive tabs for data exploration
- **Visual Charts**: Pie charts, bar charts, and geographic distributions
- **Statistical Analysis**: Comprehensive metrics and insights
- **Search & Filter**: Easy persona discovery and filtering
- **Export Options**: Multiple download formats (JSON, CSV)

### 🎨 User Experience
- **Modern UI**: Beautiful, responsive interface with custom styling
- **Interactive Elements**: Hover effects, animations, and dynamic content
- **Progress Indicators**: Clear feedback during data processing
- **Mobile Friendly**: Works on desktop and mobile devices

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Installation

1. **Clone or download the project files**
   ```bash
   git clone <repository-url>
   cd customer-persona-generator
   ```

2. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run persona_generator.py
   ```

4. **Open your browser**
   - The app will automatically open at `http://localhost:8501`
   - If not, manually navigate to the URL shown in your terminal

## 📋 Data Format

### Required Columns
Your data should include these types of columns:

- **Customer Identification**: `customer_id`, `customer_unique_id`
- **Location Data**: `customer_city`, `customer_zip_code_prefix`
- **Interest Indicators**: Columns with "Interested in" or similar patterns
- **Behavioral Data**: Frequency, preferences, habits
- **Style Information**: Fashion preferences, style choices

### Sample Data Format
```csv
customer_id,customer_city,customer_zip_code_prefix,Interested in Fashion,Style Preference,Streaming Frequency,Favorite Platform,Buys Merch
abc123,New York,10001,Yes,Streetwear,Weekly,Netflix,Yes
def456,Los Angeles,90210,No,Casual,Monthly,Hulu,No
ghi789,Chicago,60601,Yes,Vintage,Daily,Disney+,Yes
```

### Supported Interest Categories
The system automatically detects and categorizes:
- **Fashion & Style**: Clothing preferences, fashion trends
- **Beauty & Skincare**: J-beauty, skincare routines, cosmetics
- **Entertainment**: Anime, streaming, movies, shows
- **Lifestyle**: Food, culture, daily routines
- **Social Media**: Influencers, platforms, trends
- **Collecting**: Merchandise, collectibles, items

## 📊 Application Sections

### 1. 📊 Overview Tab
- **Key Metrics**: Total customers, categories, cities covered
- **Visual Charts**: Category distribution, interest analysis
- **Quick Statistics**: High-level insights about your customer base

### 2. 👥 Personas Tab
- **Detailed Personas**: Individual customer profiles with narratives
- **Search Functionality**: Find specific personas quickly
- **Category Filtering**: Filter by persona types
- **Individual Export**: Download specific persona data

### 3. 📈 Analytics Tab
- **Geographic Distribution**: Customer locations and concentrations
- **Category Analysis**: Detailed breakdown of customer segments
- **Interest Patterns**: Most common interests and behaviors
- **Trend Analysis**: Behavioral patterns across your customer base

### 4. 📋 Raw Data Tab
- **Original Data View**: Complete uploaded dataset
- **Export Options**: Download all personas, statistics, or CSV reports
- **Data Validation**: View processed vs. original data

## 🎯 Persona Categories

The system automatically categorizes customers into:

- **Fash
