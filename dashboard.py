import streamlit as st
import os
from datetime import datetime, timedelta
from styles import apply_custom_styles
from tabs_trend import render_trend_tab
from tabs_shopping import render_shopping_tab, render_shopping_insight_tab
from tabs_content import render_content_tabs
from tabs_report import render_report_tab

st.set_page_config(page_title="Naver Market Insights", layout="wide", page_icon="⚡")

st.sidebar.header("🎨 테마 설정")
is_dark = st.sidebar.toggle("다크 모드", value=False)
style = apply_custom_styles(is_dark)

st.sidebar.header("🔍 실시간 분석 설정")
target_kws = st.sidebar.text_input("분석 키워드 (쉼표 구분)", "오메가3, 비타민D, 유산균")
keywords = [k.strip() for k in target_kws.split(',') if k.strip()]

st.sidebar.divider()
st.sidebar.subheader("📅 분석 기간 설정")
today = datetime.now()
one_year_ago = today - timedelta(days=365)
date_range = st.sidebar.date_input("조회 기간 선택", value=(one_year_ago, today), max_value=today)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range[0].strftime("%Y-%m-%d"), date_range[1].strftime("%Y-%m-%d")
else:
    start_date, end_date = one_year_ago.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")

st.sidebar.divider()
st.sidebar.subheader("🏷️ 쇼핑 카테고리 필터")
DEFAULT_CATEGORIES = ["식품", "건강/의료용품", "화장품/미용", "생활/건강", "패션의류", "패션잡화", "스포츠/레저", "디지털/가전"]
selected_categories = st.sidebar.multiselect("분석할 카테고리 선택", options=DEFAULT_CATEGORIES, default=[])

st.title("⚡ 실시간 Naver Market Insights")
st.caption("네이버 API를 통해 실시간 데이터를 직접 분석합니다.")

tabs = st.tabs(["📈 트렌드 비교", "🛍️ 실시간 쇼핑", "📝 블로그", "☕ 카페", "📰 뉴스", "📊 쇼핑인사이트", "📑 종합 리포트"])

with tabs[0]: render_trend_tab(keywords, start_date, end_date, style)
with tabs[1]: render_shopping_tab(keywords, selected_categories, style)
with tabs[2]: render_content_tabs(keywords, style, "blog")
with tabs[3]: render_content_tabs(keywords, style, "cafe")
with tabs[4]: render_content_tabs(keywords, style, "news")
with tabs[5]: render_shopping_insight_tab(keywords, start_date, end_date, style)
with tabs[6]: render_report_tab(keywords, start_date, end_date, style)

st.sidebar.divider()
st.sidebar.caption(f"최종 업데이트: {datetime.now().strftime('%H:%M:%S')}")
st.sidebar.caption("[© 오늘코드](https://www.youtube.com/todaycode)")
