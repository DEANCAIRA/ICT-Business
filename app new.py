import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import plotly.express as px
import json

st.set_page_config(
    page_title="Customer Persona Generator",
    layout="wide"
)

# Initialize session state for persona definitions if not already present
if 'persona_definitions' not in st.session_state:
    st.session_state.persona_definitions = {
        "Beauty-Focused Minimalist": {
            "emoji": "🧴",
            "criteria": ["j_beauty", "daily_routine"],
            "description": "Loves Japanese beauty and skincare routines.",
            "tags": ["beauty", "care"],
            "product_recommendations": ["Japanese Cleansing Oil", "Hydrating Essence", "Sheet Masks", "Gentle Foaming Cleanser", "Ceramide Moisturizer"]
        },
        "Trend-Savvy Fashionista": {
            "emoji": "💅",
            "criteria": ["j_fashion", "style_preference", "fashion_frequency"],
            "description": "Passionate about fashion and modern Japanese style.",
            "tags": ["fashion"],
            "product_recommendations": ["Harajuku Style Hoodie", "Kimono Cardigan", "Statement Sneakers", "Graphic T-shirts", "Unique Accessories"]
        },
        "Pop Culture Power User": {
            "emoji": "📱",
            "criteria": ["follows_influencers", "streams_often", "buys_merch"],
            "description": "Follows influencers and loves trends.",
            "tags": ["trend", "influencer"],
            "product_recommendations": ["Anime Figurines", "Manga Series", "Limited Edition Merchandise", "Gaming Headsets", "Collectible Art Books"]
        },
        "Style Seeker": {
            "emoji": "👗",
            "criteria": ["j_fashion", "style_preference"],
            "description": "Always looking for the latest fashion trends and unique styles.",
            "tags": ["fashion", "style"],
            "product_recommendations": ["Streetwear Jeans", "Designer T-shirts", "Vintage Jackets", "Stylish Footwear", "Fashion Magazines"]
        }
    }

class PersonaEngine:
    def __init__(self, definitions):
        self.df = None
        self.personas = []
        self.columns = []
        self.definitions = definitions # Use definitions passed from session state

    def load_data(self, file):
        self.df = pd.read_csv(file)
        self.df.columns = self.df.columns.str.strip().str.lower()
        self.columns = list(self.df.columns)
        return not self.df.empty

    def extract_tags(self, row):
        tags = set()
        row = {k.strip().lower(): str(v).strip().lower() for k, v in row.items()}

        # Existing tag extraction logic
        if row.get("interested in j-beauty", '') in ['yes', 'true', '1']:
            tags.add("j_beauty")
        if row.get("daily routine", '') in ['yes', 'true', '1', 'defined', 'structured']:
            tags.add("daily_routine")
        if row.get("j-fashion style", '') in ['yes', 'true', '1']:
            tags.add("j_fashion")
        if any(x in row.get("style preference", '') for x in ['kawaii', 'modern', 'street', 'streetwear']):
            tags.add("style_preference")
        if row.get("fashion frequency", '') in ['frequent', 'weekly', 'daily', 'often']:
            tags.add("fashion_frequency")
        if row.get("follow fashion influencers", '') in ['yes', 'true', '1']:
            tags.add("follows_influencers")
        if row.get("streaming frequency", '') in ['daily', 'weekly', 'frequent', 'often']:
            tags.add("streams_often")
        if row.get("buys merch", '') in ['yes', 'true', '1', 'frequently', 'often']:
            tags.add("buys_merch")

        return tags

    def assign_persona(self, tags):
        best = ("Unclassified", 0)
        # Use self.definitions which now comes from session state
        for name, config in self.definitions.items():
            score = sum(1 for c in config['criteria'] if c in tags)
            if score > best[1]:
                best = (name, score)
        return best[0] if best[1] > 0 else "Unclassified"

    def process(self):
        self.personas = []
        for _, row in self.df.iterrows():
            tags = self.extract_tags(row)
            persona = self.assign_persona(tags)
            entry = {
                "customer_id": row.get("customer_id", ""),
                "city": row.get("customer_city", "Unknown"),
                "zip": row.get("customer_zip_code_prefix", "-"),
                "phone": row.get("phone number", "N/A"),
                "persona": persona,
                "emoji": self.definitions.get(persona, {}).get("emoji", "❓"),
                "description": self.definitions.get(persona, {}).get("description", "Not matched"),
                "tags": list(tags),
                "product_recommendations": self.definitions.get(persona, {}).get("product_recommendations", ["No specific recommendations"])
            }
            self.personas.append(entry)

    def get_stats(self):
        counter = Counter([p['persona'] for p in self.personas])
        return counter

    def to_df(self):
        return pd.DataFrame(self.personas)

    def grouped_by_persona(self):
        df = self.to_df()
        return df.groupby('persona')

    def export_template(self):
        columns = [
            "customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city", "phone_number",
            "Interested in J-beauty", "Daily Routine", "Anime Collector", "J-fashion Style",
            "Interested in Japanese Snacks", "Streaming Frequency", "Favorite Platform",
            "Buys Merch", "Style Preference", "Fashion Frequency", "Follow Fashion Influencers"
        ]
        df = pd.DataFrame(columns=columns)
        return df

# Streamlit App UI
st.title("Customer Persona Profiler")
st.markdown("Analyze your customers and assign personas.")

# Persona Definition UI
with st.expander("⚙️ Define Personas"):
    st.markdown("Customize your customer personas and their criteria.")
    
    # Using a list of persona names for ordering and easy manipulation
    if 'persona_order' not in st.session_state:
        st.session_state.persona_order = list(st.session_state.persona_definitions.keys())

    for i, persona_name in enumerate(st.session_state.persona_order):
        with st.container(border=True):
            col_a, col_b = st.columns([0.9, 0.1])
            with col_a:
                st.subheader(f"Persona: {persona_name}")
            with col_b:
                if st.button("❌ Remove", key=f"remove_persona_{i}"):
                    del st.session_state.persona_definitions[persona_name]
                    st.session_state.persona_order.remove(persona_name)
                    st.experimental_rerun() # Rerun to update the display

            current_def = st.session_state.persona_definitions[persona_name]
            
            new_name = st.text_input("Persona Name", value=persona_name, key=f"name_{i}")
            if new_name != persona_name and new_name and new_name not in st.session_state.persona_definitions:
                # Rename persona in definitions and order
                st.session_state.persona_definitions[new_name] = st.session_state.persona_definitions.pop(persona_name)
                st.session_state.persona_order[i] = new_name
                st.session_state.persona_definitions[new_name]["name"] = new_name # Update name inside the dict for consistency if needed later
                st.experimental_rerun()


            st.session_state.persona_definitions[new_name]["emoji"] = st.text_input("Emoji", value=current_def.get("emoji", "❓"), key=f"emoji_{i}")
            st.session_state.persona_definitions[new_name]["description"] = st.text_area("Description", value=current_def.get("description", ""), key=f"desc_{i}")
            
            # Criteria input: display existing criteria as comma-separated string
            criteria_str = ", ".join(current_def.get("criteria", []))
            edited_criteria_str = st.text_input("Criteria (comma-separated tags from your data)", value=criteria_str, key=f"criteria_{i}")
            st.session_state.persona_definitions[new_name]["criteria"] = [c.strip() for c in edited_criteria_str.split(',') if c.strip()]

            # Tags input: display existing tags as comma-separated string
            tags_str = ", ".join(current_def.get("tags", []))
            edited_tags_str = st.text_input("Tags (comma-separated for internal use)", value=tags_str, key=f"tags_{i}")
            st.session_state.persona_definitions[new_name]["tags"] = [t.strip() for t in edited_tags_str.split(',') if t.strip()]

            # Product Recommendations input
            prod_rec_str = ", ".join(current_def.get("product_recommendations", []))
            edited_prod_rec_str = st.text_area("Product Recommendations (comma-separated)", value=prod_rec_str, key=f"prod_rec_{i}")
            st.session_state.persona_definitions[new_name]["product_recommendations"] = [p.strip() for p in edited_prod_rec_str.split(',') if p.strip()]

    if st.button("➕ Add New Persona"):
        new_persona_name = f"New Persona {len(st.session_state.persona_order) + 1}"
        st.session_state.persona_definitions[new_persona_name] = {
            "emoji": "❓",
            "criteria": [],
            "description": "New persona description.",
            "tags": [],
            "product_recommendations": []
        }
        st.session_state.persona_order.append(new_persona_name)
        st.experimental_rerun() # Rerun to display the new persona

# Main app logic
engine = PersonaEngine(st.session_state.persona_definitions)
file = st.file_uploader("Upload your customer CSV file", type="csv")

if file:
    if engine.load_data(file):
        engine.process()
        df_result = engine.to_df()
        stats = engine.get_stats()

        tab1, tab2 = st.tabs(["📊 Overview", "👥 Persona Details"])

        with tab1:
            st.header("📊 Overview")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("👥 Persona Distribution")
                fig_persona = px.pie(names=list(stats.keys()), values=list(stats.values()), title="Persona Breakdown")
                st.plotly_chart(fig_persona, use_container_width=True)

            with col2:
                st.subheader("📍 Customer Location")
                if 'city' in df_result.columns and not df_result['city'].empty:
                    city_counts = df_result['city'].value_counts().reset_index()
                    city_counts.columns = ['City', 'Count']
                    fig_city = px.pie(city_counts, names='City', values='Count', title="Customers by City")
                    st.plotly_chart(fig_city, use_container_width=True)
                else:
                    st.info("No city data available or 'customer_city' column not found in the uploaded file.")

        with tab2:
            st.header("👥 Detailed Persona Assignments")
            # --- Start Interactive Data Filtering (Part 2 - initial integration) ---
            st.subheader("Filter Customer Data")
            
            all_cities = df_result['city'].unique().tolist()
            selected_cities = st.multiselect(
                "Select Cities",
                options=all_cities,
                default=all_cities
            )

            filtered_df_result = df_result[df_result['city'].isin(selected_cities)]

            # Example for zip code range (assuming it's numeric, or it can be multiselect too)
            if 'zip' in filtered_df_result.columns and pd.api.types.is_numeric_dtype(filtered_df_result['zip']):
                min_zip, max_zip = int(filtered_df_result['zip'].min()), int(filtered_df_result['zip'].max())
                zip_range = st.slider(
                    "Filter by Zip Code Range",
                    min_value=min_zip,
                    max_value=max_zip,
                    value=(min_zip, max_zip)
                )
                filtered_df_result = filtered_df_result[(filtered_df_result['zip'] >= zip_range[0]) & (filtered_df_result['zip'] <= zip_range[1])]
            elif 'zip' in filtered_df_result.columns: # treat as categorical if not numeric
                all_zips = filtered_df_result['zip'].unique().tolist()
                selected_zips = st.multiselect(
                    "Select Zip Codes",
                    options=all_zips,
                    default=all_zips
                )
                filtered_df_result = filtered_df_result[filtered_df_result['zip'].isin(selected_zips)]


            # --- End Interactive Data Filtering ---

            # Display personas based on filtered data
            if not filtered_df_result.empty:
                grouped_filtered = filtered_df_result.groupby('persona')
                for persona, group in grouped_filtered:
                    st.subheader(f"{group.iloc[0]['emoji']} {persona} ({len(group)} customers)")
                    st.write(f"**Description:** {group.iloc[0]['description']}")
                    st.write(f"**Recommended Products:** {', '.join(group.iloc[0]['product_recommendations'])}")
                    st.dataframe(group[['customer_id', 'city', 'zip', 'phone', 'tags']].reset_index(drop=True))
            else:
                st.info("No customers match the selected filters.")

    else:
        st.error("Failed to read the uploaded file.")

# Footer section
st.markdown("---")
st.markdown("© 2025 Dorenth | Made using Python 🐍", unsafe_allow_html=True)
