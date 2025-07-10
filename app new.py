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

    def load_data(self, file):
        self.df = pd.read_csv(file)
        self.df.columns = self.df.columns.str.strip().str.lower()
        return not self.df.empty

    def assign_personas(self, interest: str, product_category: str):
        """Simple presence-based persona assignment - if keywords found, assign persona"""
        # Handle list format (convert to string if needed)
        if isinstance(interest, list):
            interest_text = ", ".join(str(item) for item in interest).lower()
        else:
            interest_text = str(interest).lower()
            
        product_text = str(product_category).lower()
        
        # Remove excluded terms from analysis
        combined_text = f"{interest_text} {product_text}"
        for excluded_term in self.excluded_terms:
            combined_text = combined_text.replace(excluded_term, "")
        
        # Clean text
        combined_clean = re.sub(r'[^\w\s]', ' ', combined_text)
        combined_clean = re.sub(r'\s+', ' ', combined_clean).strip()
        
        assigned_personas = []
        simple_scores = {persona: 0 for persona in self.persona_keywords}
        
        # Simple check: if ANY keyword from a persona is found, assign that persona
        for persona, keywords in self.persona_keywords.items():
            persona_found = False
            for keyword in keywords.keys():
                if re.search(r'\b' + re.escape(keyword) + r'\b', combined_clean):
                    persona_found = True
                    simple_scores[persona] = 1  # Just mark as present
                    break  # Found one keyword, that's enough
            
            if persona_found:
                assigned_personas.append(persona)
        
        # Fallback rule if no personas found
        if not assigned_personas:
            if (("live performance" in combined_clean or "entertainment" in combined_clean) and 
                ("digital service" in combined_clean or "entertainment and digital" in combined_clean)):
                assigned_personas = ["Fashion Devotee"]
                simple_scores["Fashion Devotee"] = 1
            else:
                assigned_personas = ["Unclassified"]
        
        return assigned_personas, simple_scores

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
            
            assigned_personas, simple_scores = self.assign_personas(interest, product_category)
            
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
                "presence_scores": simple_scores,
                "total_personas": len(assigned_personas)
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

        tab1, tab2, tab3 = st.tabs(["📊 Persona Distribution", "🔄 Multi-Persona Analysis", "🔍 Customer Details"])

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
            st.subheader("🔍 Customer Groups & Details")
            
            # Search and filter options
            col1, col2 = st.columns(2)
            with col1:
                search_name = st.text_input("Search by name:")
            with col2:
                filter_persona = st.selectbox(
                    "Filter by persona:",
                    ["All"] + list(engine.persona_keywords.keys()) + ["Unclassified"]
                )
            
        with tab3:
            st.subheader("🔍 Customer Analytics & Persona Insights")
            
            # Professional search and filter bar
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    search_name = st.text_input("🔍 Search customers by name", placeholder="Enter first or last name...")
                with col2:
                    filter_persona = st.selectbox(
                        "🎭 Filter by persona",
                        ["All Personas"] + list(engine.persona_keywords.keys()) + ["Unclassified"],
                        help="Filter customers by their assigned persona types"
                    )
                with col3:
                    st.markdown("&nbsp;")  # Spacing
                    view_mode = st.radio("View", ["Cards", "Table"], horizontal=True)
            
            st.markdown("---")
            
            # Apply filters
            filtered_data = engine.personas.copy()
            
            if search_name:
                filtered_data = [
                    p for p in filtered_data 
                    if search_name.lower() in f"{p['first_name']} {p['last_name']}".lower()
                ]
            
            if filter_persona != "All Personas":
                filtered_data = [
                    p for p in filtered_data 
                    if filter_persona in p["assigned_personas"]
                ]
            
            # Display results
            if filtered_data:
                # Professional header with key metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📊 Total Customers", f"{len(filtered_data):,}")
                with col2:
                    multi_count = len([p for p in filtered_data if len(p["assigned_personas"]) > 1])
                    st.metric("🎯 Multi-Persona", f"{multi_count:,}")
                with col3:
                    avg_personas = sum(len(p["assigned_personas"]) for p in filtered_data) / len(filtered_data)
                    st.metric("📈 Avg Personas", f"{avg_personas:.1f}")
                with col4:
                    # Calculate total reach per persona
                    persona_reach = defaultdict(int)
                    for person in filtered_data:
                        for persona in person["assigned_personas"]:
                            persona_reach[persona] += 1
                    top_persona = max(persona_reach.items(), key=lambda x: x[1]) if persona_reach else ("None", 0)
                    emoji = engine.get_emoji(top_persona[0])
                    st.metric(f"{emoji} Top Persona", f"{top_persona[1]:,}")
                
                st.markdown("---")
                
                # Persona combination analysis
                combination_counts = defaultdict(int)
                combination_data = defaultdict(list)
                
                for person in filtered_data:
                    combo = person["persona_string"]
                    combination_counts[combo] += 1
                    combination_data[combo].append(person)
                
                # Professional persona reach overview
                st.markdown("### 📊 Persona Reach Overview")
                persona_reach = defaultdict(int)
                for person in filtered_data:
                    for persona in person["assigned_personas"]:
                        persona_reach[persona] += 1
                
                reach_cols = st.columns(len(persona_reach) if persona_reach else 1)
                for i, (persona, count) in enumerate(sorted(persona_reach.items(), key=lambda x: x[1], reverse=True)):
                    with reach_cols[i]:
                        emoji = engine.get_emoji(persona)
                        percentage = (count / len(filtered_data)) * 100
                        st.metric(
                            f"{emoji} {persona}",
                            f"{count:,}",
                            f"{percentage:.1f}% reach"
                        )
                
                st.markdown("### 🎯 Customer Segments by Persona Combinations")
                
                # Sort combinations by strategic value (multi-persona first, then by count)
                def sort_key(item):
                    combo, count = item
                    persona_count = len(combo.split(" + "))
                    return (-persona_count, -count)  # Multi-persona first, then highest count
                
                sorted_combinations = sorted(combination_counts.items(), key=sort_key)
                
                if view_mode == "Cards":
                    # Professional card layout
                    for combo, count in sorted_combinations:
                        personas = combo.split(" + ")
                        emoji_combo = "".join([engine.get_emoji(p) for p in personas])
                        
                        # Determine card color based on persona count
                        if len(personas) >= 3:
                            card_color = "🔥"  # VIP customers
                        elif len(personas) == 2:
                            card_color = "⭐"  # Premium customers
                        else:
                            card_color = "📌"  # Standard customers
                        
                        with st.expander(
                            f"{card_color} {emoji_combo} **{combo}** • {count:,} customers ({(count/len(filtered_data)*100):.1f}%)",
                            expanded=(count <= 30 or len(personas) >= 3)  # Auto-expand VIP and small segments
                        ):
                            combo_customers = combination_data[combo]
                            
                            # Quick insights row
                            insight_col1, insight_col2, insight_col3 = st.columns(3)
                            with insight_col1:
                                city_dist = pd.Series([p["city"] for p in combo_customers]).value_counts()
                                top_city = city_dist.index[0] if len(city_dist) > 0 else "N/A"
                                st.metric("🏙️ Top City", top_city, f"{city_dist.iloc[0]} customers" if len(city_dist) > 0 else "")
                            
                            with insight_col2:
                                concert_dist = pd.Series([p["concerts_attended"] for p in combo_customers]).value_counts()
                                top_engagement = concert_dist.index[0] if len(concert_dist) > 0 else "N/A"
                                st.metric("🎵 Top Engagement", top_engagement, f"{concert_dist.iloc[0]} customers" if len(concert_dist) > 0 else "")
                            
                            with insight_col3:
                                avg_interests = sum(len(str(p["interest"]).split(",")) for p in combo_customers) / len(combo_customers)
                                st.metric("💡 Avg Interests", f"{avg_interests:.1f}", "per customer")
                            
                            # Customer table
                            combo_df = pd.DataFrame(combo_customers)[
                                ["first_name", "last_name", "city", "interest", "product_interest", "concerts_attended"]
                            ].rename(columns={
                                "first_name": "First Name",
                                "last_name": "Last Name",
                                "city": "City",
                                "interest": "Interests", 
                                "product_interest": "Product Category",
                                "concerts_attended": "Concert Attendance"
                            })
                            
                            st.dataframe(
                                combo_df.reset_index(drop=True), 
                                use_container_width=True,
                                hide_index=True
                            )
                else:
                    # Professional table view
                    st.markdown("**Customer Segments Summary**")
                    
                    # Create summary table
                    summary_data = []
                    for combo, count in sorted_combinations:
                        personas = combo.split(" + ")
                        emoji_combo = "".join([engine.get_emoji(p) for p in personas])
                        segment_type = "VIP" if len(personas) >= 3 else "Premium" if len(personas) == 2 else "Standard"
                        percentage = (count / len(filtered_data)) * 100
                        
                        summary_data.append({
                            "🎭": emoji_combo,
                            "Segment": combo,
                            "Type": segment_type,
                            "Customers": f"{count:,}",
                            "Percentage": f"{percentage:.1f}%"
                        })
                    
                    summary_df = pd.DataFrame(summary_data)
                    st.dataframe(summary_df, use_container_width=True, hide_index=True)
                    
                    # Detailed customer table
                    with st.expander("📋 Detailed Customer List", expanded=False):
                        detailed_df = pd.DataFrame(filtered_data)[
                            ["first_name", "last_name", "city", "persona_string", 
                             "interest", "product_interest", "concerts_attended", "total_personas"]
                        ].rename(columns={
                            "first_name": "First Name",
                            "last_name": "Last Name",
                            "city": "City",
                            "persona_string": "Personas",
                            "interest": "Interests", 
                            "product_interest": "Product Category",
                            "concerts_attended": "Concert Attendance",
                            "total_personas": "# Personas"
                        }).sort_values(["# Personas", "Personas"], ascending=[False, True])
                        
                        st.dataframe(detailed_df.reset_index(drop=True), use_container_width=True, hide_index=True)
                
                # Professional download section
                st.markdown("---")
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown("**📥 Export Data**")
                with col2:
                    # Summary export
                    summary_data = []
                    for combo, count in sorted_combinations:
                        personas = combo.split(" + ")
                        segment_type = "VIP" if len(personas) >= 3 else "Premium" if len(personas) == 2 else "Standard"
                        percentage = (count / len(filtered_data)) * 100
                        summary_data.append({
                            "Segment": combo,
                            "Type": segment_type,
                            "Customers": count,
                            "Percentage": round(percentage, 1)
                        })
                    
                    summary_csv = pd.DataFrame(summary_data).to_csv(index=False)
                    st.download_button(
                        label="📊 Summary CSV",
                        data=summary_csv,
                        file_name="persona_segments_summary.csv",
                        mime="text/csv"
                    )
                
                with col3:
                    # Detailed export
                    detailed_df = pd.DataFrame(filtered_data)[
                        ["first_name", "last_name", "city", "persona_string", 
                         "interest", "product_interest", "concerts_attended", "total_personas"]
                    ].rename(columns={
                        "first_name": "First Name",
                        "last_name": "Last Name",
                        "city": "City",
                        "persona_string": "Personas",
                        "interest": "Interests", 
                        "product_interest": "Product Category",
                        "concerts_attended": "Concert Attendance",
                        "total_personas": "Number of Personas"
                    })
                    
                    detailed_csv = detailed_df.to_csv(index=False)
                    st.download_button(
                        label="📋 Detailed CSV",
                        data=detailed_csv,
                        file_name="customer_details.csv",
                        mime="text/csv"
                    )
            else:
                st.info("🔍 No customers match your search criteria. Try adjusting your filters.")

    else:
        st.error("❌ Could not read uploaded CSV. Please check formatting.")
else:
    st.info("👈 Upload your customer CSV file to begin persona analysis.")
    
    # Show example of improved logic
    st.markdown("### 🆕 Multi-Persona Classification:")
    st.markdown("""
    - **Simple logic**: If ANY keyword from a persona is found → assign that persona
    - **No complex scoring**: Just presence/absence detection
    - **Multi-persona support**: Customer can have Fashion + Beauty + Japanese personas
    - **Easy to explain**: "They mentioned fashion and beauty terms, so they get both personas"
    - **Excluded terms filter**: Removes promotional/generic terms from analysis
    - **Clean classification**: Focuses on genuine interest indicators only
    - **Transparent logic**: Easy to audit and defend to stakeholders
    - **Fast processing**: No complex calculations needed
    """)

st.markdown("---")
st.markdown("© 2025 TGC Event Analysis | Enhanced Multi-Persona Classification 🎭")
