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
        
        # Simple keyword lists
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

    def process(self):
        self.personas = []
        for _, row in self.df.iterrows():
            interest = row.get("interest", "")
            product_category = row.get("product category", "")
            concerts = row.get("concerts attended", "")
            
            assigned_personas = self.assign_personas(interest, product_category)
            
            persona_str = " + ".join(assigned_personas)
            emoji_str = "".join([self.get_emoji(p) for p in assigned_personas])
            
            self.personas.append({
                "email": row.get("email", ""),
                "phone": row.get("phone", ""),
                "first_name": row.get("first name", ""),
                "last_name": row.get("last name", ""),
                "whatsapp": row.get("whatsapp", ""),
                "age": row.get("age", ""),
                "city": row.get("city", ""),
                "gender": row.get("gender", "Unknown"),
                "interest": interest,
                "product_interest": product_category,
                "concerts_attended": concerts,
                "assigned_personas": assigned_personas,
                "persona_string": persona_str,
                "emoji": emoji_str,
                "total_personas": len(assigned_personas)
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
        df = self.to_df()
        return df["gender"].value_counts()

    def get_multi_persona_users(self):
        return [p for p in self.personas if len(p["assigned_personas"]) > 1]


# Streamlit UI
st.title("Persona Customer Profiler")

engine = PersonaEngine()
file = st.file_uploader("Upload your customer CSV file", type="csv")

if file:
    if engine.load_data(file):
        engine.process()
        df_result = engine.to_df()
        persona_stats = engine.get_persona_stats()
        combination_stats = engine.get_combination_stats()
        city_counts = engine.get_city_stats()
        gender_stats = engine.get_gender_stats()
        multi_persona_users = engine.get_multi_persona_users()

        tab1, tab2, tab3 = st.tabs(["Persona Overview", "Multi-Persona Analysis", "Customer Details"])

        with tab1:
            # Key Metrics Row
            col1, col2, col3, col4 = st.columns(4)
            
            total_customers = len(engine.personas)
            single_persona_count = len([p for p in engine.personas if len(p["assigned_personas"]) == 1])
            multi_persona_count = len(multi_persona_users)
            avg_personas = sum(len(p["assigned_personas"]) for p in engine.personas) / total_customers
            
            with col1:
                st.metric("Total Customers", f"{total_customers:,}")
            with col2:
                st.metric("Single Persona", f"{single_persona_count:,}")
            with col3:
                st.metric("Multi-Persona", f"{multi_persona_count:,}")
            with col4:
                st.metric("Avg Personas per Customer", f"{avg_personas:.1f}")

            # Main Charts Row
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Persona Reach (Multi-Persona Friendly)")
                
                # Bar chart showing total reach for each persona
                persona_data = []
                colors = {'Fashion Devotee': '#FF6B6B', 'Beauty Maven': '#4ECDC4', 
                         'Japanese Lover': '#45B7D1', 'Unclassified': '#95A99C'}
                
                for persona, count in persona_stats.items():
                    percentage = (count / total_customers) * 100
                    persona_data.append({
                        'Persona': persona,
                        'Count': count,
                        'Percentage': percentage,
                        'Color': colors.get(persona, '#95A99C')
                    })
                
                persona_df = pd.DataFrame(persona_data)
                
                fig_bar = px.bar(
                    persona_df, 
                    x='Count', 
                    y='Persona', 
                    orientation='h',
                    color='Persona',
                    color_discrete_map=colors,
                    title="Total Customers by Persona Type",
                    text='Count'
                )
                
                # Add percentage annotations
                for i, row in persona_df.iterrows():
                    fig_bar.add_annotation(
                        x=row['Count'] + max(persona_df['Count']) * 0.02,
                        y=i,
                        text=f"{row['Percentage']:.1f}%",
                        showarrow=False,
                        font=dict(size=12)
                    )
                
                fig_bar.update_layout(
                    showlegend=False,
                    yaxis={'categoryorder':'total ascending'},
                    height=400
                )
                fig_bar.update_traces(textposition='inside')
                st.plotly_chart(fig_bar, use_container_width=True)

            with col2:
                st.subheader("Interest Diversity")
                
                fig_diversity = px.pie(
                    names=["Single Interest", "Multi-Interest"],
                    values=[single_persona_count, multi_persona_count],
                    title="Customer Interest Patterns",
                    color_discrete_map={
                        'Single Interest': '#FDB462',
                        'Multi-Interest': '#80B1D3'
                    }
                )
                fig_diversity.update_traces(textposition='inside', textinfo='percent+label+value')
                st.plotly_chart(fig_diversity, use_container_width=True)

            # Demographics Row
            col3, col4 = st.columns(2)

            with col3:
                st.subheader("Gender Distribution")
                if not gender_stats.empty:
                    fig_gender = px.pie(
                        names=gender_stats.index,
                        values=gender_stats.values,
                        title="Customer Gender",
                        color_discrete_map={
                            'Male': '#4169E1',
                            'Female': '#FF69B4',
                            'M': '#4169E1',
                            'F': '#FF69B4',
                            'Unknown': '#95A99C'
                        }
                    )
                    fig_gender.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_gender, use_container_width=True)
                else:
                    st.info("No gender data available")

            with col4:
                st.subheader("City Distribution")
                top_cities = city_counts[city_counts > city_counts.sum() * 0.02]
                rest = city_counts[city_counts <= city_counts.sum() * 0.02]
                city_df = pd.DataFrame({
                    "City": list(top_cities.index) + (["Others"] if rest.sum() > 0 else []),
                    "Count": list(top_cities.values) + ([rest.sum()] if rest.sum() > 0 else [])
                })
                fig_city = px.pie(city_df, names="City", values="Count", title="Customers by City")
                fig_city.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_city, use_container_width=True)

        with tab2:
            st.subheader("Multi-Persona Deep Dive")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Top Persona Combinations**")
                combo_df = pd.DataFrame([
                    {"Combination": combo, "Count": count, "Percentage": f"{(count/total_customers)*100:.1f}%"}
                    for combo, count in combination_stats.most_common(10)
                ])
                
                fig_combo = px.bar(
                    combo_df, 
                    x="Count", 
                    y="Combination", 
                    orientation='h',
                    title="Most Common Persona Combinations",
                    text="Count"
                )
                fig_combo.update_layout(yaxis={'categoryorder':'total ascending'})
                fig_combo.update_traces(textposition='outside')
                st.plotly_chart(fig_combo, use_container_width=True)
                
                # Show the data table
                st.dataframe(combo_df, use_container_width=True)
            
            with col2:
                st.markdown("**Persona Overlap Analysis**")
                
                # Create overlap matrix for personas
                personas_list = list(engine.persona_keywords.keys())
                overlap_matrix = []
                
                for persona1 in personas_list:
                    row = []
                    for persona2 in personas_list:
                        if persona1 == persona2:
                            # Diagonal: total count for this persona
                            count = persona_stats.get(persona1, 0)
                        else:
                            # Off-diagonal: count of people with both personas
                            count = len([p for p in engine.personas 
                                       if persona1 in p["assigned_personas"] and 
                                          persona2 in p["assigned_personas"]])
                        row.append(count)
                    overlap_matrix.append(row)
                
                fig_heatmap = go.Figure(data=go.Heatmap(
                    z=overlap_matrix,
                    x=personas_list,
                    y=personas_list,
                    colorscale='Blues',
                    text=overlap_matrix,
                    texttemplate="%{text}",
                    textfont={"size": 12},
                ))
                
                fig_heatmap.update_layout(
                    title="Persona Overlap Matrix<br><sub>Diagonal: Total per persona | Off-diagonal: Shared customers</sub>",
                    xaxis_title="Persona",
                    yaxis_title="Persona",
                    height=400
                )
                st.plotly_chart(fig_heatmap, use_container_width=True)

            if multi_persona_users:
                st.markdown("**Sample Multi-Persona Customers**")
                sample_multi = pd.DataFrame(multi_persona_users[:10])[
                    ["email", "phone", "first_name", "last_name", "gender", "city", "persona_string", "interest", "product_interest"]
                ].rename(columns={
                    "email": "Email",
                    "phone": "Phone",
                    "first_name": "First Name",
                    "last_name": "Last Name",
                    "gender": "Gender",
                    "city": "City",
                    "persona_string": "Assigned Personas",
                    "interest": "Interests",
                    "product_interest": "Product Category"
                })
                st.dataframe(sample_multi, use_container_width=True)
            else:
                st.info("No multi-persona customers found in current data.")

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
                    percentage = (count / len(filtered_data)) * 100
                    
                    with st.expander(f"{emoji_combo} {combo} ({count} customers - {percentage:.1f}%)", expanded=(count <= 30)):
                        combo_customers = combination_data[combo]
                        
                        combo_df = pd.DataFrame(combo_customers)[
                            ["email", "phone", "first_name", "last_name", "gender", "age", "city", "interest", "product_interest", "concerts_attended"]
                        ].rename(columns={
                            "email": "Email",
                            "phone": "Phone",
                            "first_name": "First Name",
                            "last_name": "Last Name",
                            "gender": "Gender",
                            "age": "Age",
                            "city": "City",
                            "interest": "Interests", 
                            "product_interest": "Product Category",
                            "concerts_attended": "Concert Attendance"
                        })
                        
                        st.dataframe(combo_df.reset_index(drop=True), use_container_width=True)
                
                # Download
                detailed_df = pd.DataFrame(filtered_data)[
                    ["email", "phone", "first_name", "last_name", "gender", "age", "city", "persona_string", 
                     "interest", "product_interest", "concerts_attended"]
                ].rename(columns={
                    "email": "Email",
                    "phone": "Phone",
                    "first_name": "First Name",
                    "last_name": "Last Name",
                    "gender": "Gender",
                    "age": "Age",
                    "city": "City",
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
st.markdown("© 2025 JKEJK | Multi-Persona Classification")
