import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# --- 페이지 설정 ---
st.set_page_config(
    page_title="Naver API 실시간 데이터 대시보드",
    page_icon="⚡",
    layout="wide"
)

# --- CSS 스타일링 (세련된 다크/화이트 모음) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 4px solid #00c853; }
    h1, h2, h3 { color: #1a237e; font-weight: 800; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        height: 50px; 
        background-color: #e8eaf6; 
        border-radius: 8px 8px 0 0; 
        padding: 0 25px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] { background-color: #ffffff; border-top: 4px solid #3f51b5; color: #3f51b5; }
    div[data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #dee2e6; }
    </style>
""", unsafe_allow_html=True)

# --- 인증 및 경로 설정 ---
def get_api_keys():
    """네이버 API 키를 가져옵니다. (Cloud Secrets 및 로컬 .env 지원)"""
    try:
        if 'NAVER_CLIENT_ID' in st.secrets:
            return st.secrets['NAVER_CLIENT_ID'], st.secrets['NAVER_CLIENT_SECRET']
    except Exception:
        pass
    
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
    return os.getenv('NAVER_CLIENT_ID'), os.getenv('NAVER_CLIENT_SECRET')

CLIENT_ID, CLIENT_SECRET = get_api_keys()
HEADERS = {"X-Naver-Client-Id": CLIENT_ID, "X-Naver-Client-Secret": CLIENT_SECRET, "Content-Type": "application/json"}

# --- 실시간 API 호출 함수 ---
@st.cache_data(ttl=600)  # 10분 캐싱
def fetch_realtime_trend(keywords):
    """네이버 검색어 트렌드 API 호출"""
    if not CLIENT_ID: return None, "API Key 미설정"
    url = "https://openapi.naver.com/v1/datalab/search"
    body = {
        "startDate": "2025-01-01", "endDate": datetime.now().strftime("%Y-%m-%d"),
        "timeUnit": "date",
        "keywordGroups": [{"groupName": k, "keywords": [k]} for k in keywords]
    }
    res = requests.post(url, headers=HEADERS, data=json.dumps(body))
    if res.status_code == 200:
        dfs = [pd.DataFrame(r['data']).assign(keyword=r['title']) for r in res.json()['results']]
        return pd.concat(dfs), None
    return None, f"Trend API Error: {res.status_code}"

@st.cache_data(ttl=600)
def fetch_realtime_shopping(keyword):
    """네이버 쇼핑 검색 API 호출"""
    if not CLIENT_ID: return None, "API Key 미설정"
    url = f"https://openapi.naver.com/v1/search/shop.json?query={keyword}&display=100"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        return pd.DataFrame(res.json()['items']), None
    return None, f"Shopping API Error: {res.status_code}"

@st.cache_data(ttl=600)
def fetch_realtime_blog(keyword):
    """네이버 블로그 검색 API 호출"""
    if not CLIENT_ID: return None, "API Key 미설정"
    url = f"https://openapi.naver.com/v1/search/blog.json?query={keyword}&display=100"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        return pd.DataFrame(res.json()['items']), None
    return None, f"Blog API Error: {res.status_code}"

# --- 메인 UI ---
st.title("⚡ 실시간 Naver Market Insights")
st.caption("로컬 파일이 아닌, 네이버 API를 통해 실시간 데이터를 직접 분석합니다.")

# 사이드바
st.sidebar.header("🔍 실시간 분석 설정")
target_kws = st.sidebar.text_input("분석 키워드 (쉼표 구분)", "오메가3, 비타민D, 유산균")
keywords = [k.strip() for k in target_kws.split(',')]
main_kw = keywords[0] if keywords else "오메가3"
st.sidebar.divider()
st.sidebar.success(f"현재 주 분석 키워드: **{main_kw}**")
st.sidebar.caption("💡 10분마다 데이터가 최신화됩니다.")

tab1, tab2, tab3 = st.tabs(["📈 트렌드 비교", "�️ 실시간 쇼핑", "📝 실시간 블로그"])

# Tab 1: 트렌드 비교
with tab1:
    st.header("실시간 검색어 활동 트렌드 (2025~)")
    df_trend, err = fetch_realtime_trend(keywords)
    if err:
        st.error(err)
    elif df_trend is not None:
        df_trend['period'] = pd.to_datetime(df_trend['period'])
        
        # 그래프 1: 트렌드 라인 차트
        fig1 = px.line(df_trend, x='period', y='ratio', color='keyword', 
                       title="실시간 검색 트렌드 추이",
                       template="plotly_white", color_discrete_sequence=px.colors.qualitative.Prism)
        fig1.update_layout(hovermode="x unified")
        st.plotly_chart(fig1, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            # 그래프 2: 평균 검색량 바 차트
            avg_df = df_trend.groupby('keyword')['ratio'].mean().reset_index().sort_values('ratio', ascending=False)
            fig2 = px.bar(avg_df, x='keyword', y='ratio', color='keyword', 
                          title="평균 검색 활동 점유율", text_auto='.1f',
                          color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig2, use_container_width=True)
        with col2:
            # 표 1: 요약 통계
            st.subheader("� 데이터 요약 (상대 지표)")
            summary = df_trend.groupby('keyword')['ratio'].agg(['mean', 'max', 'std']).round(2)
            summary.columns = ['평균', '최대치', '변동성']
            st.dataframe(summary, use_container_width=True)

# Tab 2: 실시간 쇼핑
with tab2:
    st.header(f"🛍️ '{main_kw}' 실시간 마켓 현황")
    df_shop, shop_err = fetch_realtime_shopping(main_kw)
    if shop_err:
        st.error(shop_err)
    elif df_shop is not None:
        # 데이터 전처리
        df_shop['lprice'] = pd.to_numeric(df_shop['lprice'], errors='coerce')
        df_shop['title'] = df_shop['title'].str.replace('<b>', '', regex=False).str.replace('</b>', '', regex=False)
        
        # KPI 섹션
        m1, m2, m3 = st.columns(3)
        m1.metric("실시간 수집 상품", f"{len(df_shop)}개")
        m2.metric("시장 평균가", f"{int(df_shop['lprice'].mean()):,}원")
        m3.metric("활성 판매처", f"{df_shop['mallName'].nunique()}개")
        
        col3, col4 = st.columns([2, 1])
        with col3:
            # 그래프 3: 가격 분포 히스토그램
            fig3 = px.histogram(df_shop, x='lprice', nbins=30, 
                                title=f"'{main_kw}' 최저가 분포 (현재)",
                                labels={'lprice': '최저가(원)', 'count': '상품 수'},
                                color_discrete_sequence=['#43a047'], template="simple_white")
            st.plotly_chart(fig3, use_container_width=True)
        with col4:
            # 그래프 4: 몰별 비중 파이 차트
            mall_counts = df_shop['mallName'].value_counts().head(10)
            fig4 = px.pie(values=mall_counts.values, names=mall_counts.index, 
                          title="주요 판매 쇼핑몰 (Top 10)", hole=0.4,
                          color_discrete_sequence=px.colors.sequential.Greens_r)
            st.plotly_chart(fig4, use_container_width=True)
            
        st.divider()
        st.subheader("🛒 실시간 상위 노출 상품 리스트")
        st.dataframe(df_shop[['title', 'lprice', 'mallName', 'category1', 'link']].head(50), 
                     use_container_width=True)
        
        st.subheader("� 카테고리별 마켓 요약")
        cat_agg = df_shop.groupby('category1')['lprice'].agg(['count', 'mean', 'max']).round(0)
        cat_agg.columns = ['상품 수', '평균가', '최고가']
        st.table(cat_agg)

# Tab 3: 실시간 블로그
with tab3:
    st.header(f"📝 '{main_kw}' 실시간 블로그 반응")
    df_blog, blog_err = fetch_realtime_blog(main_kw)
    if blog_err:
        st.error(blog_err)
    elif df_blog is not None:
        # 데이터 전처리
        df_blog['title'] = df_blog['title'].str.replace('<b>', '', regex=False).str.replace('</b>', '', regex=False)
        df_blog['postdate'] = pd.to_datetime(df_blog['postdate'], format='%Y%m%d', errors='coerce')
        
        # 그래프 5: 일별 블로그 생성량 (Bar)
        blog_daily = df_blog.groupby('postdate').size().reset_index(name='content_count')
        fig5 = px.bar(blog_daily, x='postdate', y='content_count', 
                      title="최근 일별 게시물 분포",
                      labels={'postdate': '작성일', 'content_count': '게시물 수'},
                      color_discrete_sequence=['#ff8f00'])
        st.plotly_chart(fig5, use_container_width=True)
        
        st.divider()
        st.subheader("� 최신 블로그 콘텐츠 리스트")
        st.dataframe(df_blog[['title', 'bloggername', 'postdate', 'link']].sort_values('postdate', ascending=False).head(50), 
                     use_container_width=True)
        
        st.subheader("👤 활발한 정보 공유 블로거 TOP 10")
        blogger_top = df_blog['bloggername'].value_counts().head(10).reset_index()
        blogger_top.columns = ['블로거명', '포스팅 수']
        st.table(blogger_top)

st.sidebar.caption(f"최종 업데이트: {datetime.now().strftime('%H:%M:%S')}")
