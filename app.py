import os
import requests
import streamlit as st
import numpy as np
from bs4 import BeautifulSoup
import openai
import faiss
from dotenv import load_dotenv

# --- 환경변수 로딩 ---
load_dotenv()
AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
AZURE_OPENAI_API_KEY = os.environ["AZURE_OPENAI_API_KEY"]
AZURE_OPENAI_API_VERSION = os.environ["AZURE_OPENAI_API_VERSION"]
EMBEDDING_DEPLOY = os.environ["EMBEDDING_DEPLOY"]
CHAT_DEPLOY = os.environ["CHAT_DEPLOY"]

openai.api_type = "azure"
openai.api_key = AZURE_OPENAI_API_KEY
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_version = AZURE_OPENAI_API_VERSION

NEWS_FILE = "data/news_today.txt"
EMBEDDINGS_FILE = "data/faiss.index"
NEWS_JSON = "data/news_list.npy"

def ensure_data_dir():
    if not os.path.exists("data"):
        os.makedirs("data")

# --- 1. Bloomberg Asia 뉴스 크롤링 ---
def crawl_bloomberg_asia():
    url = "https://www.bloomberg.com/asia"
    resp = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, verify=False)
    soup = BeautifulSoup(resp.text, "html.parser")
    results = []

    # 1. Top headline 방식 (최근 기준)
    for tag in soup.select('a[data-tracking-context="section_headline"]'):
        title = tag.get_text(strip=True)
        link = tag.get('href')
        if link and not link.startswith('http'):
            link = "https://www.bloomberg.com" + link
        if title and link and link.startswith("https://www.bloomberg.com"):
            results.append({"title": title, "link": link})

    # 2. 혹시 안 나오면 backup으로 /news/articles/ 경로 대상
    if not results:
        for tag in soup.find_all("a"):
            title = tag.get_text(strip=True)
            link = tag.get("href")
            if title and link and "/news/articles/" in link:
                if not link.startswith('http'):
                    link = "https://www.bloomberg.com" + link
                results.append({"title": title, "link": link})

    # 3. 30개
    return results[:30]


# --- 2. 임베딩 생성 (Azure OpenAI) ---
def get_azure_embedding(texts):
    results = []
    for text in texts:
        response = openai.embeddings.create(
            input=text,
            model=EMBEDDING_DEPLOY  # Azure 배포이름!
        )
        vec = response.data[0].embedding
        results.append(np.array(vec, dtype=np.float32))
    return results


# --- 3. FAISS 벡터DB 생성 ---
def build_faiss_db(news_list):
    texts = [n["title"] for n in news_list]
    embeddings = get_azure_embedding(texts)
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.vstack(embeddings))
    return index, embeddings

def save_faiss_db(index, news_list):
    faiss.write_index(index, EMBEDDINGS_FILE)
    np.save(NEWS_JSON, np.array(news_list, dtype=object))

def load_faiss_db():
    if not os.path.exists(EMBEDDINGS_FILE) or not os.path.exists(NEWS_JSON):
        return None, []
    index = faiss.read_index(EMBEDDINGS_FILE)
    news_list = np.load(NEWS_JSON, allow_pickle=True).tolist()
    return index, news_list

# --- 4. 유사 뉴스 검색 ---
def search_news(query, index, news_list, top_k=3):
    q_emb = get_azure_embedding([query])[0]
    D, I = index.search(np.array([q_emb]), top_k)
    results = [news_list[i] for i in I[0]]
    return results

# --- 5. GPT-4o로 답변 생성 ---
def ask_azure_openai(context, question):
    messages = [
        {"role": "system", "content": "너는 블룸버그 아시아 오늘의 뉴스를 요약/분석해주는 AI 뉴스 비서야."},
        {"role": "user", "content": f"관련 뉴스들:\n{context}\n\n질문: {question}"}
    ]
    response = openai.chat.completions.create(
        model=CHAT_DEPLOY,    # Azure 배포이름!
        messages=messages,
        temperature=0.2,
        max_tokens=2000
    )
    return response.choices[0].message.content


# --- 6. Streamlit UI ---
st.set_page_config(page_title="Bloomberg Asia 뉴스 AI", page_icon="📰", layout="wide")
ensure_data_dir()

st.title("📰 오늘의 Bloomberg Asia 뉴스 AI")
st.markdown("Bloomberg Asia의 오늘 뉴스, 핫이슈, 키워드를 AI로 요약/분석합니다.")

if st.button("오늘 뉴스 최신화 (크롤링/임베딩)"):
    with st.spinner("뉴스 크롤링 중..."):
        news = crawl_bloomberg_asia()
    if not news:
        st.warning("뉴스를 찾지 못했습니다.")
    else:
        with st.spinner("임베딩/FAISS 인덱스 구축 중..."):
            index, embeddings = build_faiss_db(news)
            save_faiss_db(index, news)
        st.success("오늘의 뉴스 임베딩 완료!")

index, news_list = load_faiss_db()
if not news_list:
    st.info("먼저 '오늘 뉴스 최신화' 버튼을 눌러주세요.")

question = st.text_input("뉴스 분석 질문을 입력하세요 (예: 오늘의 핫이슈, 주요 키워드, 요약 등)")
if st.button("AI 뉴스 분석 요청") and question and index:
    sims = search_news(question, index, news_list)
    context = "\n".join([f"- {n['title']} ({n['link']})" for n in sims])
    with st.spinner("GPT-4o가 답변 생성 중..."):
        answer = ask_azure_openai(context, question)
    st.markdown("#### 🤖 AI 뉴스 답변")
    st.success(answer)
    st.markdown("##### 🔎 참고 뉴스")
    for n in sims:
        st.info(f"{n['title']}\n{n['link']}")

st.caption("© 2025 AI Bootcamp. Powered by Azure OpenAI & Bloomberg")
