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
        self.df = None
        self.personas = []
        self.columns = []
        self.definitions = {
            "Beauty-Focused Minimalist": {
                "emoji": "🧴",
                "criteria": ["j_beauty", "daily_routine"],
                "description": "Loves Japanese beauty and skincare routines.",
                "tags": ["beauty", "care"],
                "product_recommendations": ["Japanese Cleansing Oil", "Hydrating Essence", "Sheet Masks", "Gentle Foaming Cleanser", "Ceramide Moisturizer"]
            },
            "Trend-Savvy Fashionista": {
                "emoji": "💅",
                "criteria": ["j_fashion", "style_preference", "fashion_frequency"],
                "description": "Passionate about fashion and modern Japanese style.",
                "tags": ["fashion"],
                "product_recommendations": ["Harajuku Style Hoodie", "Kimono Cardigan", "Statement Sneakers", "Graphic T-shirts", "Unique Accessories"]
            },
            "Pop Culture Power User": {
                "emoji": "📱",
                "criteria": ["follows_influencers", "streams_often", "buys_merch"],
                "description": "Follows influencers and loves trends.",
                "tags": ["trend", "influencer"],
                "product_recommendations": ["Anime Figurines", "Manga Series", "Limited Edition Merchandise", "Gaming Headsets", "Collectible Art Books"]
            },
            # Adding a new persona for "Style Seeker" as requested in the prompt
            "Style Seeker": {
                "emoji": "👗",
                "criteria": ["j_fashion", "style_preference"],
                "description": "Always looking for the latest fashion trends and unique styles.",
                "tags": ["fashion", "style"],
                "product_recommendations": ["Streetwear Jeans", "Designer T-shirts", "Vintage Jackets", "Stylish Footwear", "Fashion Magazines"]
            }
        }

    def load_data(self, file):
        self.df = pd.read_csv(file)
        self.df.columns = self.df.columns.str.strip().str.lower()
        self.columns = list(self.df.columns)
        return not self.df.empty

    def extract_tags(self, row):
        tags = set()
        row = {k.strip().lower(): str(v).strip().lower() for k, v in row.items()}

        if row.get("interested in j-beauty", '') in ['yes', 'true', '1']:
            tags.add("j_beauty")
        if row.get("daily routine", '') in ['yes', 'true', '1', 'defined', 'structured']:
            tags.add("daily_routine")
        if row.get("j-fashion style", '') in ['yes', 'true', '1']:
            tags.add("j_fashion")
        if any(x in row.get("style preference", '') for x in ['kawaii', 'modern', 'street', 'streetwear']):
            tags.add("style_preference")
        if row.get("fashion frequency", '') in ['frequent', 'weekly', 'daily', 'often']:
            tags.add("fashion_frequency")
        if row.get("follow fashion influencers", '') in ['yes', 'true', '1']:
            tags.add("follows_influencers")
        if row.get("streaming frequency", '') in ['daily', 'weekly', 'frequent', 'often']:
            tags.add("streams_often")
        if row.get("buys merch", '') in ['yes', 'true', '1', 'frequently', 'often']:
            tags.add("buys_merch")

        return tags

    def assign_persona(self, tags):
        best = ("Unclassified", 0)
        for name, config in self.definitions.items():
            score = sum(1 for c in config['criteria'] if c in tags)
            if score > best[1]:
                best = (name, score)
        return best[0] if best[1] > 0 else "Unclassified"

    def process(self):
        self.personas = []
        for _, row in self.df.iterrows():
            tags = self.extract_tags(row)
            persona = self.assign_persona(tags)
            entry = {
                "customer_id": row.get("customer_id", ""),
                "city": row.get("customer_city", "Unknown"),
                "zip": row.get("customer_zip_code_prefix", "-"),
                "phone": row.get("phone number", "N/A"),
                "persona": persona,
                "emoji": self.definitions.get(persona, {}).get("emoji", "❓"),
                "description": self.definitions.get(persona, {}).get("description", "Not matched"),
                "tags": list(tags),
                "product_recommendations": self.definitions.get(persona, {}).get("product_recommendations", ["No specific recommendations"])
            }
            self.personas.append(entry)

    def get_stats(self):
        counter = Counter([p['persona'] for p in self.personas])
        return counter

    def to_df(self):
        return pd.DataFrame(self.personas)

    def grouped_by_persona(self):
        df = self.to_df()
        return df.groupby('persona')

    def export_template(self):
        columns = [
            "customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city", "phone_number",
            "Interested in J-beauty", "Daily Routine", "Anime Collector", "J-fashion Style",
            "Interested in Japanese Snacks", "Streaming Frequency", "Favorite Platform",
            "Buys Merch", "Style Preference", "Fashion Frequency", "Follow Fashion Influencers"
        ]
        df = pd.DataFrame(columns=columns)
        return df

st.title("Customer Persona Profiler")
st.markdown("Analyze your customers and assign personas.")

engine = PersonaEngine()
file = st.file_uploader("Upload your customer CSV file", type="csv")

if file:
    if engine.load_data(file):
        engine.process()
        df_result = engine.to_df()
        stats = engine.get_stats()

        tab1, tab2 = st.tabs(["📊 Overview", "👥 Persona Details"])

        with tab1:
            st.header("📊 Overview")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("👥 Persona Distribution")
                fig_persona = px.pie(names=list(stats.keys()), values=list(stats.values()), title="Persona Breakdown")
                st.plotly_chart(fig_persona, use_container_width=True)

            with col2:
                st.subheader("📍 Customer Location")
                if 'city' in df_result.columns and not df_result['city'].empty:
                    city_counts = df_result['city'].value_counts().reset_index()
                    city_counts.columns = ['City', 'Count']
                    fig_city = px.pie(city_counts, names='City', values='Count', title="Customers by City")
                    st.plotly_chart(fig_city, use_container_width=True)
                else:
                    st.info("No city data available or 'customer_city' column not found in the uploaded file.")

        with tab2:
            st.header("👥 Detailed Persona Assignments")
            grouped = engine.grouped_by_persona()
            for persona, group in grouped:
                st.subheader(f"{group.iloc[0]['emoji']} {persona} ({len(group)} customers)")
                st.write(f"**Description:** {group.iloc[0]['description']}")
                st.write(f"**Recommended Products:** {', '.join(group.iloc[0]['product_recommendations'])}")
                st.dataframe(group[['customer_id', 'city', 'zip', 'phone', 'tags']].reset_index(drop=True))

    else:
        st.error("Failed to read the uploaded file.")

# Footer section
st.markdown("---")
st.markdown("© 2025 Dorenth | Made using Python 🐍", unsafe_allow_html=True)
