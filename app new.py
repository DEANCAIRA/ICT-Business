import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import plotly.express as px

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
            "Fashion Devotee": {
                "emoji": "👗",
                "criteria": ["j_fashion", "style_preference", "fashion_frequency"],
                "description": "Passionate about fashion and Japanese trends.",
                "tags": ["fashion"],
                "product_recommendations": [
                    "Kimono Cardigan", "Harajuku Sneakers", "Kawaii T-shirts", "Streetwear Jacket"
                ]
            },
            "Beauty Maven": {
                "emoji": "💄",
                "criteria": ["j_beauty", "daily_routine", "j_beauty_natural"],
                "description": "Loves beauty routines and Japanese skincare.",
                "tags": ["beauty"],
                "product_recommendations": [
                    "Cleansing Oil", "Face Masks", "Natural Moisturizer", "Serum Set"
                ]
            },
            "Japanese Lover": {
                "emoji": "🎌",
                "criteria": ["follows_influencers", "streams_often", "buys_merch", "anime_collector"],
                "description": "Enthusiast of Japanese culture and media.",
                "tags": ["japan", "otaku", "influencer"],
                "product_recommendations": [
                    "Anime Merchandise", "Drama Subscription", "Cultural Books", "Figurines"
                ]
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
        if "natural" in row.get("j-beauty style", '').lower():
            tags.add("j_beauty_natural")

        if row.get("j-fashion style", '') in ['yes', 'true', '1']:
            tags.add("j_fashion")

        style_pref = row.get("style preference", '').lower()
        if style_pref:
            tags.add("style_preference")

        if row.get("fashion frequency", '') in ['frequent', 'weekly', 'daily', 'often']:
            tags.add("fashion_frequency")

        if row.get("follow fashion influencers", '') in ['yes', 'true', '1']:
            tags.add("follows_influencers")

        if row.get("streaming frequency", '') in ['daily', 'weekly', 'frequent', 'often']:
            tags.add("streams_often")

        if row.get("buys merch", '') in ['yes', 'true', '1', 'frequently', 'often']:
            tags.add("buys_merch")

        if row.get("anime collector", '') in ['yes', 'true', '1']:
            tags.add("anime_collector")

        return tags

    def assign_persona(self, tags):
        main_persona_name = "Unclassified"
        best_score = 0

        for name, config in self.definitions.items():
            score = sum(1 for c in config['criteria'] if c in tags)
            if score > best_score:
                best_score = score
                main_persona_name = name

        return main_persona_name

    def process(self):
        self.personas = []
        all_tags = []

        for _, row in self.df.iterrows():
            tags = self.extract_tags(row)
            all_tags.extend(tags)

            main_persona = self.assign_persona(tags)
            persona_config = self.definitions.get(main_persona, {})
            emoji = persona_config.get("emoji", "❓")
            description = persona_config.get("description", "No description.")
            product_recs = persona_config.get("product_recommendations", [])

            entry = {
                "customer_id": row.get("customer_id", ""),
                "city": row.get("customer_city", "Unknown"),
                "zip": row.get("customer_zip_code_prefix", "-"),
                "phone": row.get("phone number", "N/A"),
                "persona": main_persona,
                "emoji": emoji,
                "description": description,
                "product_recommendations": product_recs,
                "tags": list(tags)
            }
            self.personas.append(entry)

        self.all_extracted_tags_flat = all_tags

    def get_stats(self):
        return Counter([p['persona'] for p in self.personas])

    def get_tag_counts(self, top_n=10):
        return Counter(self.all_extracted_tags_flat).most_common(top_n)

    def to_df(self):
        return pd.DataFrame(self.personas)

    def grouped_by_persona(self):
        df = self.to_df()
        return df.groupby('persona')

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
                if stats:
                    fig_persona = px.pie(names=list(stats.keys()), values=list(stats.values()), title="Persona Breakdown")
                    st.plotly_chart(fig_persona, use_container_width=True)
                else:
                    st.info("No personas assigned yet or data is empty.")

            with col2:
                st.subheader("📍 Customer Location")
                if 'city' in df_result.columns and not df_result['city'].empty:
                    city_counts = df_result['city'].value_counts().reset_index()
                    city_counts.columns = ['City', 'Count']
                    if not city_counts.empty:
                        fig_city = px.pie(city_counts, names='City', values='Count', title="Customers by City")
                        st.plotly_chart(fig_city, use_container_width=True)
                    else:
                        st.info("No city data to display.")
                else:
                    st.info("No 'customer_city' column found or it is empty in the uploaded file.")

        with tab2:
            st.header("👥 Detailed Persona Assignments")
            grouped = engine.grouped_by_persona()
            for persona_name, group in grouped:
                st.subheader(f"{group.iloc[0]['emoji']} {persona_name} ({len(group)} customers)")
                st.write(f"**Description:** {group.iloc[0]['description']}")
                st.write(f"**Recommended Products:** {', '.join(group.iloc[0]['product_recommendations'])}")
                st.dataframe(group[['customer_id', 'city', 'zip', 'phone', 'tags']].reset_index(drop=True))
    else:
        st.error("Failed to read the uploaded file.")

st.markdown("---")
st.markdown("© 2025 Dorenth | Made using Python 🐍", unsafe_allow_html=True)
