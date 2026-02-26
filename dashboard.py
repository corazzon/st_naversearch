import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from wordcloud import WordCloud

# 페이지 설정
st.set_page_config(page_title="Naver Market Insights", layout="wide", page_icon="⚡")

# --- 테마 설정 ---
st.sidebar.header("🎨 테마 설정")
is_dark = st.sidebar.toggle("다크 모드", value=False)
theme_cls = "dark" if is_dark else "light"
plotly_template = "plotly_dark" if is_dark else "plotly_white"

# 테마 색상 정의
if is_dark:
    bg_color = "#0E1117"    # Streamlit 기본 다크 배경과 유사한 깊은 색상
    card_bg = "#1A1C24"    # 카드 레이어 구분
    text_color = "#FFFFFF" # 최대 대비를 위해 순백색 사용
    header_color = "#79A3FF" # 밝고 부드러운 블루
    accent_color = "#00D4FF" # 형광빛 블루로 시인성 확보
    border_color = "#30363D"
    tab_bg = "#21262D"
    tab_active_bg = "#30363D"
    grid_color = "rgba(255, 255, 255, 0.1)"
else:
    bg_color = "#F8F9FA"
    card_bg = "#FFFFFF"
    text_color = "#1F2937"
    header_color = "#1E3A8A"
    accent_color = "#3B82F6"
    border_color = "#E5E7EB"
    tab_bg = "#F3F4F6"
    tab_active_bg = "#FFFFFF"
    grid_color = "rgba(0, 0, 0, 0.05)"

# Plotly 공통 레이아웃 설정 함수
def update_chart_style(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=text_color, family="'Outfit', sans-serif"),
        margin=dict(t=50, b=50, l=50, r=50),
        hoverlabel=dict(bgcolor=card_bg, font_size=13, font_family="'Outfit', sans-serif"),
        xaxis=dict(gridcolor=grid_color, zerolinecolor=grid_color),
        yaxis=dict(gridcolor=grid_color, zerolinecolor=grid_color),
    )
    return fig

# CSS 스타일링
st.markdown(f"""
    <style>
    /* 전역 배경 및 기본 텍스트 색상 */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        background-color: {bg_color};
        color: {text_color};
    }}
    
    /* 사이드바 스타일 */
    [data-testid="stSidebar"] {{
        background-color: {card_bg};
        border-right: 1px solid {border_color};
    }}
    [data-testid="stSidebar"] .stMarkdown {{
        color: {text_color};
    }}
    
    /* 메인 콘텐츠 영역 */
    .main {{ background-color: {bg_color}; color: {text_color}; }}
    
    /* 메트릭 카드 */
    .stMetric {{ 
        background-color: {card_bg}; 
        padding: 15px; 
        border-radius: 10px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
        border: 1px solid {border_color}; 
    }}
    div[data-testid="stMetricValue"] {{ color: {text_color}; }}
    div[data-testid="stMetricLabel"] {{ color: {text_color}; opacity: 0.9; font-weight: 500; }}
    
    /* 제목 스타일 */
    h1, h2, h3 {{ color: {header_color} !important; font-family: 'Outfit', sans-serif; }}
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; background-color: transparent; }}
    .stTabs [data-baseweb="tab"] {{
        padding: 10px 20px;
        background-color: {tab_bg};
        border-radius: 5px 5px 0 0;
        font-weight: 600;
        color: {text_color};
        border: none;
    }}
    .stTabs [aria-selected="true"] {{ 
        background-color: {tab_active_bg} !important; 
        border-top: 4px solid {accent_color} !important; 
        color: {accent_color} !important; 
    }}
    
    /* 위젯 라벨 및 마크다운 */
    .stMarkdown, label, .stText, p, span, div {{ color: {text_color}; }}
    .stWidgetLabel p {{ color: {text_color} !important; font-weight: 500; font-size: 1rem; }}
    
    /* 사이드바 위젯 라벨 강제 적용 */
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown p {{
        color: {text_color} !important;
        font-weight: 500;
    }}
    
    /* 익스팬더 및 카드 */
    .stExpander, [data-testid="stExpander"] {{ 
        background-color: {card_bg} !important; 
        border: 1px solid {border_color} !important; 
        border-radius: 10px; 
    }}
    /* 익스팬더 헤더 제목 강제 적용 */
    .stExpander header p, [data-testid="stExpander"] summary p, [data-testid="stExpander"] label p {{ 
        color: {header_color} !important; 
        font-weight: 600 !important; 
        font-size: 1.1rem !important; 
    }}
    
    /* 하단 푸터 */
    .fixed-footer {{
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        background-color: {card_bg}f2;
        padding: 10px 20px;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        font-size: 14px;
        font-weight: 700;
        border: 2px solid {accent_color};
    }}
    
    /* 입력창 및 선택창 스타일 보정 (BaseWeb 기반) */
    div[data-baseweb="select"] {{
        background-color: {tab_bg} !important;
        color: {text_color} !important;
    }}
    div[data-baseweb="select"] * {{
        color: {text_color} !important;
    }}
    .stTextInput>div>div>input, .stSelectbox>div>div, .stMultiSelect>div {{
        background-color: {tab_bg} !important;
        color: {text_color} !important;
        border-color: {border_color} !important;
    }}
    /* 멀티셀렉트 태그 스타일 */
    span[data-baseweb="tag"] {{
        background-color: {accent_color}33 !important;
        color: {text_color} !important;
        border: 1px solid {accent_color}77 !important;
    }}
    /* 라디오 버튼 라벨 */
    div[data-testid="stRadio"] label p {{
        color: {text_color} !important;
    }}
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
    return None, "준비 중인 기능입니다."

# --- 데이터 전처리 헬퍼 ---
def clean_html(text):
    """HTML 태그 제거"""
    if pd.isna(text): return ""
    return text.replace('<b>', '').replace('</b>', '').replace('&quot;', '"').replace('&lt;', '<').replace('&gt;', '>')

@st.cache_data
def generate_wordcloud(text):
    """텍스트로 워드클라우드 생성 (한글 폰트 지원)"""
    if not text: return None
    
    # 폰트 우선순위 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_font_path = os.path.join(current_dir, "fonts", "NanumGothic.ttf")
    mac_font_path = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
    linux_font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
    
    font_path = None
    if os.path.exists(project_font_path):
        font_path = project_font_path
    elif os.path.exists(mac_font_path):
        font_path = mac_font_path
    elif os.path.exists(linux_font_path):
        font_path = linux_font_path
        
    try:
        wc = WordCloud(
            font_path=font_path, 
            width=800, 
            height=400, 
            background_color="white",
            max_words=100
        ).generate(text)
        return wc
    except Exception:
        return WordCloud(width=800, height=400, background_color="white").generate(text)

@st.cache_data
def convert_df(df):
    """데이터프레임을 CSV로 변환 (한글 깨짐 방지 utf-8-sig)"""
    return df.to_csv(index=False).encode('utf-8-sig')

def paginate(df, page_size, key_prefix):
    """데이터프레임 페이징 및 내비게이션 UI"""
    if df is None or df.empty:
        return None
    
    total_pages = (len(df) - 1) // page_size + 1
    
    # 세션 상태 초기화
    page_key = f"{key_prefix}_current_page"
    if page_key not in st.session_state:
        st.session_state[page_key] = 1
        
    # 페이지 선택 UI
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("이전", key=f"{key_prefix}_prev", disabled=st.session_state[page_key] <= 1):
            st.session_state[page_key] -= 1
            st.rerun()
    with col2:
        st.write(f"페이지 **{st.session_state[page_key]}** / {total_pages}")
    with col3:
        if st.button("다음", key=f"{key_prefix}_next", disabled=st.session_state[page_key] >= total_pages):
            st.session_state[page_key] += 1
            st.rerun()
            
    start_idx = (st.session_state[page_key] - 1) * page_size
    end_idx = start_idx + page_size
    return df.iloc[start_idx:end_idx]

# --- 메인 UI ---
st.title("⚡ 실시간 Naver Market Insights")
st.caption("로컬 파일이 아닌, 네이버 API를 통해 실시간 데이터를 직접 분석합니다.")

# 사이드바
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
one_year_ago = today - timedelta(days=365)

date_range = st.sidebar.date_input(
    "조회 기간 선택",
    value=(one_year_ago, today),
    max_value=today,
    help="시작일과 종료일을 선택하세요."
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date = date_range[0].strftime("%Y-%m-%d")
    end_date = date_range[1].strftime("%Y-%m-%d")
else:
    start_date = one_year_ago.strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")
    st.sidebar.warning("시작일과 종료일을 모두 선택해주세요.")

st.sidebar.divider()
st.sidebar.info(f"선택된 키워드: {', '.join(keywords)}")

st.sidebar.caption("💡 10분마다 데이터가 최신화됩니다.")

st.sidebar.divider()
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

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📈 트렌드 비교", "🛍️ 실시간 쇼핑", "📝 실시간 블로그", 
    "☕ 실시간 카페", "📰 실시간 뉴스", "📊 쇼핑인사이트", "📑 종합 리포트"
])

# Tab 1: 트렌드 비교
with tab1:
    st.header(f"📈 실시간 검색어 트렌드 ({start_date} ~ {end_date})")
    st.markdown("🔗 [네이버 데이터랩에서 확인하기](https://datalab.naver.com/keyword/trendSearch.naver)")

    with st.expander("📊 분석 설정 (모드 & 인구통계)", expanded=True):
        col_mode, col_gender = st.columns(2)
        with col_mode:
            analysis_mode = st.radio(
                "분석 모드", 
                ["일반 트렌드", "성별 비교"], 
                help="일반: 선택한 필터 기준 통합 추이\n성별: 남성 vs 여성 그룹별 상세 패턴 비교"
            )
        
        with col_gender:
            selected_gender = ""
            gender_option = "전체"
            if analysis_mode != "성별 비교":
                gender_option = st.radio("성별", ["전체", "남성", "여성"], horizontal=True)
                gender_map = {"전체": "", "남성": "m", "여성": "f"}
                selected_gender = gender_map[gender_option]
            else:
                st.info("성별 비교 모드: 남성 vs 여성을 비교합니다.")
        
        age_options = ["0~12세", "13~18세", "19~24세", "25~29세", "30~34세", "35~39세", "40~44세", "45~49세", "50~54세", "55~59세", "60세 이상"]
        age_codes = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"]
        age_ref = dict(zip(age_options, age_codes))
        
        selected_ages = st.multiselect("연령대 (다중 선택 가능)", age_options, placeholder="전체 연령")
        selected_age_codes = [age_ref[a] for a in selected_ages] if selected_ages else []
    
    filter_info = []
    if analysis_mode == "일반 트렌드":
        if selected_gender: filter_info.append(f"성별: {gender_option}")
        if selected_ages: filter_info.append(f"연령: {', '.join(selected_ages)}")
    elif analysis_mode == "성별 비교":
        filter_info.append("분석: 성별 비교 (남성 vs 여성)")
        if selected_ages: filter_info.append(f"연령: {', '.join(selected_ages)}")
        
    if filter_info:
        st.caption(f"적용된 필터: {' | '.join(filter_info)}")

    df_trend = None
    err = None
    
    if analysis_mode == "일반 트렌드":
        df_trend, err = fetch_realtime_trend(keywords, start_date, end_date, selected_gender, selected_age_codes)
    
    elif analysis_mode == "성별 비교":
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
            
    if err:
        st.error(err)
    elif df_trend is not None and not df_trend.empty:
        df_trend['period'] = pd.to_datetime(df_trend['period'])
        
        st.info(f"📊 총 **{len(df_trend):,}**개의 트렌드 데이터 포인트가 분석되었습니다.")
        
        if analysis_mode == "일반 트렌드":
            fig1 = px.line(df_trend, x='period', y='ratio', color='keyword', 
                           title="실시간 검색 트렌드 추이",
                           template=plotly_template, color_discrete_sequence=px.colors.qualitative.Prism)
        
        elif analysis_mode == "성별 비교":
            fig1 = px.line(df_trend, x='period', y='ratio', color='keyword', facet_col='gender',
                           title="성별 검색 트렌드 비교 (Max 100 상대지수)",
                           template=plotly_template, color_discrete_sequence=px.colors.qualitative.Prism)
            fig1.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
            
        fig1.update_layout(hovermode="x unified")
        st.plotly_chart(update_chart_style(fig1), use_container_width=True)
        
        if analysis_mode != "일반 트렌드":
            st.caption("""
            ⚠️ **주의**: Naver DataLab 그래프의 y축(ratio)은 해당 조건 내 최댓값을 100으로 둔 **상대적 지표**입니다. 
            서로 다른 그룹 간의 절대적인 검색량 크기 비교를 의미하지 않습니다. 
            각 그룹 내에서의 추세 변화 패턴을 비교하는 목적으로 활용하세요.
            """)
        
        date_diff = (df_trend['period'].max() - df_trend['period'].min()).days
        if date_diff >= 365:
            st.divider()
            st.subheader("📅 월별 트렌드 추이")
            st.caption("분석 기간이 1년 이상이므로 월별 집계 트렌드를 함께 제공합니다.")
            
            df_monthly = df_trend.copy()
            df_monthly['year_month'] = df_monthly['period'].dt.to_period('M').astype(str)
            
            if analysis_mode == "성별 비교":
                monthly_agg = df_monthly.groupby(['year_month', 'keyword', 'gender'])['ratio'].agg(
                    평균='mean', 최대='max'
                ).reset_index()
                
                fig_monthly = px.bar(
                    monthly_agg, x='year_month', y='평균', color='keyword',
                    facet_col='gender', barmode='group',
                    title="월별 평균 검색 트렌드 (성별 비교)",
                    labels={'year_month': '월', '평균': '평균 검색 지수'},
                    template=plotly_template,
                    color_discrete_sequence=px.colors.qualitative.Prism
                )
                fig_monthly.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
            else:
                monthly_agg = df_monthly.groupby(['year_month', 'keyword'])['ratio'].agg(
                    평균='mean', 최대='max'
                ).reset_index()
                
                fig_monthly = px.bar(
                    monthly_agg, x='year_month', y='평균', color='keyword',
                    barmode='group',
                    title="월별 평균 검색 트렌드",
                    labels={'year_month': '월', '평균': '평균 검색 지수'},
                    template=plotly_template,
                    color_discrete_sequence=px.colors.qualitative.Prism
                )
            
            fig_monthly.update_layout(xaxis_tickangle=-45, hovermode="x unified")
            st.plotly_chart(update_chart_style(fig_monthly), use_container_width=True)
            
            if analysis_mode == "일반 트렌드":
                fig_monthly_line = px.line(
                    monthly_agg, x='year_month', y='최대', color='keyword',
                    title="월별 최대 검색 지수 추이",
                    labels={'year_month': '월', '최대': '최대 검색 지수'},
                    template=plotly_template,
                    markers=True,
                    color_discrete_sequence=px.colors.qualitative.Safe
                )
                st.plotly_chart(update_chart_style(fig_monthly_line), use_container_width=True)
        
        st.divider()
        group_cols = ['keyword']
        if analysis_mode == "성별 비교": group_cols.append('gender')
        
        col1, col2 = st.columns(2)
        with col1:
            avg_df = df_trend.groupby(group_cols)['ratio'].mean().reset_index().sort_values('ratio', ascending=False)
            if analysis_mode == "일반 트렌드":
                fig2 = px.bar(avg_df, x='keyword', y='ratio', color='keyword', 
                               title="평균 검색 활동 점유율", text_auto='.1f',
                               color_discrete_sequence=px.colors.qualitative.Safe)
            else:
                fig2 = px.bar(avg_df, x='keyword', y='ratio', color='gender', barmode='group',
                               title="성별/키워드별 평균 검색 강도", text_auto='.1f',
                               color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig2, use_container_width=True)
            
        with col2:
            st.subheader("🔥 키워드별 피크 & 최근 추세")
            peak_trend_data = []
            for kw in df_trend['keyword'].unique():
                kw_data = df_trend[df_trend['keyword'] == kw].sort_values('period')
                peak_row = kw_data.sort_values('ratio', ascending=False).iloc[0]
                recent_7 = kw_data.tail(7)['ratio'].mean()
                overall_avg = kw_data['ratio'].mean()
                change_vs_avg = ((recent_7 - overall_avg) / overall_avg * 100) if overall_avg > 0 else 0
                peak_trend_data.append({
                    '키워드': kw,
                    '피크 날짜': peak_row['period'].strftime('%Y-%m-%d'),
                    '피크 지수': round(float(peak_row['ratio']), 1),
                    '최근7일 평균': round(recent_7, 1),
                    '전체 대비(%)': round(change_vs_avg, 1)
                })
            peak_trend_df = pd.DataFrame(peak_trend_data)
            st.dataframe(peak_trend_df, use_container_width=True, hide_index=True)
        
        st.divider()
        st.subheader("📊 키워드별 상세 기술 통계")
        detailed_stats = []
        for kw in df_trend['keyword'].unique():
            kw_data = df_trend[df_trend['keyword'] == kw].sort_values('period')
            ratio = kw_data['ratio']
            mean_val = ratio.mean()
            std_val = ratio.std()
            cv = (std_val / mean_val * 100) if mean_val > 0 else 0
            recent_7 = kw_data.tail(7)['ratio'].mean()
            recent_30 = kw_data.tail(30)['ratio'].mean()
            detailed_stats.append({
                '키워드': kw, '평균': round(mean_val, 2), '중앙값': round(ratio.median(), 2),
                '최솟값': round(ratio.min(), 2), '최댓값': round(ratio.max(), 2),
                '표준편차': round(std_val, 2), '변동계수(%)': round(cv, 1),
                '최근7일 평균': round(recent_7, 2), '최근30일 평균': round(recent_30, 2)
            })
        stats_df = pd.DataFrame(detailed_stats)
        st.dataframe(stats_df, use_container_width=True, hide_index=True)
        
        with st.expander("💡 통계 지표 해석 가이드"):
            st.markdown("""
            | 지표 | 설명 |
            |------|------|
            | **평균** | 분석 기간 전체의 평균 검색 지수 |
            | **중앙값** | 데이터의 정중앙 값 (이상치 영향을 덜 받음) |
            | **표준편차** | 검색 지수의 흩어진 정도 (클수록 변동이 큼) |
            | **변동계수(%)** | 평균 대비 표준편차 비율. 키워드 간 변동성을 비교할 때 유용 |
            """)

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
    if not keywords:
        st.warning("분석할 키워드를 사이드바에서 입력해주세요.")
    else:
        main_kw = st.selectbox("심층 분석할 키워드 선택", keywords, index=0)
        st.header(f"🛍️ '{main_kw}' 실시간 마켓 심층 분석")
        st.caption("카테고리 필터링, 가격 분석, 브랜드 인사이트, 판매처 비교 등 종합적인 쇼핑 데이터 분석")
        
        df_shop, shop_err = fetch_realtime_shopping([main_kw])
        if shop_err:
            st.error(shop_err)
        elif df_shop is not None:
            if 'lprice' in df_shop.columns:
                df_shop['lprice'] = pd.to_numeric(df_shop['lprice'], errors='coerce')
            df_shop['title'] = df_shop['title'].apply(clean_html)

            df_filtered = df_shop.copy()
            if selected_categories:
                df_filtered = df_shop[df_shop['category1'].isin(selected_categories)]
                if len(df_filtered) == 0:
                    st.warning(f"선택한 카테고리에 해당하는 상품이 없습니다. 전체 데이터를 표시합니다.")
                    df_filtered = df_shop.copy()
                else:
                    st.info(f"선택한 카테고리: {', '.join(selected_categories)} (총 {len(df_filtered)}개 상품)")

            df_filtered = df_filtered.dropna(subset=['lprice'])

            st.divider()
            st.markdown("### 📊 핵심 지표")
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("수집 상품 수", f"{len(df_filtered):,}개")
            m2.metric("평균 가격", f"{int(df_filtered['lprice'].mean()):,}원" if not df_filtered.empty else "-")
            m3.metric("중앙값 가격", f"{int(df_filtered['lprice'].median()):,}원" if not df_filtered.empty else "-")
            m4.metric("최저가", f"{int(df_filtered['lprice'].min()):,}원" if not df_filtered.empty else "-")
            m5.metric("활성 판매처", f"{df_filtered['mallName'].nunique()}개")

            st.divider()
            st.markdown("### 💰 가격 분포 및 통계 분석")
            col1, col2 = st.columns([3, 2])
            with col1:
                fig_hist = px.histogram(
                    df_filtered, x='lprice', nbins=50,
                    title=f"'{main_kw}' 가격 분포 (총 {len(df_filtered)}개 상품)",
                    labels={'lprice': '최저가(원)', 'count': '상품 수'},
                    color_discrete_sequence=['#1976d2'],
                    marginal="box", template=plotly_template
                )
                if not df_filtered.empty:
                    fig_hist.add_vline(x=df_filtered['lprice'].mean(), line_dash="dash", line_color="red", annotation_text="평균")
                    fig_hist.add_vline(x=df_filtered['lprice'].median(), line_dash="dash", line_color="green", annotation_text="중앙값")
                st.plotly_chart(update_chart_style(fig_hist), use_container_width=True)

            with col2:
                st.markdown("##### 📈 가격 통계 요약")
                if not df_filtered.empty:
                    price_stats_df = pd.DataFrame({
                        '지표': ['평균', '중앙값', '최소값', '최대값', '표준편차'],
                        '값': [
                            f"{int(df_filtered['lprice'].mean()):,}원", f"{int(df_filtered['lprice'].median()):,}원",
                            f"{int(df_filtered['lprice'].min()):,}원", f"{int(df_filtered['lprice'].max()):,}원",
                            f"{int(df_filtered['lprice'].std()):,}원"
                        ]
                    })
                    st.dataframe(price_stats_df, use_container_width=True, hide_index=True)

            st.divider()
            st.markdown("### 📂 카테고리별 상세 분석")
            col3, col4 = st.columns([2, 2])
            with col3:
                cat_counts = df_filtered.groupby('category1').size()
                top_cats_for_box = cat_counts[cat_counts >= 3].index
                cat_data = df_filtered[df_filtered['category1'].isin(top_cats_for_box)]
                if not cat_data.empty:
                    fig_box = px.box(cat_data, x='category1', y='lprice', title="카테고리별 가격 분포", color='category1', template=plotly_template)
                    st.plotly_chart(update_chart_style(fig_box), use_container_width=True)

            with col4:
                if not df_filtered.empty:
                    cat_summary = df_filtered.groupby('category1').agg({'lprice': ['count', 'mean']}).round(0)
                    cat_summary.columns = ['상품수', '평균가']
                    cat_summary = cat_summary.sort_values('상품수', ascending=False).head(10)
                    fig_cat = go.Figure()
                    fig_cat.add_trace(go.Bar(name='상품 수', x=cat_summary.index, y=cat_summary['상품수'], marker_color='lightblue'))
                    fig_cat.add_trace(go.Scatter(name='평균가', x=cat_summary.index, y=cat_summary['평균가'], marker_color='red', yaxis='y2', mode='lines+markers'))
                    fig_cat.update_layout(title="카테고리별 상품 수 & 평균가", yaxis2=dict(overlaying="y", side="right"), template=plotly_template)
                    st.plotly_chart(fig_cat, use_container_width=True)

            st.divider()
            st.markdown("### 🏪 판매처(쇼핑몰) 분석")
            col5, col6 = st.columns([2, 2])
            with col5:
                mall_counts = df_filtered['mallName'].value_counts().head(15)
                fig_mall = px.bar(x=mall_counts.values, y=mall_counts.index, orientation='h', title="주요 판매 쇼핑몰 Top 15", template=plotly_template)
                st.plotly_chart(update_chart_style(fig_mall), use_container_width=True)
            with col6:
                mall_avg = df_filtered.groupby('mallName')['lprice'].agg(['mean', 'count']).round(0)
                mall_avg = mall_avg[mall_avg['count'] >= 5].sort_values('mean', ascending=False).head(10)
                if not mall_avg.empty:
                    fig_mall_price = px.scatter(mall_avg, x='count', y='mean', size='count', color='mean', title="판매처별 평균가 vs 상품 수", template=plotly_template)
                    st.plotly_chart(update_chart_style(fig_mall_price), use_container_width=True)

            st.divider()
            st.markdown("### 🏷️ 브랜드 분석")
            def extract_brand(title):
                import re
                bracket_match = re.search(r'\[(.*?)\]', title)
                if bracket_match: return bracket_match.group(1)
                words = title.split()
                return words[0] if words else "기타"
            df_filtered['brand'] = df_filtered['title'].apply(extract_brand)
            brand_analysis = df_filtered.groupby('brand').agg({'lprice': ['count', 'mean']}).round(0)
            brand_analysis.columns = ['상품수', '평균가']
            brand_analysis = brand_analysis[brand_analysis['상품수'] >= 3].sort_values('상품수', ascending=False).head(15)
            if not brand_analysis.empty:
                fig_brand = px.bar(brand_analysis, x=brand_analysis.index, y='상품수', title="주요 브랜드 Top 15", color='평균가', template=plotly_template)
                st.plotly_chart(update_chart_style(fig_brand), use_container_width=True)

            st.divider()
            col_list_title, col_view_mode = st.columns([3, 1])
            with col_list_title: st.markdown("### 🛒 실시간 개별 상품 리스트")
            with col_view_mode: view_mode = st.radio("보기 모드", ["목록보기", "섬네일 목록"], horizontal=True, key="shop_view_mode")

            if view_mode == "목록보기":
                paged_df = paginate(df_filtered, 20, "shop_list_merged")
                if paged_df is not None:
                    for idx, row in paged_df.iterrows():
                        with st.container():
                            col_img, col_info = st.columns([1, 4])
                            with col_img:
                                if row.get('image'): st.image(row['image'], use_container_width=True)
                            with col_info:
                                st.markdown(f"### [{row['title']}]({row['link']})")
                                st.write(f"**💰 최저가:** {int(row['lprice']):,}원 | **📁 카테고리:** {row['category1']}")
                                st.link_button("상품 보러가기", row['link'], use_container_width=True)
                            st.divider()
            else:
                paged_df = paginate(df_filtered, 12, "shop_thumb_merged")
                if paged_df is not None:
                    cols_per_row = 4
                    for i in range(0, len(paged_df), cols_per_row):
                        cols = st.columns(cols_per_row)
                        for j in range(cols_per_row):
                            if i + j < len(paged_df):
                                row = paged_df.iloc[ i + j ]
                                with cols[j]:
                                    if row.get('image'): st.image(row['image'], use_container_width=True)
                                    st.markdown(f"**[{row['title']}]({row['link']})**")
                                    st.write(f"💰 {int(row['lprice']):,}원")
                                    st.link_button("보기", row['link'], use_container_width=True)

            st.download_button("📥 쇼핑 데이터 다운로드", convert_df(df_filtered), f"shop_{datetime.now().strftime('%Y%m%d')}.csv")

# Tab 3: 실시간 블로그
with tab3:
    st.header(f"📝 실시간 블로그 반응")
    df_blog, blog_err = fetch_realtime_blog(keywords)
    if blog_err:
        st.error(blog_err)
    elif df_blog is not None:
        df_blog['title'] = df_blog['title'].apply(clean_html)
        df_blog['postdate'] = pd.to_datetime(df_blog['postdate'], format='%Y%m%d', errors='coerce')
        blog_daily = df_blog.groupby('postdate').size().reset_index(name='content_count')
        fig5 = px.bar(blog_daily, x='postdate', y='content_count', title="최근 일별 게시물 분포", template=plotly_template)
        st.plotly_chart(update_chart_style(fig5), use_container_width=True)
        st.subheader("📝 최신 블로그 콘텐츠 리스트")
        st.dataframe(df_blog[['title', 'bloggername', 'postdate', 'link']].sort_values('postdate', ascending=False).head(50), use_container_width=True)

# Tab 4: 실시간 카페
with tab4:
    st.header(f"☕ 실시간 카페 커뮤니티 반응")
    df_cafe, cafe_err = fetch_realtime_cafe(keywords)
    if cafe_err:
        st.error(cafe_err)
    elif df_cafe is not None:
        df_cafe['title'] = df_cafe['title'].apply(clean_html)
        cafe_counts = df_cafe['cafename'].value_counts().head(10).reset_index()
        cafe_counts.columns = ['카페명', '게시물 수']
        fig_cafe = px.bar(cafe_counts, x='게시물 수', y='카페명', orientation='h', title="주요 활동 카페 TOP 10", template=plotly_template)
        st.plotly_chart(update_chart_style(fig_cafe), use_container_width=True)
        st.subheader("👥 최신 카페 게시물 리스트")
        st.dataframe(df_cafe[['title', 'cafename', 'cafeurl']].head(50), use_container_width=True)

# Tab 5: 실시간 뉴스
with tab5:
    st.header(f"📰 실시간 뉴스 이슈")
    df_news, news_err = fetch_realtime_news(keywords)
    if news_err:
        st.error(news_err)
    elif df_news is not None:
        df_news['title'] = df_news['title'].apply(clean_html)
        df_news['pubDate'] = pd.to_datetime(df_news['pubDate'], errors='coerce')
        news_daily = df_news.groupby(df_news['pubDate'].dt.date).size().reset_index(name='news_count')
        fig_news = px.area(news_daily, x='pubDate', y='news_count', title="최근 뉴스 발행 추이", template=plotly_template)
        st.plotly_chart(update_chart_style(fig_news), use_container_width=True)
        st.subheader("🗞️ 최신 관련 뉴스 리스트")
        st.dataframe(df_news[['title', 'pubDate', 'link']].sort_values('pubDate', ascending=False).head(50), use_container_width=True)

# Tab 6: 쇼핑인사이트
with tab6:
    st.header("📊 네이버 쇼핑인사이트 키워드 클릭 트렌드")
    with st.expander("🛠️ 쇼핑인사이트 설정", expanded=True):
        col_cat, col_dates = st.columns([1, 1])
        with col_cat:
            cat_list = {"생활/건강": "50000008", "식품": "50000006", "화장품/미용": "50000002", "디지털/가전": "50000003"}
            selected_cat_name = st.selectbox("카테고리 분야", list(cat_list.keys()))
            cat_id = cat_list[selected_cat_name]
    
    df_ins, ins_err, raw_res = fetch_shopping_insight_trend(cat_id, keywords, start_date, end_date)
    if ins_err:
        st.error(ins_err)
    elif df_ins is not None and not df_ins.empty:
        df_ins['period'] = pd.to_datetime(df_ins['period'])
        fig_ins = px.line(df_ins, x='period', y='ratio', color='keyword', title=f"{selected_cat_name} 분야 키워드 클릭 추이", template=plotly_template)
        st.plotly_chart(update_chart_style(fig_ins), use_container_width=True)

# Tab 7: 종합 리포트
with tab7:
    st.header("📑 마켓 인사이트 종합 리포트")
    if not keywords:
        st.warning("분석할 키워드를 입력해주세요.")
    else:
        st.info("💡 실시간 데이터를 기반으로 생성된 자동 요약 리포트입니다.")
        report_text = f"### 분석 키워드: {', '.join(keywords)}\n\n- 트렌드: 최근 검색량 변동성 확인 필요\n- 쇼핑: 최저가 경쟁 심화 여부 분석 중"
        st.markdown(report_text)
        st.download_button("📥 리포트 다운로드", report_text, file_name="report.txt")

auth_status = "✅ 인증 완료" if (CLIENT_ID and CLIENT_SECRET) else "❌ 인증 미완료"
st.sidebar.caption(f"상태: {auth_status} | 업데이트: {datetime.now().strftime('%H:%M:%S')}")
st.sidebar.caption("[© 오늘코드](https://www.youtube.com/todaycode)")
st.markdown('<div class="fixed-footer"><a href="https://www.youtube.com/todaycode" target="_blank">📺 유튜브 오늘코드</a></div>', unsafe_allow_html=True)
