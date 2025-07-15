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
st.title("🎯 Persona Customer Profiler")
st.markdown("*Multi-Persona Classification System*")

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

        # Summary metrics
        total_customers = len(engine.personas)
        single_persona_count = len([p for p in engine.personas if len(p["assigned_personas"]) == 1])
        multi_persona_count = len(multi_persona_users)
        avg_personas = sum(len(p["assigned_personas"]) for p in engine.personas) / total_customers

        tab1, tab2, tab3 = st.tabs(["📊 Persona Overview", "🔄 Multi-Persona Analysis", "👥 Customer Details"])

        with tab1:

            # Main visualization section
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🎯 Persona Reach (Total Instances)")
                st.caption("*Shows how many customers each persona reaches (can exceed 100% due to multi-persona)*")
                
                # Bar chart showing total reach for each persona (exclude Unclassified)
                persona_data = []
                colors = {'Fashion Devotee': '#E74C3C', 'Beauty Maven': '#2ECC71', 
                         'Japanese Lover': '#3498DB', 'Unclassified': '#95A99C'}
                
                for persona, count in persona_stats.items():
                    if persona != "Unclassified":  # Exclude Unclassified
                        percentage = (count / total_customers) * 100
                        persona_data.append({
                            'Persona': persona,
                            'Count': count,
                            'Percentage': percentage
                        })
                
                persona_df = pd.DataFrame(persona_data).sort_values('Count', ascending=True)
                
                fig_bar = px.bar(
                    persona_df, 
                    x='Count', 
                    y='Persona', 
                    orientation='h',
                    color='Persona',
                    color_discrete_map=colors,
                    title="Total Customer Reach by Persona",
                    text='Count'
                )
                
                # Add percentage annotations
                for i, row in persona_df.iterrows():
                    fig_bar.add_annotation(
                        x=row['Count'] + max(persona_df['Count']) * 0.02,
                        y=row['Persona'],
                        text=f"{row['Percentage']:.1f}%",
                        showarrow=False,
                        font=dict(size=12, color='white', family="Arial Black"),
                        xanchor='left'
                    )
                
                fig_bar.update_layout(
                    showlegend=False,
                    height=400,
                    margin=dict(l=0, r=80, t=40, b=0)
                )
                fig_bar.update_traces(textposition='inside', textfont_size=14, textfont_color='white')
                st.plotly_chart(fig_bar, use_container_width=True)

            with col2:
                st.subheader("🔀 Customer Complexity")
                st.caption("*Distribution of single vs multi-persona customers*")
                
                # Create pie chart data
                complexity_data = {
                    'Single Persona': single_persona_count,
                    'Multi-Persona': multi_persona_count
                }
                
                fig_complexity = px.pie(
                    names=list(complexity_data.keys()),
                    values=list(complexity_data.values()),
                    title="Customer Persona Complexity",
                    color_discrete_map={
                        'Single Persona': '#F39C12',
                        'Multi-Persona': '#9B59B6'
                    }
                )
                fig_complexity.update_traces(
                    textposition='inside', 
                    textinfo='percent+label+value',
                    textfont_size=14,
                    textfont_color='white',
                    marker=dict(line=dict(color='white', width=2))
                )
                fig_complexity.update_layout(
                    height=450,  # 10% smaller (500 * 0.9 = 450)
                    width=630,   # 10% smaller (700 * 0.9 = 630)
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.05,
                        font=dict(size=14)
                    ),
                    margin=dict(l=20, r=140, t=50, b=20)
                )
                st.plotly_chart(fig_complexity, use_container_width=True)

            # Second row - Demographics (make symmetric)
            st.markdown("---")
            st.subheader("👥 Demographics Overview")
            
            col3, col4 = st.columns(2)

            with col3:
                st.markdown("**Gender Distribution**")
                if not gender_stats.empty:
                    fig_gender = px.pie(
                        names=gender_stats.index,
                        values=gender_stats.values,
                        color_discrete_map={
                            'Male': '#3498DB',
                            'Female': '#E91E63',
                            'M': '#3498DB',
                            'F': '#E91E63',
                            'Unknown': '#95A99C'
                        }
                    )
                    fig_gender.update_traces(
                        textposition='inside', 
                        textinfo='percent+label+value',
                        textfont_size=14,
                        textfont_color='white',
                        marker=dict(line=dict(color='white', width=2))
                    )
                    fig_gender.update_layout(
                        height=450,  # 10% smaller
                        width=630,   # 10% smaller
                        showlegend=True,
                        legend=dict(
                            orientation="v",
                            yanchor="middle",
                            y=0.5,
                            xanchor="left",
                            x=1.05,
                            font=dict(size=14)
                        ),
                        margin=dict(l=20, r=140, t=50, b=20)
                    )
                    st.plotly_chart(fig_gender, use_container_width=True)
                else:
                    st.info("No gender data available")

            with col4:
                st.markdown("**City Distribution**")
                top_cities = city_counts[city_counts > city_counts.sum() * 0.02]
                rest = city_counts[city_counts <= city_counts.sum() * 0.02]
                
                city_data = list(top_cities.index)
                city_values = list(top_cities.values)
                
                if rest.sum() > 0:
                    city_data.append("Others")
                    city_values.append(rest.sum())
                    
                city_df = pd.DataFrame({
                    "City": city_data,
                    "Count": city_values
                })
                
                # Use high contrast colors for cities
                city_colors = ['#E74C3C', '#2ECC71', '#3498DB', '#F39C12', '#9B59B6', '#1ABC9C', '#E67E22', '#34495E']
                
                fig_city = px.pie(city_df, names="City", values="Count", 
                                color_discrete_sequence=city_colors)
                fig_city.update_traces(
                    textposition='inside', 
                    textinfo='percent+label',
                    textfont_size=12,
                    textfont_color='white',
                    marker=dict(line=dict(color='white', width=2))
                )
                fig_city.update_layout(
                    height=450,  # 10% smaller
                    width=630,   # 10% smaller
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.05,
                        font=dict(size=12)
                    ),
                    margin=dict(l=20, r=140, t=50, b=20)
                )
                st.plotly_chart(fig_city, use_container_width=True)

        with tab2:
            st.subheader("🔄 Multi-Persona Deep Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📋 Top Persona Combinations**")
                combo_df = pd.DataFrame([
                    {
                        "Combination": combo, 
                        "Count": count, 
                        "% of Total": f"{(count/total_customers)*100:.1f}%"
                    }
                    for combo, count in combination_stats.most_common(15)
                ])
                
                # Color code combinations with high contrast
                def get_combo_color(combo):
                    if " + " in combo:
                        return "#E74C3C"  # Red for multi-persona
                    else:
                        return "#2ECC71"  # Green for single persona
                
                combo_df['Color'] = combo_df['Combination'].apply(get_combo_color)
                
                fig_combo = px.bar(
                    combo_df, 
                    x="Count", 
                    y="Combination", 
                    orientation='h',
                    color='Color',
                    color_discrete_map={"#E74C3C": "#E74C3C", "#2ECC71": "#2ECC71"},
                    title="Most Common Persona Combinations",
                    text="Count"
                )
                fig_combo.update_layout(
                    yaxis={'categoryorder':'total ascending'},
                    showlegend=False,
                    height=500
                )
                fig_combo.update_traces(textposition='outside', textfont_size=12, textfont_color='white')
                st.plotly_chart(fig_combo, use_container_width=True)
                
                # Show the data table
                st.dataframe(combo_df[['Combination', 'Count', '% of Total']], use_container_width=True, hide_index=True)
            
            with col2:
                st.markdown("**🔥 Persona Overlap Heatmap**")
                
                # Create overlap matrix for personas (exclude Unclassified)
                personas_list = list(engine.persona_keywords.keys())  # Remove + ["Unclassified"]
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
                
                # Create dynamic text color based on heatmap values for better contrast
                text_colors = []
                for row in overlap_matrix:
                    text_row = []
                    for val in row:
                        # Use dark color for high values (yellow/bright colors), white for low values (dark colors)
                        if val > max([max(r) for r in overlap_matrix]) * 0.6:  # If value is in top 40% (bright/yellow area)
                            text_row.append("black")
                        else:
                            text_row.append("white")
                    text_colors.append(text_row)
                
                fig_heatmap = go.Figure(data=go.Heatmap(
                    z=overlap_matrix,
                    x=personas_list,
                    y=personas_list,
                    colorscale='Viridis',  # Back to original colorscale
                    text=overlap_matrix,
                    texttemplate="%{text}",
                    textfont={"size": 16},
                    hoverongaps=False
                ))
                
                # Apply dynamic text colors
                for i, row in enumerate(text_colors):
                    for j, color in enumerate(row):
                        fig_heatmap.add_annotation(
                            x=j,
                            y=i,
                            text=str(overlap_matrix[i][j]),
                            showarrow=False,
                            font=dict(size=16, color=color),
                            xref="x",
                            yref="y"
                        )
                
                fig_heatmap.update_layout(
                    title="Persona Overlap Matrix<br><sub>Diagonal: Total | Off-diagonal: Shared customers</sub>",
                    xaxis_title="Persona",
                    yaxis_title="Persona",
                    height=500,
                    font=dict(size=12)
                )
                st.plotly_chart(fig_heatmap, use_container_width=True)
                
                # Multi-persona statistics (exclude Unclassified from metrics)
                st.markdown("**📊 Multi-Persona Statistics**")
                
                # Calculate classified customers only
                classified_personas = [p for p in engine.personas if "Unclassified" not in p["assigned_personas"]]
                total_classified = len(classified_personas)
                classified_single = len([p for p in classified_personas if len(p["assigned_personas"]) == 1])
                classified_multi = len([p for p in classified_personas if len(p["assigned_personas"]) > 1])
                
                if total_classified > 0:
                    avg_classified_personas = sum(len(p["assigned_personas"]) for p in classified_personas) / total_classified
                    max_classified_personas = max(len(p["assigned_personas"]) for p in classified_personas)
                else:
                    avg_classified_personas = 0
                    max_classified_personas = 0
                
                multi_stats = pd.DataFrame([
                    {"Metric": "Classified customers with 1 persona", "Count": classified_single, "Percentage": f"{(classified_single/total_classified)*100:.1f}%" if total_classified > 0 else "0%"},
                    {"Metric": "Classified customers with 2+ personas", "Count": classified_multi, "Percentage": f"{(classified_multi/total_classified)*100:.1f}%" if total_classified > 0 else "0%"},
                    {"Metric": "Average personas per classified customer", "Count": f"{avg_classified_personas:.2f}", "Percentage": "-"},
                    {"Metric": "Max personas on one customer", "Count": max_classified_personas, "Percentage": "-"}
                ])
                st.dataframe(multi_stats, use_container_width=True, hide_index=True)

            if multi_persona_users:
                st.markdown("---")
                st.markdown("**🎭 Sample Multi-Persona Customers**")
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
                st.dataframe(sample_multi, use_container_width=True, hide_index=True)
            else:
                st.info("🤔 No multi-persona customers found in current data.")

        with tab3:
            st.subheader("👥 Customer Segments")
            
            # Filter controls
            col1, col2 = st.columns([2, 1])
            with col1:
                filter_persona = st.selectbox(
                    "🔍 Filter by persona:",
                    ["All"] + list(engine.persona_keywords.keys()) + ["Unclassified"]
                )
            with col2:
                show_contact = st.checkbox("📞 Show Contact Details", value=True)
            
            filtered_data = engine.personas.copy()
            
            if filter_persona != "All":
                filtered_data = [
                    p for p in filtered_data 
                    if filter_persona in p["assigned_personas"]
                ]
            
            if filtered_data:
                st.info(f"📊 Showing {len(filtered_data)} customers" + (f" with {filter_persona} persona" if filter_persona != "All" else ""))
                
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
                    
                    # Multi-persona gets expanded by default if small group
                    is_multi = len(personas) > 1
                    should_expand = count <= 50 or is_multi
                    
                    with st.expander(
                        f"{emoji_combo} **{combo}** - {count} customers ({percentage:.1f}%)", 
                        expanded=should_expand
                    ):
                        combo_customers = combination_data[combo]
                        
                        # Choose columns based on contact details setting
                        if show_contact:
                            columns = ["email", "phone", "first_name", "last_name", "gender", "age", "city", "interest", "product_interest", "concerts_attended"]
                            column_names = {
                                "email": "📧 Email",
                                "phone": "📱 Phone", 
                                "first_name": "👤 First Name",
                                "last_name": "👥 Last Name",
                                "gender": "⚧ Gender",
                                "age": "🎂 Age",
                                "city": "🏙 City",
                                "interest": "❤️ Interests", 
                                "product_interest": "🛍 Product Category",
                                "concerts_attended": "🎵 Concerts"
                            }
                        else:
                            columns = ["first_name", "last_name", "gender", "age", "city", "interest", "product_interest", "concerts_attended"]
                            column_names = {
                                "first_name": "👤 First Name",
                                "last_name": "👥 Last Name", 
                                "gender": "⚧ Gender",
                                "age": "🎂 Age",
                                "city": "🏙 City",
                                "interest": "❤️ Interests", 
                                "product_interest": "🛍 Product Category",
                                "concerts_attended": "🎵 Concerts"
                            }
                        
                        combo_df = pd.DataFrame(combo_customers)[columns].rename(columns=column_names)
                        st.dataframe(combo_df.reset_index(drop=True), use_container_width=True, hide_index=True)
                
                # Download section
                st.markdown("---")
                st.markdown("**📥 Download Data**")
                
                download_columns = ["email", "phone", "first_name", "last_name", "gender", "age", "city", "persona_string", 
                                  "interest", "product_interest", "concerts_attended"]
                download_column_names = {
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
                }
                
                detailed_df = pd.DataFrame(filtered_data)[download_columns].rename(columns=download_column_names)
                
                csv = detailed_df.to_csv(index=False)
                st.download_button(
                    label="💾 Download Customer Data (CSV)",
                    data=csv,
                    file_name=f"customer_personas_{filter_persona.lower().replace(' ', '_')}.csv",
                    mime="text/csv"
                )
                
                # Quick stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("👥 Total Filtered", len(filtered_data))
                with col2:
                    unique_combos = len(set(p["persona_string"] for p in filtered_data))
                    st.metric("🎭 Unique Combinations", unique_combos)
                with col3:
                    avg_filtered_personas = sum(len(p["assigned_personas"]) for p in filtered_data) / len(filtered_data)
                    st.metric("📊 Avg Personas", f"{avg_filtered_personas:.1f}")
                    
            else:
                st.warning("❌ No customers match your filter criteria.")

    else:
        st.error("❌ Could not read uploaded CSV. Please check formatting.")
else:
    st.info("📤 Upload your customer CSV file to begin persona analysis.")
  

st.markdown("---")
st.markdown("© 2025 JKEJK | Multi-Persona Classification System ✨")
