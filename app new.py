import streamlit as st
import pandas as pd
import re
from collections import Counter
import plotly.express as px

st.set_page_config(page_title="Smart Persona Profiler", layout="wide")

class PersonaEngine:
    def __init__(self):
        self.df = None
        self.personas = []

        self.weights = {
            "Fashion Devotee": {"fashion": 1, "designer": 1, "fashion show": 2, "designer collections": 1},
            "Beauty Maven": {"beauty": 2, "skincare": 1, "personal care": 1, "tgc": 1},
            "Japanese Lover": {"japanese": 1, "anime": 1, "kol": 1}
        }

        # Define matchable keywords for intent
        self.intent_keywords = {
            "Beauty Maven": ["beauty", "skincare", "makeup", "personal care", "cosmetic"],
            "Fashion Devotee": ["fashion", "style", "lifestyle", "designer"],
            "Japanese Lover": ["japanese", "anime", "kol"]
        }

    def load_data(self, file):
        self.df = pd.read_csv(file)
        self.df.columns = self.df.columns.str.strip().str.lower()
        return not self.df.empty

    def assign_persona(self, interest: str, product_category: str):
        product_text = str(product_category).lower()

        # Step 1: Direct match from product category
        for persona, keywords in self.intent_keywords.items():
            if any(word in product_text for word in keywords):
                return persona

        # Step 2: Fallback to interest-based scoring
        text = str(interest).lower()
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()

        scores = {p: 0 for p in self.weights}
        for persona, keywords in self.weights.items():
            for kw, w in keywords.items():
                if kw in text:
                    scores[persona] += w

        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "Unclassified"

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
st.title("🎯 Smart Customer Persona Profiler")
st.markdown("""
Personas are assigned based on product category **only if** it clearly reflects intent  
(e.g. contains "beauty", "fashion", "japanese").  
Otherwise, we fallback to `interest` using weighted scoring.
""")

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
            st.subheader("📋 Customers Grouped by Persona (With Fallback Logic)")
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
        st.error("❌ Failed to read the uploaded CSV. Please check the format.")
else:
    st.info("👈 Upload your `cleaned_unique_customers.csv` to begin.")

st.markdown("---")
st.markdown("© 2025 Dorenth | Smart Fallback Persona System", unsafe_allow_html=True)
