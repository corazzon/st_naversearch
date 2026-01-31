import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# 페이지 설정
st.set_page_config(page_title="Naver Market Insights", layout="wide", page_icon="⚡")

# CSS 스타일링
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    h1, h2, h3 { color: #1a237e; font-family: 'Outfit', sans-serif; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        background-color: #eee;
        border-radius: 5px 5px 0 0;
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
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path, override=True)
            cid = os.getenv('NAVER_CLIENT_ID')
            csec = os.getenv('NAVER_CLIENT_SECRET')

    if cid: cid = str(cid).strip().strip("'").strip('"')
    if csec: csec = str(csec).strip().strip("'").strip('"')
    
    return cid, csec

CLIENT_ID, CLIENT_SECRET = get_api_keys()
HEADERS = {"X-Naver-Client-Id": CLIENT_ID, "X-Naver-Client-Secret": CLIENT_SECRET, "Content-Type": "application/json"}

# --- 실시간 API 호출 함수 ---
@st.cache_data(ttl=600)
def fetch_realtime_trend(keywords, start_date, end_date, gender=None, ages=None):
    """네이버 검색어 트렌드 API 호출 (성별/연령 필터 추가)"""
    if not CLIENT_ID or not CLIENT_SECRET: return None, "인증 키가 설정되지 않았습니다."
    url = "https://openapi.naver.com/v1/datalab/search"
    body = {
        "startDate": start_date, "endDate": end_date,
        "timeUnit": "date",
        "keywordGroups": [{"groupName": k, "keywords": [k]} for k in keywords]
    }
    
    if gender:
        body["gender"] = gender
    if ages and len(ages) > 0:
        body["ages"] = ages
        
    res = requests.post(url, headers=HEADERS, data=json.dumps(body))
    if res.status_code == 200:
        dfs = [pd.DataFrame(r['data']).assign(keyword=r['title']) for r in res.json()['results']]
        return pd.concat(dfs), None
    return None, f"Trend API Error: {res.status_code}"

@st.cache_data(ttl=600)
def fetch_realtime_shopping(keywords):
    """네이버 쇼핑 검색 API 호출 (다중 키워드 통합)"""
    if not CLIENT_ID or not CLIENT_SECRET: return None, "인증 키 미설정"
    all_items = []
    for kw in keywords:
        url = f"https://openapi.naver.com/v1/search/shop.json?query={kw}&display=100"
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            items = res.json().get('items', [])
            for item in items:
                item['search_keyword'] = kw
            all_items.extend(items)
    return pd.DataFrame(all_items) if all_items else None, None

@st.cache_data(ttl=600)
def fetch_realtime_blog(keywords):
    """네이버 블로그 검색 API 호출 (다중 키워드 통합)"""
    if not CLIENT_ID or not CLIENT_SECRET: return None, "인증 키 미설정"
    all_items = []
    for kw in keywords:
        url = f"https://openapi.naver.com/v1/search/blog.json?query={kw}&display=100"
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            items = res.json().get('items', [])
            for item in items:
                item['search_keyword'] = kw
            all_items.extend(items)
    return pd.DataFrame(all_items) if all_items else None, None

@st.cache_data(ttl=600)
def fetch_realtime_cafe(keywords):
    """네이버 카페 검색 API 호출 (다중 키워드 통합)"""
    if not CLIENT_ID or not CLIENT_SECRET: return None, "인증 키 미설정"
    all_items = []
    for kw in keywords:
        url = f"https://openapi.naver.com/v1/search/cafearticle.json?query={kw}&display=100"
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            items = res.json().get('items', [])
            for item in items:
                item['search_keyword'] = kw
            all_items.extend(items)
    return pd.DataFrame(all_items) if all_items else None, None

@st.cache_data(ttl=600)
def fetch_realtime_news(keywords):
    """네이버 뉴스 검색 API 호출 (다중 키워드 통합)"""
    if not CLIENT_ID or not CLIENT_SECRET: return None, "인증 키 미설정"
    all_items = []
    for kw in keywords:
        url = f"https://openapi.naver.com/v1/search/news.json?query={kw}&display=100"
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            items = res.json().get('items', [])
            for item in items:
                item['search_keyword'] = kw
            all_items.extend(items)
    return pd.DataFrame(all_items) if all_items else None, None

@st.cache_data(ttl=600)
def fetch_shopping_insight_trend(cat_id, keywords, start_date, end_date):
    """쇼핑인사이트 분야 내 키워드 클릭 트렌드 API 호출"""
    if not CLIENT_ID or not CLIENT_SECRET: 
        return None, "인증 키 미설정", None
    
    url = "https://openapi.naver.com/v1/datalab/shopping/category/keywords"
    body = {
        "startDate": start_date, 
        "endDate": end_date,
        "timeUnit": "date",
        "category": cat_id,
        "keyword": [{"name": k, "param": [k]} for k in keywords]
    }
    
    res = requests.post(url, headers=HEADERS, data=json.dumps(body))
    
    # 응답 전체를 저장 (디버깅용)
    response_data = None
    try:
        response_data = res.json()
    except:
        pass
    
    if res.status_code == 200:
        results = response_data.get('results', []) if response_data else []
        
        if not results:
            # 빈 결과 - API는 성공했지만 데이터가 없음
            return pd.DataFrame(), None, response_data
        
        dfs = []
        for r in results:
            if 'data' in r and r['data']:
                df = pd.DataFrame(r['data'])
                df['keyword'] = r['title']
                dfs.append(df)
        
        if dfs:
            return pd.concat(dfs), None, response_data
        else:
            return pd.DataFrame(), None, response_data
    else:
        # API 에러
        error_msg = f"API 오류 (상태코드: {res.status_code})"
        if response_data and 'errorMessage' in response_data:
            error_msg += f" - {response_data['errorMessage']}"
        return None, error_msg, response_data


@st.cache_data(ttl=600)
def fetch_shopping_insight_demographics(cat_id):
    """쇼핑인사이트 분야별 데모그래픽(성별/연령) 분석 데이터 호출"""
    # 원칙적으로는 여러 API를 조합해야 하지만, 여기서는 성별/연령 비중 데이터를 시뮬레이션하거나 
    # 쇼핑인사이트 카테고리 키워드 API의 응답을 활용할 수 있습니다. 
    # 본 구현에서는 분야별 대표 데이터를 가져오는 로직을 구성합니다.
    return None, "준비 중인 기능입니다."

# --- 데이터 전처리 헬퍼 ---
def clean_html(text):
    """HTML 태그 제거"""
    if pd.isna(text): return ""
    return text.replace('<b>', '').replace('</b>', '').replace('&quot;', '"').replace('&lt;', '<').replace('&gt;', '>')

@st.cache_data
def convert_df(df):
    """데이터프레임을 CSV로 변환 (한글 깨짐 방지 utf-8-sig)"""
    return df.to_csv(index=False).encode('utf-8-sig')

# --- 메인 UI ---
st.title("⚡ 실시간 Naver Market Insights")
st.caption("로컬 파일이 아닌, 네이버 API를 통해 실시간 데이터를 직접 분석합니다.")

# 사이드바
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

st.sidebar.header("🔍 실시간 분석 설정")

target_kws = st.sidebar.text_input("분석 키워드 (쉼표 구분)", "오메가3, 비타민D, 유산균")
keywords = [k.strip() for k in target_kws.split(',') if k.strip()]

st.sidebar.divider()
st.sidebar.subheader("📅 분석 기간 설정")
today = datetime.now()
jan_1st = datetime(today.year, 1, 1)

date_range = st.sidebar.date_input(
    "조회 기간 선택",
    value=(jan_1st, today),
    max_value=today,
    help="시작일과 종료일을 선택하세요."
)

# 날짜 범위가 적절히 선택되었는지 확인
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date = date_range[0].strftime("%Y-%m-%d")
    end_date = date_range[1].strftime("%Y-%m-%d")
else:
    # 한 날짜만 선택된 경우나 미선택 시 기본값 적용
    start_date = jan_1st.strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")
    st.sidebar.warning("시작일과 종료일을 모두 선택해주세요.")

st.sidebar.divider()
st.sidebar.info(f"선택된 키워드: {', '.join(keywords)}")

st.sidebar.divider()
st.sidebar.subheader("📊 분석 모드 설정")
analysis_mode = st.sidebar.radio(
    "분석 모드", 
    ["일반 트렌드", "성별 비교"], 
    help="일반: 선택한 필터 기준 통합 추이\n성별: 남성 vs 여성 그룹별 상세 패턴 비교"
)

st.sidebar.subheader("👥 인구 통계 필터 (트렌드)")

# 성별 선택 (성별 비교 모드일 때는 숨김/비활성)
selected_gender = ""
gender_option = "전체"
if analysis_mode != "성별 비교":
    gender_option = st.sidebar.radio("성별", ["전체", "남성", "여성"], horizontal=True)
    gender_map = {"전체": "", "남성": "m", "여성": "f"}
    selected_gender = gender_map[gender_option]
else:
    st.sidebar.info("성별 비교 모드: 남성 vs 여성을 비교합니다.")

# 연령 선택
age_options = ["0~12세", "13~18세", "19~24세", "25~29세", "30~34세", "35~39세", "40~44세", "45~49세", "50~54세", "55~59세", "60세 이상"]
age_codes = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"]
age_ref = dict(zip(age_options, age_codes))
code_to_age = dict(zip(age_codes, age_options))

selected_ages = st.sidebar.multiselect("연령대 (다중 선택 가능)", age_options, placeholder="전체 연령")
selected_age_codes = [age_ref[a] for a in selected_ages] if selected_ages else []

st.sidebar.caption("💡 10분마다 데이터가 최신화됩니다.")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 트렌드 비교", "🛍️ 실시간 쇼핑", "📝 실시간 블로그", 
    "☕ 실시간 카페", "📰 실시간 뉴스", "📊 쇼핑인사이트"
])

# Tab 1: 트렌드 비교
with tab1:
    st.header(f"📈 실시간 검색어 트렌드 ({start_date} ~ {end_date})")
    
    # 필터 정보 표시
    filter_info = []
    if analysis_mode == "일반 트렌드":
        if selected_gender: filter_info.append(f"성별: {gender_option}")
        if selected_ages: filter_info.append(f"연령: {', '.join(selected_ages)}")
    elif analysis_mode == "성별 비교":
        filter_info.append("분석: 성별 비교 (남성 vs 여성)")
        if selected_ages: filter_info.append(f"연령: {', '.join(selected_ages)}")
        
    if filter_info:
        st.caption(f"적용된 필터: {' | '.join(filter_info)}")

    # --- 데이터 수집 로직 ---
    df_trend = None
    err = None
    
    if analysis_mode == "일반 트렌드":
        df_trend, err = fetch_realtime_trend(keywords, start_date, end_date, selected_gender, selected_age_codes)
    
    elif analysis_mode == "성별 비교":
        # 남성/여성 각각 호출 후 병합
        df_m, err_m = fetch_realtime_trend(keywords, start_date, end_date, "m", selected_age_codes)
        df_f, err_f = fetch_realtime_trend(keywords, start_date, end_date, "f", selected_age_codes)
        
        dfs = []
        if df_m is not None: 
            df_m['gender'] = '남성'
            dfs.append(df_m)
        if df_f is not None: 
            df_f['gender'] = '여성'
            dfs.append(df_f)
            
        if dfs:
            df_trend = pd.concat(dfs)
        else:
            err = err_m or err_f
            
    # --- 결과 시각화 ---
    if err:
        st.error(err)
    elif df_trend is not None and not df_trend.empty:
        df_trend['period'] = pd.to_datetime(df_trend['period'])
        
        st.info(f"📊 총 **{len(df_trend):,}**개의 트렌드 데이터 포인트가 분석되었습니다.")
        
        # 1. 그래프 그리기 (모드별 분기)
        if analysis_mode == "일반 트렌드":
            fig1 = px.line(df_trend, x='period', y='ratio', color='keyword', 
                           title="실시간 검색 트렌드 추이",
                           template="plotly_white", color_discrete_sequence=px.colors.qualitative.Prism)
        
        elif analysis_mode == "성별 비교":
            # 색상은 키워드, col은 성별로 구분
            fig1 = px.line(df_trend, x='period', y='ratio', color='keyword', facet_col='gender',
                           title="성별 검색 트렌드 비교 (Max 100 상대지수)",
                           template="plotly_white", color_discrete_sequence=px.colors.qualitative.Prism)
            # subplot 제목 깔끔하게
            fig1.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
            
        fig1.update_layout(hovermode="x unified")
        st.plotly_chart(fig1, use_container_width=True)
        
        # 비교 모드일 경우 안내 문구 추가
        if analysis_mode != "일반 트렌드":
            st.caption("""
            ⚠️ **주의**: Naver DataLab 그래프의 y축(ratio)은 해당 조건 내 최댓값을 100으로 둔 **상대적 지표**입니다. 
            서로 다른 그룹 간의 절대적인 검색량 크기 비교(예: 남성의 50과 여성의 50이 같은 검색량임)를 의미하지 않습니다. 
            각 그룹 내에서의 추세 변화 패턴을 비교하는 목적으로 활용하세요.
            """)
        
        col1, col2 = st.columns(2)
        with col1:
            # 그래프 2: 평균 검색량 바 차트
            # 그룹핑 기준이 모드에 따라 달라짐
            group_cols = ['keyword']
            if analysis_mode == "성별 비교": group_cols.append('gender')
            
            avg_df = df_trend.groupby(group_cols)['ratio'].mean().reset_index().sort_values('ratio', ascending=False)
            
            # 바차트 시각화
            if analysis_mode == "일반 트렌드":
                fig2 = px.bar(avg_df, x='keyword', y='ratio', color='keyword', 
                              title="평균 검색 활동 점유율", text_auto='.1f',
                              color_discrete_sequence=px.colors.qualitative.Safe)
            else:
                # 비교 모드에서는 Facet 활용
                facet_c = 'gender' if analysis_mode == "성별 비교" else None
                fig2 = px.bar(avg_df, x='keyword', y='ratio', color='gender', barmode='group',
                              title="성별/키워드별 평균 검색 강도", text_auto='.1f',
                              color_discrete_sequence=px.colors.qualitative.Safe)

            st.plotly_chart(fig2, use_container_width=True)
            
        with col2:
            # 표 1: 요약 통계
            st.subheader("📊 데이터 요약 (상대 지표)")
            # 요약 통계 그룹핑
            summary = df_trend.groupby(group_cols)['ratio'].agg(['mean', 'max', 'std']).round(2)
            summary.columns = ['평균', '최대치', '변동성']
            st.dataframe(summary, use_container_width=True)

        st.subheader("📋 전체 데이터 목록")
        st.dataframe(df_trend, use_container_width=True)
        st.download_button(
            label="📥 트렌드 데이터 다운로드 (CSV)",
            data=convert_df(df_trend),
            file_name=f"trend_search_{analysis_mode}_{start_date}_{end_date}.csv",
            mime="text/csv"
        )

# Tab 2: 실시간 쇼핑
with tab2:
    st.header("🛍️ 통합 실시간 쇼핑 마켓 현황")
    df_shop, shop_err = fetch_realtime_shopping(keywords)
    if shop_err:
        st.error(shop_err)
    elif df_shop is not None:
        # 데이터 전처리
        df_shop['lprice'] = pd.to_numeric(df_shop['lprice'], errors='coerce')
        df_shop['title'] = df_shop['title'].apply(clean_html)
        
        # KPI 섹션 (통합)
        m1, m2, m3 = st.columns(3)
        m1.metric("수집된 전체 상품", f"{len(df_shop)}개")
        m2.metric("전체 평균가", f"{int(df_shop['lprice'].mean()):,}원")
        m3.metric("활성 판매처", f"{df_shop['mallName'].nunique()}개")
        
        col3, col4 = st.columns([2, 1])
        with col3:
            # 그래프 3: 키워드별 가격 분포 박스 플롯
            fig3 = px.box(df_shop, x='search_keyword', y='lprice', color='search_keyword',
                          title="키워드별 최저가 분포 비교",
                          labels={'lprice': '최저가(원)', 'search_keyword': '검색어'},
                          template="simple_white")
            st.plotly_chart(fig3, use_container_width=True)
        with col4:
            # 그래프 4: 키워드별 상품 비중
            kw_counts = df_shop['search_keyword'].value_counts()
            fig4 = px.pie(values=kw_counts.values, names=kw_counts.index, 
                          title="키워드별 데이터 비중", hole=0.4,
                          color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig4, use_container_width=True)
            
        st.divider()
        st.subheader("🛒 실시간 통합 인기 상품 리스트")
        st.dataframe(
            df_shop[['search_keyword', 'title', 'lprice', 'mallName', 'category1', 'link']].head(100), 
            column_config={
                "link": st.column_config.LinkColumn(
                    "링크",
                    help="클릭시 해당 상품 페이지로 이동합니다.",
                    validate="^https://.*",
                    display_text="바로가기"
                ),
                "lprice": st.column_config.NumberColumn(
                    "최저가",
                    format="%d원"
                )
            },
            use_container_width=True,
            hide_index=True
        )
        st.download_button(
             label="📥 쇼핑 데이터 다운로드 (CSV)",
             data=convert_df(df_shop),
             file_name=f"realtime_shopping_{datetime.now().strftime('%Y%m%d')}.csv",
             mime="text/csv"
        )

# Tab 3: 실시간 블로그
with tab3:
    st.header("📝 실시간 블로그 반응 통합 분석")
    df_blog, blog_err = fetch_realtime_blog(keywords)
    if blog_err:
        st.error(blog_err)
    elif df_blog is not None:
        df_blog['title'] = df_blog['title'].apply(clean_html)
        df_blog['postdate'] = pd.to_datetime(df_blog['postdate'], format='%Y%m%d', errors='coerce')
        
        st.metric("수집된 블로그 문서", f"{len(df_blog):,}건")
        
        # 키워드별 게시물 추이
        blog_daily = df_blog.groupby(['postdate', 'search_keyword']).size().reset_index(name='content_count')
        fig5 = px.line(blog_daily, x='postdate', y='content_count', color='search_keyword',
                       title="키워드별 최근 블로그 게시물 분포",
                       labels={'postdate': '작성일', 'content_count': '게시물 수'},
                       template="plotly_white")
        st.plotly_chart(fig5, use_container_width=True)
        
        col_blog1, col_blog2 = st.columns(2)
        with col_blog1:
            # 주요 블로거 랭킹
            top_bloggers = df_blog['bloggername'].value_counts().head(10).reset_index()
            top_bloggers.columns = ['블로거명', '게시물 수']
            fig_top_blog = px.bar(top_bloggers, x='게시물 수', y='블로거명', orientation='h',
                                  title="🏆 주요 활동 블로거 TOP 10",
                                  color='게시물 수', color_continuous_scale='Magma')
            st.plotly_chart(fig_top_blog, use_container_width=True)
            
        with col_blog2:
            # 블로그 제목 키워드 분석
            st.write("🔍 블로그 제목 핵심 단어")
            all_blog_titles = " ".join(df_blog['title'].dropna().tolist())
            blog_words = [w for w in all_blog_titles.split() if len(w) > 1 and w not in keywords]
            from collections import Counter
            blog_word_counts = Counter(blog_words).most_common(12)
            if blog_word_counts:
                df_blog_word = pd.DataFrame(blog_word_counts, columns=['단어', '빈도'])
                fig_blog_word = px.bar(df_blog_word, x='단어', y='빈도',
                                       title="블로그 제목 빈출 키워드",
                                       color='빈도',
                                       color_continuous_scale=px.colors.sequential.PuRd)
                st.plotly_chart(fig_blog_word, use_container_width=True)
        
        st.divider()
        st.subheader("📖 최근 블로그 콘텐츠 통합 리스트")
        st.dataframe(
            df_blog[['search_keyword', 'title', 'bloggername', 'postdate', 'link']].sort_values('postdate', ascending=False).head(100), 
            column_config={
                "link": st.column_config.LinkColumn(
                    "링크",
                    help="클릭시 해당 블로그로 이동합니다.",
                    validate="^https://.*",
                    display_text="바로가기"
                ),
                "postdate": st.column_config.DateColumn(
                    "작성일",
                    format="YYYY-MM-DD"
                )
            },
            use_container_width=True,
            hide_index=True
        )
        st.download_button(
             label="📥 블로그 데이터 다운로드 (CSV)",
             data=convert_df(df_blog),
             file_name=f"realtime_blog_{datetime.now().strftime('%Y%m%d')}.csv",
             mime="text/csv"
        )

# Tab 4: 실시간 카페
with tab4:
    st.header("☕ 실시간 카페 커뮤니티 반응 통합")
    df_cafe, cafe_err = fetch_realtime_cafe(keywords)
    if cafe_err:
        st.error(cafe_err)
    elif df_cafe is not None:
        df_cafe['title'] = df_cafe['title'].apply(clean_html)
        
        st.metric("수집된 카페 게시글", f"{len(df_cafe):,}건")

        # 1. 키워드별 카페 게시물 비중 (기존)
        cafe_kw_counts = df_cafe['search_keyword'].value_counts().reset_index()
        cafe_kw_counts.columns = ['키워드', '게시물 수']
        
        col_cafe1, col_cafe2 = st.columns(2)
        with col_cafe1:
            fig_cafe = px.bar(cafe_kw_counts, x='게시물 수', y='키워드', orientation='h',
                              title="키워드별 카페 활동량 비교", color='키워드',
                              color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_cafe, use_container_width=True)
            
        with col_cafe2:
            # 2. 주요 활동 카페 랭킹 (신규)
            top_cafes = df_cafe['cafename'].value_counts().head(10).reset_index()
            top_cafes.columns = ['카페명', '게시물 수']
            fig_top_cafe = px.bar(top_cafes, x='게시물 수', y='카페명', orientation='h',
                                  title="🏆 주요 활동 카페 TOP 10",
                                  color='게시물 수', color_continuous_scale='Viridis')
            st.plotly_chart(fig_top_cafe, use_container_width=True)

        st.divider()
        
        # 3. 게시글 제목 핵심 키워드 분석 (신규)
        st.subheader("🔍 카페 게시글 핵심 키워드 분석 (Top 15)")
        all_titles = " ".join(df_cafe['title'].dropna().tolist())
        # 단순 형태소 분석 대신 공백 분리 및 기본 불용어 처리
        words = [w for w in all_titles.split() if len(w) > 1 and w not in keywords]
        from collections import Counter
        word_counts = Counter(words).most_common(15)
        if word_counts:
            df_word = pd.DataFrame(word_counts, columns=['단어', '빈도'])
            fig_word = px.bar(df_word, x='단어', y='빈도', color='빈도',
                              title="제목 내 빈출 단어", text_auto=True,
                              color_continuous_scale='Blues')
            st.plotly_chart(fig_word, use_container_width=True)
            st.caption("💡 제목에서 추출한 단어 빈도입니다. '추천', '비교', '후기' 등 사용자 의도를 파악해 보세요.")
        
        st.divider()
        st.subheader("👥 최신 통합 카페 게시물")
        st.dataframe(
            df_cafe[['search_keyword', 'title', 'cafename', 'cafeurl']].head(100),
            column_config={
                "cafeurl": st.column_config.LinkColumn(
                    "링크",
                    help="클릭시 해당 카페 게시글로 이동합니다.",
                    validate="^https://.*",
                    display_text="바로가기"
                )
            },
            use_container_width=True,
            hide_index=True
        )
        st.download_button(
             label="📥 카페 데이터 다운로드 (CSV)",
             data=convert_df(df_cafe),
             file_name=f"realtime_cafe_{datetime.now().strftime('%Y%m%d')}.csv",
             mime="text/csv"
        )

# Tab 5: 실시간 뉴스
with tab5:
    st.header("📰 실시간 최신 뉴스 통합 이슈")
    df_news, news_err = fetch_realtime_news(keywords)
    if news_err:
        st.error(news_err)
    elif df_news is not None:
        df_news['title'] = df_news['title'].apply(clean_html)
        df_news['pubDate'] = pd.to_datetime(df_news['pubDate'], errors='coerce')
        
        st.metric("수집된 뉴스 기사", f"{len(df_news):,}건")
        
        # 시간대별 키워드 뉴스 발행 추이
        news_daily = df_news.groupby([df_news['pubDate'].dt.date, 'search_keyword']).size().reset_index(name='news_count')
        news_daily.columns = ['발행일', '키워드', '뉴스 수']
        fig_news = px.bar(news_daily, x='발행일', y='뉴스 수', color='키워드', barmode='group',
                          title="날짜별 뉴스 발행 현황",
                          template="simple_white")
        st.plotly_chart(fig_news, use_container_width=True)
        
        # 뉴스 제목 키워드 분석
        st.subheader("🔍 실시간 뉴스 핵심 키워드 (Hot Topics)")
        all_news_titles = " ".join(df_news['title'].dropna().tolist())
        news_words = [w for w in all_news_titles.split() if len(w) > 1 and w not in keywords]
        from collections import Counter
        news_word_counts = Counter(news_words).most_common(15)
        if news_word_counts:
            df_news_word = pd.DataFrame(news_word_counts, columns=['단어', '빈도'])
            fig_news_word = px.bar(df_news_word, x='빈도', y='단어', orientation='h',
                                   title="뉴스 제목 내 상위 키워드", text_auto=True,
                                   color='빈도', color_continuous_scale='Reds')
            st.plotly_chart(fig_news_word, use_container_width=True)
            st.caption("💡 뉴스의 핵심 단어를 통해 현재 시장의 주요 이슈를 파악해 보세요.")

        st.divider()
        st.subheader("🗞️ 최신 관련 뉴스 통합 리스트")
        st.dataframe(
            df_news[['search_keyword', 'title', 'pubDate', 'link']].sort_values('pubDate', ascending=False).head(100), 
            column_config={
                "link": st.column_config.LinkColumn(
                    "링크",
                    help="클릭시 해당 뉴스 기사로 이동합니다.",
                    validate="^https://.*",
                    display_text="바로가기"
                ),
                "pubDate": st.column_config.DatetimeColumn(
                    "발행일시",
                    format="YYYY-MM-DD HH:mm"
                )
            },
            use_container_width=True,
            hide_index=True
        )
        st.download_button(
             label="📥 뉴스 데이터 다운로드 (CSV)",
             data=convert_df(df_news),
             file_name=f"realtime_news_{datetime.now().strftime('%Y%m%d')}.csv",
             mime="text/csv"
        )

# Tab 6: 쇼핑인사이트
with tab6:
    st.header("📊 쇼핑인사이트 Deep Dive")
    
    # --- 쇼핑인사이트 설정 (탭 내부 상단으로 이동) ---
    st.subheader("⚙️ 분석 분야 설정")
    
    # 대분류 카테고리만 정의
    CAT_OPTIONS = {
        "패션의류": "50000000",
        "패션잡화": "50000001",
        "화장품/미용": "50000002",
        "디지털/가전": "50000003",
        "가구/인테리어": "50000004",
        "출산/육아": "50000005",
        "식품": "50000006",
        "스포츠/레저": "50000007",
        "생활/건강": "50000008",
        "여가/생활편의": "50000009",
        "면세점": "50000010",
        "도서": "50000011",
        "직접 입력": "manual"
    }
    
    cat_col1, cat_col2 = st.columns([1, 2])
    
    with cat_col1:
        # 생활/건강(index=8)을 기본값으로 설정하여 '오메가3' 키워드와 매칭
        selected_cat_name = st.selectbox("대분류 카테고리 선택", list(CAT_OPTIONS.keys()), index=8)
    
    with cat_col2:
        if selected_cat_name == "직접 입력":
            cat_id = st.text_input("카테고리 ID 직접 입력", "50000000")
        else:
            cat_id = CAT_OPTIONS[selected_cat_name]
            st.info(f"선택된 분야: **{selected_cat_name}** (ID: `{cat_id}`)")

    
    st.divider()
    
    st.markdown(f"""
    **쇼핑인사이트**는 네이버 쇼핑 내에서 발생하는 사용자 클릭 데이터를 기반으로 마켓 트렌드를 분석합니다.
    - 선택 카테고리: **{selected_cat_name}** (ID: `{cat_id}`)
    - 분석 키워드: **{', '.join(keywords)}**
    """)
    
    st.subheader(f"📈 분야 내 키워드 클릭 트렌드 ({start_date} ~ {end_date})")
    df_ins, ins_err, api_response = fetch_shopping_insight_trend(cat_id, keywords, start_date, end_date)
    
    # 디버깅 정보 표시 (expander)
    with st.expander("🔍 API 요청/응답 정보 (디버깅)"):
        st.write("**요청 정보:**")
        st.json({
            "URL": "https://openapi.naver.com/v1/datalab/shopping/category/keywords",
            "카테고리 ID": cat_id,
            "키워드": keywords,
            "시작일": start_date,
            "종료일": end_date,
            "시간 단위": "date"
        })
        
        if api_response:
            st.write("**API 응답:**")
            st.json(api_response)
        else:
            st.warning("API 응답 데이터가 없습니다.")
    
    # 에러 처리
    if ins_err:
        st.error(f"❌ API 호출 오류: {ins_err}")
        st.info("""
        **문제 해결 방법:**
        - API 인증 키가 올바른지 확인하세요.
        - 카테고리 ID가 유효한지 확인하세요.
        - 위의 '🔍 API 요청/응답 정보'를 확인하여 상세 오류를 파악하세요.
        """)
    elif df_ins is None:
        st.warning("⚠️ API 응답이 없습니다. 네트워크 연결을 확인하세요.")
    elif df_ins.empty:
        st.warning(f"⚠️ 선택하신 카테고리 **'{selected_cat_name}'** 에는 키워드 **{', '.join(keywords)}** 에 대한 클릭 데이터가 존재하지 않습니다.")
        st.info("""
        **데이터가 보이지 않는 이유:**
        - **카테고리 불일치**: 키워드가 해당 카테고리에 속하지 않는 상품일 수 있습니다. (예: '원피스'를 '식품'에서 검색)
        - **검색량 부족**: 해당 기간 내 클릭량이 집계 기준 미만일 수 있습니다.
        
        **해결 방법:**
        1. **카테고리 변경**: 키워드에 맞는 올바른 카테고리를 선택해주세요.
        2. **키워드 변경**: 더 일반적이거나 인기 있는 키워드로 시도해보세요.
        """)
    elif 'period' not in df_ins.columns:
        st.error(f"❌ 예상치 못한 데이터 형식입니다. 컬럼: {df_ins.columns.tolist()}")
        with st.expander("🔍 원본 데이터 확인"):
            st.dataframe(df_ins)
    else:
        # 데이터 전처리
        df_ins['period'] = pd.to_datetime(df_ins['period'])
        
        st.info(f"📊 총 **{len(df_ins):,}**개의 쇼핑 클릭 데이터 포인트가 분석되었습니다.")
        
        # 메인 트렌드 차트
        fig_ins = px.line(df_ins, x='period', y='ratio', color='keyword',
                          title="키워드별 쇼핑 클릭 지수 추이",
                          template="plotly_white", 
                          color_discrete_sequence=px.colors.qualitative.Vivid,
                          markers=True)
        fig_ins.update_layout(
            hovermode="x unified",
            xaxis_title="날짜",
            yaxis_title="클릭 지수",
            legend_title="키워드"
        )
        st.plotly_chart(fig_ins, use_container_width=True)
        st.info("💡 클릭 지수는 기간 내 최대 수치를 100으로 둔 상대적 활동 지표입니다.")
        
        # 상세 분석 섹션
        st.divider()
        st.subheader("📊 키워드별 상세 분석")
        
        col_analysis1, col_analysis2 = st.columns(2)
        
        with col_analysis1:
            # 키워드별 평균/최대/최소 통계
            stats_df = df_ins.groupby('keyword')['ratio'].agg([
                ('평균 클릭지수', 'mean'),
                ('최대 클릭지수', 'max'),
                ('최소 클릭지수', 'min'),
                ('변동성(표준편차)', 'std')
            ]).round(2).reset_index()
            
            st.write("**📈 키워드별 클릭 지수 통계**")
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
            
            # 평균 클릭지수 바차트
            fig_avg = px.bar(stats_df, x='keyword', y='평균 클릭지수', 
                            color='평균 클릭지수',
                            title="키워드별 평균 클릭 지수 비교",
                            text_auto='.1f',
                            color_continuous_scale='Blues')
            st.plotly_chart(fig_avg, use_container_width=True)
        
        with col_analysis2:
            # 키워드별 피크 시점 찾기
            peak_data = []
            for kw in df_ins['keyword'].unique():
                kw_data = df_ins[df_ins['keyword'] == kw]
                peak_idx = kw_data['ratio'].idxmax()
                peak_row = kw_data.loc[peak_idx]
                peak_data.append({
                    '키워드': kw,
                    '피크 날짜': peak_row['period'].strftime('%Y-%m-%d'),
                    '피크 지수': round(peak_row['ratio'], 2)
                })
            
            peak_df = pd.DataFrame(peak_data)
            st.write("**🔥 키워드별 최고 인기 시점**")
            st.dataframe(peak_df, use_container_width=True, hide_index=True)
            
            # 최근 7일 vs 이전 7일 변화율
            if len(df_ins) >= 14:
                recent_change = []
                for kw in df_ins['keyword'].unique():
                    kw_data = df_ins[df_ins['keyword'] == kw].sort_values('period')
                    if len(kw_data) >= 14:
                        recent_7 = kw_data.tail(7)['ratio'].mean()
                        prev_7 = kw_data.tail(14).head(7)['ratio'].mean()
                        change_rate = ((recent_7 - prev_7) / prev_7 * 100) if prev_7 > 0 else 0
                        recent_change.append({
                            '키워드': kw,
                            '최근 7일 평균': round(recent_7, 2),
                            '이전 7일 평균': round(prev_7, 2),
                            '변화율(%)': round(change_rate, 2)
                        })
                
                if recent_change:
                    change_df = pd.DataFrame(recent_change)
                    st.write("**📊 최근 트렌드 변화 (최근 7일 vs 이전 7일)**")
                    st.dataframe(change_df, use_container_width=True, hide_index=True)
        
        # 전체 데이터 테이블
        st.divider()
        with st.expander("📋 전체 데이터 보기"):
            display_df = df_ins.copy()
            display_df['period'] = display_df['period'].dt.strftime('%Y-%m-%d')
            st.dataframe(display_df.sort_values(['keyword', 'period'], ascending=[True, False]), 
                        use_container_width=True, hide_index=True)
            st.download_button(
                label="📥 쇼핑인사이트 데이터 다운로드 (CSV)",
                data=convert_df(display_df),
                file_name=f"shopping_insight_{start_date}_{end_date}.csv",
                mime="text/csv"
            )



    st.divider()
    st.subheader("💡 쇼핑인사이트 활용법")
    st.markdown("""
    1. **cat_id 확인 방법**: [네이버 쇼핑](https://shopping.naver.com)에서 특정 카테고리를 선택한 후 주소창의 `cat_id=` 뒤에 오는 숫자를 복사하세요.
    2. **트렌드 분석**: 클릭 지수가 급증하는 시기는 해당 상품의 제철이거나 특정 이벤트가 발생한 시점입니다.
    3. **비즈니스 접목**: 클릭 지수 변화에 맞춰 소상공인의 재고 확보 및 이벤트 마케팅을 최적화할 수 있습니다.
    """)

auth_status = "✅ 인증 완료" if (CLIENT_ID and CLIENT_SECRET) else "❌ 인증 미완료"
st.sidebar.caption(f"상태: {auth_status} | 업데이트: {datetime.now().strftime('%H:%M:%S')}")
