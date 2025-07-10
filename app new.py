import streamlit as st
import pandas as pd
import re
from collections import Counter
import plotly.express as px

st.set_page_config(page_title="Persona Profiler", layout="wide")

class PersonaEngine:
    def __init__(self):
        self.df = None
        self.personas = []

    def load_data(self, file):
        self.df = pd.read_csv(file)
        self.df.columns = self.df.columns.str.strip().str.lower()
        return not self.df.empty

    def assign_persona(self, interest: str, product_category: str):
        # Normalize inputs
        interest = str(interest).lower()
        product_category = str(product_category).lower()

        # Step 1: Check if Q1 (interest) includes "Japanese Fashion and Culture"
        if "japanese fashion and culture" in interest:
            return "Japanese Lover"

        # Step 2: Check if Q2 (product interest) includes "Beauty and Personal Care"
        if "beauty and personal care" in product_category:
            return "Beauty Maven"

        # Step 3: Default fallback
        return "Fashion Devotee"

    def get_emoji(self, persona):
        return {
            "Fashion Devotee": "👗",
            "Beauty Maven": "💄",
            "Japanese Lover": "🎌",
            "Unclassified": "❓"
        }.get(persona, "❓")

    def process(self):
        self.personas = []
        for _, row in self.df.iterrows():
            interest = row.get("interest", "")
            product_category = row.get("product category", "")
            concerts = row.get("concerts attended", "")
            persona = self.assign_persona(interest, product_category)

            self.personas.append({
                "email": row.get("email", ""),
                "phone": row.get("phone", ""),
                "city": row.get("city", ""),
                "interest": interest,
                "product_interest": product_category,
                "concerts_attended": concerts,
                "persona": persona,
                "emoji": self.get_emoji(persona)
            })

    def to_df(self):
        return pd.DataFrame(self.personas)

    def get_stats(self):
        return Counter(p["persona"] for p in self.personas)

    def get_city_stats(self):
        return self.to_df()["city"].value_counts()

    def grouped_by_persona(self):
        return self.to_df().groupby("persona")


# --- Streamlit UI ---
st.title("Accurate Persona Profiler")

engine = PersonaEngine()
file = st.file_uploader("📤 Upload your `cleaned_unique_customers.csv`", type="csv")

if file:
    if engine.load_data(file):
        engine.process()
        df_result = engine.to_df()
        stats = engine.get_stats()
        city_counts = engine.get_city_stats()

        tab1, tab2 = st.tabs(["📊 Overview", "👥 Persona Groups"])

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
                top = city_counts[city_counts > city_counts.sum() * 0.02]
                rest = city_counts[city_counts <= city_counts.sum() * 0.02]
                city_df = pd.DataFrame({
                    "City": list(top.index) + ["Others"],
                    "Count": list(top.values) + [rest.sum()]
                })
                fig_city = px.pie(city_df, names="City", values="Count", title="Customers by City")
                st.plotly_chart(fig_city, use_container_width=True)

        with tab2:
            st.subheader("📋 Customers Grouped by Persona (Split Interests)")
            group_df = df_result[[
                "email", "phone", "city", "interest", "product_interest", "concerts_attended",
                "emoji", "persona"
            ]].rename(columns={
                "emoji": "🎭", "persona": "Primary Persona"
            })

            for persona in ["Fashion Devotee", "Beauty Maven", "Japanese Lover", "Unclassified"]:
                filtered = group_df[group_df["Primary Persona"] == persona]
                if not filtered.empty:
                    st.markdown(f"### {filtered.iloc[0]['🎭']} {persona} ({len(filtered)} customers)")
                    st.dataframe(filtered.drop(columns=["Primary Persona", "🎭"]).reset_index(drop=True), use_container_width=True)

    else:
        st.error("❌ Could not read uploaded CSV. Please check formatting.")
else:
    st.info("👈 Upload your `cleaned_unique_customers.csv` to begin.")

st.markdown("---")
st.markdown("© 2025 JKEJK | Made using Python 🐍", unsafe_allow_html=True)
