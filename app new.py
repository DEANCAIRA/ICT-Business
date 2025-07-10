import streamlit as st
import pandas as pd
import re
from collections import Counter, defaultdict
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Persona Profiler", layout="wide")

class PersonaEngine:
    def __init__(self):
        self.df = None
        self.personas = []
        
        # Enhanced keyword weights with more comprehensive coverage
        self.persona_keywords = {
            "Fashion Devotee": {
                # Fashion-specific terms
                "fashion": 3,
                "style": 2,
                "designer": 3,
                "fashion show": 4,
                "designer collections": 4,
                "lifestyle": 2,
                "clothing": 2,
                "outfit": 2,
                "trendy": 2,
                "boutique": 2,
                # Entertainment terms (fallback for fashion)
                "live performance": 1,
                "entertainment": 1,
                "digital service": 1
            },
            "Beauty Maven": {
                # Beauty-specific terms
                "beauty": 3,
                "skincare": 3,
                "makeup": 3,
                "personal care": 4,
                "cosmetic": 3,
                "beauty and personal care": 4,
                "tgc": 2,  # TGC often associated with beauty
                "wellness": 2,
                "grooming": 2,
                "spa": 2
            },
            "Japanese Lover": {
                # Japanese culture terms
                "japanese": 4,
                "japan": 3,
                "anime": 3,
                "manga": 3,
                "kol": 2,
                "japanese fashion": 4,
                "japanese culture": 4,
                "jpop": 3,
                "kawaii": 3,
                "otaku": 3,
                "cosplay": 3
            }
        }
        
        # Minimum threshold for persona assignment
        self.min_threshold = 2

    def load_data(self, file):
        self.df = pd.read_csv(file)
        self.df.columns = self.df.columns.str.strip().str.lower()
        return not self.df.empty

    def calculate_persona_scores(self, interest: str, product_category: str):
        """Calculate scores for all personas based on interest and product category"""
        # Combine both fields for comprehensive analysis
        combined_text = f"{str(interest).lower()} {str(product_category).lower()}"
        
        # Clean and normalize text
        combined_text = re.sub(r'[^\w\s]', ' ', combined_text)
        combined_text = re.sub(r'\s+', ' ', combined_text).strip()
        
        scores = {persona: 0 for persona in self.persona_keywords}
        
        # Score each persona based on keyword matches
        for persona, keywords in self.persona_keywords.items():
            for keyword, weight in keywords.items():
                # Count occurrences of keyword in text
                count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', combined_text))
                scores[persona] += count * weight
        
        return scores

    def assign_personas(self, interest: str, product_category: str):
        """Assign multiple personas based on scores above threshold"""
        scores = self.calculate_persona_scores(interest, product_category)
        
        # Get personas that meet the minimum threshold
        qualified_personas = [
            persona for persona, score in scores.items() 
            if score >= self.min_threshold
        ]
        
        # If no persona meets threshold, check for special fallback rules
        if not qualified_personas:
            # Special rule: Live performance + entertainment + digital service = Fashion Devotee
            combined_text = f"{str(interest).lower()} {str(product_category).lower()}"
            
            if (("live performance" in combined_text or "entertainment" in combined_text) and 
                ("digital service" in combined_text or "entertainment and digital" in combined_text)):
                qualified_personas = ["Fashion Devotee"]
                scores["Fashion Devotee"] += 2  # Add fallback score
            else:
                # Original fallback logic
                max_persona = max(scores, key=scores.get)
                if scores[max_persona] > 0:
                    qualified_personas = [max_persona]
                else:
                    qualified_personas = ["Unclassified"]
        
        return qualified_personas, scores

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
            
            assigned_personas, scores = self.assign_personas(interest, product_category)
            
            # Create persona string representation
            persona_str = " + ".join(assigned_personas)
            emoji_str = "".join([self.get_emoji(p) for p in assigned_personas])
            
            self.personas.append({
                "email": row.get("email", ""),
                "phone": row.get("phone", ""),
                "first_name": row.get("first name", ""),
                "last_name": row.get("last name", ""),
                "city": row.get("city", ""),
                "interest": interest,
                "product_interest": product_category,
                "concerts_attended": concerts,
                "assigned_personas": assigned_personas,
                "persona_string": persona_str,
                "emoji": emoji_str,
                "scores": scores,
                "total_score": sum(scores.values())
            })

    def to_df(self):
        return pd.DataFrame(self.personas)

    def get_persona_stats(self):
        """Get statistics for individual personas (including multi-persona users)"""
        persona_counts = defaultdict(int)
        for person in self.personas:
            for persona in person["assigned_personas"]:
                persona_counts[persona] += 1
        return dict(persona_counts)

    def get_combination_stats(self):
        """Get statistics for persona combinations"""
        combination_counts = Counter(p["persona_string"] for p in self.personas)
        return combination_counts

    def get_city_stats(self):
        return self.to_df()["city"].value_counts()

    def get_multi_persona_users(self):
        """Get users with multiple personas"""
        return [p for p in self.personas if len(p["assigned_personas"]) > 1]


# --- Streamlit UI ---
st.title("Multi-Persona Customer Profiler")
st.markdown("*Captures customers with multiple interests - no one gets left behind!*")

engine = PersonaEngine()
file = st.file_uploader("📤 Upload your customer CSV file", type="csv")

if file:
    if engine.load_data(file):
        engine.process()
        df_result = engine.to_df()
        persona_stats = engine.get_persona_stats()
        combination_stats = engine.get_combination_stats()
        city_counts = engine.get_city_stats()
        multi_persona_users = engine.get_multi_persona_users()

        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Customers", len(df_result))
        with col2:
            st.metric("Multi-Persona Users", len(multi_persona_users))
        with col3:
            st.metric("Unique Combinations", len(combination_stats))
        with col4:
            coverage = len([p for p in engine.personas if p["assigned_personas"] != ["Unclassified"]])
            st.metric("Classification Coverage", f"{coverage/len(df_result)*100:.1f}%")

        tab1, tab2, tab3, tab4 = st.tabs(["📊 Persona Distribution", "🔄 Multi-Persona Analysis", "👥 Customer Groups", "🔍 Detailed View"])

        with tab1:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Individual Persona Distribution")
                fig_pie = px.pie(
                    names=list(persona_stats.keys()),
                    values=list(persona_stats.values()),
                    title="Total Persona Assignments (including overlaps)"
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            with col2:
                st.subheader("City Distribution")
                top_cities = city_counts[city_counts > city_counts.sum() * 0.02]
                rest = city_counts[city_counts <= city_counts.sum() * 0.02]
                city_df = pd.DataFrame({
                    "City": list(top_cities.index) + ["Others"],
                    "Count": list(top_cities.values) + [rest.sum()]
                })
                fig_city = px.pie(city_df, names="City", values="Count", title="Customers by City")
                st.plotly_chart(fig_city, use_container_width=True)

        with tab2:
            st.subheader("🔄 Multi-Persona Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Persona Combination Frequency**")
                combo_df = pd.DataFrame([
                    {"Combination": combo, "Count": count}
                    for combo, count in combination_stats.most_common(10)
                ])
                fig_combo = px.bar(combo_df, x="Count", y="Combination", orientation='h',
                                 title="Top 10 Persona Combinations")
                fig_combo.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_combo, use_container_width=True)
            
            with col2:
                st.markdown("**Multi-Persona Statistics**")
                single_persona = len([p for p in engine.personas if len(p["assigned_personas"]) == 1])
                multi_persona = len(multi_persona_users)
                
                fig_multi = px.pie(
                    names=["Single Persona", "Multi-Persona"],
                    values=[single_persona, multi_persona],
                    title="Single vs Multi-Persona Users"
                )
                st.plotly_chart(fig_multi, use_container_width=True)

            # Show sample multi-persona users
            if multi_persona_users:
                st.markdown("**Sample Multi-Persona Users**")
                sample_multi = pd.DataFrame(multi_persona_users[:5])[
                    ["first_name", "last_name", "city", "persona_string", "interest", "product_interest"]
                ].rename(columns={
                    "first_name": "First Name",
                    "last_name": "Last Name", 
                    "city": "City",
                    "persona_string": "Assigned Personas",
                    "interest": "Interests",
                    "product_interest": "Product Category"
                })
                st.dataframe(sample_multi, use_container_width=True)

        with tab3:
            st.subheader("👥 Customers by Persona Groups")
            
            # Group by individual personas
            all_personas = list(engine.persona_keywords.keys()) + ["Unclassified"]
            
            for persona in all_personas:
                # Get customers who have this persona (including multi-persona)
                customers_with_persona = [
                    p for p in engine.personas if persona in p["assigned_personas"]
                ]
                
                if customers_with_persona:
                    emoji = engine.get_emoji(persona)
                    st.markdown(f"### {emoji} {persona} ({len(customers_with_persona)} customers)")
                    
                    persona_df = pd.DataFrame(customers_with_persona)[
                        ["first_name", "last_name", "city", "persona_string", "interest", "product_interest", "total_score"]
                    ].rename(columns={
                        "first_name": "First Name",
                        "last_name": "Last Name",
                        "city": "City", 
                        "persona_string": "All Personas",
                        "interest": "Interests",
                        "product_interest": "Product Category",
                        "total_score": "Match Score"
                    }).sort_values("Match Score", ascending=False)
                    
                    st.dataframe(persona_df.reset_index(drop=True), use_container_width=True)

        with tab4:
            st.subheader("🔍 Detailed Customer Analysis")
            
            # Search and filter options
            col1, col2 = st.columns(2)
            with col1:
                search_name = st.text_input("Search by name:")
            with col2:
                filter_persona = st.selectbox(
                    "Filter by persona:",
                    ["All"] + list(engine.persona_keywords.keys()) + ["Unclassified"]
                )
            
            # Apply filters
            filtered_data = engine.personas.copy()
            
            if search_name:
                filtered_data = [
                    p for p in filtered_data 
                    if search_name.lower() in f"{p['first_name']} {p['last_name']}".lower()
                ]
            
            if filter_persona != "All":
                filtered_data = [
                    p for p in filtered_data 
                    if filter_persona in p["assigned_personas"]
                ]
            
            # Display detailed results
            if filtered_data:
                detailed_df = pd.DataFrame(filtered_data)[
                    ["emoji", "first_name", "last_name", "city", "persona_string", 
                     "interest", "product_interest", "concerts_attended", "total_score"]
                ].rename(columns={
                    "emoji": "🎭",
                    "first_name": "First Name",
                    "last_name": "Last Name",
                    "city": "City",
                    "persona_string": "Assigned Personas",
                    "interest": "Interests", 
                    "product_interest": "Product Category",
                    "concerts_attended": "Concerts Attended",
                    "total_score": "Match Score"
                }).sort_values("Match Score", ascending=False)
                
                st.dataframe(detailed_df.reset_index(drop=True), use_container_width=True)
                
                # Download button
                csv = detailed_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download filtered results as CSV",
                    data=csv,
                    file_name="persona_analysis_results.csv",
                    mime="text/csv"
                )
            else:
                st.info("No customers match your filter criteria.")

    else:
        st.error("❌ Could not read uploaded CSV. Please check formatting.")
else:
    st.info("👈 Upload your customer CSV file to begin persona analysis.")
    
    # Show example of improved logic
    st.markdown("### 🆕 Improved Features:")
    st.markdown("""
    - **Multi-persona assignment**: Customers can have multiple personas (e.g., "Fashion Devotee + Beauty Maven")
    - **keyword detection**: Weighted scoring
    - **fallback rules**: Live performance + entertainment + digital service → Fashion Devotee
    - **Threshold-based classification**: Only assigns personas when there's sufficient evidence
    - **Detailed scoring**: Shows match confidence for each assignment
    - **Better coverage**: Captures customers with diverse interests more accurately
    """)

st.markdown("---")
st.markdown("© 2025 TGC Event Analysis | Enhanced Multi-Persona Classification")
