import streamlit as st
import pandas as pd
import re
from collections import Counter, defaultdict
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Multi-Persona Profiler", layout="wide")

class PersonaEngine:
    def __init__(self):
        self.df = None
        self.personas = []
        
        # Simplified equal-weight keywords - using full phrases, no individual words
        self.persona_keywords = {
            "Fashion Devotee": {
                # Fashion-specific phrases (full terms only)
                "fashion shows": 1,
                "fashion shows and designer collections": 1,
                "designer collections": 1,
                "fashion and lifestyle": 1,
                "live performances": 1,
                "live performances or entertainment": 1,
                "entertainment": 1,
                "digital services": 1,
                "entertainment and digital services": 1,
                "shopping and brand booths": 1,
                "shopping": 1,
                "brand booths": 1,
                "fashion": 1,
                "style": 1,
                "designer": 1,
                "lifestyle": 1,
                "clothing": 1,
                "outfit": 1,
                "trendy": 1,
                "boutique": 1
            },
            "Beauty Maven": {
                # Beauty-specific phrases (full terms only)
                "beauty and personal care": 1,
                "personal care": 1,
                "beauty": 1,
                "skincare": 1,
                "makeup": 1,
                "cosmetic": 1,
                "wellness": 1,
                "grooming": 1,
                "spa": 1
            },
            "Japanese Lover": {
                # Japanese culture phrases (full terms only)
                "japanese fashion and culture": 1,
                "japanese fashion": 1,
                "japanese culture": 1,
                "japanese": 1,
                "japan": 1,
                "anime": 1,
                "manga": 1,
                "jpop": 1,
                "kawaii": 1,
                "otaku": 1,
                "cosplay": 1
            }
        }
        
        # Words to exclude from scoring (but keep in display)
        self.excluded_terms = [
            "exclusive tgc products",
            "exclusive tgc product", 
            "tgc products",
            "tgc product",
            "voucher",
            "vouchers",
            "exclusive",
            "kol influencer appearances"  # Too generic - doesn't indicate specific persona
        ]
        
        # Minimum threshold for persona assignment (simplified)
        self.min_threshold = 1

    def load_data(self, file):
        self.df = pd.read_csv(file)
        self.df.columns = self.df.columns.str.strip().str.lower()
        return not self.df.empty

    def calculate_persona_scores(self, interest: str, product_category: str):
        """Calculate scores for all personas - using full phrases and excluding certain terms"""
        # Handle list format (convert to string if needed)
        if isinstance(interest, list):
            interest_text = ", ".join(str(item) for item in interest).lower()
        else:
            interest_text = str(interest).lower()
            
        product_text = str(product_category).lower()
        
        # Remove excluded terms from scoring (but keep original text for display)
        interest_for_scoring = interest_text
        product_for_scoring = product_text
        
        for excluded_term in self.excluded_terms:
            interest_for_scoring = interest_for_scoring.replace(excluded_term, "")
            product_for_scoring = product_for_scoring.replace(excluded_term, "")
        
        # Clean and normalize text for scoring
        interest_clean = re.sub(r'[^\w\s]', ' ', interest_for_scoring)
        interest_clean = re.sub(r'\s+', ' ', interest_clean).strip()
        
        product_clean = re.sub(r'[^\w\s]', ' ', product_for_scoring)
        product_clean = re.sub(r'\s+', ' ', product_clean).strip()
        
        scores = {persona: 0 for persona in self.persona_keywords}
        
        # Create copies for phrase removal tracking
        interest_remaining = interest_clean
        product_remaining = product_clean
        
        # Score using full phrases - prioritize longer phrases first to avoid double counting
        for persona, keywords in self.persona_keywords.items():
            # Sort keywords by length (longest first) to match full phrases before sub-phrases
            sorted_keywords = sorted(keywords.keys(), key=len, reverse=True)
            
            for keyword in sorted_keywords:
                # Count in interest field (only if not already matched by longer phrase)
                interest_matches = len(re.findall(r'\b' + re.escape(keyword) + r'\b', interest_remaining))
                if interest_matches > 0:
                    scores[persona] += interest_matches
                    # Remove matched phrases to prevent double counting
                    interest_remaining = re.sub(r'\b' + re.escape(keyword) + r'\b', '', interest_remaining)
                
                # Count in product category
                product_matches = len(re.findall(r'\b' + re.escape(keyword) + r'\b', product_remaining))
                if product_matches > 0:
                    scores[persona] += product_matches
                    # Remove matched phrases to prevent double counting
                    product_remaining = re.sub(r'\b' + re.escape(keyword) + r'\b', '', product_remaining)
        
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
            interest_text = str(interest).lower()
            product_text = str(product_category).lower()
            combined_text = f"{interest_text} {product_text}"
            
            # Remove excluded terms for fallback rule checking too
            for excluded_term in self.excluded_terms:
                combined_text = combined_text.replace(excluded_term, "")
            
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

    def get_engagement_quality_score(self, person):
        """Calculate engagement quality to differentiate genuine vs spillover traffic"""
        score = 0
        
        # Higher score for multiple interests mentioned
        interest_count = len(re.split(r'[,;]', str(person.get('interest', ''))))
        score += min(interest_count, 3) * 2  # Cap at 6 points
        
        # Higher score for specific/detailed interests vs generic ones
        interest_text = str(person.get('interest', '')).lower()
        if any(specific in interest_text for specific in ['designer', 'japanese fashion', 'fashion show', 'skincare', 'makeup']):
            score += 3
        
        # Concert attendance indicates genuine event engagement
        concerts = str(person.get('concerts_attended', '')).lower()
        if 'more than 3' in concerts:
            score += 3
        elif '2 to 3' in concerts:
            score += 2
        elif '1' in concerts:
            score += 1
            
        return score

    def analyze_engagement_quality(self):
        """Analyze engagement quality to validate persona assignments"""
        results = {}
        for persona in self.persona_keywords.keys():
            persona_users = [p for p in self.personas if persona in p["assigned_personas"]]
            if persona_users:
                scores = [self.get_engagement_quality_score(p) for p in persona_users]
                results[persona] = {
                    'avg_engagement': sum(scores) / len(scores),
                    'high_engagement_count': len([s for s in scores if s >= 6]),
                    'total_count': len(persona_users)
                }
    def get_multi_persona_users(self):
        """Get users with multiple personas"""
        return [p for p in self.personas if len(p["assigned_personas"]) > 1]


# --- Streamlit UI ---
st.title("Persona Customer Profiler")

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
        engagement_analysis = engine.analyze_engagement_quality()

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

        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Persona Distribution", "🔄 Multi-Persona Analysis", "🎯 Engagement Quality", "👥 Customer Groups", "🔍 Detailed View"])

        with tab1:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Individual Persona Distribution")
                
                # Add validation note
                st.info("💡 **Validation Note**: High Beauty Maven percentage could indicate:\n"
                       "• Genuine beauty interest from TGC attendees\n"  
                       "• Cross-event traffic from nearby beauty events\n"
                       "• Natural overlap between fashion and beauty interests")
                
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
            st.subheader("🎯 Engagement Quality Analysis")
            st.markdown("*Validates persona assignments by measuring engagement depth*")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Engagement Quality by Persona**")
                if engagement_analysis:
                    engagement_df = pd.DataFrame([
                        {
                            "Persona": persona,
                            "Avg Engagement Score": f"{data['avg_engagement']:.1f}",
                            "High Engagement %": f"{(data['high_engagement_count']/data['total_count']*100):.1f}%",
                            "Total Users": data['total_count']
                        }
                        for persona, data in engagement_analysis.items()
                    ])
                    st.dataframe(engagement_df, use_container_width=True)
                    
                    st.markdown("**📈 Engagement Score Factors:**")
                    st.markdown("""
                    - Multiple specific interests: +2-6 pts
                    - Detailed preferences (designer, japanese fashion, etc): +3 pts  
                    - High concert attendance: +1-3 pts
                    - **Score ≥6**: High engagement (genuine interest)
                    - **Score <4**: Potential spillover traffic
                    """)
            
            with col2:
                st.markdown("**Persona Validation Insights**")
                if engagement_analysis:
                    beauty_data = engagement_analysis.get('Beauty Maven', {})
                    fashion_data = engagement_analysis.get('Fashion Devotee', {})
                    japanese_data = engagement_analysis.get('Japanese Lover', {})
                    
                    if beauty_data:
                        beauty_high_pct = (beauty_data['high_engagement_count']/beauty_data['total_count']*100)
                        if beauty_high_pct > 60:
                            st.success(f"✅ **Beauty Maven validated**: {beauty_high_pct:.1f}% show high engagement")
                        elif beauty_high_pct > 40:
                            st.warning(f"⚠️ **Beauty Maven mixed**: {beauty_high_pct:.1f}% high engagement, {100-beauty_high_pct:.1f}% potential spillover")
                        else:
                            st.error(f"❌ **Beauty Maven concern**: Only {beauty_high_pct:.1f}% high engagement - investigate spillover")
                    
                    st.markdown("**🔍 Spillover Indicators:**")
                    st.markdown("""
                    - Low engagement scores in dominant persona
                    - Generic interests only
                    - Low concert attendance  
                    - Concentrated in specific time periods
                    - Geographic clustering near other events
                    """)

        with tab5:
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
    st.markdown("### 🆕 Refined Multi-Persona Approach:")
  

st.markdown("---")
st.markdown("© 2025 TGC Event Analysis | Enhanced Multi-Persona Classification 🎭")
