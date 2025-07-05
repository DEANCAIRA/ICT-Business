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
        return not self.df.empty

    def extract_tags(self, row):
        tags = set()
        def val(key): return str(row.get(key, '')).lower()

        if 'yes' in val("interested in j-beauty") or 'true' in val("interested in j-beauty"):
            tags.add("j_beauty")
        if 'yes' in val("daily routine") or 'defined' in val("daily routine"):
            tags.add("daily_routine")
        if 'yes' in val("j-fashion style"):
            tags.add("j_fashion")
        if any(x in val("style preference") for x in ['kawaii', 'modern', 'street']):
            tags.add("style_preference")
        if val("fashion frequency") in ['frequent', 'weekly', 'daily']:
            tags.add("fashion_frequency")
        if 'yes' in val("follow fashion influencers"):
            tags.add("follows_influencers")
        if val("streaming frequency") in ['daily', 'weekly']:
            tags.add("streams_often")
        if 'yes' in val("buys merch"):
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

st.title("🎌 J-Culture Customer Persona Profiler")
st.markdown("Analyze your customers and assign personas based on their interests in Japanese fashion, beauty, and trends.")

engine = PersonaEngine()
file = st.file_uploader("Upload your customer CSV file", type="csv")

if file:
    if engine.load_data(file):
        engine.process()

        df_result = engine.to_df()
        stats = engine.get_stats()

        st.success("Personas assigned successfully!")

        st.subheader("📊 Persona Distribution")
        fig = px.pie(names=list(stats.keys()), values=list(stats.values()), title="Persona Breakdown")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("👥 Customer Persona Details")
        for p in engine.personas:
            with st.expander(f"{p['emoji']} {p['persona']} - {p['city']}"):
                st.write(f"**Customer ID:** {p['customer_id']}")
                st.write(f"**City:** {p['city']}")
                st.write(f"**ZIP Code:** {p['zip']}")
                st.write(f"**Persona:** {p['persona']}")
                st.write(f"**Profile Tags:** {', '.join(p['tags'])}")
                st.write(f"**Summary:** {p['description']}")

        st.subheader("📥 Download Persona Results")
        st.download_button(
            label="Download as CSV",
            data=df_result.to_csv(index=False),
            file_name="persona_results.csv",
            mime="text/csv"
        )
    else:
        st.error("Failed to read the uploaded file.")
