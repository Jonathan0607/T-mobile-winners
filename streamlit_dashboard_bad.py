import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page configuration - SIDEBAR MUST BE EXPANDED BY DEFAULT
st.set_page_config(
    page_title="T-Mobile Vibe Check - Mission Control",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"  # This ensures sidebar is visible on load
)

# ============================================================================
# MOCK DATA
# ============================================================================

MOCK_SUMMARY = {
    "chi_score": 85.2,
    "chi_trend": -1.5,
    "trend_direction": "down",
    "trend_period": "Last Hour",
    "top_reasons": ["5G Speed Degradation (NY)", "Billing Error Confusion"],
    "action_cards": [
        {
            "id": "A101",
            "team": "Network Engineering",
            "priority": "Critical",
            "title": "Investigate 5G outage in Miami",
            "insight": "40% spike in 'slow data' complaints in zip 33139 over 1hr.",
            "location": "Miami, FL"
        },
        {
            "id": "A102",
            "team": "Social Media Support",
            "priority": "High",
            "title": "Draft response to #SlowMagenta trend",
            "insight": "Sentiment velocity shows high risk of negative virality in 2 hours.",
            "location": "National"
        }
    ]
}

MOCK_COMPETITIVE_DATA = [
    {"carrier": "T-Mobile", "score": 85.2},
    {"carrier": "AT&T", "score": 87.7},
    {"carrier": "Verizon", "score": 81.2},
]

# Generate 24-hour trend data
def generate_trend_data():
    hours = ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00']
    values = [86.5, 87.0, 86.8, 87.2, 86.9, 85.7, 85.2]
    return pd.DataFrame({'hour': hours, 'value': values})

# Present state heat map data
PRESENT_HEATMAP_DATA = [
    {"city": "New York", "lat": 40.7128, "lon": -74.0060, "intensity": "high", "velocity": "high", "issues": 45},
    {"city": "Los Angeles", "lat": 34.0522, "lon": -118.2437, "intensity": "medium", "velocity": "medium", "issues": 28},
    {"city": "Miami", "lat": 25.7617, "lon": -80.1918, "intensity": "high", "velocity": "high", "issues": 52},
    {"city": "Chicago", "lat": 41.8781, "lon": -87.6298, "intensity": "low", "velocity": "low", "issues": 12},
    {"city": "Seattle", "lat": 47.6062, "lon": -122.3321, "intensity": "medium", "velocity": "medium", "issues": 19},
    {"city": "Dallas", "lat": 32.7767, "lon": -96.7970, "intensity": "medium", "velocity": "medium", "issues": 22},
    {"city": "Houston", "lat": 29.7604, "lon": -95.3698, "intensity": "low", "velocity": "low", "issues": 15},
    {"city": "Atlanta", "lat": 33.7490, "lon": -84.3880, "intensity": "high", "velocity": "high", "issues": 38},
]

# Predictive heat map data (projected future issues)
PREDICTIVE_HEATMAP_DATA = [
    {"city": "New York", "lat": 40.7128, "lon": -74.0060, "intensity": "high", "velocity": "high", "issues": 58, "predicted": True},
    {"city": "Los Angeles", "lat": 34.0522, "lon": -118.2437, "intensity": "high", "velocity": "high", "issues": 42, "predicted": True},
    {"city": "Miami", "lat": 25.7617, "lon": -80.1918, "intensity": "high", "velocity": "high", "issues": 65, "predicted": True},
    {"city": "Chicago", "lat": 41.8781, "lon": -87.6298, "intensity": "medium", "velocity": "medium", "issues": 25, "predicted": True},
    {"city": "Seattle", "lat": 47.6062, "lon": -122.3321, "intensity": "high", "velocity": "high", "issues": 32, "predicted": True},
    {"city": "Dallas", "lat": 32.7767, "lon": -96.7970, "intensity": "medium", "velocity": "medium", "issues": 28, "predicted": True},
    {"city": "Houston", "lat": 29.7604, "lon": -95.3698, "intensity": "medium", "velocity": "medium", "issues": 22, "predicted": True},
    {"city": "Atlanta", "lat": 33.7490, "lon": -84.3880, "intensity": "high", "velocity": "high", "issues": 48, "predicted": True},
    {"city": "Phoenix", "lat": 33.4484, "lon": -112.0740, "intensity": "medium", "velocity": "medium", "issues": 18, "predicted": True},
    {"city": "Denver", "lat": 39.7392, "lon": -104.9903, "intensity": "low", "velocity": "low", "issues": 14, "predicted": True},
]

# ============================================================================
# CUSTOM CSS
# ============================================================================

CUSTOM_CSS = """
<style>
    /* Global dark mode styling */
    .stApp {
        background-color: #1A1A1A;
        color: #FFFFFF;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sidebar styling - ONLY style colors, NEVER hide or change display */
    [data-testid="stSidebar"] {
        background-color: #2C2C2C;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #FFFFFF;
    }
    
    /* CRITICAL: Do not modify sidebar visibility in global CSS */
    /* Sidebar visibility is controlled by Streamlit and session state only */
    
    
    /* Card styling */
    .dashboard-card {
        background-color: #2C2C2C;
        border-radius: 8px;
        padding: 24px;
        border: 1px solid #404040;
        margin-bottom: 20px;
    }
    
    .vibe-score-card {
        background-color: #2C2C2C;
        border-radius: 8px;
        padding: 24px;
        border: 1px solid #404040;
        text-align: center;
    }
    
    .action-card {
        background-color: #2C2C2C;
        border-radius: 8px;
        padding: 24px;
        border-left: 4px solid;
        margin-bottom: 20px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .action-card.critical {
        border-left-color: #D62828;
    }
    
    .action-card.high {
        border-left-color: #FFC300;
    }
    
    .priority-badge {
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        padding: 4px 8px;
        border-radius: 4px;
        display: inline-block;
    }
    
    .priority-critical {
        color: #D62828;
    }
    
    .priority-high {
        color: #FFC300;
    }
    
    .magenta-button {
        background-color: #E20074;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 600;
        cursor: pointer;
    }
    
    .magenta-button:hover {
        background-color: #C1005F;
    }
    
    .vibe-score-display {
        font-size: 64px;
        font-weight: bold;
        color: #FFFFFF;
        margin: 20px 0;
    }
    
    .chi-label {
        font-size: 14px;
        color: #9CA3AF;
        margin-top: 8px;
    }
    
    .trend-indicator {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        margin: 16px 0;
        color: #D62828;
        font-weight: 600;
    }
    
    .sidebar-logo {
        font-size: 24px;
        font-weight: bold;
        color: #E20074;
        margin-bottom: 8px;
    }
    
    .sidebar-subtitle {
        font-size: 12px;
        color: #9CA3AF;
        margin-bottom: 24px;
    }
    
    .nav-item {
        padding: 12px 16px;
        margin: 4px 0;
        border-radius: 8px;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .nav-item.active {
        background-color: rgba(226, 0, 116, 0.2);
        color: #E20074;
        border-left: 4px solid #E20074;
    }
    
    .nav-item:hover {
        background-color: #404040;
    }
    
    .heatmap-container {
        background-color: #1A1A1A;
        border-radius: 8px;
        padding: 20px;
        border: 1px solid #404040;
        height: 300px;
        position: relative;
    }
    
    .action-card-container {
        background-color: #2C2C2C;
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 20px;
        height: 100%;
    }
    
    .stButton > button {
        background-color: #E20074;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 600;
        width: 100%;
    }
    
    .stButton > button:hover {
        background-color: #C1005F;
    }
    
    /* Radio button styling for map toggle */
    .stRadio > div {
        display: flex;
        gap: 20px;
        margin-bottom: 16px;
    }
    
    .stRadio > div > label {
        color: #FFFFFF;
        font-weight: 500;
        padding: 8px 16px;
        border-radius: 6px;
        background-color: #2C2C2C;
        border: 1px solid #404040;
        transition: all 0.2s;
    }
    
    .stRadio > div > label:hover {
        background-color: #404040;
        border-color: #E20074;
    }
    
    .stRadio > div > label[data-baseweb="radio"] {
        background-color: #E20074;
        border-color: #E20074;
    }
</style>
"""

# Inject CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - PAGE NAVIGATION
# ============================================================================

# Initialize session state - sidebar is VISIBLE by default
if 'current_page' not in st.session_state:
    st.session_state.current_page = "All Teams"
if 'sidebar_visible' not in st.session_state:
    st.session_state.sidebar_visible = True

# Apply hiding CSS ONLY when sidebar_visible is explicitly False
# When True (default), Streamlit's native sidebar is visible - we do nothing
if st.session_state.sidebar_visible == False:
    st.markdown("""
    <style>
    section[data-testid="stSidebar"],
    [data-testid="stSidebar"] {
        display: none !important;
    }
    [data-testid="stAppViewContainer"] > [data-testid="stAppViewBlockContainer"] {
        margin-left: 0 !important;
        max-width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

# SIDEBAR - Always render this, Streamlit will handle visibility
with st.sidebar:
    # Logo and Title
    st.markdown('<div class="sidebar-logo">T-Mobile</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtitle">Vibe Check</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Navigation
    st.markdown('<p style="font-size: 14px; font-weight: 600; color: #9CA3AF; margin-bottom: 10px;">Navigation</p>', unsafe_allow_html=True)
    
    nav_options = ["All Teams", "Network Engineering", "Social Media", "Sales"]
    selected_page = st.selectbox(
        "Select Page",
        options=nav_options,
        index=nav_options.index(st.session_state.current_page) if st.session_state.current_page in nav_options else 0,
        label_visibility="collapsed",
        key="page_selector"
    )
    st.session_state.current_page = selected_page
    
    st.markdown("---")
    st.markdown("**Mission Control**")
    st.markdown("© 2025 T-Mobile")
    st.markdown("---")
    
    # Hide Sidebar Button - Only show if sidebar is currently visible
    if st.session_state.sidebar_visible:
        if st.button("🔲 Hide Sidebar", key="hide_sidebar_btn", use_container_width=True):
            st.session_state.sidebar_visible = False
            st.rerun()

# ============================================================================
# PAGE CONTENT BASED ON SELECTION
# ============================================================================

# Show Sidebar Button - appears in main content when sidebar is hidden
if not st.session_state.sidebar_visible:
    # Prominent notification
    st.error("⚠️ Sidebar is hidden. Click below to show it.")
    
    # Show sidebar button
    col1, col2, col3 = st.columns([2, 3, 2])
    with col2:
        if st.button("☰ SHOW SIDEBAR", key="show_sidebar_btn", type="primary", use_container_width=True):
            st.session_state.sidebar_visible = True
            st.rerun()
    st.markdown("---")

# Header (shown on all pages)
col_header1, col_header2 = st.columns([3, 1])
with col_header1:
    page_title = f"T-Mobile Vibe Check - {st.session_state.current_page}"
    st.title(page_title)
with col_header2:
    st.markdown(f"<div style='text-align: right; color: #9CA3AF; margin-top: 20px;'>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>", unsafe_allow_html=True)

st.markdown("---")

# Page-specific content
selected_page = st.session_state.current_page

# ============================================================================
# ALL TEAMS PAGE (Default Dashboard)
# ============================================================================
if selected_page == "All Teams":
    # ROW 1: Vibe Score Card + Action Cards
    col1, col2 = st.columns([1, 2])
    
    # Column 1: Vibe Score Card
    with col1:
        # Circular progress indicator using HTML/CSS
        score = MOCK_SUMMARY["chi_score"]
        percentage = score / 100.0
        radius = 88
        circumference = 2 * 3.14159 * radius
        dash_offset = circumference * (1 - percentage)
        
        # SVG Circular Progress
        svg_circle = f"""
        <div style="position: relative; width: 200px; height: 200px; margin: 0 auto;">
            <svg width="200" height="200" style="transform: rotate(-90deg);">
                <circle cx="100" cy="100" r="{radius}" stroke="#404040" stroke-width="12" fill="none"/>
                <circle cx="100" cy="100" r="{radius}" stroke="#E20074" stroke-width="12" fill="none"
                        stroke-dasharray="{circumference}"
                        stroke-dashoffset="{dash_offset}"
                        stroke-linecap="round"/>
            </svg>
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; width: 100%;">
                <div style="font-size: 48px; font-weight: bold; color: #FFFFFF;">{score}</div>
                <div style="font-size: 14px; color: #9CA3AF; margin-top: 4px;">CHI Score</div>
            </div>
        </div>
        """
        st.markdown(svg_circle, unsafe_allow_html=True)
        
        # Trend Indicator
        trend_value = abs(MOCK_SUMMARY["chi_trend"])
        trend_period = MOCK_SUMMARY["trend_period"]
        trend_html = f"""
        <div class="trend-indicator">
            <span style="font-size: 20px;">↓</span>
            <span>{trend_value} vs {trend_period}</span>
        </div>
        """
        st.markdown(trend_html, unsafe_allow_html=True)
        
        # 24-hour Trend Line Chart
        trend_df = generate_trend_data()
        fig_trend = px.line(
            trend_df,
            x='hour',
            y='value',
            markers=True,
            color_discrete_sequence=['#E20074']
        )
        fig_trend.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#9CA3AF', size=10),
            margin=dict(l=0, r=0, t=0, b=0),
            height=120,
            xaxis=dict(
                gridcolor='#404040',
                showgrid=True,
                tickfont=dict(size=10, color='#9CA3AF')
            ),
            yaxis=dict(
                gridcolor='#404040',
                showgrid=True,
                range=[80, 90],
                tickfont=dict(size=10, color='#9CA3AF'),
                visible=False
            ),
            showlegend=False
        )
        fig_trend.update_traces(
            line=dict(width=2),
            marker=dict(size=4),
            hovertemplate='<b>%{x}</b><br>Score: %{y}<extra></extra>'
        )
        st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})

    # Column 2: Action Cards
    with col2:
        action_col1, action_col2 = st.columns(2)
        
        for i, card in enumerate(MOCK_SUMMARY["action_cards"]):
            with (action_col1 if i == 0 else action_col2):
                priority_color = "#D62828" if card["priority"] == "Critical" else "#FFC300"
                
                # Card container with border
                card_html = f"""
                <div class="action-card-container" style="border-left: 4px solid {priority_color};">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                        <span style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: {priority_color};">
                            {card["priority"]}
                        </span>
                        <span style="font-size: 12px; color: #9CA3AF;">{card["location"]}</span>
                    </div>
                    <h3 style="font-size: 20px; font-weight: bold; color: #FFFFFF; margin-bottom: 8px;">
                        {card["title"]}
                    </h3>
                    <div style="margin-bottom: 8px;">
                        <span style="font-size: 14px; color: #9CA3AF;">Team: </span>
                        <span style="font-size: 14px; color: #FFFFFF; font-weight: 600;">{card["team"]}</span>
                    </div>
                    <p style="font-size: 14px; color: #D1D5DB; margin-bottom: 16px;">
                        {card["insight"]}
                    </p>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)

    # ============================================================================
    # ROW 2: Predictive Heatmap + Competitive Check
    # ============================================================================
    st.markdown("---")  # Horizontal divider
    
    col3, col4 = st.columns(2)
    
    # Column 3: Predictive Issue Heat Map
    with col3:
        st.markdown('<h2 style="font-size: 24px; font-weight: bold; color: #FFFFFF; margin-bottom: 24px;">Issue Heat Map</h2>', unsafe_allow_html=True)
        
        # Map view toggle
        map_view = st.radio(
            "Map View",
            options=["Present", "Predictive"],
            index=0,
            horizontal=True,
            label_visibility="visible",
            key="map_view_toggle"
        )
        
        # Select data based on view
        if map_view == "Present":
            map_data = PRESENT_HEATMAP_DATA
            map_title = "Current Issue Distribution"
        else:
            map_data = PREDICTIVE_HEATMAP_DATA
            map_title = "Predicted Issue Distribution (24h Forecast)"
        
        # Create DataFrame for map
        map_df = pd.DataFrame(map_data)
        
        # Determine marker size based on intensity (scaled for geo plot)
        map_df['size'] = map_df['intensity'].map({'high': 25, 'medium': 18, 'low': 12})
        
        # Create figure with scattergeo (works without tokens)
        fig_map = go.Figure()
        
        # Add each city as a separate trace for better hover control
        for _, row in map_df.iterrows():
            # For Present view: color by intensity, for Predictive view: color by velocity
            if map_view == "Present":
                # Present: Color by intensity
                intensity = row['intensity']
                color = '#D62828' if intensity == 'high' else ('#FF6B35' if intensity == 'medium' else '#E20074')
            else:
                # Predictive: Color by velocity
                velocity = row['velocity']
                color = '#D62828' if velocity == 'high' else ('#FF6B35' if velocity == 'medium' else '#E20074')
            
            fig_map.add_trace(go.Scattergeo(
                lat=[row['lat']],
                lon=[row['lon']],
                mode='markers+text',
                text=[row['city']],
                textposition="middle right",
                textfont=dict(size=10, color='white'),
                marker=dict(
                    size=[row['size']],
                    color=color,
                    opacity=0.8,
                    line=dict(width=1, color='white')
                ),
                hovertemplate=f"<b>{row['city']}</b><br>" +
                            f"Issues: {row['issues']}<br>" +
                            f"Intensity: {row['intensity'].title()}<br>" +
                            f"Velocity: {row['velocity'].title()}<br>" +
                            (f"<i>Predicted</i><extra></extra>" if map_view == "Predictive" else "<extra></extra>"),
                name=row['city'],
                showlegend=False
            ))
        
        # Update layout for US focus
        fig_map.update_layout(
            geo=dict(
                scope='usa',
                projection_type='albers usa',
                showland=True,
                landcolor='#2C2C2C',
                coastlinecolor='#404040',
                lakecolor='#1A1A1A',
                showlakes=True,
                showocean=True,
                oceancolor='#1A1A1A',
                bgcolor='rgba(0,0,0,0)',
                lonaxis_range=[-130, -65],
                lataxis_range=[25, 50]
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            height=350,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        
        st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})
        
        # Map title and legend
        map_info_html = f"""
        <div style="margin-top: 12px;">
            <p style="font-size: 12px; color: #9CA3AF; margin-bottom: 12px; font-style: italic;">
                {map_title}
            </p>
        </div>
        """
        st.markdown(map_info_html, unsafe_allow_html=True)
        
        # Legend - Different for Present vs Predictive
        if map_view == "Present":
            # Present view: Show Intensity levels (colors match intensity)
            legend_html = """
            <div style="display: flex; gap: 24px; margin-top: 16px; font-size: 14px; flex-wrap: wrap;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 16px; height: 16px; background-color: #D62828; border-radius: 50%;"></div>
                    <span style="color: #D1D5DB;">High Intensity</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 16px; height: 16px; background-color: #FF6B35; border-radius: 50%;"></div>
                    <span style="color: #D1D5DB;">Medium Intensity</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 16px; height: 16px; background-color: #E20074; border-radius: 50%;"></div>
                    <span style="color: #D1D5DB;">Low Intensity</span>
                </div>
            </div>
            """
        else:
            # Predictive view: Show Velocity levels (colors match velocity)
            legend_html = """
            <div style="display: flex; gap: 24px; margin-top: 16px; font-size: 14px; flex-wrap: wrap;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 16px; height: 16px; background-color: #D62828; border-radius: 50%;"></div>
                    <span style="color: #D1D5DB;">High Velocity</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 16px; height: 16px; background-color: #FF6B35; border-radius: 50%;"></div>
                    <span style="color: #D1D5DB;">Medium Velocity</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 16px; height: 16px; background-color: #E20074; border-radius: 50%;"></div>
                    <span style="color: #D1D5DB;">Low Velocity</span>
                </div>
            </div>
            """
        st.markdown(legend_html, unsafe_allow_html=True)

    # Column 4: Competitive Vibe Check
    with col4:
        st.markdown('<h2 style="font-size: 24px; font-weight: bold; color: #FFFFFF; margin-bottom: 24px;">Competitive Vibe Check</h2>', unsafe_allow_html=True)
        
        # Competitive Bar Chart
        competitive_df = pd.DataFrame(MOCK_COMPETITIVE_DATA)
        
        # Determine T-Mobile color based on comparison with competitors
        tmobile_score = competitive_df[competitive_df['carrier'] == 'T-Mobile']['score'].values[0]
        att_score = competitive_df[competitive_df['carrier'] == 'AT&T']['score'].values[0]
        verizon_score = competitive_df[competitive_df['carrier'] == 'Verizon']['score'].values[0]
        
        # Green if T-Mobile is greater than both, red if less than both
        if tmobile_score > att_score and tmobile_score > verizon_score:
            tmobile_color = '#10B981'  # Green
        elif tmobile_score < att_score and tmobile_score < verizon_score:
            tmobile_color = '#EF4444'  # Red
        else:
            tmobile_color = '#E20074'  # Magenta (default, if in between)
        
        fig_competitive = px.bar(
            competitive_df,
            x='carrier',
            y='score',
            color='carrier',
            color_discrete_map={
                'T-Mobile': tmobile_color,
                'AT&T': '#6B7280',
                'Verizon': '#6B7280'
            }
        )
        
        fig_competitive.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#9CA3AF', size=12),
            margin=dict(l=20, r=30, t=20, b=20),
            height=300,
            xaxis=dict(
                title='',
                gridcolor='#404040',
                showgrid=False,
                tickfont=dict(size=12, color='#9CA3AF')
            ),
            yaxis=dict(
                title=dict(text='Score', font=dict(size=12, color='#9CA3AF')),
                gridcolor='#404040',
                showgrid=True,
                range=[75, 90],
                tickfont=dict(size=12, color='#9CA3AF')
            ),
            showlegend=False
        )
        
        fig_competitive.update_traces(
            marker=dict(line=dict(width=0)),
            hovertemplate='<b>%{x}</b><br>Score: %{y}<extra></extra>'
        )
        
        # Add status indicator text
        if tmobile_color == '#10B981':
            status_text = "✓ T-Mobile Leading"
            status_color = "#10B981"
        elif tmobile_color == '#EF4444':
            status_text = "⚠ T-Mobile Trailing"
            status_color = "#EF4444"
        else:
            status_text = "T-Mobile Competitive"
            status_color = "#E20074"
        
        status_html = f"""
        <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #404040;">
            <p style="font-size: 13px; font-weight: 600; color: {status_color}; margin-bottom: 8px;">
                {status_text}
            </p>
        </div>
        """
        
        st.plotly_chart(fig_competitive, use_container_width=True, config={'displayModeBar': False})
        
        # Status indicator
        st.markdown(status_html, unsafe_allow_html=True)
        
        # Competitor Weakness
        weakness_html = """
        <div style="margin-top: 8px;">
            <p style="font-size: 14px; color: #D1D5DB;">
                <span style="font-weight: 600; color: #FFFFFF;">Verizon Weakness:</span> Expensive Plans
            </p>
        </div>
        """
        st.markdown(weakness_html, unsafe_allow_html=True)

# ============================================================================
# NETWORK ENGINEERING PAGE
# ============================================================================
elif selected_page == "Network Engineering":
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown('<h2 style="font-size: 28px; font-weight: bold; color: #FFFFFF; margin-bottom: 20px;">Network Engineering Dashboard</h2>', unsafe_allow_html=True)
    
    # Network-specific metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Active Incidents", "12", "-2")
    with col2:
        st.metric("Network Uptime", "99.8%", "0.1%")
    with col3:
        st.metric("5G Coverage", "87.5%", "1.2%")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Filter action cards for Network Engineering
    network_cards = [card for card in MOCK_SUMMARY["action_cards"] if card["team"] == "Network Engineering"]
    
    if network_cards:
        st.markdown('<h3 style="font-size: 22px; font-weight: bold; color: #FFFFFF; margin-top: 30px; margin-bottom: 20px;">Network Engineering Actions</h3>', unsafe_allow_html=True)
        for card in network_cards:
            priority_color = "#D62828" if card["priority"] == "Critical" else "#FFC300"
            card_html = f"""
            <div class="action-card-container" style="border-left: 4px solid {priority_color}; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                    <span style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: {priority_color};">
                        {card["priority"]}
                    </span>
                    <span style="font-size: 12px; color: #9CA3AF;">{card["location"]}</span>
                </div>
                <h3 style="font-size: 20px; font-weight: bold; color: #FFFFFF; margin-bottom: 8px;">
                    {card["title"]}
                </h3>
                <div style="margin-bottom: 8px;">
                    <span style="font-size: 14px; color: #9CA3AF;">Team: </span>
                    <span style="font-size: 14px; color: #FFFFFF; font-weight: 600;">{card["team"]}</span>
                </div>
                <p style="font-size: 14px; color: #D1D5DB; margin-bottom: 16px;">
                    {card["insight"]}
                </p>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.info("No active actions for Network Engineering at this time.")

# ============================================================================
# SOCIAL MEDIA PAGE
# ============================================================================
elif selected_page == "Social Media":
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown('<h2 style="font-size: 28px; font-weight: bold; color: #FFFFFF; margin-bottom: 20px;">Social Media Dashboard</h2>', unsafe_allow_html=True)
    
    # Social media metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Mentions (24h)", "1,247", "23")
    with col2:
        st.metric("Sentiment Score", "72.5", "-5.2")
    with col3:
        st.metric("Engagement Rate", "4.8%", "0.3%")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Filter action cards for Social Media
    social_cards = [card for card in MOCK_SUMMARY["action_cards"] if card["team"] == "Social Media Support"]
    
    if social_cards:
        st.markdown('<h3 style="font-size: 22px; font-weight: bold; color: #FFFFFF; margin-top: 30px; margin-bottom: 20px;">Social Media Actions</h3>', unsafe_allow_html=True)
        for card in social_cards:
            priority_color = "#D62828" if card["priority"] == "Critical" else "#FFC300"
            card_html = f"""
            <div class="action-card-container" style="border-left: 4px solid {priority_color}; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                    <span style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: {priority_color};">
                        {card["priority"]}
                    </span>
                    <span style="font-size: 12px; color: #9CA3AF;">{card["location"]}</span>
                </div>
                <h3 style="font-size: 20px; font-weight: bold; color: #FFFFFF; margin-bottom: 8px;">
                    {card["title"]}
                </h3>
                <div style="margin-bottom: 8px;">
                    <span style="font-size: 14px; color: #9CA3AF;">Team: </span>
                    <span style="font-size: 14px; color: #FFFFFF; font-weight: 600;">{card["team"]}</span>
                </div>
                <p style="font-size: 14px; color: #D1D5DB; margin-bottom: 16px;">
                    {card["insight"]}
                </p>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.info("No active actions for Social Media at this time.")

# ============================================================================
# SALES PAGE
# ============================================================================
elif selected_page == "Sales":
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown('<h2 style="font-size: 28px; font-weight: bold; color: #FFFFFF; margin-bottom: 20px;">Sales Dashboard</h2>', unsafe_allow_html=True)
    
    # Sales metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Revenue (MTD)", "$2.4M", "$125K")
    with col2:
        st.metric("New Customers", "1,842", "47")
    with col3:
        st.metric("Conversion Rate", "34.2%", "2.1%")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Sales performance chart
    sales_data = pd.DataFrame({
        'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'Sales': [1250, 1320, 1180, 1450, 1390, 980, 1100]
    })
    
    fig_sales = px.line(
        sales_data,
        x='Day',
        y='Sales',
        markers=True,
        color_discrete_sequence=['#E20074']
    )
    fig_sales.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#9CA3AF', size=12),
        margin=dict(l=20, r=20, t=20, b=20),
        height=300,
        xaxis=dict(gridcolor='#404040', showgrid=True, tickfont=dict(size=12, color='#9CA3AF')),
        yaxis=dict(gridcolor='#404040', showgrid=True, tickfont=dict(size=12, color='#9CA3AF')),
        showlegend=False
    )
    st.plotly_chart(fig_sales, use_container_width=True, config={'displayModeBar': False})

