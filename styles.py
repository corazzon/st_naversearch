import streamlit as st

def apply_custom_styles(is_dark):
    if is_dark:
        bg_color, card_bg, text_color, accent_color, grid_color = "#0E1117", "#1A1C24", "#FFFFFF", "#00D4FF", "rgba(255, 255, 255, 0.1)"
    else:
        bg_color, card_bg, text_color, accent_color, grid_color = "#F8F9FA", "#FFFFFF", "#1F2937", "#3B82F6", "rgba(0, 0, 0, 0.05)"

    st.markdown(f"""
        <style>
        .main {{ background-color: {bg_color}; color: {text_color}; }}
        div[data-testid="stMetricValue"] {{ color: {accent_color}; font-weight: 700; }}
        </style>
    """, unsafe_allow_html=True)
    
    return {
        "text_color": text_color,
        "grid_color": grid_color,
        "plotly_template": "plotly_dark" if is_dark else "plotly_white"
    }

def update_chart_style(fig, style):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=style["text_color"]),
        xaxis=dict(gridcolor=style["grid_color"]),
        yaxis=dict(gridcolor=style["grid_color"]),
    )
    return fig
