import streamlit as st
import pandas as pd
import plotly.express as px
from utils import fetch_realtime_trend
from styles import update_chart_style

def render_trend_tab(keywords, start_date, end_date, style):
    st.header(f"📈 실시간 검색어 트렌드 ({start_date} ~ {end_date})")
    with st.expander("📊 분석 설정", expanded=True):
        col_mode, col_gender = st.columns(2)
        with col_mode: analysis_mode = st.radio("분석 모드", ["일반 트렌드", "성별 비교"])
        with col_gender:
            selected_gender = ""
            if analysis_mode != "성별 비교":
                gender_option = st.radio("성별", ["전체", "남성", "여성"], horizontal=True)
                selected_gender = {"전체": "", "남성": "m", "여성": "f"}[gender_option]
        age_options = ["0~12세", "13~18세", "19~24세", "25~29세", "30~34세", "35~39세", "40~44세", "45~49세", "50~54세", "55~59세", "60세 이상"]
        selected_ages = st.multiselect("연령대", age_options)
        selected_age_codes = [str(age_options.index(a) + 1) for a in selected_ages] if selected_ages else []

    df_trend, err = None, None
    if analysis_mode == "일반 트렌드":
        df_trend, err = fetch_realtime_trend(keywords, start_date, end_date, selected_gender, selected_age_codes)
    else:
        df_m, _ = fetch_realtime_trend(keywords, start_date, end_date, "m", selected_age_codes)
        df_f, _ = fetch_realtime_trend(keywords, start_date, end_date, "f", selected_age_codes)
        dfs = []
        if df_m is not None: dfs.append(df_m.assign(gender='남성'))
        if df_f is not None: dfs.append(df_f.assign(gender='여성'))
        df_trend = pd.concat(dfs) if dfs else None

    if err: st.error(err)
    elif df_trend is not None:
        df_trend['period'] = pd.to_datetime(df_trend['period'])
        fig = px.line(df_trend, x='period', y='ratio', color='keyword', 
                     facet_col='gender' if analysis_mode == "성별 비교" else None,
                     template=style["plotly_template"])
        st.plotly_chart(update_chart_style(fig, style), use_container_width=True)
