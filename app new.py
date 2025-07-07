import streamlit as st
import pandas as pd
from collections import Counter
import plotly.express as px

st.set_page_config(page_title="Customer Persona Profiler", layout="wide")

class PersonaEngine:
    def __init__(self):
        self.df = None
        self.personas = []

    def load_data(self, file):
        self.df = pd.read_csv(file)
        self.df.columns = self.df.columns.str.strip().str.lower()
        return not self.df.empty

    def assign_persona(self, interest, product_category):
        interest = str(interest).lower()
        category = str(product_category).lower()

        # Define keyword sets
        fashion_keywords = ["fashion show", "fashion shows", "designer", "designer collections"]
        beauty_keywords = ["beauty", "personal care", "skincare", "tgc"]
        japanese_keywords = ["japanese fashion and culture", "live performance", "japanese", "anime", "kol"]

        # Prioritized persona assignment
        if any(k in interest for k in fashion_keywords):
            return "Fashion Devotee"
        elif any(k in category for k in beauty_keywords) or any(k in interest for k in beauty_keywords):
            return "Beauty Maven"
        elif any(k in interest for k in japanese_keywords):
            return "Japanese Lover"
        else:
            return "Unclassified"

    def process(self):
        self.personas = []
        for _, row in self.df.iterrows():
            interest = row.get("interest", "")
            product_category = row.get("product category", "")
            concerts_attended = row.get("concerts attended", "")

            persona = self.assign_persona(interest, product_category)

            self.personas.append({
                "email": row.get("email", ""),
                "phone": row.get("phone", ""),
                "city": row.get("city", ""),
                "interest": interest,
                "product_interest": product_category,
                "concerts_attended": concerts_attended,
                "persona": persona,
                "emoji": self.get_emoji(persona)
            })

    def get_emoji(self, persona):
        return {
            "Fashion Devotee": "👗",
            "Beauty Maven": "💄",
            "Japanese Lover": "🎌",
            "Unclassified": "❓"
        }.get(persona, "❓")

    def to_df(self):
        return pd.DataFrame(self.personas)

    def get_stats(self):
        return Counter([p["persona"] for p in self.personas])

    def get_city_stats(self):
        df = self.to_df()
        return df['city'].value_counts()

    def grouped_by_persona(self):
        return self.to_df().groupby("persona")


# --- Streamlit UI ---
st.title("🎯 Customer Persona Profiler")
st.markdown("Upload your customer CSV to generate exclusive personas based on preferences.")

engine = PersonaEngine()
file = st.file_uploader("📤 Upload your `cleaned_unique_customers.csv`", type="csv")

if file:
    if engine.load_data(file):
        engine.process()
        df_result = engine.to_df()
        stats = engine.get_stats()
        city_counts = engine.get_city_stats()

        tab1, tab2 = st.tabs(["📊 Overview", "👥 Persona Details"])

        with tab1:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Persona Distribution")
                fig_pie = px.pie(
                    names=list(stats.keys()),
                    values=list(stats.values()),
                    title="Persona Breakdown"
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            with col2:
                st.subheader("City Distribution")
                top_cities = city_counts[city_counts > (city_counts.sum() * 0.02)]
                others = city_counts[city_counts <= (city_counts.sum() * 0.02)]
                city_df = pd.DataFrame({
                    "City": list(top_cities.index) + ["Others"],
                    "Count": list(top_cities.values) + [others.sum()]
                })
                fig_city = px.pie(city_df, names='City', values='Count', title="Customer City")
                st.plotly_chart(fig_city, use_container_width=True)

        with tab2:
            st.subheader("👥 Detailed Persona List")
            grouped = engine.grouped_by_persona()
            for persona, group in grouped:
                st.subheader(f"{group.iloc[0]['emoji']} {persona} ({len(group)} customers)")
                st.dataframe(group[[
                    'email', 'phone', 'city', 'interest', 'product_interest', 'concerts_attended'
                ]].reset_index(drop=True))
    else:
        st.error("❌ Could not read file. Please check format.")
else:
    st.info("👈 Upload your `cleaned_unique_customers.csv` to begin.")

st.markdown("---")
st.markdown("© 2025 Dorenth | Made using Python 🐍", unsafe_allow_html=True)
