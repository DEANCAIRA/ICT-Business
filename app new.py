import streamlit as st
import pandas as pd
from collections import Counter
import plotly.express as px

st.set_page_config(page_title="Customer Persona Generator", layout="wide")

class PersonaEngine:
    def __init__(self):
        self.df = None
        self.personas = []

        self.definitions = {
            "Fashion Devotee": {
                "emoji": "👗",
                "keywords": ["fashion", "designer", "style", "runway"],
                "description": "Passionate about fashion, style, and designer culture.",
            },
            "Beauty Maven": {
                "emoji": "💄",
                "keywords": ["beauty", "skincare", "personal care", "makeup", "cosmetic"],
                "description": "Enthusiast of skincare routines and beauty trends.",
            },
            "Japanese Lover": {
                "emoji": "🎌",
                "keywords": ["japanese", "anime", "pop culture", "culture", "japan", "drama"],
                "description": "Loves Japanese pop culture, anime, and traditions.",
            }
        }

    def load_data(self, file):
        self.df = pd.read_csv(file)
        self.df.columns = self.df.columns.str.strip().str.lower()
        return not self.df.empty

    def assign_persona(self, interest_text):
        interest_text = str(interest_text).lower()
        for persona, config in self.definitions.items():
            for kw in config["keywords"]:
                if kw in interest_text:
                    return persona
        return "Unclassified"

    def process(self):
        self.personas = []
        for _, row in self.df.iterrows():
            interest = row.get("interest", "")
            persona = self.assign_persona(interest)
            config = self.definitions.get(persona, {})

            self.personas.append({
                "email": row.get("email", ""),
                "phone": row.get("phone", ""),
                "city": row.get("city", ""),
                "interest": interest,
                "persona": persona,
                "emoji": config.get("emoji", "❓"),
                "description": config.get("description", "No description available."),
            })

    def to_df(self):
        return pd.DataFrame(self.personas)

    def get_stats(self):
        return Counter([p["persona"] for p in self.personas])

    def grouped_by_persona(self):
        return self.to_df().groupby("persona")


# Streamlit UI
st.title("🎯 Customer Persona Profiler (Preference-Based)")
st.markdown("Upload your customer CSV with preferences, and get grouped personas.")

engine = PersonaEngine()
file = st.file_uploader("📤 Upload CSV", type="csv")

if file:
    if engine.load_data(file):
        engine.process()
        df_result = engine.to_df()
        stats = engine.get_stats()

        tab1, tab2 = st.tabs(["📊 Overview", "👥 Persona Groups"])

        with tab1:
            st.subheader("📊 Persona Distribution")
            fig = px.pie(names=list(stats.keys()), values=list(stats.values()), title="Persona Breakdown")
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("📍 City Distribution")
            if "city" in df_result.columns:
                city_counts = df_result['city'].value_counts().reset_index()
                city_counts.columns = ['City', 'Count']
                fig_city = px.pie(city_counts, names='City', values='Count', title="Customer City")
                st.plotly_chart(fig_city, use_container_width=True)

        with tab2:
            st.header("👥 Persona Details")
            grouped = engine.grouped_by_persona()
            for persona, group in grouped:
                st.subheader(f"{group.iloc[0]['emoji']} {persona} ({len(group)} customers)")
                st.write(group.iloc[0]['description'])
                st.dataframe(group[['email', 'phone', 'city', 'interest']].reset_index(drop=True))
    else:
        st.error("❌ Failed to read the file.")
else:
    st.info("👈 Please upload a CSV file to begin.")

st.markdown("---")
st.markdown("© 2025 Dorenth | Made with ❤️ using Python and Streamlit")
