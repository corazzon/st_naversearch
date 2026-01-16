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
    cid, csec = None, None
    
    # 1. Streamlit Secrets (Cloud 배포시)
    try:
        if 'NAVER_CLIENT_ID' in st.secrets:
            cid = st.secrets['NAVER_CLIENT_ID']
            csec = st.secrets['NAVER_CLIENT_SECRET']
    except Exception:
        pass
    
    # 2. 로컬 .env 파일
    if not cid or not csec:
        # 현재 파일의 디렉토리에 있는 .env 파일을 로드
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            # override=True를 설정하여 .env 파일 변경 시 서버 재시작 없이 반영되도록 함
            load_dotenv(env_path, override=True)
            cid = os.getenv('NAVER_CLIENT_ID')
            csec = os.getenv('NAVER_CLIENT_SECRET')

    # 공백 및 따옴표 제거 (사용자 입력 실수 방지)
    if cid: cid = str(cid).strip().strip("'").strip('"')
    if csec: csec = str(csec).strip().strip("'").strip('"')
    
    return cid, csec

CLIENT_ID, CLIENT_SECRET = get_api_keys()
HEADERS = {"X-Naver-Client-Id": CLIENT_ID, "X-Naver-Client-Secret": CLIENT_SECRET, "Content-Type": "application/json"}

# --- 실시간 API 호출 함수 ---
@st.cache_data(ttl=600)  # 10분 캐싱
def fetch_realtime_trend(keywords):
    """네이버 검색어 트렌드 API 호출"""
    if not CLIENT_ID or not CLIENT_SECRET: return None, "인증 키가 설정되지 않았습니다."
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
    return None, f"Trend API Error: {res.status_code} (인증 오류 가능성)" if res.status_code == 401 else f"Trend API Error: {res.status_code}"

@st.cache_data(ttl=600)
def fetch_realtime_shopping(keyword):
    """네이버 쇼핑 검색 API 호출"""
    if not CLIENT_ID or not CLIENT_SECRET: return None, "인증 키 미설정"
    url = f"https://openapi.naver.com/v1/search/shop.json?query={keyword}&display=100"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        return pd.DataFrame(res.json()['items']), None
    return None, f"Shopping API Error: {res.status_code}"

@st.cache_data(ttl=600)
def fetch_realtime_blog(keyword):
    """네이버 블로그 검색 API 호출"""
    if not CLIENT_ID or not CLIENT_SECRET: return None, "인증 키 미설정"
    url = f"https://openapi.naver.com/v1/search/blog.json?query={keyword}&display=100"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        return pd.DataFrame(res.json()['items']), None
    return None, f"Blog API Error: {res.status_code}"

@st.cache_data(ttl=600)
def fetch_realtime_cafe(keyword):
    """네이버 카페 검색 API 호출"""
    if not CLIENT_ID or not CLIENT_SECRET: return None, "인증 키 미설정"
    url = f"https://openapi.naver.com/v1/search/cafearticle.json?query={keyword}&display=100"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        return pd.DataFrame(res.json()['items']), None
    return None, f"Cafe API Error: {res.status_code}"

@st.cache_data(ttl=600)
def fetch_realtime_news(keyword):
    """네이버 뉴스 검색 API 호출"""
    if not CLIENT_ID or not CLIENT_SECRET: return None, "인증 키 미설정"
    url = f"https://openapi.naver.com/v1/search/news.json?query={keyword}&display=100"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        return pd.DataFrame(res.json()['items']), None
    return None, f"News API Error: {res.status_code}"

# --- 데이터 전처리 헬퍼 ---
def clean_html(text):
    """HTML 태그 제거"""
    if pd.isna(text): return ""
    return text.replace('<b>', '').replace('</b>', '').replace('&quot;', '"').replace('&lt;', '<').replace('&gt;', '>')

# --- 메인 UI ---
st.title("⚡ 실시간 Naver Market Insights")
st.caption("로컬 파일이 아닌, 네이버 API를 통해 실시간 데이터를 직접 분석합니다.")

# 사이드바
st.sidebar.header("🔍 실시간 분석 설정")

# API 인증 상태 진단 (오류 시에만 상단 노출)
if not CLIENT_ID or not CLIENT_SECRET:
    st.sidebar.error("❌ API 인증 키를 로드할 수 없습니다.")
    st.sidebar.markdown("""
        **해결 가이드:**
        1. `naverapieda/.env` 파일 생성 확인
        2. 파일 내용:
           ```text
           NAVER_CLIENT_ID=고객아이디
           NAVER_CLIENT_SECRET=비밀키
           ```
        3. 공백이나 따옴표 없이 입력 권장
    """)

target_kws = st.sidebar.text_input("분석 키워드 (쉼표 구분)", "오메가3, 비타민D, 유산균")
keywords = [k.strip() for k in target_kws.split(',')]
main_kw = keywords[0] if keywords else "오메가3"
st.sidebar.divider()
st.sidebar.success(f"현재 주 분석 키워드: **{main_kw}**")

# 카테고리 선택 기능
st.sidebar.subheader("🏷️ 쇼핑 카테고리 필터")
DEFAULT_CATEGORIES = [
    "식품", "건강/의료용품", "화장품/미용", "생활/건강",
    "패션의류", "패션잡화", "스포츠/레저", "생활/가전",
    "가구/인테리어", "디지털/가전", "출산/육아", "반려동물용품",
    "도서/음반/DVD", "완구/취미", "문구/오피스", "차량/오토바이"
]
selected_categories = st.sidebar.multiselect(
    "분석할 카테고리 선택 (전체 또는 일부)",
    options=DEFAULT_CATEGORIES,
    default=[],
    help="선택하지 않으면 모든 카테고리를 분석합니다"
)
st.sidebar.caption("💡 10분마다 데이터가 최신화됩니다.")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 트렌드 비교", "🛍️ 실시간 쇼핑", "📝 실시간 블로그", "☕ 실시간 카페", "📰 실시간 뉴스"])

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
    st.header(f"🛍️ '{main_kw}' 실시간 마켓 심층 분석")
    st.caption("카테고리 필터링, 가격 분석, 브랜드 인사이트, 판매처 비교 등 종합적인 쇼핑 데이터 분석")
    df_shop, shop_err = fetch_realtime_shopping(main_kw)
    if shop_err:
        st.error(shop_err)
    elif df_shop is not None:
        # 데이터 전처리
        df_shop['lprice'] = pd.to_numeric(df_shop['lprice'], errors='coerce')
        df_shop['title'] = df_shop['title'].apply(clean_html)

        # 카테고리 필터링 적용
        df_filtered = df_shop.copy()
        if selected_categories:
            df_filtered = df_shop[df_shop['category1'].isin(selected_categories)]
            if len(df_filtered) == 0:
                st.warning(f"선택한 카테고리에 해당하는 상품이 없습니다. 전체 데이터를 표시합니다.")
                df_filtered = df_shop.copy()
            else:
                st.info(f"선택한 카테고리: {', '.join(selected_categories)} (총 {len(df_filtered)}개 상품)")

        df_filtered = df_filtered.dropna(subset=['lprice'])  # 가격 없는 상품 제거

        # === 섹션 1: 향상된 KPI ===
        st.divider()
        st.markdown("### 📊 핵심 지표")
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("수집 상품 수", f"{len(df_filtered):,}개")
        m2.metric("평균 가격", f"{int(df_filtered['lprice'].mean()):,}원")
        m3.metric("중앙값 가격", f"{int(df_filtered['lprice'].median()):,}원")
        m4.metric("최저가", f"{int(df_filtered['lprice'].min()):,}원")
        m5.metric("활성 판매처", f"{df_filtered['mallName'].nunique()}개")

        # === 섹션 2: 가격 분포 및 통계 분석 ===
        st.divider()
        st.markdown("### 💰 가격 분포 및 통계 분석")

        col1, col2 = st.columns([3, 2])
        with col1:
            # 가격 분포 히스토그램 (향상)
            fig_hist = px.histogram(
                df_filtered, x='lprice', nbins=50,
                title=f"'{main_kw}' 가격 분포 (총 {len(df_filtered)}개 상품)",
                labels={'lprice': '최저가(원)', 'count': '상품 수'},
                color_discrete_sequence=['#1976d2'],
                marginal="box"  # 박스플롯 추가
            )
            fig_hist.add_vline(x=df_filtered['lprice'].mean(),
                              line_dash="dash", line_color="red",
                              annotation_text="평균", annotation_position="top")
            fig_hist.add_vline(x=df_filtered['lprice'].median(),
                              line_dash="dash", line_color="green",
                              annotation_text="중앙값", annotation_position="top")
            st.plotly_chart(fig_hist, use_container_width=True)

        with col2:
            # 가격 통계 요약
            st.markdown("##### 📈 가격 통계 요약")
            price_stats_df = pd.DataFrame({
                '지표': ['평균', '중앙값', '최소값', '최대값', '표준편차', 'Q1', 'Q3', '범위'],
                '값': [
                    f"{int(df_filtered['lprice'].mean()):,}원",
                    f"{int(df_filtered['lprice'].median()):,}원",
                    f"{int(df_filtered['lprice'].min()):,}원",
                    f"{int(df_filtered['lprice'].max()):,}원",
                    f"{int(df_filtered['lprice'].std()):,}원",
                    f"{int(df_filtered['lprice'].quantile(0.25)):,}원",
                    f"{int(df_filtered['lprice'].quantile(0.75)):,}원",
                    f"{int(df_filtered['lprice'].max() - df_filtered['lprice'].min()):,}원"
                ]
            })
            st.dataframe(price_stats_df, use_container_width=True, hide_index=True)

        # === 섹션 3: 카테고리별 상세 분석 ===
        st.divider()
        st.markdown("### 📂 카테고리별 상세 분석")

        col3, col4 = st.columns([2, 2])
        with col3:
            # 카테고리별 가격 박스플롯
            cat_data = df_filtered.groupby('category1').filter(lambda x: len(x) >= 3)
            if not cat_data.empty:
                fig_box = px.box(
                    cat_data, x='category1', y='lprice',
                    title="카테고리별 가격 분포 (박스플롯)",
                    labels={'category1': '카테고리', 'lprice': '가격(원)'},
                    color='category1',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_box.update_xaxis(tickangle=-45)
                st.plotly_chart(fig_box, use_container_width=True)

        with col4:
            # 카테고리별 상품 수 및 평균가
            cat_summary = df_filtered.groupby('category1').agg({
                'lprice': ['count', 'mean']
            }).round(0)
            cat_summary.columns = ['상품수', '평균가']
            cat_summary = cat_summary.sort_values('상품수', ascending=False).head(10)

            fig_cat = go.Figure()
            fig_cat.add_trace(go.Bar(
                name='상품 수', x=cat_summary.index, y=cat_summary['상품수'],
                marker_color='lightblue', yaxis='y', offsetgroup=1
            ))
            fig_cat.add_trace(go.Scatter(
                name='평균가', x=cat_summary.index, y=cat_summary['평균가'],
                marker_color='red', yaxis='y2', mode='lines+markers'
            ))
            fig_cat.update_layout(
                title="카테고리별 상품 수 & 평균가",
                xaxis=dict(tickangle=-45),
                yaxis=dict(title="상품 수", side="left"),
                yaxis2=dict(title="평균가(원)", overlaying="y", side="right"),
                legend=dict(x=0.01, y=0.99)
            )
            st.plotly_chart(fig_cat, use_container_width=True)

        # === 섹션 4: 판매처(몰) 분석 ===
        st.divider()
        st.markdown("### 🏪 판매처(쇼핑몰) 분석")

        col5, col6 = st.columns([2, 2])
        with col5:
            # 몰별 상품 수 Top 15
            mall_counts = df_filtered['mallName'].value_counts().head(15)
            fig_mall = px.bar(
                x=mall_counts.values, y=mall_counts.index,
                orientation='h',
                title="주요 판매 쇼핑몰 Top 15",
                labels={'x': '상품 수', 'y': '쇼핑몰'},
                color=mall_counts.values,
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig_mall, use_container_width=True)

        with col6:
            # 몰별 평균가 비교
            mall_avg = df_filtered.groupby('mallName')['lprice'].agg(['mean', 'count']).round(0)
            mall_avg = mall_avg[mall_avg['count'] >= 5].sort_values('mean', ascending=False).head(10)

            fig_mall_price = px.scatter(
                mall_avg, x='count', y='mean',
                size='count', color='mean',
                hover_name=mall_avg.index,
                title="판매처별 평균가 vs 상품 수 (5개 이상)",
                labels={'count': '상품 수', 'mean': '평균가(원)'},
                color_continuous_scale='RdYlGn_r'
            )
            st.plotly_chart(fig_mall_price, use_container_width=True)

        # === 섹션 5: 가격대별 분석 ===
        st.divider()
        st.markdown("### 💵 가격대별 상품 분포")

        # 가격대 구간 설정
        max_price = df_filtered['lprice'].max()
        if max_price <= 50000:
            bins = [0, 10000, 20000, 30000, 40000, 50000, max_price]
            labels = ['~1만', '1~2만', '2~3만', '3~4만', '4~5만', '5만~']
        elif max_price <= 100000:
            bins = [0, 20000, 40000, 60000, 80000, 100000, max_price]
            labels = ['~2만', '2~4만', '4~6만', '6~8만', '8~10만', '10만~']
        else:
            bins = [0, 50000, 100000, 200000, 500000, max_price]
            labels = ['~5만', '5~10만', '10~20만', '20~50만', '50만~']

        df_filtered['price_range'] = pd.cut(df_filtered['lprice'], bins=bins, labels=labels, include_lowest=True)
        price_range_counts = df_filtered['price_range'].value_counts().sort_index()

        col7, col8 = st.columns(2)
        with col7:
            fig_range = px.bar(
                x=price_range_counts.index, y=price_range_counts.values,
                title="가격대별 상품 분포",
                labels={'x': '가격대', 'y': '상품 수'},
                color=price_range_counts.values,
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_range, use_container_width=True)

        with col8:
            fig_pie = px.pie(
                values=price_range_counts.values,
                names=price_range_counts.index,
                title="가격대별 비율",
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        # === 섹션 6: 브랜드 분석 ===
        st.divider()
        st.markdown("### 🏷️ 브랜드 분석")

        # 브랜드 추출 (간단한 방법: 대괄호 또는 첫 단어)
        def extract_brand(title):
            import re
            # [브랜드] 형식 찾기
            bracket_match = re.search(r'\[(.*?)\]', title)
            if bracket_match:
                return bracket_match.group(1)
            # 첫 단어 추출
            words = title.split()
            if words:
                return words[0]
            return "기타"

        df_filtered['brand'] = df_filtered['title'].apply(extract_brand)
        brand_analysis = df_filtered.groupby('brand').agg({
            'lprice': ['count', 'mean', 'min', 'max']
        }).round(0)
        brand_analysis.columns = ['상품수', '평균가', '최저가', '최고가']
        brand_analysis = brand_analysis[brand_analysis['상품수'] >= 3].sort_values('상품수', ascending=False).head(15)

        col9, col10 = st.columns([2, 1])
        with col9:
            fig_brand = px.bar(
                brand_analysis, x=brand_analysis.index, y='상품수',
                title="주요 브랜드 Top 15 (3개 이상)",
                labels={'x': '브랜드', 'index': '브랜드', '상품수': '상품 수'},
                color='평균가',
                color_continuous_scale='Sunset'
            )
            fig_brand.update_xaxis(tickangle=-45)
            st.plotly_chart(fig_brand, use_container_width=True)

        with col10:
            st.markdown("##### 브랜드 통계")
            st.dataframe(brand_analysis, use_container_width=True)

        # === 섹션 7: 카테고리별 TOP 상품 ===
        st.divider()
        st.markdown("### ⭐ 카테고리별 인기 상품 (최저가 기준)")

        top_cats = df_filtered['category1'].value_counts().head(5).index
        for cat in top_cats:
            with st.expander(f"📦 {cat} - Top 10 상품"):
                cat_products = df_filtered[df_filtered['category1'] == cat].nsmallest(10, 'lprice')
                display_df = cat_products[['title', 'lprice', 'mallName', 'link']].copy()
                display_df['lprice'] = display_df['lprice'].apply(lambda x: f"{int(x):,}원")
                display_df.columns = ['상품명', '최저가', '판매처', '링크']
                st.dataframe(display_df, use_container_width=True, hide_index=True)

        # === 섹션 8: 전체 상품 리스트 ===
        st.divider()
        st.markdown("### 🛒 전체 상품 리스트")

        if 'brand' in df_filtered.columns:
            display_all = df_filtered[['title', 'lprice', 'mallName', 'category1', 'brand', 'link']].copy()
            display_all['lprice'] = display_all['lprice'].apply(lambda x: f"{int(x):,}원")
            display_all.columns = ['상품명', '최저가', '판매처', '카테고리', '브랜드', '링크']
        else:
            display_all = df_filtered[['title', 'lprice', 'mallName', 'category1', 'link']].copy()
            display_all['lprice'] = display_all['lprice'].apply(lambda x: f"{int(x):,}원")
            display_all.columns = ['상품명', '최저가', '판매처', '카테고리', '링크']
        st.dataframe(display_all.head(100), use_container_width=True, hide_index=True)

        # === 섹션 9: 상세 카테고리 테이블 ===
        st.divider()
        st.markdown("### 📊 카테고리별 종합 통계")
        cat_detail = df_filtered.groupby('category1').agg({
            'lprice': ['count', 'mean', 'median', 'std', 'min', 'max']
        }).round(0)
        cat_detail.columns = ['상품수', '평균가', '중앙값', '표준편차', '최저가', '최고가']
        cat_detail = cat_detail.sort_values('상품수', ascending=False)
        st.dataframe(cat_detail, use_container_width=True)

# Tab 3: 실시간 블로그
with tab3:
    st.header(f"📝 '{main_kw}' 실시간 블로그 반응")
    df_blog, blog_err = fetch_realtime_blog(main_kw)
    if blog_err:
        st.error(blog_err)
    elif df_blog is not None:
        # 데이터 전처리
        df_blog['title'] = df_blog['title'].apply(clean_html)
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

# Tab 4: 실시간 카페
with tab4:
    st.header(f"☕ '{main_kw}' 실시간 카페 커뮤니티 반응")
    df_cafe, cafe_err = fetch_realtime_cafe(main_kw)
    if cafe_err:
        st.error(cafe_err)
    elif df_cafe is not None:
        df_cafe['title'] = df_cafe['title'].apply(clean_html)
        
        # 카페 이름별 분포
        cafe_counts = df_cafe['cafename'].value_counts().head(10).reset_index()
        cafe_counts.columns = ['카페명', '게시물 수']
        fig_cafe = px.bar(cafe_counts, x='게시물 수', y='카페명', orientation='h',
                          title="주요 활동 카페 TOP 10",
                          color='게시물 수', color_continuous_scale='Teal')
        st.plotly_chart(fig_cafe, use_container_width=True)
        
        st.divider()
        st.subheader("👥 최신 카페 게시물 리스트")
        st.dataframe(df_cafe[['title', 'cafename', 'cafeurl']].head(50), use_container_width=True)

# Tab 5: 실시간 뉴스
with tab5:
    st.header(f"📰 '{main_kw}' 실시간 뉴스 이슈")
    df_news, news_err = fetch_realtime_news(main_kw)
    if news_err:
        st.error(news_err)
    elif df_news is not None:
        df_news['title'] = df_news['title'].apply(clean_html)
        df_news['pubDate'] = pd.to_datetime(df_news['pubDate'], errors='coerce')
        
        # 시간대별 뉴스 발행 분포
        news_daily = df_news.groupby(df_news['pubDate'].dt.date).size().reset_index(name='news_count')
        news_daily.columns = ['발행일', '뉴스 수']
        fig_news = px.area(news_daily, x='발행일', y='뉴스 수', 
                           title="최근 뉴스 발행 추이",
                           color_discrete_sequence=['#d32f2f'])
        st.plotly_chart(fig_news, use_container_width=True)
        
        st.divider()
        st.subheader("🗞️ 최신 관련 뉴스 리스트")
        st.dataframe(df_news[['title', 'pubDate', 'link']].sort_values('pubDate', ascending=False).head(50), 
                     use_container_width=True)

auth_status = "✅ 인증 완료" if (CLIENT_ID and CLIENT_SECRET) else "❌ 인증 미완료"
st.sidebar.caption(f"상태: {auth_status} | 업데이트: {datetime.now().strftime('%H:%M:%S')}")
