import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import base64

# Page Configuration
st.set_page_config(
    page_title="T-Mobile Vibe Check Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Mock Data Definitions
MOCK_SUMMARY = {
    "chi_score": 85.2,
    "chi_trend": -1.5,
    "trend_direction": "down",
    "trend_period": "Last Hour",
    "action_cards": [
        {"id": "A101", "team": "Network Engineering", "priority": "Critical", "title": "Investigate 5G outage in Miami", "insight": "40% spike in 'slow data' complaints in zip 33139 over 1hr.", "color": "#D62828"},
        {"id": "A102", "team": "Social Media Support", "priority": "High", "title": "Draft response to #SlowMagenta trend", "insight": "Sentiment velocity shows high risk of negative virality in 2 hours.", "color": "#FFC300"}
    ]
}

MOCK_COMPETITIVE_DATA = [
    {"carrier": "T-Mobile (85.2)", "score": 85.2},
    {"carrier": "AT&T (87.7)", "score": 87.7},
    {"carrier": "Verizon (81.2)", "score": 81.2},
]

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

# Generate Trend Data for 24-hour chart
def generate_trend_data():
    hours = pd.date_range(end=datetime.now(), periods=24, freq='H')
    # Generate realistic trend data with some variance
    base_score = 85.2
    trend_values = []
    for i in range(24):
        # Add some realistic variation
        value = base_score + np.sin(i * np.pi / 12) * 3 + np.random.normal(0, 0.5)
        trend_values.append(max(70, min(95, value)))  # Keep within reasonable bounds
    return pd.DataFrame({"time": hours, "score": trend_values})

# Function to encode image to base64 for HTML embedding
def get_image_base64(image_path):
    """Convert image file to base64 string for HTML embedding."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        return None

# Custom CSS Styling
st.markdown("""
    <style>
        /* Global Styles */
        .main {
            background-color: #000000;
            color: white;
        }
        
        .stApp {
            background-color: #000000;
        }
        
        /* Sidebar Styling */
        .css-1d391kg {
            background-color: #000000;
        }
        
        [data-testid="stSidebar"] {
            background-color: #000000;
            border-right: 2px solid #555555 !important;
            min-width: 21rem !important;
            max-width: 21rem !important;
            resize: none !important;
        }
        
        [data-testid="stSidebar"] .css-1d391kg {
            background-color: #2C2C2C;
        }
        
        /* Disable sidebar resize handle */
        [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
            width: 21rem !important;
        }
        
        /* Hide the resize handle/divider */
        [data-testid="stSidebar"] > div:nth-child(2) {
            display: none !important;
        }
        
        /* Alternative: Hide resize handle if it exists */
        .resizable-handle,
        [data-testid="stSidebar"] .resizable-handle,
        [data-testid="stSidebar"] .sidebar-resize-handle {
            display: none !important;
            pointer-events: none !important;
        }
        
        /* Main content area - remove border-left since sidebar has border-right */
        .main .block-container {
            padding-left: 2rem;
        }
        
        /* Ensure sidebar width is fixed */
        section[data-testid="stSidebar"] {
            width: 21rem !important;
            min-width: 21rem !important;
            max-width: 21rem !important;
            position: relative;
        }
        
        /* Ensure border is visible and on top */
        [data-testid="stSidebar"]::after {
            content: "";
            position: absolute;
            right: 0;
            top: 0;
            bottom: 0;
            width: 0.5px;
            background-color: #555555;
            z-index: 1000;
        }
        
        /* Disable resize cursor on sidebar edge */
        [data-testid="stSidebar"]:hover {
            cursor: default !important;
        }
        
        /* Prevent mouse events on sidebar edge for resizing */
        [data-testid="stSidebar"] {
            touch-action: none;
        }
        
        /* Allow text selection in sidebar content but prevent resize */
        [data-testid="stSidebar"] .nav-link,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            user-select: text;
            -webkit-user-select: text;
        }
        
        /* Hide Streamlit's resize handle completely */
        [data-testid="stSidebar"] button[title*="resize"],
        [data-testid="stSidebar"] button[aria-label*="resize"],
        button[data-testid*="resize"] {
            display: none !important;
        }
        
        /* Card Styling */
        .vibe-card {
            background-color: #2C2C2C;
            border-radius: 12px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            border-left: 4px solid #E20074;
        }
        
        .action-card {
            background-color: #2C2C2C;
            border-radius: 12px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            border-left: 4px solid;
        }
        
        .insight-card {
            background-color: #2C2C2C;
            border-radius: 12px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        
        /* Vibe Score Styling */
        .vibe-score {
            font-size: 48px;
            font-weight: bold;
            color: #E20074;
            margin: 10px 0;
        }
        
        .trend-indicator {
            font-size: 16px;
            margin: 10px 0;
        }
        
        /* Text Colors */
        .main .block-container {
            color: white;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: white;
        }
        
        /* Button Styling */
        .stButton > button {
            background-color: #E20074;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 0.5rem 1rem;
            font-weight: 600;
        }
        
        .stButton > button:hover {
            background-color: #C1005F;
        }
        
        /* Sidebar Navigation */
        .nav-link {
            padding: 10px 15px;
            margin: 5px 0;
            border-radius: 6px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        
        .nav-link.active {
            background-color: #E20074;
            color: white;
        }
        
        .nav-link:hover {
            background-color: #3C3C3C;
        }
        
        /* Priority Colors */
        .priority-critical {
            color: #D62828;
            font-weight: bold;
        }
        
        .priority-high {
            color: #FFC300;
            font-weight: bold;
        }
        
        /* Heatmap Styling */
        .heatmap-container {
            background-color: #2C2C2C;
            border-radius: 12px;
            padding: 20px;
        }
        
        .heatspot {
            fill: #E20074;
            opacity: 0.7;
        }
        
        .heatspot.critical {
            fill: #D62828;
        }
        
        /* Bar Chart Container Styling */
        .bar-chart-container {
            background-color: #2C2C2C;
            border-radius: 12px;
            padding: 10px;
            overflow: hidden;
        }
        
        /* Round corners on plotly chart containers */
        [data-testid="stPlotlyChart"] {
            border-radius: 12px;
            overflow: hidden;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    # T-Mobile Logo - Look for image file (at the very top)
    logo_paths = [
        "tmobile_logo_black.png",
    ]
    
    logo_found = None
    for logo_path in logo_paths:
        if os.path.exists(logo_path):
            logo_found = logo_path
            break
    
    # Display logo at the very top
    if logo_found:
        # Convert image to base64 for HTML embedding (prevents zoom)
        img_base64 = get_image_base64(logo_found)
        if img_base64:
            # Get file extension to determine image type
            ext = os.path.splitext(logo_found)[1].lower()
            img_type = "png" if ext == ".png" else "jpeg" if ext in [".jpg", ".jpeg"] else "png"
            
            # Display logo as HTML img tag (not zoomable - HTML img tags don't trigger Streamlit's zoom modal)
            logo_html = f"""
            <div style="background-color: #000000; padding: 8px; border-radius: 8px; margin-bottom: 10px; margin-top: -35px; overflow: hidden;">
                <img src="data:image/{img_type};base64,{img_base64}" 
                     style="max-width: 100%; height: auto; display: block; user-select: none; -webkit-user-select: none; transform: scale(1.2); transform-origin: center top;" 
                     alt="T-Mobile Logo"
                     draggable="false">
            </div>
            """
            st.markdown(logo_html, unsafe_allow_html=True)
        else:
            # Fallback to st.image if base64 conversion fails
            st.markdown('<div style="background-color: #000000; padding: 8px; border-radius: 8px; margin-bottom: 10px; margin-top: -50px; overflow: hidden;">', unsafe_allow_html=True)
            st.image(logo_found, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="margin-top: -20px;"></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation Links
    st.markdown("""
        <div style="padding: 10px 0;">
            <div class="nav-link active" style="background-color: #E20074; color: white; padding: 12px 15px; border-radius: 6px; margin: 8px 0; font-size: 16px; font-weight: 600;">
                Home Page
            </div>
            <div class="nav-link" style="padding: 12px 15px; border-radius: 6px; margin: 8px 0; font-size: 16px; font-weight: 500;">
                🔧 Network Engineering
            </div>
            <div class="nav-link" style="padding: 12px 15px; border-radius: 6px; margin: 8px 0; font-size: 16px; font-weight: 500;">
                💬 Social Media
            </div>
            <div class="nav-link" style="padding: 12px 15px; border-radius: 6px; margin: 8px 0; font-size: 16px; font-weight: 500;">
                📈 Sales
            </div>
        </div>
    """, unsafe_allow_html=True)

# Main Content
st.title("T-Mobile Vibe Check Dashboard")

# Row 1: Critical Metrics
col1, col2 = st.columns([1, 2])

with col1:
    # Circular progress indicator using HTML/CSS
    score = MOCK_SUMMARY["chi_score"]
    percentage = score / 100.0
    radius = 100  # Increased from 88
    circumference = 2 * 3.14159 * radius
    dash_offset = circumference * (1 - percentage)
    circle_size = 240  # Increased from 200
    
    # SVG Circular Progress
    svg_circle = f"""
    <div style="position: relative; width: {circle_size}px; height: {circle_size}px; margin: 0 auto;">
        <svg width="{circle_size}" height="{circle_size}" style="transform: rotate(-90deg);">
            <circle cx="{circle_size/2}" cy="{circle_size/2}" r="{radius}" stroke="#404040" stroke-width="16" fill="none"/>
            <circle cx="{circle_size/2}" cy="{circle_size/2}" r="{radius}" stroke="#E20074" stroke-width="16" fill="none"
                    stroke-dasharray="{circumference}"
                    stroke-dashoffset="{dash_offset}"
                    stroke-linecap="round"/>
        </svg>
        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; width: 100%;">
            <div style="font-size: 64px; font-weight: bold; color: #FFFFFF;">{score}</div>
            <div style="font-size: 16px; color: #9CA3AF; margin-top: 4px;">CHI Score</div>
        </div>
    </div>
    """
    st.markdown(svg_circle, unsafe_allow_html=True)
    
    # Trend Indicator
    trend_value = abs(MOCK_SUMMARY["chi_trend"])
    trend_period = MOCK_SUMMARY["trend_period"]
    trend_html = f"""
    <div style="display: flex; align-items: center; justify-content: center; gap: 8px; margin: 16px 0; color: #D62828; font-weight: 600;">
        <span style="font-size: 20px;">↓</span>
        <span>{trend_value} vs {trend_period}</span>
    </div>
    """
    st.markdown(trend_html, unsafe_allow_html=True)
    
    # Mini 24-hour trend chart
    trend_df = generate_trend_data()
    fig_trend = px.line(
        trend_df,
        x="time",
        y="score",
        title="",
        labels={"time": "", "score": "Score"},
        color_discrete_sequence=["#E20074"]
    )
    fig_trend.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#9CA3AF', size=10),
        margin=dict(l=0, r=0, t=0, b=0),
        height=200,  # Increased from 120
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

with col2:
    # Action Cards
    for action in MOCK_SUMMARY["action_cards"]:
        priority_class = "priority-critical" if action["priority"] == "Critical" else "priority-high"
        st.markdown(f"""
            <div class="action-card" style="border-left-color: {action['color']}; padding: 12px; margin: 8px 0;">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <div style="color: {action['color']}; font-weight: bold; font-size: 12px; text-transform: uppercase; margin-bottom: 8px;">
                            {action['priority']} • {action['team']}
                        </div>
                        <h4 style="color: white; margin: 8px 0;">{action['title']}</h4>
                        <p style="color: #CCCCCC; font-size: 14px; margin: 8px 0;">{action['insight']}</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# Row 2: Insights
col3, col4 = st.columns([1, 1])

with col3:
    # Predictive Issue Heatmap
    st.markdown("""
        <div class="insight-card">
            <h3 style="color: white; margin-top: 0; text-align: center;">Predictive Issue Heat Map</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Map view toggle
    map_view = st.radio(
        " ",
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

with col4:
    # Competitive Vibe Check
    st.markdown("""
        <div class="insight-card">
            <h3 style="color: white; margin-top: 0; text-align: center;">Competitive Vibe Check</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Add spacing between heading and chart
    st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
    
    # Competitive Bar Chart
    competitive_df = pd.DataFrame(MOCK_COMPETITIVE_DATA)
    
    # Create colors list - magenta for T-Mobile, gray for others
    colors = []
    for carrier in competitive_df['carrier']:
        if 'T-Mobile' in carrier:
            colors.append('#E20074')
        else:
            colors.append('#666666')
    
    fig_competitive = px.bar(
        competitive_df,
        x='carrier',
        y='score',
        labels={'carrier': 'Carrier', 'score': 'Vibe Score'},
        color='carrier',
        color_discrete_map={
            'T-Mobile (85.2)': '#E20074',
            'AT&T (87.7)': '#666666',
            'Verizon (81.2)': '#666666'
        }
    )
    
    fig_competitive.update_layout(
        plot_bgcolor="#2C2C2C",
        paper_bgcolor="#2C2C2C",
        font_color="white",
        height=300,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(showgrid=False, showline=False),
        yaxis=dict(showgrid=False, showline=False, range=[75, 90]),
        showlegend=False
    )
    
    fig_competitive.update_traces(marker_line_width=0)
    st.plotly_chart(fig_competitive, use_container_width=True, config={"displayModeBar": False})
    
    # Insight Text
    st.markdown("""
        <div style="background-color: #2C2C2C; border-radius: 8px; padding: 15px; margin-top: 10px;">
            <p style="color: #CCCCCC; font-size: 14px; margin: 0;">
                <strong style="color: #E20074;">Insight:</strong> Verizon Weakness: Expensive Plans
            </p>
        </div>
    """, unsafe_allow_html=True)

