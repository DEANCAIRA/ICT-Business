import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import plotly.express as px
import json

st.set_page_config(
    page_title="J-Culture Customer Persona Generator",
    page_icon="🎌",
    layout="wide"
)

class PersonaEngine:
    def __init__(self):
        self.df = None
        self.personas = []
        self.columns = []
        self.definitions = {
            "Beauty-Focused Minimalist": {
                "emoji": "🧴",
                "criteria": ["j_beauty", "daily_routine"],
                "description": "Loves Japanese beauty and skincare routines.",
                "tags": ["beauty", "care"]
            },
            "Trend-Savvy Fashionista": {
                "emoji": "💅",
                "criteria": ["j_fashion", "style_preference", "fashion_frequency"],
                "description": "Passionate about fashion and modern Japanese style.",
                "tags": ["fashion"]
            },
            "Pop Culture Power User": {
                "emoji": "📱",
                "criteria": ["follows_influencers", "streams_often", "buys_merch"],
                "description": "Follows influencers and loves trends.",
                "tags": ["trend", "influencer"]
            }
        }
        self.product_recommendations = {
            "Beauty-Focused Minimalist": [
                {"name": "Hada Labo Gokujyun Hyaluronic Acid Lotion", "link": "https://hadalabousa.com/products/hada-labo-gokujyun-lotion"},
                {"name": "SK-II Facial Treatment Essence", "link": "https://www.sk-ii.com/product/facial-treatment-essence"},
                {"name": "Biore UV Aqua Rich Watery Essence Sunscreen", "link": "https://www.amazon.com/Biore-Aqua-Watery-Essence-Sunscreen/dp/B07FF3R53F"},
                {"name": "MUJI Sensitive Skin Moisturizing Toner", "link": "https://www.muji.us/products/toner-moisturizing-hsm51a"}
            ],
            "Trend-Savvy Fashionista": [
                {"name": "Uniqlo AirSense Blazer", "link": "https://www.uniqlo.com/us/en/products/E458269-000/00"},
                {"name": "Comme des Garçons PLAY Heart T-Shirt", "link": "https://www.doverstreetmarket.com/shops/cdgplay.html"},
                {"name": "A Bathing Ape (BAPE) Camo Hoodie", "link": "https://bape.com/"},
                {"name": "Traditional Kimono (modern twist)", "link": "https://shop.japanobjects.com/collections/kimono"}
            ],
            "Pop Culture Power User": [
                {"name": "Good Smile Company Nendoroid Figures", "link": "https://www.goodsmile.info/en/products/category/nendoroid_series/announced/2025"},
                {"name": "Bandai Gunpla (Gundam Model Kits)", "link": "https://bandai-hobby.net/site/gunpla/index.html"},
                {"name": "Pokémon Trading Card Game Booster Packs", "link": "https://www.pokemoncenter.com/category/trading-card-game"},
                {"name": "Studio Ghibli Merchandise (e.g., Totoro Plush)", "link": "https://www.gbl.tokyo/"}
            ]
        }


    def load_data(self, file):
        self.df = pd.read_csv(file)
        self.df.columns = self.df.columns.str.lower().str.replace(' ', '_') # Normalize column names
        self.columns = self.df.columns.tolist()
        return True

    def assign_persona(self, row):
        assigned_personas = []
        interested_products = []
        for persona_name, details in self.definitions.items():
            criteria_met = True
            for criterion in details["criteria"]:
                if criterion not in row.index or not row[criterion]: # Check if column exists and value is True/non-empty
                    criteria_met = False
                    break
            if criteria_met:
                assigned_personas.append(persona_name)
                # Add product recommendations for this persona
                interested_products.extend(self.product_recommendations.get(persona_name, []))

        if not assigned_personas:
            return "General Interest", [], []

        return assigned_personas[0], assigned_personas, interested_products # Return first persona, all assigned, and combined products

    def process(self):
        if self.df is None:
            st.error("No data loaded. Please upload a CSV file.")
            return

        self.df[['persona', 'all_assigned_personas', 'recommended_products']] = self.df.apply(
            lambda row: pd.Series(self.assign_persona(row)), axis=1
        )
        # Format recommended products for display with links
        self.df['Recommended Products'] = self.df['recommended_products'].apply(
            lambda prods: "<br>".join([f'<a href="{p["link"]}" target="_blank">{p["name"]}</a>' for p in prods])
        )

        # Generate tags based on assigned persona definitions
        self.df['tags'] = self.df['persona'].apply(
            lambda p: ', '.join(self.definitions.get(p, {}).get('tags', []))
        )
        
        # Add a dummy 'phone' column for demonstration if it doesn't exist
        if 'phone' not in self.df.columns:
            np.random.seed(42) # for reproducibility
            random_numbers = np.random.randint(100000000, 999999999, size=len(self.df))
            phone_numbers = ['0' + str(num) for num in random_numbers]
            self.df['phone'] = phone_numbers


    def to_df(self):
        return self.df

    def get_stats(self):
        if self.df is None:
            return {}
        return dict(Counter(self.df['persona']))

    def grouped_by_persona(self):
        if self.df is None:
            return []
        grouped = self.df.groupby('persona')
        result = []
        for name, group in grouped:
            result.append((name, group.copy())) # Use .copy() to avoid SettingWithCopyWarning
        return result

    def export_template(self):
        # Create a blank DataFrame with relevant columns for a new template
        template_columns = [col for col in self.columns if col not in ['persona', 'all_assigned_personas', 'recommended_products', 'Recommended Products', 'tags', 'phone']]
        template_columns.extend(["j_beauty", "daily_routine", "j_fashion", "style_preference", "fashion_frequency",
                                 "follows_influencers", "streams_often", "buys_merch", "city", "zip", "phone"])
        
        # Add other potential columns if they exist in the original data but not in criteria
        for col in self.df.columns:
            if col not in template_columns and col not in ['persona', 'all_assigned_personas', 'recommended_products', 'Recommended Products', 'tags', 'phone']:
                template_columns.append(col)

        # Ensure unique columns
        template_columns = list(pd.unique(template_columns))
        
        # Create an empty DataFrame for the template
        template_df = pd.DataFrame(columns=template_columns)

        return template_df.to_csv(index=False)


# Streamlit UI
engine = PersonaEngine()

st.title("🎌 J-Culture Customer Persona Generator")

st.sidebar.header("Upload Your Customer Data")
file = st.sidebar.file_uploader("Upload CSV file", type=["csv"], key="csv_uploader")

if file:
    if engine.load_data(file):
        st.sidebar.subheader("📋 Columns Detected")
        st.sidebar.write(engine.columns)

        engine.process()
        df_result = engine.to_df()
        stats = engine.get_stats()

        tab1, tab2 = st.tabs(["📊 Overview", "👥 Persona Details"])

        with tab1:
            st.header("📊 Persona Distribution Overview")
            if stats:
                fig = px.pie(names=list(stats.keys()), values=list(stats.values()), title="Persona Breakdown")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No personas assigned yet. Please check your data or criteria.")

        with tab2:
            st.header("👥 Detailed Persona Assignments")
            grouped = engine.grouped_by_persona()
            if grouped:
                for persona, group in grouped:
                    st.subheader(f"{engine.definitions.get(persona, {}).get('emoji', '')} {persona} ({len(group)} customers)")
                    # Display relevant columns, including the new 'Recommended Products'
                    display_cols = ['customer_id', 'city', 'zip', 'phone', 'tags', 'Recommended Products']
                    # Ensure all display_cols are actually in the DataFrame before selecting
                    display_cols = [col for col in display_cols if col in group.columns]
                    st.dataframe(group[display_cols].reset_index(drop=True), unsafe_allow_html=True) # Allow HTML for links
            else:
                st.info("No detailed persona assignments to display.")


        st.download_button(
            label="📥 Download Persona Results (CSV)",
            data=df_result.to_csv(index=False),
            file_name="persona_results.csv",
            mime="text/csv"
        )

        cleaned_template = engine.export_template()
        st.download_button(
            label="📥 Download Clean CSV Template",
            data=cleaned_template,
            file_name="clean_customer_template.csv",
            mime="text/csv"
        )
else:
    st.info("Please upload your customer CSV file to get started.")
    st.markdown("""
    **Expected CSV Format (Example Columns):**
    `customer_id`, `city`, `zip`, `j_beauty` (True/False), `daily_routine` (True/False),
    `j_fashion` (True/False), `style_preference` (True/False), `fashion_frequency` (True/False),
    `follows_influencers` (True/False), `streams_often` (True/False), `buys_merch` (True/False),
    ... (other customer data)

    **Note:** Ensure your CSV contains boolean-like values (e.g., 'True', 'False', 1, 0) for the criteria columns.
    The app will add a 'Phone Number' column if one doesn't exist and generate 'tags' and 'Recommended Products'.
    """)
