import streamlit as st
import pandas as pd
import re
from collections import Counter, defaultdict
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="TGC Fan Engagement & Monetization Analytics", layout="wide")

class PersonaEngine:
    def __init__(self):
        self.df = None
        self.personas = []
        
        # Enhanced keyword lists for TGC monetization focus
        self.persona_keywords = {
            "Fashion Devotee": {
                "fashion shows": 1, [cite: 2]
                "fashion shows and designer collections": 1, [cite: 2]
                "designer collections": 1, [cite: 2]
                "fashion and lifestyle": 1, [cite: 2]
                "live performances": 1, [cite: 2]
                "live performances or entertainment": 1, [cite: 3]
                "entertainment": 1, [cite: 3]
                "digital services": 1, [cite: 3]
                "entertainment and digital services": 1, [cite: 3]
                "shopping and brand booths": 1, [cite: 3]
                "shopping": 1, [cite: 4]
                "brand booths": 1, [cite: 4]
                "fashion": 1, [cite: 4]
                "style": 1, [cite: 4]
                "designer": 1, [cite: 4]
                "lifestyle": 1, [cite: 4]
                "clothing": 1, [cite: 5]
                "outfit": 1, [cite: 5]
                "trendy": 1, [cite: 5]
                "boutique": 1 [cite: 5]
            },
            "Beauty Maven": {
                "beauty and personal care": 1, [cite: 6]
                "personal care": 1, [cite: 6]
                "beauty": 1, [cite: 6]
                "skincare": 1, [cite: 6]
                "makeup": 1, [cite: 6]
                "cosmetic": 1, [cite: 6]
                "wellness": 1, [cite: 7]
                "grooming": 1, [cite: 7]
                "spa": 1 [cite: 7]
            },
            "Japanese Lover": {
                "japanese fashion and culture": 1, [cite: 8]
                "japanese fashion": 1, [cite: 8]
                "japanese culture": 1, [cite: 8]
                "japanese": 1, [cite: 8]
                "japan": 1, [cite: 8]
                "anime": 1, [cite: 8]
                "manga": 1, [cite: 8]
                "jpop": 1, [cite: 9]
                "kawaii": 1, [cite: 9]
                "otaku": 1, [cite: 9]
                "cosplay": 1 [cite: 9]
            }
        }
        
        # Excluded terms
        self.excluded_terms = [
            "exclusive tgc products", [cite: 10]
            "exclusive tgc product", [cite: 10]
            "tgc products", [cite: 10]
            "tgc product", [cite: 10]
            "voucher", [cite: 10]
            "vouchers", [cite: 10]
            "exclusive", [cite: 10]
            "kol influencer appearances" [cite: 11]
        ]

    def load_data(self, file):
        self.df = pd.read_csv(file)
        self.df.columns = self.df.columns.str.strip().str.lower()
        if 'gender' in self.df.columns: [cite: 12]
            st.write("✅ **Gender Column Found!**") [cite: 12]
        return not self.df.empty [cite: 13]

    def assign_personas(self, interest: str, product_category: str):
        interest_text = str(interest).lower()
        product_text = str(product_category).lower()
        combined_text = f"{interest_text} {product_text}" [cite: 14]
        for excluded_term in self.excluded_terms:
            combined_text = combined_text.replace(excluded_term, "") [cite: 14]
        
        combined_clean = re.sub(r'[^\w\s]', ' ', combined_text) [cite: 14]
        combined_clean = re.sub(r'\s+', ' ', combined_clean).strip() [cite: 14]
        
        assigned_personas = [] [cite: 15]
        for persona, keywords in self.persona_keywords.items():
            for keyword in keywords.keys():
                if re.search(r'\b' + re.escape(keyword) + r'\b', combined_clean): [cite: 16]
                    assigned_personas.append(persona)
                    break
        
        if not assigned_personas: [cite: 17]
             assigned_personas = ["Unclassified"] [cite: 18]
        
        return assigned_personas

    def get_emoji(self, persona):
        return {
            "Fashion Devotee": "👗",
            "Beauty Maven": "💄",
            "Japanese Lover": "🎌",
            "Unclassified": "❓"
        }.get(persona, "❓") [cite: 19]

    def get_affluence_score(self, concerts_attended):
        concerts = str(concerts_attended).lower()
        if "more than 3" in concerts:
            return 5
        elif "2 to 3" in concerts:
            return 3
        elif "1" in concerts: [cite: 20]
            return 2
        else:
            return 1

    def get_engagement_potential(self, persona_count, affluence_score):
        base_score = persona_count * 2
        return min(base_score + affluence_score, 10) [cite: 21]

    def process(self):
        self.personas = []
        for _, row in self.df.iterrows():
            interest = row.get("interest", "")
            product_category = row.get("product category", "")
            concerts = row.get("concerts attended", "")
            
            assigned_personas = self.assign_personas(interest, product_category) [cite: 22]
            persona_str = " + ".join(assigned_personas)
            emoji_str = "".join([self.get_emoji(p) for p in assigned_personas])
            affluence_score = self.get_affluence_score(concerts)
            engagement_potential = self.get_engagement_potential(len(assigned_personas), affluence_score) [cite: 23]
            
            if len(assigned_personas) >= 2 and affluence_score >= 4:
                fan_segment = "VIP Fan (High Value)"
            elif len(assigned_personas) >= 2 or affluence_score >= 3:
                fan_segment = "Premium Fan" [cite: 24]
            elif affluence_score >= 2:
                fan_segment = "Active Fan"
            else:
                fan_segment = "Casual Visitor"
            
            self.personas.append({
                "email": row.get("email", ""), [cite: 25]
                "phone": row.get("phone", ""), [cite: 25]
                "first_name": row.get("first name", ""), [cite: 25]
                "last_name": row.get("last name", ""), [cite: 25]
                "city": row.get("city", ""), [cite: 25]
                "gender": row.get("gender", "Unknown"),
                "interest": interest, [cite: 26]
                "product_interest": product_category, [cite: 26]
                "concerts_attended": concerts, [cite: 26]
                "assigned_personas": assigned_personas, [cite: 26]
                "persona_string": persona_str, [cite: 26]
                "emoji": emoji_str, [cite: 26]
                "total_personas": len(assigned_personas), [cite: 27]
                "affluence_score": affluence_score, [cite: 27]
                "engagement_potential": engagement_potential, [cite: 27]
                "fan_segment": fan_segment [cite: 27]
            })

    def to_df(self):
        return pd.DataFrame(self.personas)

    def get_persona_stats(self):
        persona_counts = defaultdict(int) [cite: 28]
        for person in self.personas:
            for persona in person["assigned_personas"]:
                persona_counts[persona] += 1 [cite: 28]
        return dict(persona_counts)

    def get_gender_stats(self):
        df = self.to_df()
        if 'gender' in df.columns:
            return df["gender"].value_counts()
        return None

    def get_persona_portions(self):
        df = self.to_df()
        total_customers = len(df)
        persona_reach = defaultdict(int) [cite: 29]
        for person in self.personas:
            for persona in set(person["assigned_personas"]): # Use set to count each user once per persona
                persona_reach[persona] += 1
        
        persona_portions = {}
        if total_customers > 0:
            for persona, count in persona_reach.items():
                persona_portions[persona] = {
                    'count': count,
                    'percentage': (count / total_customers) * 100 [cite: 31]
                }
        return persona_portions

    def get_monetization_insights(self):
        df = self.to_df()
        fan_segments = df['fan_segment'].value_counts() [cite: 32]
        high_affluence = len(df[df['affluence_score'] >= 4]) [cite: 32]
        medium_affluence = len(df[df['affluence_score'] == 3]) [cite: 32]
        premium_customers = len(df[df['total_personas'] >= 2]) [cite: 32]
        tgc_aligned = len(df[df['persona_string'].str.contains('Fashion|Japanese', na=False)]) [cite: 33]
        
        return {
            'fan_segments': fan_segments,
            'high_affluence_count': high_affluence,
            'medium_affluence_count': medium_affluence,
            'premium_customers': premium_customers,
            'tgc_content_aligned': tgc_aligned, [cite: 34]
            'total_customers': len(df) [cite: 34]
        }


# --- Streamlit UI ---
st.title("🎪 TGC Fan Engagement & Monetization Analytics")
st.markdown("*Analyzing customer segments for sponsorship value, merchandise sales, and WA campaign targeting*")

engine = PersonaEngine()
file = st.file_uploader("Upload TGC customer data CSV", type="csv")

if file:
    if engine.load_data(file):
        engine.process()
        df_result = engine.to_df()
        persona_portions = engine.get_persona_portions()
        gender_stats = engine.get_gender_stats()
        monetization_insights = engine.get_monetization_insights() [cite: 35]

        # --- Dashboard Metrics ---
        st.markdown("### 💰 TGC Monetization Dashboard")
        col1, col2, col3, col4 = st.columns(4)
        total_customers = monetization_insights['total_customers']
        if total_customers > 0:
            with col1:
                st.metric(
                    "💎 VIP Segment", [cite: 39]
                    len(df_result[df_result['fan_segment'] == 'VIP Fan (High Value)']),
                    f"{(len(df_result[df_result['fan_segment'] == 'VIP Fan (High Value)'])/total_customers*100):.1f}% of base"
                )
            with col2:
                st.metric(
                    "⭐ Premium Customers", [cite: 37]
                    monetization_insights['premium_customers'],
                    f"{(monetization_insights['premium_customers']/total_customers*100):.1f}% multi-persona"
                )
            with col3:
                st.metric(
                    "🎯 High-Value Fans", [cite: 36]
                    monetization_insights['high_affluence_count'],
                    f"{(monetization_insights['high_affluence_count']/total_customers*100):.1f}% of base"
                )
            with col4:
                st.metric(
                    "🎪 TGC Content Aligned", [cite: 38]
                    monetization_insights['tgc_content_aligned'],
                    f"{(monetization_insights['tgc_content_aligned']/total_customers*100):.1f}% alignment"
                )

        # --- Tabs ---
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Fan Segments", "📊 Persona & Demographics", "💰 Monetization Potential", "🛒 EC Performance (Pending)", "🔍 Customer Details"])

        with tab1:
            st.subheader("Fan Segment Analysis for TGC Monetization") [cite: 40]
            col1, col2 = st.columns(2)
            with col1:
                fan_segments = df_result['fan_segment'].value_counts() [cite: 41]
                fig_segments = px.pie(
                    names=fan_segments.index,
                    values=fan_segments.values,
                    title="Fan Segments (Monetization Priority)",
                    color_discrete_map={
                        'VIP Fan (High Value)': '#FFD700', [cite: 42]
                        'Premium Fan': '#C0C0C0', [cite: 42]
                        'Active Fan': '#CD7F32', [cite: 42]
                        'Casual Visitor': '#808080' [cite: 43]
                    }
                )
                st.plotly_chart(fig_segments, use_container_width=True)
            with col2:
                fig_scatter = px.scatter(
                    df_result, x='affluence_score', y='engagement_potential',
                    color='fan_segment', [cite: 45]
                    size='total_personas',
                    title="Affluence vs Engagement Potential",
                    labels={'affluence_score': 'Spending Power (Concert Attendance)', 'engagement_potential': 'Marketing Engagement Score'} [cite: 46]
                )
                st.plotly_chart(fig_scatter, use_container_width=True)

        with tab2:
            st.subheader("Persona & Demographic Analysis")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("**Persona Reach**")
                if persona_portions:
                    fig_pie = px.pie(
                        names=list(persona_portions.keys()),
                        values=[d['count'] for d in persona_portions.values()],
                        title="Persona Reach (% of Fan Base)"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("No persona data to display.")
            with col2:
                st.markdown("**Gender Distribution**")
                if gender_stats is not None and not gender_stats.empty:
                    fig_gender = px.pie(names=gender_stats.index, values=gender_stats.values, title="Gender Distribution")
                    st.plotly_chart(fig_gender, use_container_width=True)
                else:
                    st.info("Gender data not available in the uploaded file.")
            with col3:
                st.markdown("**Interest Diversity**")
                single_persona = len(df_result[df_result['total_personas'] == 1])
                multi_persona = len(df_result[df_result['total_personas'] > 1])
                fig_multi = px.pie(
                    names=["Single Interest", "Multi-Interest"],
                    values=[single_persona, multi_persona],
                    title="Customer Interest Diversity" [cite: 81]
                )
                st.plotly_chart(fig_multi, use_container_width=True)

        with tab3:
            st.subheader("Monetization Strategy Analysis")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**WA Campaign Targeting Priority**") [cite: 51]
                targeting_data = []
                for segment in df_result['fan_segment'].unique():
                    segment_df = df_result[df_result['fan_segment'] == segment] [cite: 52]
                    avg_engagement = segment_df['engagement_potential'].mean()
                    avg_affluence = segment_df['affluence_score'].mean()
                    count = len(segment_df)
                    targeting_data.append({ [cite: 53]
                        'Segment': segment, 'Count': count,
                        'Avg Engagement': round(avg_engagement, 1), [cite: 54]
                        'Avg Affluence': round(avg_affluence, 1), [cite: 54]
                        'Priority': 'High' if avg_engagement >= 6 else 'Medium' if avg_engagement >= 4 else 'Low' [cite: 54]
                    })
                targeting_df = pd.DataFrame(targeting_data).sort_values('Avg Engagement', ascending=False) [cite: 55]
                st.dataframe(targeting_df, use_container_width=True)
            with col2:
                st.markdown("**Expected Performance vs Shopee**")
                metrics_data = {
                    'Metric': ['Customer Base Quality', 'Personalization Accuracy', 'Affluence Level', 'TGC Content Affinity'], [cite: 57]
                    'TGC Score': [85, 90, 75, 95], [cite: 57]
                    'Shopee Benchmark': [70, 75, 80, 60] [cite: 57]
                }
                comparison_df = pd.DataFrame(metrics_data) [cite: 58]
                fig_comparison = px.bar(
                    comparison_df, x='Metric', y=['TGC Score', 'Shopee Benchmark'], [cite: 59]
                    title="TGC vs Shopee Performance Hypothesis", barmode='group'
                )
                st.plotly_chart(fig_comparison, use_container_width=True) [cite: 60]

        with tab4:
            st.subheader("🛒 EC Shop Performance Analysis")
            st.warning("⏳ **EC Performance Data Integration - Coming Soon**") [cite: 61]
            st.info("When EC data is available, we will validate conversion rates, AOV, and product affinity by persona.") [cite: 69, 70, 71, 72, 73, 74]

        with tab5:
            st.subheader("Customer Segments for Targeted Campaigns")
            filter_options = ["All"] + list(engine.persona_keywords.keys()) + ["Unclassified"] + list(df_result['fan_segment'].unique())
            filter_selection = st.selectbox("Filter customers by:", filter_options) [cite: 82]

            filtered_df = df_result.copy()
            if filter_selection != "All":
                if filter_selection in engine.persona_keywords.keys() or filter_selection == "Unclassified":
                    filtered_df = df_result[df_result['assigned_personas'].apply(lambda x: filter_selection in x)] [cite: 83, 84]
                else:
                    filtered_df = df_result[df_result['fan_segment'] == filter_selection] [cite: 85]

            if not filtered_df.empty:
                st.dataframe(filtered_df[[
                    "first_name", "last_name", "persona_string", "fan_segment",
                    "affluence_score", "engagement_potential", "interest", "product_interest"
                ]].rename(columns={
                    "first_name": "First Name", "last_name": "Last Name",
                    "persona_string": "Personas", "fan_segment": "Fan Segment",
                    "affluence_score": "Affluence", "engagement_potential": "Engagement"
                }), height=400)

                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Campaign Target List", [cite: 106]
                    data=csv,
                    file_name=f"tgc_campaign_targets_{filter_selection}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No customers match your filter criteria.") [cite: 107]

    else:
        st.error("Could not read uploaded CSV. Please check formatting.") [cite: 132]
else:
    st.info("Upload your TGC customer data CSV to begin monetization analysis.")
    st.markdown("### 🎯 TGC Monetization Analysis Features:") [cite: 108]
    st.markdown("""
    - **Fan Segmentation**: VIP, Premium, Active, and Casual visitors based on spending and engagement
    - **Affluence Scoring**: Concert attendance as proxy for spending power
    - **Campaign Targeting**: Prioritized customer lists for WA campaigns
    - **Content Alignment**: Identify customers aligned with TGC themes for higher engagement
    - **Shopee Comparison**: Framework to validate hypothesis about customer quality vs Shopee [cite: 109]
    - **Revenue Optimization**: Multi-persona customers for cross-selling opportunities [cite: 109]
    """)

st.markdown("---")
st.markdown("© 2025 TGC Event Analysis | Fan Monetization & Engagement Analytics")
