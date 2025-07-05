import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import plotly.express as px
import json

st.set_page_config(
    page_title="J-Culture Customer Persona Generator",
    page_icon="🎌",
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
                "persona": persona,
                "emoji": self.definitions.get(persona, {}).get("emoji", "❓"),
                "description": self.definitions.get(persona, {}).get("description", "Not matched"),
                "tags": list(tags)
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
            "customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city",
            "Interested in J-beauty", "Daily Routine", "Anime Collector", "J-fashion Style",
            "Interested in Japanese Snacks", "Streaming Frequency", "Favorite Platform",
            "Buys Merch", "Style Preference", "Fashion Frequency", "Follow Fashion Influencers"
        ]
        df = pd.DataFrame(columns=columns)
        return df

st.title("🎌 J-Culture Customer Persona Profiler")
st.markdown("Analyze your customers and assign personas based on their interests in Japanese fashion, beauty, and trends.")

engine = PersonaEngine()
file = st.file_uploader("Upload your customer CSV file", type="csv")

if file:
    if engine.load_data(file):
        st.sidebar.subheader("📋 Columns Detected")
        st.sidebar.write(engine.columns)

        engine.process()
        df_result = engine.to_df()
        stats = engine.get_stats()

        tab1, tab2 = st.tabs(["📊 Overview", "👥 Persona Details"])

        with tab1:
            st.header("📊 Persona Distribution Overview")
            fig = px.pie(names=list(stats.keys()), values=list(stats.values()), title="Persona Breakdown")
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.header("👥 Detailed Persona Assignments")
            grouped = engine.grouped_by_persona()
            for persona, group in grouped:
                st.subheader(f"{group.iloc[0]['emoji']} {persona} ({len(group)} customers)")
                for _, row in group.iterrows():
                    st.markdown(f"- **ID:** {row['customer_id']} | **City:** {row['city']} | **Tags:** {', '.join(row['tags'])}")

        st.download_button(
            label="📥 Download Persona Results",
            data=df_result.to_csv(index=False),
            file_name="persona_results.csv",
            mime="text/csv"
        )

        cleaned_template = engine.export_template()
        st.download_button(
            label="📥 Download Clean CSV Template",
            data=cleaned_template.to_csv(index=False),
            file_name="cleaned_template.csv",
            mime="text/csv"
        )
    else:
        st.error("Failed to read the uploaded file.")
