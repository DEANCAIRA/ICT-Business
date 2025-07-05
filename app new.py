import streamlit as st
import pandas as pd
import numpy as np # Ensure numpy is imported
from collections import Counter
import plotly.express as px
import json

st.set_page_config(
    page_title="Customer Persona Generator", # Retaining the simplified title
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
                "tags": ["beauty", "care"]
            },
            "Trend-Savvy Fashionista": {
                "emoji": "💅",
                "criteria": ["j_fashion", "style_preference", "fashion_frequency"],
                "description": "Passionate about fashion and modern Japanese style.",
                "tags": ["fashion"]
            },
            "Pop Culture Power User": {
                "emoji": "📱",
                "criteria": ["follows_influencers", "streams_often", "buys_merch"],
                "description": "Follows influencers and loves trends.",
                "tags": ["trend", "influencer"]
            }
        }
        self.product_recommendations = {
            "Beauty-Focused Minimalist": [
                {"name": "Hada Labo Gokujyun Hyaluronic Acid Lotion", "link": "https://hadalabousa.com/products/hada-labo-gokujyun-lotion"},
                {"name": "SK-II Facial Treatment Essence", "link": "https://www.sk-ii.com/product/facial-treatment-essence"},
                {"name": "Biore UV Aqua Rich Watery Essence Sunscreen", "link": "https://www.amazon.com/Biore-Aqua-Watery-Essence-Sunscreen/dp/B07FF3R53F"},
                {"name": "MUJI Sensitive Skin Moisturizing Toner", "link": "https://www.muji.us/products/toner-moisturizing-hsm51a"}
            ],
            "Trend-Savvy Fashionista": [
                {"name": "Uniqlo AirSense Blazer", "link": "https://www.uniqlo.com/us/en/products/E458269-000/00"},
                {"name": "Comme des Garçons PLAY Heart T-Shirt", "link": "https://www.doverstreetmarket.com/shops/cdgplay.html"},
                {"name": "A Bathing Ape (BAPE) Camo Hoodie", "link": "https://bape.com/"},
                {"name": "Traditional Kimono (modern twist)", "link": "https://shop.japanobjects.com/collections/kimono"}
            ],
            "Pop Culture Power User": [
                {"name": "Good Smile Company Nendoroid Figures", "link": "https://www.goodsmile.info/en/products/category/nendoroid_series/announced/2025"},
                {"name": "Bandai Gunpla (Gundam Model Kits)", "link": "https://bandai-hobby.net/site/gunpla/index.html"},
                {"name": "Pokémon Trading Card Game Booster Packs", "link": "https://www.pokemoncenter.com/category/trading-card-game"},
                {"name": "Studio Ghibli Merchandise (e.g., Totoro Plush)", "link": "https://www.gbl.tokyo/"}
            ]
        }


    def load_data(self, file):
        self.df = pd.read_csv(file)
        self.df.columns = self.df.columns.str.strip().str.lower() # Just lower and strip, don't replace spaces
        self.columns = list(self.df.columns)
        return not self.df.empty

    def extract_tags(self, row):
        tags = set()
        # Convert row keys to lower and strip to match definitions
        row_normalized = {k.strip().lower(): str(v).strip().lower() for k, v in row.items()}

        if row_normalized.get("interested in j-beauty", '') in ['yes', 'true', '1']:
            tags.add("j_beauty")
        if row_normalized.get("daily routine", '') in ['yes', 'true', '1', 'defined', 'structured']:
            tags.add("daily_routine")
        if row_normalized.get("j-fashion style", '') in ['yes', 'true', '1']:
            tags.add("j_fashion")
        if any(x in row_normalized.get("style preference", '') for x in ['kawaii', 'modern', 'street', 'streetwear']):
            tags.add("style_preference")
        if row_normalized.get("fashion frequency", '') in ['frequent', 'weekly', 'daily', 'often']:
            tags.add("fashion_frequency")
        if row_normalized.get("follow fashion influencers", '') in ['yes', 'true', '1']:
            tags.add("follows_influencers")
        if row_normalized.get("streaming frequency", '') in ['daily', 'weekly', 'frequent', 'often']:
            tags.add("streams_often")
        if row_normalized.get("buys merch", '') in ['yes', 'true', '1', 'frequently', 'often']:
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

            # Determine interested products and generate EC links based on the assigned persona
            # This logic can be further refined to use individual tags if a customer might fit multiple product categories
            # even if only assigned one primary persona. For now, it maps directly from the assigned persona.
            recommended_products_list = self.product_recommendations.get(persona, [])
            
            # Format product names with clickable links for display
            formatted_products_for_display = []
            for prod in recommended_products_list:
                formatted_products_for_display.append(f'<a href="{prod["link"]}" target="_blank">{prod["name"]}</a>')
            
            # Ensure phone column exists and is populated
            phone_number = row.get("phone number", "N/A") # Access 'phone number' with space as loaded

            entry = {
                "customer_id": row.get("customer_id", ""),
                "city": row.get("customer_city", "Unknown"),
                "zip": row.get("customer_zip_code_prefix", "-"),
                "phone": phone_number,
                "persona": persona,
                "emoji": self.definitions.get(persona, {}).get("emoji", "❓"),
                "description": self.definitions.get(persona, {}).get("description", "Not matched"),
                "tags": list(tags),
                "Recommended Products": "<br>".join(formatted_products_for_display) if formatted_products_for_display else "No specific recommendations"
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
        # This will create a template based on the current DataFrame's columns
        # You might want to adjust this if you have specific columns for a blank template
        template_df = pd.DataFrame(columns=self.df.columns)
        return template_df.to_csv(index=False)


# Streamlit UI
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
                st.subheader(f"{engine.definitions.get(persona, {}).get('emoji', '❓')} {persona} ({len(group)} customers)")
                
                # Ensure all desired columns exist before displaying
                display_cols = ['customer_id', 'city', 'zip', 'phone', 'tags', 'Recommended Products']
                actual_display_cols = [col for col in display_cols if col in group.columns]
                
                st.dataframe(group[actual_display_cols].reset_index(drop=True), unsafe_allow_html=True)

    else:
        st.error("Failed to read the uploaded file.")

# Footer section
st.markdown("---")
st.markdown("© 2025 Dorenth | Made using Python 🐍", unsafe_allow_html=True)
