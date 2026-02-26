import streamlit as st
import pandas as pd
import plotly.express as px
from utils import fetch_realtime_shopping, fetch_shopping_insight_trend, clean_html, convert_df, paginate
from styles import update_chart_style

def render_shopping_tab(keywords, selected_categories, style):
    if not keywords: return
    main_kw = st.selectbox("키워드 선택", keywords)
    df_shop, err = fetch_realtime_shopping([main_kw])
    if err: st.error(err)
    elif df_shop is not None:
        df_shop['lprice'] = pd.to_numeric(df_shop['lprice'], errors='coerce')
        df_shop['title'] = df_shop['title'].apply(clean_html)
        df_filtered = df_shop[df_shop['category1'].isin(selected_categories)] if selected_categories else df_shop
        df_filtered = df_filtered.dropna(subset=['lprice'])
        st.metric("상품 수", f"{len(df_filtered):,}개")
        fig = px.histogram(df_filtered, x='lprice', title="가격 분포", template=style["plotly_template"])
        st.plotly_chart(update_chart_style(fig, style), use_container_width=True)
        st.dataframe(df_filtered, use_container_width=True)

def render_shopping_insight_tab(keywords, start_date, end_date, style):
    st.header("📊 쇼핑인사이트")
    cat_id = "50000008" # 생활/건강
    df_ins, err, _ = fetch_shopping_insight_trend(cat_id, keywords, start_date, end_date)
    if not err and df_ins is not None:
        df_ins['period'] = pd.to_datetime(df_ins['period'])
        fig = px.line(df_ins, x='period', y='ratio', color='keyword', title="클릭 트렌드", template=style["plotly_template"])
        st.plotly_chart(update_chart_style(fig, style), use_container_width=True)
