import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re

# Set page config
st.set_page_config(
    page_title="Customer Persona Generator",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .persona-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .persona-header {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .persona-detail {
        margin: 5px 0;
        font-size: 16px;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin: 5px;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
</style>
""", unsafe_allow_html=True)

class CustomerPersonaGenerator:
    def __init__(self):
        self.df = None
        self.personas = []
    
    def load_data(self, uploaded_file):
        """Load and process uploaded customer data"""
        try:
            if uploaded_file.name.endswith('.csv'):
                self.df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                self.df = pd.read_excel(uploaded_file)
            else:
                st.error("Please upload a CSV or Excel file")
                return False
            
            # Clean column names
            self.df.columns = self.df.columns.str.strip()
            
            # Basic data validation
            if self.df.empty:
                st.error("The uploaded file is empty")
                return False
            
            st.success(f"Data loaded successfully! {len(self.df)} customers found.")
            return True
            
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return False
    
    def analyze_customer_interests(self, row):
        """Analyze customer interests and behaviors"""
        interests = []
        behaviors = []
        preferences = {}
        
        # Extract interests and behaviors from all columns
        for col, value in row.items():
            if pd.isna(value):
                continue
                
            col_lower = col.lower()
            value_str = str(value).strip()
            
            # Interest detection
            if 'interest' in col_lower or 'like' in col_lower:
                if value_str.lower() in ['yes', 'true', '1'] or value_str.lower() not in ['no', 'false', '0', 'nan']:
                    interests.append(col.replace('Interested in ', '').replace('_', ' '))
            
            # Behavior patterns
            if 'frequency' in col_lower:
                preferences['frequency'] = value_str
            elif 'platform' in col_lower:
                preferences['platform'] = value_str
            elif 'style' in col_lower:
                preferences['style'] = value_str
            elif 'routine' in col_lower:
                preferences['routine'] = value_str
            elif 'merch' in col_lower:
                preferences['buys_merch'] = value_str
            elif 'follow' in col_lower:
                preferences['follows_influencers'] = value_str
        
        return interests, behaviors, preferences
    
    def generate_persona_description(self, customer_data, interests, preferences):
        """Generate a narrative persona description"""
        name = f"Customer {customer_data.get('customer_id', 'Unknown')[:8]}"
        city = customer_data.get('customer_city', 'Unknown City')
        
        # Base description
        description = f"Meet {name}, a customer from {city}. "
        
        # Add interests
        if interests:
            if len(interests) == 1:
                description += f"They are passionate about {interests[0]}. "
            else:
                description += f"They have diverse interests including {', '.join(interests[:-1])} and {interests[-1]}. "
        
        # Add behavioral patterns
        if preferences.get('frequency'):
            description += f"They engage with content {preferences['frequency'].lower()}. "
        
        if preferences.get('platform'):
            description += f"Their preferred platform is {preferences['platform']}. "
        
        if preferences.get('style'):
            description += f"Their style preference leans towards {preferences['style']}. "
        
        if preferences.get('follows_influencers') == 'Yes':
            description += "They actively follow fashion influencers. "
        
        if preferences.get('buys_merch') == 'Yes':
            description += "They frequently purchase merchandise. "
        
        return description
    
    def categorize_persona(self, interests, preferences):
        """Categorize persona into predefined types"""
        categories = {
            'Fashion Enthusiast': ['fashion', 'style', 'streetwear', 'clothing'],
            'Beauty Lover': ['beauty', 'j-beauty', 'skincare', 'makeup'],
            'Entertainment Fan': ['anime', 'streaming', 'netflix', 'entertainment'],
            'Lifestyle Enthusiast': ['snacks', 'japanese', 'culture', 'lifestyle'],
            'Trendsetter': ['influencers', 'social media', 'trends'],
            'Collector': ['collector', 'merch', 'merchandise', 'items']
        }
        
        scores = {}
        interest_str = ' '.join(interests).lower()
        pref_str = ' '.join([str(v) for v in preferences.values()]).lower()
        combined_text = interest_str + ' ' + pref_str
        
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            if score > 0:
                scores[category] = score
        
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        else:
            return 'General Consumer'
    
    def generate_personas(self):
        """Generate personas for all customers"""
        if self.df is None:
            return False
        
        self.personas = []
        
        for idx, row in self.df.iterrows():
            interests, behaviors, preferences = self.analyze_customer_interests(row)
            
            persona = {
                'customer_id': row.get('customer_id', f'customer_{idx}'),
                'customer_unique_id': row.get('customer_unique_id', ''),
                'location': {
                    'city': row.get('customer_city', 'Unknown'),
                    'zip_code': row.get('customer_zip_code_prefix', 'Unknown')
                },
                'interests': interests,
                'preferences': preferences,
                'category': self.categorize_persona(interests, preferences),
                'description': self.generate_persona_description(row, interests, preferences),
                'raw_data': row.to_dict()
            }
            
            self.personas.append(persona)
        
        return True
    
    def get_persona_statistics(self):
        """Get statistics about generated personas"""
        if not self.personas:
            return {}
        
        categories = [persona['category'] for persona in self.personas]
        cities = [persona['location']['city'] for persona in self.personas]
        
        stats = {
            'total_personas': len(self.personas),
            'categories': dict(Counter(categories)),
            'cities': dict(Counter(cities)),
            'top_interests': self.get_top_interests()
        }
        
        return stats
    
    def get_top_interests(self):
        """Get most common interests across all personas"""
        all_interests = []
        for persona in self.personas:
            all_interests.extend(persona['interests'])
        
        return dict(Counter(all_interests).most_common(10))

def main():
    st.title("🎯 Customer Persona Generator")
    st.markdown("Upload your customer data and generate detailed personas automatically!")
    
    # Initialize the generator
    if 'generator' not in st.session_state:
        st.session_state.generator = CustomerPersonaGenerator()
    
    # Sidebar for file upload
    with st.sidebar:
        st.header("📤 Upload Data")
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload your customer data file with columns like customer_id, customer_city, interests, etc."
        )
        
        if uploaded_file is not None:
            if st.button("🔄 Process Data"):
                with st.spinner("Loading and processing data..."):
                    if st.session_state.generator.load_data(uploaded_file):
                        with st.spinner("Generating personas..."):
                            if st.session_state.generator.generate_personas():
                                st.success("✅ Personas generated successfully!")
                                st.rerun()
        
        st.markdown("---")
        st.markdown("### 📋 Data Format Example")
        st.code("""
customer_id,customer_city,Interested in Fashion,
Style Preference,Streaming Frequency
abc123,New York,Yes,Streetwear,Weekly
def456,Los Angeles,No,Casual,Monthly
        """)
    
    # Main content area
    if st.session_state.generator.df is not None:
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "👥 Personas", "📈 Analytics", "📋 Raw Data"])
        
        with tab1:
            st.header("📊 Data Overview")
            
            # Statistics
            stats = st.session_state.generator.get_persona_statistics()
            
            if stats:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Customers", stats['total_personas'])
                
                with col2:
                    st.metric("Unique Categories", len(stats['categories']))
                
                with col3:
                    st.metric("Cities Covered", len(stats['cities']))
                
                with col4:
                    st.metric("Total Interests", len(stats['top_interests']))
                
                # Charts
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Customer Categories")
                    if stats['categories']:
                        fig_cat = px.pie(
                            values=list(stats['categories'].values()),
                            names=list(stats['categories'].keys()),
                            title="Distribution of Customer Categories"
                        )
                        st.plotly_chart(fig_cat, use_container_width=True)
                
                with col2:
                    st.subheader("Top Interests")
                    if stats['top_interests']:
                        fig_int = px.bar(
                            x=list(stats['top_interests'].keys())[:8],
                            y=list(stats['top_interests'].values())[:8],
                            title="Most Common Customer Interests"
                        )
                        st.plotly_chart(fig_int, use_container_width=True)
        
        with tab2:
            st.header("👥 Customer Personas")
            
            if st.session_state.generator.personas:
                # Search and filter
                search_term = st.text_input("🔍 Search personas", placeholder="Search by city, interest, or category...")
                
                category_filter = st.multiselect(
                    "Filter by category",
                    options=list(set(p['category'] for p in st.session_state.generator.personas)),
                    default=[]
                )
                
                # Filter personas
                filtered_personas = st.session_state.generator.personas
                
                if search_term:
                    filtered_personas = [
                        p for p in filtered_personas 
                        if search_term.lower() in str(p).lower()
                    ]
                
                if category_filter:
                    filtered_personas = [
                        p for p in filtered_personas 
                        if p['category'] in category_filter
                    ]
                
                st.write(f"Showing {len(filtered_personas)} of {len(st.session_state.generator.personas)} personas")
                
                # Display personas
                for i, persona in enumerate(filtered_personas):
                    with st.expander(f"👤 {persona['category']} - {persona['location']['city']} ({persona['customer_id'][:8]}...)"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"**📝 Description:**")
                            st.write(persona['description'])
                            
                            if persona['interests']:
                                st.markdown(f"**🎯 Interests:** {', '.join(persona['interests'])}")
                            
                            if persona['preferences']:
                                st.markdown("**⚙️ Preferences:**")
                                for key, value in persona['preferences'].items():
                                    if value and str(value).lower() not in ['nan', 'none']:
                                        st.write(f"• {key.replace('_', ' ').title()}: {value}")
                        
                        with col2:
                            st.markdown(f"**📍 Location:** {persona['location']['city']}")
                            st.markdown(f"**📮 Zip Code:** {persona['location']['zip_code']}")
                            st.markdown(f"**🏷️ Category:** {persona['category']}")
                            
                            # Export individual persona
                            persona_json = json.dumps(persona, indent=2)
                            st.download_button(
                                "📥 Download Persona",
                                persona_json,
                                f"persona_{persona['customer_id'][:8]}.json",
                                "application/json",
                                key=f"download_{i}"
                            )
        
        with tab3:
            st.header("📈 Analytics Dashboard")
            
            stats = st.session_state.generator.get_persona_statistics()
            
            if stats:
                # Geographic distribution
                st.subheader("🗺️ Geographic Distribution")
                if stats['cities']:
                    city_df = pd.DataFrame(list(stats['cities'].items()), columns=['City', 'Count'])
                    fig_geo = px.bar(city_df, x='Count', y='City', orientation='h', 
                                   title="Customer Distribution by City")
                    st.plotly_chart(fig_geo, use_container_width=True)
                
                # Detailed category breakdown
                st.subheader("📊 Category Analysis")
                col1, col2 = st.columns(2)
                
                with col1:
                    if stats['categories']:
                        cat_df = pd.DataFrame(list(stats['categories'].items()), columns=['Category', 'Count'])
                        fig_cat_bar = px.bar(cat_df, x='Category', y='Count', 
                                           title="Customer Count by Category")
                        fig_cat_bar.update_xaxis(tickangle=45)
                        st.plotly_chart(fig_cat_bar, use_container_width=True)
                
                with col2:
                    if stats['top_interests']:
                        int_df = pd.DataFrame(list(stats['top_interests'].items()), columns=['Interest', 'Count'])
                        fig_int_pie = px.pie(int_df, values='Count', names='Interest', 
                                           title="Interest Distribution")
                        st.plotly_chart(fig_int_pie, use_container_width=True)
        
        with tab4:
            st.header("📋 Raw Data")
            
            st.subheader("Original Data")
            st.dataframe(st.session_state.generator.df, use_container_width=True)
            
            st.subheader("Export Options")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Export all personas as JSON
                if st.session_state.generator.personas:
                    all_personas_json = json.dumps(st.session_state.generator.personas, indent=2)
                    st.download_button(
                        "📥 Download All Personas (JSON)",
                        all_personas_json,
                        "all_personas.json",
                        "application/json"
                    )
            
            with col2:
                # Export personas as CSV
                if st.session_state.generator.personas:
                    personas_for_csv = []
                    for persona in st.session_state.generator.personas:
                        row = {
                            'customer_id': persona['customer_id'],
                            'city': persona['location']['city'],
                            'zip_code': persona['location']['zip_code'],
                            'category': persona['category'],
                            'interests': ', '.join(persona['interests']),
                            'description': persona['description']
                        }
                        personas_for_csv.append(row)
                    
                    personas_df = pd.DataFrame(personas_for_csv)
                    csv = personas_df.to_csv(index=False)
                    st.download_button(
                        "📥 Download Personas (CSV)",
                        csv,
                        "personas.csv",
                        "text/csv"
                    )
            
            with col3:
                # Export statistics
                if st.session_state.generator.personas:
                    stats_json = json.dumps(stats, indent=2)
                    st.download_button(
                        "📥 Download Statistics (JSON)",
                        stats_json,
                        "persona_statistics.json",
                        "application/json"
                    )
    
    else:
        # Welcome screen
        st.markdown("""
        ## 🚀 Welcome to Customer Persona Generator!
        
        This tool helps you create detailed customer personas from your data. Here's what it can do:
        
        ### ✨ Features:
        - **📤 Easy Upload**: Support for CSV and Excel files
        - **🤖 Automatic Analysis**: Intelligently extracts interests and behaviors
        - **🎯 Smart Categorization**: Groups customers into meaningful personas
        - **📊 Visual Analytics**: Interactive charts and statistics
        - **📥 Export Options**: Download personas in multiple formats
        
        ### 📋 Getting Started:
        1. Upload your customer data file using the sidebar
        2. Click "Process Data" to generate personas
        3. Explore the different tabs to analyze your customers
        4. Export the results for further use
        
        ### 📊 Sample Data Format:
        Your data should include columns like:
        - Customer ID
        - Location information (city, zip code)
        - Interest indicators (Yes/No columns)
        - Behavioral data (frequency, preferences)
        - Style preferences
        - Platform usage
        
        **Ready to get started? Upload your data using the sidebar! 👈**
        """)

if __name__ == "__main__":
    main()
