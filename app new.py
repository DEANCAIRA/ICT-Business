# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import plotly.express as px
import json

st.set_page_config(
    page_title="Customer Persona Generator",
    layout="wide"
)

class PersonaEngine:
    def __init__(self):
        """
        Initializes the PersonaEngine.
        The persona definitions are now hardcoded to the three requested personas.
        """
        self.df = None
        self.personas = []
        self.columns = []
        # Updated persona definitions as per your request
        self.definitions = {
            "Fashion Devotee": {
                "emoji": "�",
                "criteria": ["fashion_lover"],
                "description": "Passionate about the latest fashion trends, with a keen interest in unique and stylish apparel.",
                "tags": ["fashion", "style", "apparel"],
                "product_recommendations": ["Limited Edition Sneakers", "Designer Handbags", "Vintage Jackets", "Personal Styling Session", "Fashion Magazine Subscription"]
            },
            "Beauty Maven": {
                "emoji": "💄",
                "criteria": ["beauty_lover"],
                "description": "A skincare and makeup enthusiast, dedicated to a daily beauty regimen and discovering new products.",
                "tags": ["beauty", "skincare", "cosmetics"],
                "product_recommendations": ["Advanced Skincare Serum", "Luxury Foundation", "Artisan Makeup Brushes", "LED Therapy Mask", "Beauty Box Subscription"]
            },
            "Japanese Lover": {
                "emoji": "🇯🇵",
                "criteria": ["japan_lover"],
                "description": "Deeply interested in Japanese pop culture, including anime, manga, music, and snacks.",
                "tags": ["anime", "manga", "j-pop", "snacks", "japan"],
                "product_recommendations": ["Rare Anime Figurines", "Complete Manga Series Box Set", "Japanese Snack Box Subscription", "Tickets to a Comic Convention", "J-Pop Concert Tickets"]
            }
        }

    def load_data(self, file):
        """
        Loads data from an uploaded CSV file.
        It cleans column names to be lowercase and stripped of whitespace.
        """
        try:
            self.df = pd.read_csv(file)
            # Standardize column names
            self.df.columns = self.df.columns.str.strip().str.lower()
            self.columns = list(self.df.columns)
            return not self.df.empty
        except Exception as e:
            st.error(f"Error loading CSV file: {e}")
            return False

    def extract_tags(self, row):
        """
        Extracts relevant tags from a single row of customer data.
        This function now specifically looks for keywords in preference-based columns 
        (like 'interests' and 'product_category') to ensure more accurate persona assignment.
        """
        tags = set()
        
        # --- More Accurate Persona Assignment ---
        # Define columns that indicate customer preference from your questionnaire
        preference_columns = ['interests', 'product_category']
        
        # Build a single string from preference columns only
        preference_text = ' '.join(str(row.get(col, '')).lower() for col in preference_columns)

        # Keywords for each persona
        fashion_keywords = ['fashion', 'style', 'apparel', 'clothing', 'outfit', 'brand']
        beauty_keywords = ['beauty', 'skincare', 'cosmetics', 'makeup', 'routine', 'serum', 'lipstick']
        japan_keywords = ['japan', 'anime', 'manga', 'j-pop', 'sushi', 'ramen', 'kawaii', 'tokyo', 'snack']

        # Check for keywords within the specific preference text
        if any(keyword in preference_text for keyword in fashion_keywords):
            tags.add("fashion_lover")
        
        if any(keyword in preference_text for keyword in beauty_keywords):
            tags.add("beauty_lover")
            
        if any(keyword in preference_text for keyword in japan_keywords):
            tags.add("japan_lover")
            
        return tags

    def assign_persona(self, tags):
        """
        Assigns a persona to a customer based on the extracted tags.
        It finds the best match from the defined personas.
        If a customer matches multiple personas, it will be assigned to the first one it matches based on the definition order.
        """
        # This simple approach assigns the first persona that matches.
        for name, config in self.definitions.items():
            if any(c in tags for c in config['criteria']):
                return name
        return "Unclassified"

    def process(self):
        """
        Processes the entire dataframe to assign a persona to each customer.
        """
        self.personas = []
        if self.df is None:
            return

        for _, row in self.df.iterrows():
            tags = self.extract_tags(row)
            persona_name = self.assign_persona(tags)
            
            persona_info = self.definitions.get(persona_name, {})
            
            # Use a default dictionary for unclassified personas
            if not persona_info:
                persona_info = {
                    "emoji": "❓",
                    "description": "Not enough data to classify.",
                    "product_recommendations": ["General Store Voucher"],
                    "tags": []
                }
            
            # --- Improved Demographic Data Extraction ---
            # Added more fallbacks to find the correct columns for demographic data.
            entry = {
                "customer_id": row.get("customer_id", row.get("customer_unique_id", _)),
                "city": row.get("city", row.get("customer_city", row.get("city_of_residence", "Unknown"))),
                "age": row.get("age", "N/A"),
                "email": row.get("email", "N/A"),
                "phone": row.get("phone number", row.get("whatsapp_number", "N/A")),
                "persona": persona_name,
                "emoji": persona_info.get("emoji"),
                "description": persona_info.get("description"),
                "product_recommendations": persona_info.get("product_recommendations"),
                "tags": list(tags)
            }
            self.personas.append(entry)

    def get_stats(self):
        """
        Calculates the distribution of the generated personas.
        """
        counter = Counter([p['persona'] for p in self.personas])
        return counter

    def to_df(self):
        """
        Converts the list of persona assignments to a pandas DataFrame.
        """
        return pd.DataFrame(self.personas)

    def grouped_by_persona(self):
        """
        Groups the resulting DataFrame by the assigned persona name.
        """
        df = self.to_df()
        if 'persona' in df.columns:
            return df.groupby('persona')
        return None

# --- Streamlit UI ---

st.title("Customer Persona Profiler")
st.markdown("Upload your customer CSV file to automatically group them into defined personas.")

# Instantiate the engine
engine = PersonaEngine()

# File uploader
file = st.file_uploader("Upload your customer CSV file", type="csv")

if file:
    if engine.load_data(file):
        # Process the data and generate personas
        engine.process()
        df_result = engine.to_df()
        stats = engine.get_stats()

        tab1, tab2 = st.tabs(["📊 Overview", "👥 Persona Details"])

        with tab1:
            st.header("📊 Overview")
            
            if not df_result.empty:
                total_customers = len(df_result)
                unclassified = stats.get("Unclassified", 0)
                st.metric("Total Customers Processed", f"{total_customers}")
                st.metric("Unclassified Customers", f"{unclassified} ({(unclassified/total_customers)*100:.1f}%)")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("👥 Persona Distribution")
                if stats:
                    filtered_stats = {k: v for k, v in stats.items() if k != "Unclassified"}
                    if filtered_stats:
                        fig_persona = px.pie(
                            names=list(filtered_stats.keys()), 
                            values=list(filtered_stats.values()), 
                            title="Persona Breakdown"
                        )
                        st.plotly_chart(fig_persona, use_container_width=True)
                    else:
                        st.info("No customers were classified into the defined personas.")
                else:
                    st.info("No data to display.")

            with col2:
                st.subheader("📍 Customer Location")
                if 'city' in df_result.columns and not df_result['city'].dropna().empty:
                    city_counts = df_result['city'].value_counts().nlargest(10).reset_index()
                    city_counts.columns = ['City', 'Count']
                    fig_city = px.bar(city_counts, x='City', y='Count', title="Top 10 Cities by Customer Count")
                    st.plotly_chart(fig_city, use_container_width=True)
                else:
                    st.info("No city data found to display.")

        with tab2:
            st.header("👥 Detailed Persona Assignments")
            
            grouped = engine.grouped_by_persona()
            if grouped:
                persona_order = list(engine.definitions.keys()) + ["Unclassified"]
                for persona_name in persona_order:
                    if persona_name in grouped.groups:
                        group = grouped.get_group(persona_name)
                        st.subheader(f"{group.iloc[0]['emoji']} {persona_name} ({len(group)} customers)")
                        st.write(f"**Description:** {group.iloc[0]['description']}")
                        st.write(f"**Recommended Products:** {', '.join(group.iloc[0]['product_recommendations'])}")
                        
                        # --- Enhanced Details View ---
                        # Displaying more demographic info to verify data capture.
                        display_cols = ['customer_id', 'city', 'age', 'email', 'phone', 'tags']
                        cols_to_show = [col for col in display_cols if col in group.columns]
                        st.dataframe(group[cols_to_show].reset_index(drop=True))
            else:
                st.warning("Could not group personas. The result data might be empty.")

    else:
        st.error("The uploaded file could not be processed. Please ensure it is a valid CSV file.")

# The problematic footer has been removed to prevent encoding errors.
�
