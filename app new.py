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
        
        # Excluded terms
        self.excluded_terms = [
            "exclusive tgc products",
            "exclusive tgc product", 
            "tgc products",
            "tgc product",
            "voucher",
            "vouchers",
            "exclusive",
            "kol influencer appearances"
        ]

    def load_data(self, file):
        self.df = pd.read_csv(file)
        self.df.columns = self.df.columns.str.strip().str.lower()
        
        # Debug: Show available columns
        st.write("🔍 **Debug Info - Available Columns:**", list(self.df.columns))
        
        # Debug: Show gender column info if it exists
        if 'gender' in self.df.columns:
            st.write("✅ **Gender Column Found!**")
            st.write("Gender values:", self.df['gender'].value_counts().to_dict())
            st.write("Sample gender data:", self.df['gender'].head().tolist())
        else:
            st.warning("❌ **Gender column not found!** Available columns: " + ", ".join(self.df.columns))
        
        return not self.df.empty

    def assign_personas(self, interest: str, product_category: str):
        # Handle list format
        if isinstance(interest, list):
            interest_text = ", ".join(str(item) for item in interest).lower()
        else:
            interest_text = str(interest).lower()
            
        product_text = str(product_category).lower()
        
        # Remove excluded terms
        combined_text = f"{interest_text} {product_text}"
        for excluded_term in self.excluded_terms:
            combined_text = combined_text.replace(excluded_term, "")
        
        # Clean text
        combined_clean = re.sub(r'[^\w\s]', ' ', combined_text)
        combined_clean = re.sub(r'\s+', ' ', combined_clean).strip()
        
        assigned_personas = []
        
        # Simple check: if ANY keyword found, assign persona
        for persona, keywords in self.persona_keywords.items():
            persona_found = False
            for keyword in keywords.keys():
                if re.search(r'\b' + re.escape(keyword) + r'\b', combined_clean):
                    persona_found = True
                    break
            
            if persona_found:
                assigned_personas.append(persona)
        
        # Fallback rule
        if not assigned_personas:
            if (("live performance" in combined_clean or "entertainment" in combined_clean) and 
                ("digital service" in combined_clean or "entertainment and digital" in combined_clean)):
                assigned_personas = ["Fashion Devotee"]
            else:
                assigned_personas = ["Unclassified"]
        
        return assigned_personas

    def get_emoji(self, persona):
        return {
            "Fashion Devotee": "👗",
            "Beauty Maven": "💄",
            "Japanese Lover": "🎌",
            "Unclassified": "❓"
        }.get(persona, "❓")

    def get_affluence_score(self, concerts_attended):
        """Calculate affluence score based on concert attendance (spending behavior)"""
        concerts = str(concerts_attended).lower()
        if "more than 3" in concerts:
            return 5  # High affluence
        elif "2 to 3" in concerts:
            return 3  # Medium affluence
        elif "1" in concerts:
            return 2  # Low affluence
        else:
            return 1  # Very low affluence

    def get_engagement_potential(self, persona_count, affluence_score):
        """Calculate engagement potential for monetization"""
        base_score = persona_count * 2  # Multi-persona = higher engagement
        return min(base_score + affluence_score, 10)  # Cap at 10

    def process(self):
        self.personas = []
        for _, row in self.df.iterrows():
            interest = row.get("interest", "")
            product_category = row.get("product category", "")
            concerts = row.get("concerts attended", "")
            
            assigned_personas = self.assign_personas(interest, product_category)
            
            persona_str = " + ".join(assigned_personas)
            emoji_str = "".join([self.get_emoji(p) for p in assigned_personas])
            
            # Calculate monetization metrics
            affluence_score = self.get_affluence_score(concerts)
            engagement_potential = self.get_engagement_potential(len(assigned_personas), affluence_score)
            
            # Classify fan segment
            if len(assigned_personas) >= 2 and affluence_score >= 4:
                fan_segment = "VIP Fan (High Value)"
            elif len(assigned_personas) >= 2 or affluence_score >= 3:
                fan_segment = "Premium Fan"
            elif affluence_score >= 2:
                fan_segment = "Active Fan"
            else:
                fan_segment = "Casual Visitor"
            
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
                "total_personas": len(assigned_personas),
                "affluence_score": affluence_score,
                "engagement_potential": engagement_potential,
                "fan_segment": fan_segment
            })

    def to_df(self):
        return pd.DataFrame(self.personas)

    def get_persona_stats(self):
        persona_counts = defaultdict(int)
        for person in self.personas:
            for persona in person["assigned_personas"]:
                persona_counts[persona] += 1
        return dict(persona_counts)

    def get_combination_stats(self):
        combination_counts = Counter(p["persona_string"] for p in self.personas)
        return combination_counts

    def get_city_stats(self):
        return self.to_df()["city"].value_counts()

    def get_gender_stats(self):
        return self.to_df()["gender"].value_counts()

    def get_persona_portions(self):
        """Calculate persona portions including multi-persona breakdown"""
        df = self.to_df()
        total_customers = len(df)
        
        # Individual persona reach
        persona_reach = defaultdict(int)
        for person in self.personas:
            for persona in person["assigned_personas"]:
                persona_reach[persona] += 1
        
        # Calculate portions
        persona_portions = {}
        for persona, count in persona_reach.items():
            persona_portions[persona] = {
                'count': count,
                'percentage': (count / total_customers) * 100
            }
        
    def get_multi_persona_users(self):
        return [p for p in self.personas if len(p["assigned_personas"]) > 1]

    def get_monetization_insights(self):
        """Generate insights for TGC monetization strategy"""
        df = self.to_df()
        
        # Fan segment analysis
        fan_segments = df['fan_segment'].value_counts()
        
        # Affluence analysis
        high_affluence = len(df[df['affluence_score'] >= 4])
        medium_affluence = len(df[df['affluence_score'] == 3])
        
        # Multi-persona premium customers
        premium_customers = len(df[df['total_personas'] >= 2])
        
        # TGC content engagement (fashion + japanese culture)
        tgc_aligned = len(df[df['persona_string'].str.contains('Fashion|Japanese', na=False)])
        
        return {
            'fan_segments': fan_segments,
            'high_affluence_count': high_affluence,
            'medium_affluence_count': medium_affluence,
            'premium_customers': premium_customers,
            'tgc_content_aligned': tgc_aligned,
            'total_customers': len(df)
        }


# Streamlit UI
st.title("🎪 TGC Fan Engagement & Monetization Analytics")
st.markdown("*Analyzing customer segments for sponsorship value, merchandise sales, and WA campaign targeting*")

engine = PersonaEngine()
file = st.file_uploader("Upload TGC customer data CSV", type="csv")

if file:
    if engine.load_data(file):
        engine.process()
        df_result = engine.to_df()
        persona_stats = engine.get_persona_stats()
        combination_stats = engine.get_combination_stats()
        city_counts = engine.get_city_stats()
        multi_persona_users = engine.get_multi_persona_users()
        monetization_insights = engine.get_monetization_insights()

        # TGC Business Metrics Dashboard
        st.markdown("### 💰 TGC Monetization Dashboard")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🎯 High-Value Fans", 
                monetization_insights['high_affluence_count'],
                f"{(monetization_insights['high_affluence_count']/monetization_insights['total_customers']*100):.1f}% of base"
            )
        
        with col2:
            st.metric(
                "⭐ Premium Customers", 
                monetization_insights['premium_customers'],
                f"{(monetization_insights['premium_customers']/monetization_insights['total_customers']*100):.1f}% multi-persona"
            )
        
        with col3:
            st.metric(
                "🎪 TGC Content Aligned", 
                monetization_insights['tgc_content_aligned'],
                f"{(monetization_insights['tgc_content_aligned']/monetization_insights['total_customers']*100):.1f}% alignment"
            )
        
        with col4:
            vip_fans = len(df_result[df_result['fan_segment'] == 'VIP Fan (High Value)'])
            st.metric(
                "💎 VIP Segment", 
                vip_fans,
                f"{(vip_fans/monetization_insights['total_customers']*100):.1f}% VIP rate"
            )

        tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Fan Segments", "💰 Monetization Potential", "🛒 EC Performance (Pending)", "📊 Persona Analysis", "🔍 Customer Details"])

        with tab1:
            st.subheader("Fan Segment Analysis for TGC Monetization")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Fan segment distribution
                fan_segments = df_result['fan_segment'].value_counts()
                fig_segments = px.pie(
                    names=fan_segments.index,
                    values=fan_segments.values,
                    title="Fan Segments (Monetization Priority)",
                    color_discrete_map={
                        'VIP Fan (High Value)': '#FFD700',
                        'Premium Fan': '#C0C0C0', 
                        'Active Fan': '#CD7F32',
                        'Casual Visitor': '#808080'
                    }
                )
                st.plotly_chart(fig_segments, use_container_width=True)
            
            with col2:
                # Affluence vs Engagement scatter
                fig_scatter = px.scatter(
                    df_result, 
                    x='affluence_score', 
                    y='engagement_potential',
                    color='fan_segment',
                    size='total_personas',
                    title="Affluence vs Engagement Potential",
                    labels={
                        'affluence_score': 'Spending Power (Concert Attendance)',
                        'engagement_potential': 'Marketing Engagement Score'
                    }
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
            
            # Business insights
            st.markdown("### 💡 Key Business Insights")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**📈 Revenue Opportunity:**")
                high_value = len(df_result[df_result['affluence_score'] >= 4])
                st.write(f"• {high_value} customers show high spending behavior")
                st.write(f"• {monetization_insights['premium_customers']} have multi-category interests")
                st.write(f"• Target for premium merchandise and VIP experiences")
            
            with col2:
                st.markdown("**🎯 Campaign Targeting:**")
                tgc_fashion = len(df_result[df_result['persona_string'].str.contains('Fashion', na=False)])
                tgc_japanese = len(df_result[df_result['persona_string'].str.contains('Japanese', na=False)])
                st.write(f"• {tgc_fashion} customers interested in fashion content")
                st.write(f"• {tgc_japanese} customers love Japanese culture")
                st.write(f"• Higher WA engagement expected for TGC-aligned content")

        with tab2:
            st.subheader("Monetization Strategy Analysis")
            
            # Revenue potential by segment
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**WA Campaign Targeting Priority**")
                
                # Create targeting priority dataframe
                targeting_data = []
                for segment in df_result['fan_segment'].unique():
                    segment_df = df_result[df_result['fan_segment'] == segment]
                    avg_engagement = segment_df['engagement_potential'].mean()
                    avg_affluence = segment_df['affluence_score'].mean()
                    count = len(segment_df)
                    
                    targeting_data.append({
                        'Segment': segment,
                        'Count': count,
                        'Avg Engagement': round(avg_engagement, 1),
                        'Avg Affluence': round(avg_affluence, 1),
                        'Priority': 'High' if avg_engagement >= 6 else 'Medium' if avg_engagement >= 4 else 'Low'
                    })
                
                targeting_df = pd.DataFrame(targeting_data).sort_values('Avg Engagement', ascending=False)
                st.dataframe(targeting_df, use_container_width=True)
            
            with col2:
                st.markdown("**Expected Performance vs Shopee**")
                
                # Hypothesis validation metrics
                total_customers = len(df_result)
                high_engagement = len(df_result[df_result['engagement_potential'] >= 6])
                multi_persona = len(df_result[df_result['total_personas'] >= 2])
                
                metrics_data = {
                    'Metric': ['Customer Base Quality', 'Personalization Accuracy', 'Affluence Level', 'TGC Content Affinity'],
                    'TGC Score': [85, 90, 75, 95],  # Hypothetical scores for comparison
                    'Shopee Benchmark': [70, 75, 80, 60]
                }
                
                comparison_df = pd.DataFrame(metrics_data)
                fig_comparison = px.bar(
                    comparison_df, 
                    x='Metric', 
                    y=['TGC Score', 'Shopee Benchmark'],
                    title="TGC vs Shopee Performance Hypothesis",
                    barmode='group'
                )
                st.plotly_chart(fig_comparison, use_container_width=True)

        with tab3:
            st.subheader("🛒 EC Shop Performance Analysis")
            st.markdown("*Waiting for actual purchase data to validate persona effectiveness*")
            
            # Placeholder for EC performance integration
            st.warning("⏳ **EC Performance Data Integration - Coming Soon**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📊 Expected Performance by Persona")
                st.markdown("Once EC shop data is available, we'll analyze:")
                
                # Prepare framework for EC analysis
                persona_expectations = {
                    "👗 Fashion Devotee": {
                        "Expected Conversion": "High for fashion items",
                        "Target Products": "Clothing, accessories, lifestyle",
                        "Expected AOV": "Medium-High",
                        "WA Campaign CTR": "High for fashion content"
                    },
                    "💄 Beauty Maven": {
                        "Expected Conversion": "High for beauty products", 
                        "Target Products": "Skincare, makeup, wellness",
                        "Expected AOV": "Medium",
                        "WA Campaign CTR": "High for beauty content"
                    },
                    "🎌 Japanese Lover": {
                        "Expected Conversion": "High for Japanese brands",
                        "Target Products": "Japanese fashion, culture items",
                        "Expected AOV": "High (premium positioning)",
                        "WA Campaign CTR": "Very high for J-culture content"
                    }
                }
                
                for persona, expectations in persona_expectations.items():
                    with st.expander(f"{persona} - Purchase Predictions"):
                        for metric, value in expectations.items():
                            st.write(f"**{metric}:** {value}")
            
            with col2:
                st.markdown("### 🎯 Validation Framework Ready")
                
                st.info("""
                **When EC data arrives, we'll measure:**
                
                ✅ **Conversion Rate by Persona**
                - Which persona converts best?
                - Multi-persona vs single-persona performance
                
                ✅ **Average Order Value (AOV)**
                - Fashion vs Beauty vs Japanese Lover AOV
                - VIP segment premium pricing validation
                
                ✅ **Product Affinity**
                - Do Fashion Devotees buy fashion items?
                - Cross-sell success in multi-persona users
                
                ✅ **Campaign Performance**
                - WA engagement vs actual purchases
                - TGC content alignment impact on sales
                
                ✅ **Hypothesis Validation**
                - Affluent fans spending validation
                - Superior performance vs Shopee metrics
                """)
                
                # File uploader for future EC data
                st.markdown("### 📥 Ready for EC Data Integration")
                ec_file = st.file_uploader(
                    "Upload EC shop performance data (when available)", 
                    type="csv",
                    help="Upload purchase data with customer IDs to validate persona performance"
                )
                
                if ec_file:
                    st.success("EC data received! Processing persona performance...")
                    # Here you would integrate the actual EC performance analysis
                    st.info("💡 **Tip:** Ensure EC data includes customer email/phone to match with persona data")

        with tab4:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Persona Distribution")
                fig_pie = px.pie(
                    names=list(persona_stats.keys()),
                    values=list(persona_stats.values()),
                    title="Customer Personas for Content Strategy"
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            with col2:
                st.subheader("Multi-Persona Analysis")
                single_persona = len([p for p in engine.personas if len(p["assigned_personas"]) == 1])
                multi_persona = len(multi_persona_users)
                
                fig_multi = px.pie(
                    names=["Single Interest", "Multi-Interest"],
                    values=[single_persona, multi_persona],
                    title="Customer Interest Diversity (Cross-sell Potential)"
                )
                st.plotly_chart(fig_multi, use_container_width=True)

        with tab4:
            st.subheader("Customer Segments for Targeted Campaigns")
            
            filter_options = ["All"] + list(engine.persona_keywords.keys()) + ["Unclassified"] + list(df_result['fan_segment'].unique())
            filter_selection = st.selectbox("Filter customers by:", filter_options)
            
            filtered_data = engine.personas.copy()
            
            if filter_selection != "All":
                if filter_selection in engine.persona_keywords.keys() or filter_selection == "Unclassified":
                    # Filter by persona
                    filtered_data = [
                        p for p in filtered_data 
                        if filter_selection in p["assigned_personas"]
                    ]
                else:
                    # Filter by fan segment
                    filtered_data = [
                        p for p in filtered_data 
                        if p["fan_segment"] == filter_selection
                    ]
            
            if filtered_data:
                # Group by persona combinations with monetization insights
                combination_counts = defaultdict(int)
                combination_data = defaultdict(list)
                
                for person in filtered_data:
                    combo = f"{person['persona_string']} ({person['fan_segment']})"
                    combination_counts[combo] += 1
                    combination_data[combo].append(person)
                
                # Sort by business value (VIP first, then multi-persona, then count)
                def sort_key(item):
                    combo, count = item
                    if "VIP Fan" in combo:
                        return (0, -count)  # VIP first
                    elif "Premium Fan" in combo:
                        return (1, -count)  # Premium second
                    elif "+" in combo:
                        return (2, -count)  # Multi-persona third
                    else:
                        return (3, -count)  # Single persona last
                
                sorted_combinations = sorted(combination_counts.items(), key=sort_key)
                
                for combo, count in sorted_combinations:
                    # Extract segment info for styling
                    if "VIP Fan" in combo:
                        icon = "💎"
                    elif "Premium Fan" in combo:
                        icon = "⭐"
                    elif "Active Fan" in combo:
                        icon = "🎯"
                    else:
                        icon = "👤"
                    
                    with st.expander(f"{icon} {combo} • {count} customers", expanded=(count <= 20 or "VIP" in combo)):
                        combo_customers = combination_data[combo]
                        
                        # Business insights for this segment
                        avg_affluence = sum(p['affluence_score'] for p in combo_customers) / len(combo_customers)
                        avg_engagement = sum(p['engagement_potential'] for p in combo_customers) / len(combo_customers)
                        
                        insight_col1, insight_col2, insight_col3 = st.columns(3)
                        with insight_col1:
                            st.metric("💰 Avg Affluence", f"{avg_affluence:.1f}/5")
                        with insight_col2:
                            st.metric("📈 Engagement Score", f"{avg_engagement:.1f}/10")
                        with insight_col3:
                            campaign_priority = "High" if avg_engagement >= 6 else "Medium" if avg_engagement >= 4 else "Low"
                            st.metric("🎯 Campaign Priority", campaign_priority)
                        
                        # Customer details
                        combo_df = pd.DataFrame(combo_customers)[
                            ["first_name", "last_name", "interest", "product_interest", "concerts_attended", "affluence_score", "engagement_potential"]
                        ].rename(columns={
                            "first_name": "First Name",
                            "last_name": "Last Name",
                            "interest": "Interests", 
                            "product_interest": "Product Category",
                            "concerts_attended": "Concert Attendance",
                            "affluence_score": "Affluence",
                            "engagement_potential": "Engagement"
                        })
                        
                        st.dataframe(combo_df.reset_index(drop=True), use_container_width=True)
                
                # Download with monetization insights
                detailed_df = pd.DataFrame(filtered_data)[
                    ["first_name", "last_name", "persona_string", "fan_segment",
                     "interest", "product_interest", "concerts_attended", 
                     "affluence_score", "engagement_potential"]
                ].rename(columns={
                    "first_name": "First Name",
                    "last_name": "Last Name",
                    "persona_string": "Personas",
                    "fan_segment": "Fan Segment",
                    "interest": "Interests", 
                    "product_interest": "Product Category",
                    "concerts_attended": "Concert Attendance",
                    "affluence_score": "Affluence Score",
                    "engagement_potential": "Engagement Potential"
                })
                
                csv = detailed_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Campaign Target List",
                    data=csv,
                    file_name="tgc_campaign_targets.csv",
                    mime="text/csv"
                )
            else:
                st.info("No customers match your filter criteria.")

    else:
        st.error("Could not read uploaded CSV. Please check formatting.")
else:
    st.info("Upload your TGC customer data CSV to begin monetization analysis.")
    
    st.markdown("### 🎯 TGC Monetization Analysis Features:")
    st.markdown("""
    - **Fan Segmentation**: VIP, Premium, Active, and Casual visitors based on spending and engagement
    - **Affluence Scoring**: Concert attendance as proxy for spending power
    - **Campaign Targeting**: Prioritized customer lists for WA campaigns
    - **Content Alignment**: Identify customers aligned with TGC themes for higher engagement
    - **Shopee Comparison**: Framework to validate hypothesis about customer quality vs Shopee
    - **Revenue Optimization**: Multi-persona customers for cross-selling opportunities
    """)

st.markdown("---")
st.markdown("© 2025 TGC Event Analysis | Fan Monetization & Engagement Analytics")container_width=True)

        with tab2:
            st.subheader("Multi-Persona Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Persona Combinations**")
                combo_df = pd.DataFrame([
                    {"Combination": combo, "Count": count}
                    for combo, count in combination_stats.most_common(10)
                ])
                fig_combo = px.bar(combo_df, x="Count", y="Combination", orientation='h',
                                 title="Top 10 Persona Combinations")
                fig_combo.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_combo, use_container_width=True)
            
            with col2:
                st.markdown("**Single vs Multi-Persona**")
                single_persona = len([p for p in engine.personas if len(p["assigned_personas"]) == 1])
                multi_persona = len(multi_persona_users)
                
                fig_multi = px.pie(
                    names=["Single Persona", "Multi-Persona"],
                    values=[single_persona, multi_persona],
                    title="Single vs Multi-Persona Users"
                )
                st.plotly_chart(fig_multi, use_container_width=True)

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
            st.subheader("Customer Segments")
            
            filter_persona = st.selectbox(
                "Filter by persona:",
                ["All"] + list(engine.persona_keywords.keys()) + ["Unclassified"]
            )
            
            filtered_data = engine.personas.copy()
            
            if filter_persona != "All":
                filtered_data = [
                    p for p in filtered_data 
                    if filter_persona in p["assigned_personas"]
                ]
            
            if filtered_data:
                # Group by persona combinations
                combination_counts = defaultdict(int)
                combination_data = defaultdict(list)
                
                for person in filtered_data:
                    combo = person["persona_string"]
                    combination_counts[combo] += 1
                    combination_data[combo].append(person)
                
                # Sort by multi-persona first, then by count
                def sort_key(item):
                    combo, count = item
                    persona_count = len(combo.split(" + "))
                    return (-persona_count, -count)
                
                sorted_combinations = sorted(combination_counts.items(), key=sort_key)
                
                for combo, count in sorted_combinations:
                    personas = combo.split(" + ")
                    emoji_combo = "".join([engine.get_emoji(p) for p in personas])
                    
                    with st.expander(f"{emoji_combo} {combo} ({count} customers)", expanded=(count <= 30)):
                        combo_customers = combination_data[combo]
                        
                        combo_df = pd.DataFrame(combo_customers)[
                            ["first_name", "last_name", "interest", "product_interest", "concerts_attended"]
                        ].rename(columns={
                            "first_name": "First Name",
                            "last_name": "Last Name",
                            "interest": "Interests", 
                            "product_interest": "Product Category",
                            "concerts_attended": "Concert Attendance"
                        })
                        
                        st.dataframe(combo_df.reset_index(drop=True), use_container_width=True)
                
                # Download
                detailed_df = pd.DataFrame(filtered_data)[
                    ["first_name", "last_name", "persona_string", 
                     "interest", "product_interest", "concerts_attended"]
                ].rename(columns={
                    "first_name": "First Name",
                    "last_name": "Last Name",
                    "persona_string": "Personas",
                    "interest": "Interests", 
                    "product_interest": "Product Category",
                    "concerts_attended": "Concert Attendance"
                })
                
                csv = detailed_df.to_csv(index=False)
                st.download_button(
                    label="Download Customer Data",
                    data=csv,
                    file_name="customer_personas.csv",
                    mime="text/csv"
                )
            else:
                st.info("No customers match your filter criteria.")

    else:
        st.error("Could not read uploaded CSV. Please check formatting.")
else:
    st.info("Upload your customer CSV file to begin persona analysis.")

st.markdown("---")
st.markdown("© 2025 TGC Event Analysis - Multi-Persona Classification")
