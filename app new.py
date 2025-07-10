import streamlit as st
import pandas as pd
import re
from collections import Counter, defaultdict
import plotly.express as px

# --- App Configuration ---
st.set_page_config(page_title="TGC Fan Distribution Analytics", layout="wide")

# --- Persona Engine Class ---
class PersonaEngine:
    def __init__(self):
        self.df = None
        self.personas = []
        # [cite_start]Keywords for defining personas [cite: 1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.persona_keywords = {
            "Fashion Devotee": {"fashion", "style", "designer", "lifestyle", "clothing", "outfit", "trendy", "boutique", "shows", "collections"},
            "Beauty Maven": {"beauty", "personal care", "skincare", "makeup", "cosmetic", "wellness", "grooming", "spa"},
            "Japanese Lover": {"japanese", "japan", "anime", "manga", "jpop", "kawaii", "otaku", "cosplay"}
        }
        # [cite_start]Terms to exclude from persona analysis [cite: 10, 11]
        self.excluded_terms = {"exclusive tgc product", "voucher", "kol influencer appearance"}

    def load_data(self, file):
        """Loads and cleans the uploaded CSV file."""
        self.df = pd.read_csv(file)
        self.df.columns = self.df.columns.str.strip().str.lower()
        return not self.df.empty

    def assign_personas(self, interest: str, product_category: str):
        """Assigns one or more personas based on interest and product category."""
        text = f"{str(interest).lower()} {str(product_category).lower()}"
        # [cite_start]Clean text by removing special characters and excluded terms [cite: 14]
        clean_text = re.sub(r'[^\w\s]', ' ', text)
        for term in self.excluded_terms:
            clean_text = clean_text.replace(term, "")
        
        words = set(clean_text.split())
        assigned = []
        for persona, keywords in self.persona_keywords.items():
            if not keywords.isdisjoint(words):
                assigned.append(persona)
        
        [cite_start]return assigned if assigned else ["Unclassified"] # [cite: 17, 18]

    def process(self):
        """Processes the entire dataframe to assign personas and calculate metrics."""
        self.personas = []
        for _, row in self.df.iterrows():
            assigned_personas = self.assign_personas(row.get("interest", ""), row.get("product category", ""))
            # [cite_start]Determine Fan Segment based on number of personas and concert attendance [cite: 23, 24]
            affluence_score = self.get_affluence_score(row.get("concerts attended", ""))
            if len(assigned_personas) >= 2 and affluence_score >= 4:
                fan_segment = "VIP Fan (High Value)"
            elif len(assigned_personas) >= 2 or affluence_score >= 3:
                fan_segment = "Premium Fan"
            else:
                fan_segment = "Active Fan"

            self.personas.append({
                "first_name": row.get("first name", ""),
                "last_name": row.get("last name", ""),
                "city": row.get("city", "Unknown"),
                "gender": row.get("gender", "Unknown"),
                "assigned_personas": assigned_personas,
                "persona_string": " + ".join(assigned_personas),
                "total_personas": len(assigned_personas),
                "fan_segment": fan_segment,
                "interest": row.get("interest", "")
            })

    def get_affluence_score(self, concerts_attended):
        """Calculates a score based on concert attendance as a proxy for spending."""
        concerts = str(concerts_attended).lower()
        if "more than 3" in concerts: return 5
        if "2 to 3" in concerts: return 3
        if "1" in concerts: return 2
        [cite_start]return 1 # [cite: 19, 20]
        
    def to_df(self):
        """Converts the processed persona list to a DataFrame."""
        return pd.DataFrame(self.personas)

    # --- Data Getter Functions for Charts ---
    [cite_start]def get_persona_portions(self): # [cite: 30, 31]
        counts = defaultdict(int)
        for p in self.personas:
            for persona in p["assigned_personas"]:
                counts[persona] += 1
        return dict(counts)

    [cite_start]def get_gender_stats(self): # [cite: 29]
        df = self.to_df()
        return df["gender"].value_counts() if 'gender' in df.columns else None

    [cite_start]def get_city_stats(self): # [cite: 29]
        df = self.to_df()
        return df["city"].value_counts() if 'city' in df.columns else None

# --- Streamlit UI ---
st.title("TGC Fan Base Distribution Analytics")
st.markdown("*A simplified dashboard focusing on key fan distributions.*")

engine = PersonaEngine()
file = st.file_uploader("Upload your customer CSV file", type="csv")

if file:
    if engine.load_data(file):
        engine.process()
        df_result = engine.to_df()

        # --- Data for Charts ---
        persona_portions = engine.get_persona_portions()
        gender_stats = engine.get_gender_stats()
        city_stats = engine.get_city_stats()
        
        # --- UI Tabs ---
        tab1, tab2, tab3 = st.tabs(["📊 Detailed Distributions", "🎯 Fan Segments", "🔍 Customer Details"])

        with tab1:
            st.subheader("Fan Base Distributions")
            
            col1, col2 = st.columns(2)

            with col1:
                # 1. Persona Distribution
                st.markdown("**Persona Distribution**")
                if persona_portions:
                    fig_persona = px.pie(names=list(persona_portions.keys()), values=list(persona_portions.values()), hole=0.3)
                    fig_persona.update_traces(textinfo='percent+label', textposition='inside')
                    st.plotly_chart(fig_persona, use_container_width=True)
                else:
                    st.info("No persona data to display.")

                # 2. City Distribution
                st.markdown("**Top 10 City Distribution**")
                if city_stats is not None and not city_stats.empty:
                    top_10_cities = city_stats.nlargest(10)
                    fig_city = px.pie(names=top_10_cities.index, values=top_10_cities.values, hole=0.3)
                    fig_city.update_traces(textinfo='percent+label', textposition='inside')
                    st.plotly_chart(fig_city, use_container_width=True)
                else:
                    st.info("City data not available.")

            with col2:
                # 3. Gender Distribution
                st.markdown("**Gender Distribution**")
                if gender_stats is not None and not gender_stats.empty:
                    fig_gender = px.pie(names=gender_stats.index, values=gender_stats.values, hole=0.3)
                    fig_gender.update_traces(textinfo='percent+label', textposition='inside')
                    st.plotly_chart(fig_gender, use_container_width=True)
                else:
                    st.info("Gender data not available in the uploaded file.")

                # 4. Multi-Persona Distribution
                st.markdown("**Single vs. Multi-Persona Fans**")
                single = len(df_result[df_result['total_personas'] == 1])
                multi = len(df_result[df_result['total_personas'] > 1])
                fig_multi = px.pie(names=["Single Persona", "Multi-Persona"], values=[single, multi], hole=0.3,
                                   color_discrete_sequence=["#636EFA", "#FFA15A"])
                fig_multi.update_traces(textinfo='percent+label', textposition='inside')
                st.plotly_chart(fig_multi, use_container_width=True)

        with tab2:
            st.subheader("Fan Segment Distribution")
            fan_segments = df_result['fan_segment'].value_counts()
            fig_segments = px.bar(fan_segments, x=fan_segments.index, y=fan_segments.values,
                                 title="Fan Segments by Monetization Potential",
                                 labels={'x': 'Fan Segment', 'y': 'Number of Customers'},
                                 color=fan_segments.index,
                                 color_discrete_map={
                                     'VIP Fan (High Value)': '#FFD700',
                                     'Premium Fan': '#C0C0C0',
                                     'Active Fan': '#CD7F32'
                                 })
            st.plotly_chart(fig_segments, use_container_width=True)

        with tab3:
            st.subheader("Customer Details")
            # Allow filtering by persona
            all_personas = list(engine.persona_keywords.keys()) + ["Unclassified"]
            filter_persona = st.selectbox("Filter by persona:", ["All"] + all_personas)

            if filter_persona == "All":
                filtered_df = df_result
            else:
                filtered_df = df_result[df_result['assigned_personas'].apply(lambda x: filter_persona in x)]
            
            st.dataframe(filtered_df[["first_name", "last_name", "city", "gender", "persona_string", "fan_segment"]].rename(columns={
                "first_name": "First Name", "last_name": "Last Name", "city": "City", "gender": "Gender",
                "persona_string": "Assigned Personas", "fan_segment": "Fan Segment"
            }), use_container_width=True)

            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Filtered List",
                data=csv,
                file_name=f"tgc_filtered_customers_{filter_persona}.csv",
                mime="text/csv"
            )

    else:
        st.error("Could not read the uploaded CSV. Please check the file format.")
else:
    st.info("Upload your customer CSV file to begin analysis.")

st.markdown("---")
st.markdown("© 2025 TGC Event Analysis")
