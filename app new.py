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
        # Reverting to hardcoded definitions and adding sub-personas
        self.definitions = {
            "Beauty-Focused Minimalist": {
                "emoji": "🧴",
                "criteria": ["j_beauty", "daily_routine"],
                "description": "Loves Japanese beauty and skincare routines.",
                "tags": ["beauty", "care"],
                "product_recommendations": ["Japanese Cleansing Oil", "Hydrating Essence", "Sheet Masks", "Gentle Foaming Cleanser", "Ceramide Moisturizer"],
                "sub_personas": {
                    "Skincare Enthusiast": {
                        "emoji": "💧",
                        "criteria": ["daily_routine"],
                        "description": "Dedicated to a multi-step skincare regimen.",
                        "product_recommendations": ["Vitamin C Serum", "Retinol Cream", "Facial Massager"]
                    },
                    "Natural Beauty Seeker": {
                        "emoji": "🌿",
                        "criteria": ["j_beauty_natural"], # Assuming a more specific tag for natural preference
                        "description": "Prefers natural and organic beauty products.",
                        "product_recommendations": ["Green Tea Face Mask", "Rice Bran Cleanser", "Aloe Vera Gel"]
                    }
                }
            },
            "Trend-Savvy Fashionista": {
                "emoji": "💅",
                "criteria": ["j_fashion", "style_preference", "fashion_frequency"],
                "description": "Passionate about fashion and modern Japanese style.",
                "tags": ["fashion"],
                "product_recommendations": ["Harajuku Style Hoodie", "Kimono Cardigan", "Statement Sneakers", "Graphic T-shirts", "Unique Accessories"],
                "sub_personas": {
                    "Harajuku Chic Enthusiast": {
                        "emoji": "🎀",
                        "criteria": ["style_preference_kawaii"],
                        "description": "Loves vibrant and playful Harajuku fashion.",
                        "product_recommendations": ["Kawaii Accessories", "Platform Shoes", "Colorful Hair Dye"]
                    },
                    "Streetwear Aesthete": {
                        "emoji": "👟",
                        "criteria": ["style_preference_streetwear"],
                        "description": "Prefers edgy and comfortable Japanese streetwear.",
                        "product_recommendations": ["Oversized Graphic Tees", "Utility Pants", "Limited Edition Sneakers"]
                    },
                    "Traditional Modernist": {
                        "emoji": "👘",
                        "criteria": ["style_preference_traditional_modern"],
                        "description": "Appreciates modern interpretations of traditional Japanese attire.",
                        "product_recommendations": ["Modern Kimono", "Haori Jacket", "Tabi Boots"]
                    }
                }
            },
            "Pop Culture Power User": {
                "emoji": "📱",
                "criteria": ["follows_influencers", "streams_often", "buys_merch"],
                "description": "Follows influencers and loves trends.",
                "tags": ["trend", "influencer"],
                "product_recommendations": ["Anime Figurines", "Manga Series", "Limited Edition Merchandise", "Gaming Headsets", "Collectible Art Books"],
                "sub_personas": {
                    "Anime & Manga Collector": {
                        "emoji": "📚",
                        "criteria": ["anime_collector"], # Assuming this can be a direct tag from data
                        "description": "Enthusiastic collector of anime and manga.",
                        "product_recommendations": ["Rare Manga Volumes", "Scale Figurines", "Art Books"]
                    },
                    "Streaming Binge Watcher": {
                        "emoji": "📺",
                        "criteria": ["streams_often"],
                        "description": "Consumes a high volume of Japanese dramas and anime.",
                        "product_recommendations": ["Streaming Service Subscription", "Comfortable Headphones", "Snack Box"]
                    }
                }
            },
            "Style Seeker": {
                "emoji": "👗",
                "criteria": ["j_fashion", "style_preference"],
                "description": "Always looking for the latest fashion trends and unique styles.",
                "tags": ["fashion", "style"],
                "product_recommendations": ["Streetwear Jeans", "Designer T-shirts", "Vintage Jackets", "Stylish Footwear", "Fashion Magazines"]
                # No sub-personas for Style Seeker by default, but can be added
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
        # Example for j_beauty_natural - assuming 'natural' is a specific value in 'j-beauty style' or similar
        if "natural" in row.get("j-beauty style", '').lower():
            tags.add("j_beauty_natural")

        if row.get("j-fashion style", '') in ['yes', 'true', '1']:
            tags.add("j_fashion")

        # More specific style_preference tags
        style_pref = row.get("style preference", '').lower()
        if "kawaii" in style_pref:
            tags.add("style_preference_kawaii")
        if "modern" in style_pref or "street" in style_pref or "streetwear" in style_pref:
            tags.add("style_preference_streetwear") # Grouping street and streetwear
        if "traditional" in style_pref: # For "Traditional Modernist" sub-persona
            tags.add("style_preference_traditional_modern")
        
        if row.get("fashion frequency", '') in ['frequent', 'weekly', 'daily', 'often']:
            tags.add("fashion_frequency")
        if row.get("follow fashion influencers", '') in ['yes', 'true', '1']:
            tags.add("follows_influencers")
        if row.get("streaming frequency", '') in ['daily', 'weekly', 'frequent', 'often']:
            tags.add("streams_often")
        if row.get("buys merch", '') in ['yes', 'true', '1', 'frequently', 'often']:
            tags.add("buys_merch")
        # Add a tag for Anime Collector if that's a direct column/data point
        if row.get("anime collector", '') in ['yes', 'true', '1']:
            tags.add("anime_collector")

        return tags

    def assign_persona(self, tags):
        main_persona_name = "Unclassified"
        best_main_score = 0
        
        for name, config in self.definitions.items():
            score = sum(1 for c in config['criteria'] if c in tags)
            if score > best_main_score:
                best_main_score = score
                main_persona_name = name
        
        if main_persona_name == "Unclassified":
            return "Unclassified", None # No main persona, no sub-persona

        main_persona_config = self.definitions[main_persona_name]
        sub_persona_name = None
        best_sub_score = 0

        if "sub_personas" in main_persona_config:
            for sub_name, sub_config in main_persona_config["sub_personas"].items():
                sub_score = sum(1 for c in sub_config['criteria'] if c in tags)
                if sub_score > best_sub_score:
                    best_sub_score = sub_score
                    sub_persona_name = sub_name
        
        return main_persona_name, sub_persona_name

    def process(self):
        self.personas = []
        for _, row in self.df.iterrows():
            tags = self.extract_tags(row)
            main_persona, sub_persona = self.assign_persona(tags)
            
            persona_display_name = main_persona
            full_description = self.definitions.get(main_persona, {}).get("description", "Not matched")
            product_recs = self.definitions.get(main_persona, {}).get("product_recommendations", ["No specific recommendations"])
            persona_emoji = self.definitions.get(main_persona, {}).get("emoji", "❓")

            if sub_persona:
                sub_config = self.definitions[main_persona]["sub_personas"][sub_persona]
                persona_display_name = f"{main_persona} ({sub_persona})"
                full_description = f"{full_description} - {sub_config.get('description', '')}"
                # Combine product recommendations, prioritize sub-persona's if defined
                sub_product_recs = sub_config.get("product_recommendations", [])
                if sub_product_recs:
                    product_recs = sub_product_recs
                # Use sub-persona emoji if available, otherwise main persona's
                persona_emoji = sub_config.get("emoji", persona_emoji)


            entry = {
                "customer_id": row.get("customer_id", ""),
                "city": row.get("customer_city", "Unknown"),
                "zip": row.get("customer_zip_code_prefix", "-"),
                "phone": row.get("phone number", "N/A"),
                "persona": persona_display_name, # This is the combined name
                "main_persona": main_persona,
                "sub_persona": sub_persona if sub_persona else "N/A", # Store sub-persona separately
                "emoji": persona_emoji,
                "description": full_description,
                "tags": list(tags),
                "product_recommendations": product_recs
            }
            self.personas.append(entry)

    def get_stats(self):
        # Stats based on the combined persona_display_name
        counter = Counter([p['persona'] for p in self.personas])
        return counter

    def to_df(self):
        return pd.DataFrame(self.personas)

    def grouped_by_persona(self):
        df = self.to_df()
        # Grouping by the combined persona name
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

# Instantiate PersonaEngine without passing definitions (it uses its internal hardcoded ones now)
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
                # Ensure persona distribution reflects combined persona names
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
            # No interactive filters here as per user's request to simplify/revert
            
            grouped = engine.grouped_by_persona()
            for persona_combined_name, group in grouped:
                # Use the 'persona' column (which is the combined name) for display
                st.subheader(f"{group.iloc[0]['emoji']} {persona_combined_name} ({len(group)} customers)")
                st.write(f"**Description:** {group.iloc[0]['description']}")
                st.write(f"**Recommended Products:** {', '.join(group.iloc[0]['product_recommendations'])}")
                st.dataframe(group[['customer_id', 'city', 'zip', 'phone', 'main_persona', 'sub_persona', 'tags']].reset_index(drop=True))

    else:
        st.error("Failed to read the uploaded file.")

# Footer section
st.markdown("---")
st.markdown("© 2025 Dorenth | Made using Python 🐍", unsafe_allow_html=True)
