# 안티그래비티로 네이버 API 활용 보고서와 대시보드 만들기 
* 📺 유튜브 영상 ▶️ https://youtu.be/C8WxCXHSiko

[![YouTube](https://img.youtube.com/vi/C8WxCXHSiko/maxresdefault.jpg)](https://youtu.be/C8WxCXHSiko)


## 네이버 API 발급 방법 안내

* 네이버 검색 API, 데이터랩 API 등 네이버 오픈 API를 사용하기 위해 필요한 **애플리케이션 등록 및 인증 키 발급 절차**

---

## 1. 네이버 개발자 센터 접속 및 로그인

먼저 네이버 개발자 센터에 접속합니다.

* 주소: [https://developers.naver.com](https://developers.naver.com)
* 네이버 개인 계정 또는 조직 계정으로 로그인합니다.

로그인하지 않으면 애플리케이션 등록 및 API 키 발급이 불가능합니다.

---

## 2. 애플리케이션 등록 메뉴 이동

로그인 후 상단 메뉴에서 다음 경로로 이동합니다. 
* [애플리케이션 - NAVER Developers](https://developers.naver.com/apps/#/register)

```
Application > 내 애플리케이션 > 애플리케이션 등록
```

해당 메뉴에서 새로운 애플리케이션을 생성할 수 있습니다.

---

## 3. 애플리케이션 기본 정보 입력

애플리케이션 등록 화면에서 다음 항목을 입력합니다.

### 3-1. 애플리케이션 이름

* 자유롭게 지정 가능
* 예: `마케팅 데이터 분석`, `검색 트렌드 수집 도구`

### 3-2. 사용 API 선택

* 필요한 API만 선택

  * 검색 API (블로그, 뉴스, 쇼핑 등)
  * 데이터랩 API (검색어 트렌드, 쇼핑인사이트)
* 선택하지 않은 API는 호출할 수 없습니다.

### 3-3. 서비스 환경 및 URL

* 웹 서비스: `http://localhost` 또는 실제 서비스 URL
* 테스트·개발 단계에서도 URL 입력은 필수입니다.

---

## 4. 애플리케이션 등록 완료 및 인증 정보 확인

애플리케이션 등록이 완료되면 다음 정보가 자동으로 발급됩니다.

* Client ID
* Client Secret

이 두 값은 네이버 API 호출 시 **인증 정보**로 사용됩니다.

---

## 5. Client ID / Client Secret 관리 시 주의사항

* Client Secret은 비밀번호와 동일한 민감 정보입니다.
* 다음 사항을 반드시 준수하는 것이 좋습니다.

  * GitHub, 노션, 블로그 등에 절대 그대로 노출하지 않기
  * 코드에는 직접 하드코딩하지 않고 환경 변수로 관리
  * 외부 유출 시 즉시 재발급 처리

예시(환경 변수 사용 개념):

```
NAVER_CLIENT_ID=발급받은_ID
NAVER_CLIENT_SECRET=발급받은_SECRET
```

---

## 6. API별 추가 설정 및 확인 사항

* 일부 API는 호출 한도(QPS, 일일 제한)가 다릅니다.
* 데이터랩 API는 검색 API보다 일일 호출 한도가 낮습니다.

---

# 🚀 대시보드 실행 가이드

아래 두 가지 방법 중 원하는 방식을 선택하여 대시보드를 실행할 수 있습니다.

---

## 방법 1: 내 컴퓨터(로컬)에서 직접 실행하기

> 💡 Python이 설치되어 있어야 합니다. (Python 3.13 이상 권장)

### 1단계: 저장소 복제(Clone)

터미널(또는 명령 프롬프트)을 열고, 원하는 작업 폴더로 이동한 뒤 아래 명령어를 입력합니다.

```bash
git clone https://github.com/corazzon/st_naversearch.git
cd st_naversearch
```

* `git clone`은 GitHub에 있는 프로젝트 파일 전체를 내 컴퓨터로 복사하는 명령어입니다.
* `cd st_naversearch`는 복사된 폴더 안으로 이동하는 명령어입니다.

### 2단계: 가상환경 생성 및 의존성 설치

프로젝트 전용 가상환경을 만들고, 필요한 라이브러리를 설치합니다.

```bash
# 가상환경 생성 (uv 사용 시)
uv venv .venv

# 가상환경 활성화 (Mac / Linux)
source .venv/bin/activate

# 가상환경 활성화 (Windows)
.venv\Scripts\activate

# 라이브러리 설치
pip install -r requirements.txt
```

* 가상환경을 사용하면 다른 프로젝트와 라이브러리 버전이 충돌하는 것을 방지할 수 있습니다.
* `requirements.txt`에는 `streamlit`, `pandas`, `plotly` 등 이 프로젝트에 필요한 모든 패키지가 명시되어 있습니다.

### 3단계: 환경 변수(.env) 설정

프로젝트 폴더 최상위에 `.env` 파일을 만들고, 위에서 발급받은 API 키를 입력합니다.

```text
NAVER_CLIENT_ID=내_클라이언트_ID
NAVER_CLIENT_SECRET=내_클라이언트_시크릿
```

* ⚠️ **주의**: 등호(`=`) 앞뒤에 공백이 없어야 하며, 따옴표 없이 값만 입력합니다.

### 4단계: 대시보드 실행

```bash
streamlit run dashboard.py
```

* 실행 후 터미널에 `http://localhost:8501` 주소가 표시됩니다.
* 웹 브라우저가 자동으로 열리며, 대시보드를 확인할 수 있습니다.
* 종료하려면 터미널에서 `Ctrl + C`를 누르면 됩니다.

---

## 방법 2: Streamlit Community Cloud에 무료 배포하기

> 💡 GitHub 계정과 Streamlit Cloud 계정이 필요합니다. 별도의 서버 비용 없이 무료로 배포할 수 있습니다.

### 1단계: GitHub에 저장소 준비

* 이미 이 저장소를 Fork 했거나, 본인의 GitHub 계정에 프로젝트가 업로드되어 있어야 합니다.
* 저장소에 아래 파일들이 반드시 포함되어 있는지 확인합니다.
  * `dashboard.py` — 메인 대시보드 코드
  * `requirements.txt` — 의존성 패키지 목록

### 2단계: Streamlit Cloud 접속 및 로그인

* [https://share.streamlit.io](https://share.streamlit.io) 에 접속합니다.
* **Continue with GitHub** 버튼을 클릭하여 GitHub 계정으로 로그인합니다.

### 3단계: 새 앱 배포

1. 우측 상단의 **New app** 버튼을 클릭합니다.
2. 아래 항목을 입력합니다.
   * **Repository**: `corazzon/st_naversearch` (본인 저장소 경로)
   * **Branch**: `main`
   * **Main file path**: `dashboard.py`
3. **Deploy!** 버튼을 클릭합니다.

### 4단계: API 키를 Secrets에 등록

배포 후 API 키가 없으면 데이터를 불러올 수 없습니다. Streamlit Cloud의 **Secrets** 기능을 사용하여 안전하게 키를 등록합니다.

1. 배포된 앱 페이지에서 우측 하단 **⋮ (메뉴)** → **Settings** 클릭
2. 왼쪽 메뉴에서 **Secrets** 선택
3. 아래 내용을 입력하고 **Save** 클릭

```toml
NAVER_CLIENT_ID = "내_클라이언트_ID"
NAVER_CLIENT_SECRET = "내_클라이언트_시크릿"
```

* ⚠️ Secrets에서는 **TOML 형식**을 사용하므로, 값을 **큰따옴표**로 감싸야 합니다.
* 저장 후 앱이 자동으로 재시작되며, API 데이터가 정상적으로 표시됩니다.

### 배포 완료! 🎉

* 배포가 완료되면 `https://본인계정-st-naversearch.streamlit.app` 형태의 고유 URL이 생성됩니다.
* 이 URL을 통해 누구나 웹 브라우저에서 대시보드에 접속할 수 있습니다.
* GitHub에 코드를 Push하면 Streamlit Cloud가 자동으로 변경 사항을 감지하고 재배포합니다.

---

## ❓ 자주 묻는 질문 (FAQ)

| 문제 | 해결 방법 |
|------|-----------|
| `ModuleNotFoundError` 발생 | `pip install -r requirements.txt`로 패키지를 재설치해 주세요. |
| 포트 충돌 (`8501` 사용 중) | `streamlit run dashboard.py --server.port 8502`로 포트를 변경합니다. |
| API 데이터가 표시되지 않음 | `.env` 파일(로컬) 또는 Secrets(Cloud)에 API 키가 올바르게 입력되었는지 확인합니다. |
| 워드클라우드 한글이 깨짐 | `fonts/` 폴더에 `NanumGothic.ttf` 파일을 추가하거나, Cloud 환경에서는 자동 대체 폰트를 사용합니다. |
