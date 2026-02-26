import streamlit as st
import pandas as pd
import plotly.express as px
from utils import fetch_realtime_trend, fetch_realtime_shopping, fetch_realtime_blog, fetch_realtime_cafe, fetch_realtime_news
from styles import update_chart_style
from datetime import datetime

def render_report_tab(keywords, start_date, end_date, style):
    st.header("📑 종합 리포트")
    trend_df, _ = fetch_realtime_trend(keywords, start_date, end_date)
    shop_df, _ = fetch_realtime_shopping(keywords)
    blog_df, _ = fetch_realtime_blog(keywords)
    total_buzz = sum(len(x) for x in [blog_df] if x is not None)
    st.metric("총 버즈량", f"{total_buzz:,}건")
    report_text = f"마켓 인사이트 리포트 ({datetime.now().strftime('%Y-%m-%d')})\n키워드: {', '.join(keywords)}"
    st.markdown(f"```\n{report_text}\n```")
    st.download_button("📥 리포트 다운로드", report_text, "report.txt")
