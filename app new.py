import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re

# Set page config
st.set_page_config(
    page_title="J-Culture Customer Persona Generator",
    page_icon="🎌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .persona-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .persona-header {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .persona-detail {
        margin: 5px 0;
        font-size: 16px;
    }
    .target-section {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #28a745;
    }
    .criteria-met {
        color: #28a745;
        font-weight: bold;
    }
    .criteria-not-met {
        color: #dc3545;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
</style>
""", unsafe_allow_html=True)

class JCulturePersonaGenerator:
    def __init__(self):
        self.df = None
        self.personas = []
        self.persona_definitions = {
            "Trend-Savvy Fashionista": {
                "emoji": "💅",
                "criteria": {
                    "required": ["j_fashion", "j_beauty", "follows_influencers", "fashion_frequency_high"],
                    "preferred": ["modern_style", "street_style", "kawaii_style", "streams_culture"]
                },
                "targets": ["Cosmetics", "Fashion drops", "Influencer collabs", "Limited edition makeup", "Trendy accessories"],
                "description_template": "A trendsetting fashion enthusiast who stays ahead of Japanese fashion and beauty trends"
            },
            "Otaku Collector": {
                "emoji": "🎌",
                "criteria": {
                    "required": ["anime_collector", "buys_merch_frequently", "streams_often"],
                    "preferred": ["crunchyroll", "netflix", "youtube", "daily_streaming"]
                },
                "targets": ["Anime figures", "Special edition items", "Collector's goods", "Limited anime merchandise", "Exclusive releases"],
                "description_template": "A dedicated anime fan who actively collects merchandise and streams content regularly"
            },
            "Casual J-Culture Enjoyer": {
                "emoji": "🍣",
                "criteria": {
                    "required": ["some_japanese_interest"],
                    "excluded": ["follows_influencers", "buys_merch_frequently", "fashion_frequency_high"],
                    "preferred": ["japanese_snacks", "casual_streaming", "rare_fashion"]
                },
                "targets": ["Snack boxes", "Simple lifestyle kits", "Light fandom bundles", "Cultural exploration kits"],
                "description_template": "Someone with casual interest in Japanese culture who enjoys exploring without deep commitment"
            },
            "Beauty-Focused Minimalist": {
                "emoji": "🧴",
                "criteria": {
                    "required": ["j_beauty", "daily_routine"],
                    "excluded": ["anime_collector", "buys_merch_frequently", "fashion_frequency_high"],
                    "preferred": ["skincare_focused", "minimalist_approach"]
                },
                "targets": ["Skincare kits", "Minimalist beauty routines", "J-beauty essentials", "Quality skincare products"],
                "description_template": "A beauty enthusiast focused on Japanese skincare with a minimalist, quality-over-quantity approach"
            },
            "Pop Culture Power User": {
                "emoji": "📱",
                "criteria": {
                    "required": ["streams_a_lot", "follows_influencers", "buys_merch_frequently", "fashion_frequent"],
                    "preferred": ["tiktok", "youtube", "styling_focused"]
                },
                "targets": ["Hype campaigns", "Limited drops", "Social media-driven promotions", "Viral products", "Influencer exclusives"],
                "description_template": "A highly engaged pop culture enthusiast who drives trends through social media and frequent purchases"
            },
            "Snack & Lifestyle Explorer": {
                "emoji": "🍱",
                "criteria": {
                    "required": ["japanese_snacks", "daily_routine_explorer"],
                    "excluded": ["fashion_frequency_high", "anime_collector"],
                    "preferred": ["trend_exploration", "lifestyle_focused"]
                },
                "targets": ["Subscription boxes", "Limited-edition snack collabs", "Bento kits", "Lifestyle exploration sets"],
                "description_template": "A lifestyle enthusiast who loves exploring Japanese snacks and daily routine trends"
            }
        }
    
    def load_data(self, uploaded_file):
        """Load and process uploaded customer data"""
        try:
            if uploaded_file.name.endswith('.csv'):
                self.df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                self.df = pd.read_excel(uploaded_file)
            else:
                st.error("Please upload a CSV or Excel file")
                return False
            
            # Clean column names
            self.df.columns = self.df.columns.str.strip()
            
            # Basic data validation
            if self.df.empty:
                st.error("The uploaded file is empty")
                return False
            
            st.success(f"Data loaded successfully! {len(self.df)} customers found.")
            return True
            
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return False
    
    def extract_customer_attributes(self, row):
        """Extract and normalize customer attributes for persona matching"""
        attributes = set()
        
        # Convert all values to lowercase strings for comparison
        row_str = {k: str(v).lower().strip() for k, v in row.items() if pd.notna(v)}
        
        # J-Fashion interest
        if any('j-fashion' in str(k).lower() or 'japanese fashion' in str(k).lower() for k in row.keys()):
            for k, v in row_str.items():
                if ('j-fashion' in k or 'japanese fashion' in k) and v in ['yes', 'true', '1']:
                    attributes.add('j_fashion')
        
        # J-Beauty interest
        if any('j-beauty' in str(k).lower() or 'japanese beauty' in str(k).lower() for k in row.keys()):
            for k, v in row_str.items():
                if ('j-beauty' in k or 'japanese beauty' in k) and v in ['yes', 'true', '1']:
                    attributes.add('j_beauty')
        
        # Style preferences
        for k, v in row_str.items():
            if 'style' in k:
                if 'modern' in v or 'street' in v or 'streetwear' in v:
                    attributes.add('modern_style')
                    attributes.add('street_style')
                if 'kawaii' in v or 'cute' in v:
                    attributes.add('kawaii_style')
        
        # Fashion frequency
        for k, v in row_str.items():
            if 'fashion frequency' in k:
                if v in ['daily', 'weekly', 'high', 'frequent']:
                    attributes.add('fashion_frequency_high')
                elif v in ['rarely', 'never', 'low']:
                    attributes.add('rare_fashion')
        
        # Follows influencers
        for k, v in row_str.items():
            if 'follow' in k and 'influencer' in k:
                if v in ['yes', 'true', '1']:
                    attributes.add('follows_influencers')
        
        # Anime collector
        for k, v in row_str.items():
            if 'anime' in k and 'collector' in k:
                if v in ['yes', 'true', '1']:
                    attributes.add('anime_collector')
        
        # Buys merch
        for k, v in row_str.items():
            if 'buys merch' in k or 'buy merch' in k:
                if v in ['yes', 'frequently', 'often', 'true', '1']:
                    attributes.add('buys_merch_frequently')
        
        # Streaming frequency
        for k, v in row_str.items():
            if 'streaming frequency' in k:
                if v in ['daily', 'weekly']:
                    attributes.add('streams_often')
                    attributes.add('daily_streaming')
                elif v in ['monthly', 'sometimes']:
                    attributes.add('casual_streaming')
                if v in ['daily', 'weekly', 'frequently']:
                    attributes.add('streams_a_lot')
        
        # Favorite platforms
        for k, v in row_str.items():
            if 'platform' in k:
                if 'crunchyroll' in v:
                    attributes.add('crunchyroll')
                elif 'netflix' in v:
                    attributes.add('netflix')
                elif 'youtube' in v:
                    attributes.add('youtube')
                elif 'tiktok' in v:
                    attributes.add('tiktok')
        
        # Japanese snacks
        for k, v in row_str.items():
            if 'japanese snacks' in k or 'snacks' in k:
                if v in ['yes', 'true', '1']:
                    attributes.add('japanese_snacks')
        
        # Daily routine
        for k, v in row_str.items():
            if 'daily routine' in k:
                if v in ['yes', 'defined', 'structured']:
                    attributes.add('daily_routine')
                if 'explore' in v or 'new' in v:
                    attributes.add('daily_routine_explorer')
        
        # General Japanese interest
        japanese_keywords = ['japanese', 'j-', 'anime', 'manga', 'kawaii']
        if any(keyword in str(row).lower() for keyword in japanese_keywords):
            attributes.add('some_japanese_interest')
        
        # Fashion frequency indicators
        for k, v in row_str.items():
            if 'fashion' in k and 'frequency' in k:
                if v in ['frequent', 'often', 'regularly']:
                    attributes.add('fashion_frequent')
        
        return attributes
    
    def calculate_persona_score(self, attributes, persona_name):
        """Calculate how well a customer matches a persona"""
        persona_def = self.persona_definitions[persona_name]
        score = 0
        max_score = 0
        details = {"met": [], "not_met": [], "excluded_present": []}
        
        # Check required criteria
        for req in persona_def["criteria"]["required"]:
            max_score += 10
            if req in attributes:
                score += 10
                details["met"].append(req)
            else:
                details["not_met"].append(req)
        
        # Check preferred criteria
        if "preferred" in persona_def["criteria"]:
            for pref in persona_def["criteria"]["preferred"]:
                max_score += 5
                if pref in attributes:
                    score += 5
                    details["met"].append(pref)
        
        # Check excluded criteria (negative scoring)
        if "excluded" in persona_def["criteria"]:
            for excl in persona_def["criteria"]["excluded"]:
                if excl in attributes:
                    score -= 15
                    details["excluded_present"].append(excl)
        
        # Calculate percentage score
        if max_score > 0:
            percentage = max(0, (score / max_score) * 100)
        else:
            percentage = 0
        
        return percentage, details
    
    def assign_persona(self, customer_data):
        """Assign the best matching persona to a customer"""
        attributes = self.extract_customer_attributes(customer_data)
        
        best_persona = None
        best_score = 0
        best_details = None
        scores = {}
        
        for persona_name in self.persona_definitions.keys():
            score, details = self.calculate_persona_score(attributes, persona_name)
            scores[persona_name] = score
            
            if score > best_score:
                best_score = score
                best_persona = persona_name
                best_details = details
        
        # Only assign persona if score is above threshold
        if best_score >= 20:  # 20% match threshold
            return best_persona, best_score, best_details, scores
        else:
            return "Unclassified", best_score, best_details, scores
    
    def generate_persona_description(self, customer_data, persona_name, score, details):
        """Generate a detailed persona description"""
        if persona_name == "Unclassified":
            return "This customer doesn't strongly match any of our defined J-culture personas. They may need a custom approach or represent a new persona type."
        
        persona_def = self.persona_definitions[persona_name]
        
        # Base description
        description = f"{persona_def['description_template']}. "
        
        # Add customer specifics
        city = customer_data.get('customer_city', 'Unknown City')
        description += f"Based in {city}, "
        
        # Add matching criteria
        if details["met"]:
            description += f"they demonstrate {len(details['met'])} key characteristics of this persona type. "
        
        # Add confidence
        if score >= 80:
            description += "This is a high-confidence match with strong alignment to persona characteristics."
        elif score >= 60:
            description += "This is a good match with solid alignment to persona characteristics."
        else:
            description += "This is a moderate match - consider this persona with some customization."
        
        return description
    
    def generate_personas(self):
        """Generate personas for all customers"""
        if self.df is None:
            return False
        
        self.personas = []
        
        for idx, row in self.df.iterrows():
            persona_name, score, details, all_scores = self.assign_persona(row)
            
            persona = {
                'customer_id': row.get('customer_id', f'customer_{idx}'),
                'customer_unique_id': row.get('customer_unique_id', ''),
                'location': {
                    'city': row.get('customer_city', 'Unknown'),
                    'zip_code': row.get('customer_zip_code_prefix', 'Unknown')
                },
                'persona_type': persona_name,
                'persona_emoji': self.persona_definitions.get(persona_name, {}).get('emoji', '❓'),
                'confidence_score': round(score, 1),
                'matching_details': details,
                'all_scores': {k: round(v, 1) for k, v in all_scores.items()},
                'target_products': self.persona_definitions.get(persona_name, {}).get('targets', []),
                'description': self.generate_persona_description(row, persona_name, score, details),
                'raw_data': row.to_dict()
            }
            
            self.personas.append(persona)
        
        return True
    
    def get_persona_statistics(self):
        """Get statistics about generated personas"""
        if not self.personas:
            return {}
        
        persona_counts = Counter([p['persona_type'] for p in self.personas])
        cities = Counter([p['location']['city'] for p in self.personas])
        
        # Calculate average confidence by persona type
        confidence_by_persona = {}
        for persona_type in persona_counts.keys():
            scores = [p['confidence_score'] for p in self.personas if p['persona_type'] == persona_type]
            confidence_by_persona[persona_type] = round(sum(scores) / len(scores), 1) if scores else 0
        
        stats = {
            'total_personas': len(self.personas),
            'persona_distribution': dict(persona_counts),
            'cities': dict(cities),
            'confidence_by_persona': confidence_by_persona,
            'high_confidence_count': len([p for p in self.personas if p['confidence_score'] >= 80]),
            'medium_confidence_count': len([p for p in self.personas if 60 <= p['confidence_score'] < 80]),
            'low_confidence_count': len([p for p in self.personas if p['confidence_score'] < 60])
        }
        
        return stats

def main():
    st.title("🎌 J-Culture Customer Persona Generator")
    st.markdown("Generate targeted personas for Japanese culture enthusiasts and plan your marketing strategy!")
    
    # Initialize the generator
    if 'generator' not in st.session_state:
        st.session_state.generator = JCulturePersonaGenerator()
    
    # Sidebar for file upload and persona guide
    with st.sidebar:
        st.header("📤 Upload Data")
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload your customer data with J-culture related columns"
        )
        
        if uploaded_file is not None:
            if st.button("🔄 Generate Personas"):
                with st.spinner("Processing customer data..."):
                    if st.session_state.generator.load_data(uploaded_file):
                        with st.spinner("Matching customers to personas..."):
                            if st.session_state.generator.generate_personas():
                                st.success("✅ Personas generated successfully!")
                                st.rerun()
        
        st.markdown("---")
        st.header("🎯 Our 6 Personas")
        
        for persona_name, persona_def in st.session_state.generator.persona_definitions.items():
            with st.expander(f"{persona_def['emoji']} {persona_name}"):
                st.write(f"**Focus**: {persona_def['description_template']}")
                st.write(f"**Targets**: {', '.join(persona_def['targets'][:3])}...")
    
    # Main content area
    if st.session_state.generator.df is not None:
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "👥 Personas", "🎯 Marketing Strategy", "📋 Raw Data"])
        
        with tab1:
            st.header("📊 Persona Distribution Overview")
            
            stats = st.session_state.generator.get_persona_statistics()
            
            if stats:
                # Key metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Customers", stats['total_personas'])
                
                with col2:
                    st.metric("High Confidence", stats['high_confidence_count'])
                
                with col3:
                    st.metric("Active Personas", len([k for k, v in stats['persona_distribution'].items() if v > 0]))
                
                with col4:
                    avg_confidence = sum(stats['confidence_by_persona'].values()) / len(stats['confidence_by_persona'])
                    st.metric("Avg Confidence", f"{avg_confidence:.1f}%")
                
                # Visualization
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Persona Distribution")
                    if stats['persona_distribution']:
                        # Create pie chart with emojis
                        labels = []
                        values = []
                        for persona, count in stats['persona_distribution'].items():
                            emoji = st.session_state.generator.persona_definitions.get(persona, {}).get('emoji', '❓')
                            labels.append(f"{emoji} {persona}")
                            values.append(count)
                        
                        fig = px.pie(values=values, names=labels, title="Customer Persona Breakdown")
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.subheader("Confidence Levels")
                    confidence_data = {
                        'Level': ['High (80%+)', 'Medium (60-80%)', 'Low (<60%)'],
                        'Count': [stats['high_confidence_count'], stats['medium_confidence_count'], stats['low_confidence_count']]
                    }
                    fig = px.bar(confidence_data, x='Level', y='Count', title="Persona Matching Confidence")
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.header("👥 Customer Personas")
            
            if st.session_state.generator.personas:
                # Filters
                col1, col2 = st.columns(2)
                
                with col1:
                    persona_filter = st.multiselect(
                        "Filter by persona type",
                        options=list(st.session_state.generator.persona_definitions.keys()) + ["Unclassified"],
                        default=[]
                    )
                
                with col2:
                    confidence_filter = st.select_slider(
                        "Minimum confidence level",
                        options=[0, 40, 60, 80],
                        value=0,
                        format_func=lambda x: f"{x}%+"
                    )
                
                # Filter personas
                filtered_personas = st.session_state.generator.personas
                
                if persona_filter:
                    filtered_personas = [p for p in filtered_personas if p['persona_type'] in persona_filter]
                
                if confidence_filter > 0:
                    filtered_personas = [p for p in filtered_personas if p['confidence_score'] >= confidence_filter]
                
                st.write(f"Showing {len(filtered_personas)} of {len(st.session_state.generator.personas)} personas")
                
                # Display personas
                for persona in filtered_personas:
                    with st.expander(f"{persona['persona_emoji']} {persona['persona_type']} - {persona['location']['city']} ({persona['confidence_score']}% match)"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"**📝 Description:**")
                            st.write(persona['description'])
                            
                            # Show matching criteria
                            if persona['matching_details']['met']:
                                st.markdown("**✅ Matching Criteria:**")
                                for criteria in persona['matching_details']['met']:
                                    st.write(f"• {criteria.replace('_', ' ').title()}")
                            
                            if persona['matching_details']['not_met']:
                                st.markdown("**❌ Missing Criteria:**")
                                for criteria in persona['matching_details']['not_met']:
                                    st.write(f"• {criteria.replace('_', ' ').title()}")
                        
                        with col2:
                            st.markdown(f"**📍 Location:** {persona['location']['city']}")
                            st.markdown(f"**🎯 Confidence:** {persona['confidence_score']}%")
                            
                            # Target products
                            if persona['target_products']:
                                st.markdown("**🛍️ Target Products:**")
                                for product in persona['target_products']:
                                    st.write(f"• {product}")
                            
                            # All scores
                            with st.expander("See all persona scores"):
                                for p_name, score in persona['all_scores'].items():
                                    st.write(f"{p_name}: {score}%")
        
        with tab3:
            st.header("🎯 Marketing Strategy Recommendations")
            
            if st.session_state.generator.personas:
                stats = st.session_state.generator.get_persona_statistics()
                
                # Strategy recommendations for each persona
                for persona_name, persona_def in st.session_state.generator.persona_definitions.items():
                    count = stats['persona_distribution'].get(persona_name, 0)
                    if count > 0:
                        avg_confidence = stats['confidence_by_persona'].get(persona_name, 0)
                        
                        st.markdown(f"### {persona_def['emoji']} {persona_name} ({count} customers)")
                        
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown("**🎯 Recommended Products:**")
                            for product in persona_def['targets']:
                                st.write(f"• {product}")
                            
                            # Marketing channel recommendations
                            st.markdown("**📢 Marketing Channels:**")
                            if persona_name == "Trend-Savvy Fashionista":
                                st.write("• Instagram fashion posts & stories")
                                st.write("• TikTok fashion challenges")
                                st.write("• Influencer partnerships")
                            elif persona_name == "Otaku Collector":
                                st.write("• Anime convention partnerships")
                                st.write("• Collector community forums")
                                st.write("• Limited edition launches")
                            elif persona_name == "Pop Culture Power User":
                                st.write("• Social media campaigns")
                                st.write("• Viral marketing tactics")
                                st.write("• Platform-specific content")
                            else:
                                st.write("• Email newsletters")
                                st.write("• Content marketing")
                                st.write("• Targeted social ads")
                        
                        with col2:
                            st.metric("Customer Count", count)
                            st.metric("Avg Confidence", f"{avg_confidence}%")
                            
                            # Priority level
                            if count >= 5 and avg_confidence >= 70:
                                st.success("🔥 High Priority Segment")
                            elif count >= 3 and avg_confidence >= 60:
                                st.info("📈 Medium Priority Segment")
                            else:
                                st.warning("💡 Low Priority Segment")
                        
                        st.markdown("---")
        
        with tab4:
            st.header("📋 Data Export & Analysis")
            
            # Raw data view
            st.subheader("Original Customer Data")
            st.dataframe(st.session_state.generator.df, use_container_width=True)
            
            # Export options
            st.subheader("📥 Export Options")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.session_state.generator.personas:
                    # Export detailed personas
                    personas_json = json.dumps(st.session_state.generator.personas, indent=2)
                    st.download_button(
                        "📥 Download Detailed Personas (JSON)",
                        personas_json,
                        "j_culture_personas.json",
                        "application/json"
                    )
            
            with col2:
                if st.session_state.generator.personas:
                    # Export marketing summary
                    marketing_data = []
                    for persona in st.session_state.generator.personas:
                        marketing_data.append({
                            'customer_id': persona['customer_id'],
                            'persona_type': persona['persona_type'],
                            'confidence': persona['confidence_score'],
                            'city': persona['location']['city'],
                            'target_products': ', '.join(persona['target_products'][:3])
                        })
                    
                    marketing_df = pd.DataFrame(marketing_data)
                    csv = marketing_df.to_csv(index=False)
                    st.download_button(
                        "📥 Download Marketing Summary (CSV)",
                        csv,
                        "marketing_summary.csv",
                        "text/csv"
                    )
            
            with col3:
                if st.session_state.generator.personas:
                    # Export statistics
                    stats = st.session_state.generator.get_persona_statistics()
                    stats_json = json.dumps(stats, indent=2)
                    st.download_button(
                        "📥 Download Statistics (JSON)",
                        stats_json,
                        "persona_statistics.json",
                        "application/json"
                    )
    
    else:
        # Welcome screen
        st.markdown("""
        ## 🎌 Welcome to J-Culture Persona Generator!
        
        Transform your customer data into actionable J-culture personas for targeted marketing.
        
        ### 🎯 Our 6 Specialized Personas:
        
        **💅 Trend-Savvy Fashionista** - Fashion & beauty enthusiasts who follow trends
        **🎌 Otaku Collector** - Dedicated anime fans and merchandise collectors  
        **🍣 Casual J-Culture Enjoyer** - Light interest in Japanese culture
        **🧴 Beauty-Focused Minimalist** - J-beauty enthusiasts with minimalist approach
        **📱 Pop Culture Power User** - Social media savvy trend drivers
        **🍱 Snack & Lifestyle Explorer** - Food and lifestyle trend explorers
        
        ### 📊 What You'll Get:
        - **Persona Assignment**: Each customer matched to best-fit persona
        - **Confidence Scoring**: Know how well each match fits
        - **Target Products**: Specific product recommendations per persona
        - **Marketing Strategy**: Channel and campaign recommendations
        - **Export Options**: Download results for your marketing team
        
        ### 📋 Data Format:
        Your CSV/Excel should include columns like:
        - Customer identification (customer_id, customer_city)
        - J-culture interests (Interested in J-fashion, J-beauty, etc.)
        - Behavioral data (Fashion Frequency, Streaming Frequency, etc.)
        - Preferences (Style Preference, Favorite Platform, etc.)
        - Actions (Buys Merch, Follows Fashion Influencers, etc.)
        
        **Ready to get started? Upload your data using the sidebar! 👈**
        """)

if __name__ == "__main__":
    main()
