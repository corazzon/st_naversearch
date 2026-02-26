import streamlit as st
import pandas as pd
import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from wordcloud import WordCloud

def get_api_keys():
    cid, csec = None, None
    try:
        if 'NAVER_CLIENT_ID' in st.secrets:
            cid = st.secrets['NAVER_CLIENT_ID']
            csec = st.secrets['NAVER_CLIENT_SECRET']
    except Exception:
        pass
    
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

@st.cache_data(ttl=600)
def fetch_realtime_trend(keywords, start_date, end_date, gender=None, ages=None):
    if not CLIENT_ID or not CLIENT_SECRET: return None, "인증 키 미설정"
    url = "https://openapi.naver.com/v1/datalab/search"
    body = {
        "startDate": start_date, "endDate": end_date,
        "timeUnit": "date",
        "keywordGroups": [{"groupName": k, "keywords": [k]} for k in keywords]
    }
    if gender: body["gender"] = gender
    if ages: body["ages"] = ages
    res = requests.post(url, headers=HEADERS, data=json.dumps(body))
    if res.status_code == 200:
        dfs = [pd.DataFrame(r['data']).assign(keyword=r['title']) for r in res.json()['results']]
        return pd.concat(dfs), None
    return None, f"Trend API Error: {res.status_code}"

@st.cache_data(ttl=600)
def fetch_realtime_shopping(keywords):
    if not CLIENT_ID or not CLIENT_SECRET: return None, "인증 키 미설정"
    all_items = []
    for kw in keywords:
        url = f"https://openapi.naver.com/v1/search/shop.json?query={kw}&display=100"
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            items = res.json().get('items', [])
            for item in items: item['search_keyword'] = kw
            all_items.extend(items)
    return pd.DataFrame(all_items) if all_items else None, None

@st.cache_data(ttl=600)
def fetch_realtime_blog(keywords):
    if not CLIENT_ID or not CLIENT_SECRET: return None, "인증 키 미설정"
    all_items = []
    for kw in keywords:
        url = f"https://openapi.naver.com/v1/search/blog.json?query={kw}&display=100"
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            items = res.json().get('items', [])
            for item in items: item['search_keyword'] = kw
            all_items.extend(items)
    return pd.DataFrame(all_items) if all_items else None, None

@st.cache_data(ttl=600)
def fetch_realtime_cafe(keywords):
    if not CLIENT_ID or not CLIENT_SECRET: return None, "인증 키 미설정"
    all_items = []
    for kw in keywords:
        url = f"https://openapi.naver.com/v1/search/cafearticle.json?query={kw}&display=100"
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            items = res.json().get('items', [])
            for item in items: item['search_keyword'] = kw
            all_items.extend(items)
    return pd.DataFrame(all_items) if all_items else None, None

@st.cache_data(ttl=600)
def fetch_realtime_news(keywords):
    if not CLIENT_ID or not CLIENT_SECRET: return None, "인증 키 미설정"
    all_items = []
    for kw in keywords:
        url = f"https://openapi.naver.com/v1/search/news.json?query={kw}&display=100"
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            items = res.json().get('items', [])
            for item in items: item['search_keyword'] = kw
            all_items.extend(items)
    return pd.DataFrame(all_items) if all_items else None, None

@st.cache_data(ttl=600)
def fetch_shopping_insight_trend(cat_id, keywords, start_date, end_date):
    if not CLIENT_ID or not CLIENT_SECRET: return None, "인증 키 미설정", None
    url = "https://openapi.naver.com/v1/datalab/shopping/category/keywords"
    body = {
        "startDate": start_date, "endDate": end_date, "timeUnit": "date",
        "category": cat_id, "keyword": [{"name": k, "param": [k]} for k in keywords]
    }
    res = requests.post(url, headers=HEADERS, data=json.dumps(body))
    try: response_data = res.json()
    except: response_data = None
    if res.status_code == 200:
        results = response_data.get('results', []) if response_data else []
        if not results: return pd.DataFrame(), None, response_data
        dfs = []
        for r in results:
            if 'data' in r and r['data']:
                df = pd.DataFrame(r['data'])
                df['keyword'] = r['title']
                dfs.append(df)
        return pd.concat(dfs) if dfs else pd.DataFrame(), None, response_data
    return None, f"API 오류: {res.status_code}", response_data

def clean_html(text):
    if pd.isna(text): return ""
    return text.replace('<b>', '').replace('</b>', '').replace('&quot;', '"').replace('&lt;', '<').replace('&gt;', '>')

@st.cache_data
def generate_wordcloud(text):
    if not text: return None
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_font_path = os.path.join(current_dir, "fonts", "NanumGothic.ttf")
    mac_font_path = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
    linux_font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
    font_path = next((p for p in [project_font_path, mac_font_path, linux_font_path] if os.path.exists(p)), None)
    try:
        return WordCloud(font_path=font_path, width=800, height=400, background_color="white", max_words=100).generate(text)
    except:
        return WordCloud(width=800, height=400, background_color="white").generate(text)

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8-sig')

def paginate(df, page_size, key_prefix):
    if df is None or df.empty: return None
    total_pages = (len(df) - 1) // page_size + 1
    page_key = f"{key_prefix}_current_page"
    if page_key not in st.session_state: st.session_state[page_key] = 1
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("이전", key=f"{key_prefix}_prev", disabled=st.session_state[page_key] <= 1):
            st.session_state[page_key] -= 1
            st.rerun()
    with col2: st.write(f"페이지 **{st.session_state[page_key]}** / {total_pages}")
    with col3:
        if st.button("다음", key=f"{key_prefix}_next", disabled=st.session_state[page_key] >= total_pages):
            st.session_state[page_key] += 1
            st.rerun()
    start_idx = (st.session_state[page_key] - 1) * page_size
    return df.iloc[start_idx : start_idx + page_size]
