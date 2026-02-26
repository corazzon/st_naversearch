import streamlit as st
import pandas as pd
from utils import fetch_realtime_blog, fetch_realtime_cafe, fetch_realtime_news, clean_html, generate_wordcloud, paginate, convert_df
from styles import update_chart_style

def render_content_tabs(keywords, style, active_tab):
    if active_tab == "blog": df, err = fetch_realtime_blog(keywords)
    elif active_tab == "cafe": df, err = fetch_realtime_cafe(keywords)
    else: df, err = fetch_realtime_news(keywords)
    if not err and df is not None:
        df['title'] = df['title'].apply(clean_html)
        st.metric(f"{active_tab.upper()} 문서", f"{len(df):,}건")
        all_titles = " ".join(df['title'].dropna().tolist())
        wc = generate_wordcloud(all_titles)
        if wc: st.image(wc.to_array())
        paged = paginate(df, 20, f"{active_tab}_list")
        if paged is not None: st.dataframe(paged, use_container_width=True)
