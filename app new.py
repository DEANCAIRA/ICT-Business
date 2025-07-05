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
                "description": "Loves Japanese beauty and skincare routines, preferring a minimalist approach with high-quality products.",
                "tags": ["beauty", "care"],
                "recommendations": [
                    "Biore UV Aqua Rich Watery Essence (Sunscreen)",
                    "Hada Labo Gokujyun Hyaluronic Acid Lotion (Hydrating Lotion)",
                    "Melano CC Intensive Anti-Spot Essence (Vitamin C Serum)",
                    "Canmake Mermaid Skin Gel UV (Sunscreen)",
                    "Shiseido Fino Premium Touch Hair Mask (Hair Treatment)",
                    "Senka Perfect Whip Cleansing Foam (Facial Cleanser)",
                    "Keana Nadeshiko Rice Mask (Face Mask)",
                    "Products from ILEM JAPAN, MUJI, and Minimalist brands for essential skincare."
                ]
            },
            "Trend-Savvy Fashionista": {
                "emoji": "💅",
                "criteria": ["j_fashion", "style_preference", "fashion_frequency"],
                "description": "Passionate about fashion and modern Japanese style, always looking for the latest trends.",
                "tags": ["fashion"],
                "recommendations": [
                    "Apparel from popular Japanese brands like Sacai, Comme des Garçons, AMBUSH, Hysteric Glamour, AURALEE, Doublet, SS Stein.",
                    "Affordable and trendy items from UNIQLO, GU, and BEAMS.",
                    "Streetwear collections from Neighborhood, Needles, and WTAPS.",
                    "Unique designs from Issey Miyake and Yohji Yamamoto.",
                    "Iconic streetwear pieces from BAPE and Undercover."
                ]
            },
            "Pop Culture Power User": {
                "emoji": "📱",
                "criteria": ["follows_influencers", "streams_often", "buys_merch"],
                "description": "Follows influencers, streams frequently, and loves collecting merchandise from popular Japanese pop culture.",
                "tags": ["trend", "influencer"],
                "recommendations": [
                    "Anime figures (e.g., from series like Demon Slayer, My Hero Academia, Jujutsu Kaisen)",
                    "Official merchandise (T-shirts, hoodies, keychains, plushies) from popular anime/manga (e.g., Attack on Titan, Naruto, One Piece).",
                    "Manga volumes and light novels.",
                    "Exclusive items from stores like BoxLunch, Hot Topic, Crunchyroll Store, Atsuko, Kyou Hobby Shop, and Anime Kaika.",
                    "Collectibles inspired by Studio Ghibli films or popular video games like Genshin Impact."
                ]
            }
        }

    def load_data(self, file):
        self.df = pd.read_csv(file)
        # Normalize column names: lowercase, strip spaces, replace spaces with underscores
        self.df.columns = self.df.columns.str.strip().str.lower().str.replace(' ', '_')
        self.columns = self.df.columns.tolist()

    def assign_persona(self, customer_data):
        assigned_personas = []
        customer_tags = self.extract_tags(customer_data)

        for persona_name, persona_info in self.definitions.items():
            criteria_met = all(tag in customer_tags for tag in persona_info["criteria"])
            if criteria_met:
                assigned_personas.append(persona_name)
        return assigned_personas if assigned_personas else ["Unassigned"]

    def extract_tags(self, customer_data):
        tags = []
        # Extract tags based on normalized column names and expected values (e.g., 1 for true)
        if 'interested_in_j-beauty' in customer_data and customer_data['interested_in_j-beauty'] == 1:
            tags.append('j_beauty')
        if 'daily_routine' in customer_data and customer_data['daily_routine'] == 1:
            tags.append('daily_routine')
        if 'j-fashion_style' in customer_data and customer_data['j-fashion_style'] == 1:
            tags.append('j_fashion')
        if 'style_preference' in customer_data and customer_data['style_preference'] == 1:
            tags.append('style_preference')
        if 'fashion_frequency' in customer_data and customer_data['fashion_frequency'] == 1:
            tags.append('fashion_frequency')
        if 'follows_fashion_influencers' in customer_data and customer_data['follows_fashion_influencers'] == 1:
            tags.append('follows_influencers')
        if 'streaming_frequency' in customer_data and customer_data['streaming_frequency'] == 1:
            tags.append('streams_often')
        if 'buys_merch' in customer_data and customer_data['buys_merch'] == 1:
            tags.append('buys_merch')
        return tags

    def run_analysis(self):
        if self.df is None:
            return None

        # Ensure 'persona' column exists and is assigned
        if 'persona' not in self.df.columns:
            self.df['persona'] = self.df.apply(lambda row: self.assign_persona(row), axis=1)
            # Take the first assigned persona if multiple, or keep as list for multi-persona assignment
            self.df['persona'] = self.df['persona'].apply(lambda x: x[0] if x else 'Unassigned')


        persona_counts = self.df['persona'].value_counts()
        return persona_counts.to_dict()

    def grouped_by_persona(self):
        if self.df is None:
            return []

        grouped = self.df.groupby('persona')
        result = []
        for persona, group in grouped:
            emoji = self.definitions.get(persona, {}).get('emoji', '❓')
            group_with_emoji = group.copy()
            group_with_emoji['emoji'] = emoji
            result.append((persona, group_with_emoji))
        return result


st.title("Customer Persona Generator & Product Recommender")

engine = PersonaEngine()

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    try:
        engine.load_data(uploaded_file)
        st.success("File uploaded and data loaded successfully!")

        st.sidebar.header("Data Preview")
        st.sidebar.dataframe(engine.df.head())

        if st.sidebar.button("Run Persona Analysis"):
            stats = engine.run_analysis()

            tab1, tab2 = st.tabs(["📊 Dashboard", "👥 Detailed Persona Assignments"])

            with tab1:
                st.header("📊 Persona Overview")
                if stats:
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("👥 Persona Distribution")
                        fig_persona = px.pie(names=list(stats.keys()), values=list(stats.values()), title="Persona Breakdown")
                        st.plotly_chart(fig_persona, use_container_width=True)

                    with col2:
                        st.subheader("📍 Customer Location")
                        # Adjust column names for display if they exist after normalization
                        city_col = next((col for col in ['customer_city', 'city'] if col in engine.df.columns), None)
                        if city_col and not engine.df[city_col].empty:
                            city_counts = engine.df[city_col].value_counts().reset_index()
                            city_counts.columns = ['City', 'Count']
                            fig_city = px.pie(city_counts, names='City', values='Count', title="Customers by City")
                            st.plotly_chart(fig_city, use_container_width=True)
                        else:
                            st.info("No city data available or relevant city column not found in the uploaded file.")
                else:
                    st.error("Failed to generate persona statistics. Please check your file format and content.")

            with tab2:
                st.header("👥 Detailed Persona Assignments and Product Recommendations")
                grouped = engine.grouped_by_persona()
                if grouped:
                    for persona, group in grouped:
                        st.subheader(f"{group.iloc[0]['emoji']} {persona} ({len(group)} customers)")
                        
                        # Select relevant display columns, adjusting for normalized names
                        display_cols = ['customer_id', 'tags']
                        if 'customer_city' in group.columns:
                            display_cols.insert(1, 'customer_city')
                        elif 'city' in group.columns:
                            display_cols.insert(1, 'city')
                        
                        if 'customer_zip_code_prefix' in group.columns:
                            display_cols.insert(2, 'customer_zip_code_prefix')
                        elif 'zip' in group.columns:
                            display_cols.insert(2, 'zip')

                        st.dataframe(group[display_cols].reset_index(drop=True))

                        # Display product recommendations
                        if persona in engine.definitions and "recommendations" in engine.definitions[persona]:
                            st.markdown(f"**💡 Product Recommendations for {persona}:**")
                            for rec in engine.definitions[persona]["recommendations"]:
                                st.write(f"- {rec}")
                        st.markdown("---") # Separator
                else:
                    st.info("No detailed persona assignments to display. Please run the analysis.")

    except Exception as e:
        st.error(f"Failed to read the uploaded file: {e}. Please ensure it's a valid CSV.")

# Footer (optional)
st.markdown("---")
st.markdown("Developed by Your Name/Company")
