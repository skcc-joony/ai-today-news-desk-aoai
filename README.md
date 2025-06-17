# Bloomberg Asia 오늘의 뉴스 AI 분석 서비스

> **Azure OpenAI + FAISS 기반 RAG(검색·생성형) AI 뉴스 요약/분석 에이전트**
> Bloomberg Asia의 최신 뉴스 헤드라인을 자동 크롤링, 임베딩 및 유사 뉴스 검색을 통해
> "오늘의 핫이슈", "핫 키워드" 등 실시간 AI 뉴스 분석 서비스를 제공합니다.

---

## 1. 과제 개요 - 프로젝트 기획 배경 및 핵심 내용

* **기획 배경**
  글로벌 경제/금융 뉴스는 실무자와 투자자 모두에게 필수 정보입니다.
  Bloomberg 등 프리미엄 뉴스 미디어의 오늘의 헤드라인을
  한국 사용자가 실시간 요약/분석받을 수 있는 AI 에이전트가 필요했습니다.

* **해결하고자 하는 문제**
  방대한 영문 뉴스의 신속한 해석, 주요 이슈/키워드 추출,
  개인화된 AI 뉴스 요약 서비스 부재

* **AI Agent의 핵심 기능**

  * Bloomberg Asia의 오늘 뉴스 자동 크롤링
  * Azure OpenAI 임베딩 + FAISS로 벡터DB화, 질문과 유사 뉴스 검색
  * AI(GPT-4o)가 뉴스 기반으로 요약/핫이슈/키워드 분석 답변 제공

* **기대하는 사용자 경험**

  * 별도의 데이터 업로드 없이 “버튼 한 번”으로 오늘의 최신 뉴스 갱신
  * 한글로 직관적인 AI 요약/분석/참고 뉴스 제시
  * 누구나 웹에서 바로 사용, 빠른 정보 습득

---

## 2. 기술 구성 - 프로젝트에 포함된 주요 기술 스택

**1) Prompt Engineering**

* 역할 프롬프트(뉴스 요약 비서)
* 다양한 유형(핫이슈, 키워드 등) 질문에도 일관된 응답 설계

**2) Azure OpenAI 활용**

* Embedding/Chat API (임베딩/생성 모두 Azure 배포이름 사용)
* openai-python 1.x 표준방식

**3) RAG (Retrieval-Augmented Generation)**

* 크롤링 뉴스 임베딩→FAISS 저장→질문 임베딩→유사뉴스 검색→AI 생성형 답변

**4) Streamlit 및 서비스 개발/패키징**

* 웹UI, 환경변수 관리, 모듈화, data 폴더 자동생성

---

## 3. 주요 기능 및 동작 시나리오 - AI Agent 사용자 흐름

### 3-1. 사용자 Flow 요약

1. 사용자가 Streamlit 웹페이지 접속
2. "오늘 뉴스 최신화" 버튼 클릭
   → Bloomberg Asia 크롤링 → 임베딩 → FAISS 저장
3. 사용자가 자연어 질문 입력(핫이슈, 키워드 등)
4. 질문 임베딩 후, FAISS에서 유사 뉴스 검색
5. 뉴스 context + 질문을 Azure OpenAI GPT-4o로 전송
6. AI 답변 + 참고 뉴스(타이틀/링크) UI에 표시

---

## 4. 실행법(Quickstart)

1. **클론 & 환경 준비**

   ```bash
   git clone https://github.com/skcc-joony/ai-today-news-desk-aoai.git
   cd ai-today-news-desk-aoai
   python -m venv .venv
   .venv\Scripts\activate           # (Windows)
   source .venv/Scripts/activate    # (Linux)
   pip install -r requirements.txt
   ```

2. **.env 파일 생성**

   ```
   AZURE_OPENAI_ENDPOINT=https://skcc-atl-dev-openai-01.openai.azure.com/
   AZURE_OPENAI_API_KEY=<API_KEY>
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   EMBEDDING_DEPLOY=text-embedding-3-large     # Azure Portal 배포 이름
   CHAT_DEPLOY=gpt-4o            # Azure Portal 배포 이름
   ```

3. **실행**

   ```bash
   python -m streamlit run app.py
   ```

---

## 5. 프로젝트 구조

```
├── app.py                # Streamlit 메인 파이프라인
├── data/                 # 뉴스/임베딩/FAISS 저장
├── requirements.txt      # 패키지 목록
├── README.md             # 읽어줘
├── .env                  # (직접 생성) Azure OpenAI 환경변수
└── README.md
```

---

## 6. 사용 기술 및 참고

* **Azure OpenAI (임베딩/Chat, GPT-4o 등)**
* **FAISS 벡터DB**
* **requests, BeautifulSoup (크롤링)**
* **Streamlit UI**
* **python-dotenv**

---

## 7. 확장 아이디어

* 뉴스 본문/다른 미디어 크롤링
* 다국어 번역, 키워드 통계/시각화
* Docker 패키징 및 클라우드 배포 등

---

## 8. 문의

* 피드백/지원: [ai.admin@ai-today-news-desk.com](mailto:ai.admin@ai-today-news-desk.com)

---

## LICENSE

MIT License
Copyright (c) 2025 \[ai.admin/ai-today-news-desk]
