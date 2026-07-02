import os
import sys

# SQLite3 override for ChromaDB (Required for Render/Linux environments with old sqlite3)
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

# Disable Chroma Telemetry to prevent hanging
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import re
import datetime
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from fredapi import Fred
import ssl

# Fix macOS Python 3 SSL Certificate error for fredapi
ssl._create_default_https_context = ssl._create_unverified_context

from dotenv import load_dotenv
import plotly.graph_objects as go
import json

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from apscheduler.schedulers.background import BackgroundScheduler

# 환경 변수 로드
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
FRED_API_KEY = os.getenv("FRED_API_KEY", "").strip()

# Flask 앱 초기화 및 정적 파일 경로 지정 (현재 디렉토리 기준)
app = Flask(__name__, static_folder=".")
CORS(app)

# ── SEP 데이터 로드 (요청마다 fresh하게 읽기 위해 함수로 분리) ──
SEP_LATEST_DATA = {}

def get_sep_context() -> tuple[str, dict]:
    """CSV에서 최신 SEP 데이터를 읽어 (context_str, latest_data_dict) 반환."""
    try:
        if os.path.exists("sep_values.csv"):
            df_sep = pd.read_csv("sep_values.csv")
            if not df_sep.empty:
                latest_row = df_sep.iloc[-1]
                data = latest_row.to_dict()
                date = str(latest_row['Date'])
                ctx = f"--- LATEST FED SEP PROJECTIONS (As of {date}) ---\n"
                ctx += f"GDP Growth: Year 1: {latest_row.get('GDP_Year1')}%, Year 2: {latest_row.get('GDP_Year2')}%, Year 3: {latest_row.get('GDP_Year3')}%, Longer Run: {latest_row.get('GDP_LongerRun')}%\n"
                ctx += f"Unemployment Rate: Year 1: {latest_row.get('UNRATE_Year1')}%, Year 2: {latest_row.get('UNRATE_Year2')}%, Year 3: {latest_row.get('UNRATE_Year3')}%, Longer Run: {latest_row.get('UNRATE_LongerRun')}%\n"
                ctx += f"PCE Inflation: Year 1: {latest_row.get('PCE_Year1')}%, Year 2: {latest_row.get('PCE_Year2')}%, Year 3: {latest_row.get('PCE_Year3')}%, Longer Run: {latest_row.get('PCE_LongerRun')}%\n"
                ctx += f"Core PCE Inflation: Year 1: {latest_row.get('CORE_PCE_Year1')}%, Year 2: {latest_row.get('CORE_PCE_Year2')}%, Year 3: {latest_row.get('CORE_PCE_Year3')}%\n"
                ctx += f"Fed Funds Rate: Year 1: {latest_row.get('FEDFUNDS_Year1')}%, Year 2: {latest_row.get('FEDFUNDS_Year2')}%, Year 3: {latest_row.get('FEDFUNDS_Year3')}%, Longer Run: {latest_row.get('FEDFUNDS_LongerRun')}%\n"
                ctx += "-" * 40
                return ctx, data
    except Exception as e:
        print(f"Error loading SEP data: {e}")
    return "", {}

# ── 1. 스케줄러: 연준 문서 크롤링 ────────────────────────────────────
def update_vector_db():
    print(f"[{datetime.datetime.now()}] 신규 연설문/회의록 수집 & ChromaDB 업데이트 실행 중...")
    try:
        import requests
        from bs4 import BeautifulSoup
        import xml.etree.ElementTree as ET
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain.docstore.document import Document
        
        rss_url = "https://www.federalreserve.gov/feeds/press_monetary.xml"
        response = requests.get(rss_url)
        root = ET.fromstring(response.content)
        
        urls_to_scrape = []
        for item in root.findall('./channel/item')[:3]:
            link = item.find('link').text
            if link:
                urls_to_scrape.append(link)
                
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small", max_retries=0)
        db = Chroma(persist_directory="./fed_db", embedding_function=embeddings)

        existing = db.get(include=["metadatas"])
        existing_sources = {m.get("source") for m in existing["metadatas"] if m.get("source")}

        docs = []
        headers = {'User-Agent': 'Mozilla/5.0'}
        for url in urls_to_scrape:
            if url in existing_sources:
                print(f"[{datetime.datetime.now()}] 이미 인덱싱된 문서, 건너뜀: {url}")
                continue
            page_resp = requests.get(url, headers=headers)
            soup = BeautifulSoup(page_resp.text, 'html.parser')
            article = soup.find('div', id='article')
            if not article:
                article = soup.find('body')
            text = article.get_text(separator='\n', strip=True) if article else ""
            if text:
                docs.append(Document(page_content=text, metadata={"source": url}))

        if docs:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            split_docs = text_splitter.split_documents(docs)
            db.add_documents(split_docs)
            print(f"[{datetime.datetime.now()}] 업데이트 완료: {len(split_docs)}개 청크 추가됨.")
        else:
            print(f"[{datetime.datetime.now()}] 새로운 문서 없음. DB 업데이트 건너뜀.")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] 업데이트 중 오류 발생: {e}")

# 스케줄러를 한 번만 실행되도록 설정
scheduler = BackgroundScheduler(timezone="Asia/Seoul")
scheduler.add_job(update_vector_db, 'cron', hour=4, minute=0)
scheduler.start()

# ── 2. 지표 설정 및 분할기 ──────────────────────────────────────────
INDICATORS = {
    "FEDFUNDS": "Fed Funds Rate",
    "DGS10":    "10-Year Treasury Yield",
    "DGS2":     "2-Year Treasury Yield",
    "T10Y2Y":   "10Y-2Y Yield Spread",
    "CPIAUCSL": "CPI",
    "PCEPI":    "PCE Price Index",
    "UNRATE":   "Unemployment Rate",
    "PAYEMS":   "Nonfarm Payrolls",
    "GDPC1":    "Real GDP",
    "M2SL":     "M2 Money Supply",
}

# Chart labels per language: {ticker: (display_name, unit)}
CHART_I18N = {
    "ko": {
        "FEDFUNDS": ("기준금리 (Fed Funds Rate)", "금리 (%)"),
        "DGS10":    ("10년물 국채금리",           "금리 (%)"),
        "DGS2":     ("2년물 국채금리",            "금리 (%)"),
        "T10Y2Y":   ("장단기 금리차 (10Y-2Y)",    "금리차 (%)"),
        "CPIAUCSL": ("소비자물가지수 (CPI)",       "지수 (Index, 1982-84=100)"),
        "PCEPI":    ("PCE 물가지수",              "지수"),
        "UNRATE":   ("실업률",                   "비율 (%)"),
        "PAYEMS":   ("비농업 취업자수",            "천 명"),
        "GDPC1":    ("실질 GDP",                 "10억 달러 (Billions of $)"),
        "M2SL":     ("M2 통화량",                "십억 달러"),
        "_x_label":   "연도 (Year)",
        "_sep_suffix": "예상 경로 (SEP 전망)",
    },
    "en": {
        "FEDFUNDS": ("Fed Funds Rate",          "Rate (%)"),
        "DGS10":    ("10-Year Treasury Yield",  "Rate (%)"),
        "DGS2":     ("2-Year Treasury Yield",   "Rate (%)"),
        "T10Y2Y":   ("10Y-2Y Yield Spread",     "Spread (%)"),
        "CPIAUCSL": ("CPI",                     "Index (1982-84=100)"),
        "PCEPI":    ("PCE Price Index",         "Index"),
        "UNRATE":   ("Unemployment Rate",       "Rate (%)"),
        "PAYEMS":   ("Nonfarm Payrolls",        "Thousands"),
        "GDPC1":    ("Real GDP",                "Billions of $"),
        "M2SL":     ("M2 Money Supply",         "Billions of $"),
        "_x_label":   "Year",
        "_sep_suffix": "Projected Path (SEP Forecast)",
    },
    "es": {
        "FEDFUNDS": ("Tasa de Fondos Federales",        "Tasa (%)"),
        "DGS10":    ("Rendimiento del Tesoro 10 años",  "Tasa (%)"),
        "DGS2":     ("Rendimiento del Tesoro 2 años",   "Tasa (%)"),
        "T10Y2Y":   ("Diferencial 10Y-2Y",              "Diferencial (%)"),
        "CPIAUCSL": ("IPC",                             "Índice (1982-84=100)"),
        "PCEPI":    ("Índice de Precios PCE",           "Índice"),
        "UNRATE":   ("Tasa de Desempleo",               "Tasa (%)"),
        "PAYEMS":   ("Empleo No Agrícola",              "Miles"),
        "GDPC1":    ("PIB Real",                        "Miles de Millones $"),
        "M2SL":     ("Oferta Monetaria M2",             "Miles de Millones $"),
        "_x_label":   "Año",
        "_sep_suffix": "Trayectoria Proyectada (SEP)",
    },
}

KEYWORD_MAP = {
    ("inflation", "price", "cpi", "물가", "인플레"): ("CPIAUCSL", "Index"),
    ("pce",): ("PCEPI", "Index"),
    ("unemployment", "employment", "job", "고용", "실업", "일자리"): ("UNRATE", "Rate (%)"),
    ("payroll", "취업자", "고용자"): ("PAYEMS", "Thousands"),
    ("gdp", "gdp growth", "economic growth", "real gdp", "성장", "경기", "경제성장"): ("GDPC1", "Billions of $"),
    ("10년", "10-year", "dgs10", "장기금리"): ("DGS10", "Rate (%)"),
    ("2년", "2-year", "dgs2", "단기금리"): ("DGS2", "Rate (%)"),
    ("금리차", "yield curve", "t10y2y", "장단기"): ("T10Y2Y", "Spread (%)"),
    ("m2", "통화량", "money supply"): ("M2SL", "Billions of $"),
    ("interest rate", "interest rates", "fed funds", "federal funds",
     "rate hike", "rate cut", "rate increase", "rate decrease",
     "금리", "기준금리"): ("FEDFUNDS", "Rate (%)"),
}

def analyze_prompt(prompt: str):
    lower = prompt.lower()
    tickers = []
    for keywords, (ticker, unit) in KEYWORD_MAP.items():
        if any(k in lower for k in keywords):
            tickers.append((ticker, INDICATORS.get(ticker, ticker), unit))
    # Return empty list if no economic indicator keywords found — no chart for off-topic questions
    years = re.findall(r'\b(20\d{2})\b', prompt)
    start_year = min(years) if years else None
    end_year = max(years) if years else None
    
    recent_years = re.search(
        r'최근\s*(\d+)년|(?:last|past|recent)\s+(\d+)\s+years?',
        prompt, re.IGNORECASE
    )
    if recent_years and not start_year:
        n_years = int(recent_years.group(1) or recent_years.group(2))
        start_year = str(datetime.datetime.now().year - n_years)

    is_relation = any(w in lower for w in ["relationship", "관계", "상관", "비교"])
    chart_type = "scatter_xy" if is_relation and len(tickers) == 2 else "line"
    return tickers, start_year, end_year, chart_type

def load_fred_data(ticker: str, start: str = None, end: str = None):
    try:
        fred = Fred(api_key=FRED_API_KEY)
        kwargs = {}
        if start:
            kwargs["observation_start"] = start
        if end:
            kwargs["observation_end"] = end
        series = fred.get_series(ticker, **kwargs)
        df = pd.DataFrame({ticker: series})
        df.index.name = "Date"
        return df
    except Exception as e:
        print(f"load_fred_data error ({ticker}): {e}")
        return pd.DataFrame()

# ── 3. Langchain RAG 초기화 ──────────────────────────────────────────
_rag_chain = None
_retriever = None

def get_rag_chain_and_retriever():
    global _rag_chain, _retriever
    if _rag_chain is None:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small", max_retries=0)
        llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0, max_retries=0)
        db = Chroma(persist_directory="./fed_db", embedding_function=embeddings)
        _retriever = db.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 8, "fetch_k": 20, "lambda_mult": 0.7},
        )

        # sep_context is injected per-request so it always reflects the latest CSV data
        template = """You are a Federal Reserve data assistant. You answer questions strictly based on two sources:
1. The Fed documents (meeting minutes, speeches) retrieved below as Context.
2. The latest SEP projections provided below.
Today's date is {today}.

Rules:
- ONLY answer questions related to Federal Reserve monetary policy, U.S. economic indicators (interest rates, inflation, GDP, unemployment, etc.), or Fed documents.
- If the question is unrelated to the Fed or U.S. macroeconomics, respond with: "This question is outside the scope of this tool. Please ask about Federal Reserve policy or U.S. economic data." (Korean: "이 질문은 연준 데이터 분석 도구의 범위를 벗어납니다. 연준 정책이나 미국 경제 지표에 대해 질문해 주세요.")
- If the provided Context does not contain enough information to answer accurately, say so explicitly. Do NOT fabricate or guess.
- FRED API data (charts) is shown separately by the UI — do not describe what charts look like; just provide analytical commentary on the economics.
- If the question is in Korean, answer in Korean. If in English, answer in English.
- Be concise (3-5 sentences) and cite numbers from the context when available.

Latest SEP Forward Projections:
{sep_context}

Context from Fed documents:
{context}

Question: {question}

Answer:"""
        prompt_template = ChatPromptTemplate.from_template(template)
        _rag_chain = (
            {
                "context": (lambda x: x["question"]) | _retriever | (lambda docs: "\n\n".join([d.page_content for d in docs])),
                "question": lambda x: x["question"],
                "sep_context": lambda x: x["sep_context"],
                "today": lambda x: x["today"],
            }
            | prompt_template | llm | StrOutputParser()
        )
    return _rag_chain, _retriever

def get_sources(question: str):
    try:
        _, retriever = get_rag_chain_and_retriever()
        docs = retriever.invoke(question)
        sources = []
        for doc in docs:
            src = doc.metadata.get("source", "")
            if src:
                basename = os.path.basename(src).replace(".txt", "").replace("_", " ")
                if basename not in sources:
                    sources.append(basename)
        return sources[:3]
    except:
        return []

# ── 4. 라우팅 ──────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(".", path)

@app.route("/api/chat", methods=["POST"])
def api_chat():
    try:
        data = request.json
        question = data.get("message", "")
        if not question:
            return jsonify({"error": "No message provided"}), 400

        tickers, start_yr, end_yr, chart_type = analyze_prompt(question)
        sep_context, sep_data = get_sep_context()
        rag_chain, _ = get_rag_chain_and_retriever()
        answer = rag_chain.invoke({
            "question": question,
            "sep_context": sep_context,
            "today": datetime.datetime.now().strftime('%Y-%m-%d'),
        })
        sources = get_sources(question)

        return jsonify({
            "answer": answer,
            "sources": sources,
            "tickers": tickers,
            "start_yr": start_yr,
            "end_yr": end_yr,
            "chart_type": chart_type
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"서버 내부 오류: {str(e)}"}), 500

def make_trace(chart_type, x, y, name, color, secondary=False):
    opacity = 0.7 if secondary else 1.0
    if chart_type == "bar":
        return go.Bar(x=x, y=y, name=name, marker_color=color, opacity=opacity)
    elif chart_type == "scatter":
        return go.Scatter(x=x, y=y, name=name, mode="markers",
                         marker=dict(color=color, size=5, opacity=opacity))
    elif chart_type == "area":
        return go.Scatter(x=x, y=y, name=name, mode="lines",
                         fill="tozeroy", line=dict(color=color, width=2),
                         fillcolor=color.replace(")", f",{0.15})").replace("rgb", "rgba") if "rgb" in color else color,
                         opacity=opacity)
    else:  # line
        return go.Scatter(x=x, y=y, name=name, mode="lines",
                         line=dict(color=color, width=2), opacity=opacity)

PLOTLY_LAYOUT = dict(
    paper_bgcolor="#111827",
    plot_bgcolor="#111827",
    font=dict(color="#f8fafc", family="Pretendard"),
    xaxis=dict(
        showgrid=True, gridcolor="#334155", gridwidth=1,
        tickfont=dict(color="#94a3b8", size=11),
        tickformat="%Y",
        showline=True, linecolor="#475569", linewidth=1, zeroline=False,
    ),
    yaxis=dict(
        showgrid=True, gridcolor="#334155", gridwidth=1,
        tickfont=dict(color="#94a3b8", size=11),
        showline=True, linecolor="#475569", linewidth=1, zeroline=False,
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom", y=1.05,
        xanchor="right", x=1,
        bgcolor="rgba(15,23,42,0.8)",
        bordercolor="#334155", borderwidth=1,
        font=dict(color="#f8fafc", size=11),
    ),
    margin=dict(l=50, r=20, t=60, b=80),
    hovermode="x unified",
    hoverlabel=dict(bgcolor="#1e293b", bordercolor="#3b82f6", font=dict(color="#f8fafc")),
)

@app.route("/api/chart", methods=["POST"])
def api_chart():
    data = request.json
    tickers = data.get("tickers", [])
    start_yr = data.get("start_yr")
    end_yr = data.get("end_yr")
    chart_type = data.get("chart_type", "line")
    lang = data.get("lang", "en")

    if not tickers:
        return jsonify({"error": "No tickers provided"}), 400

    i18n = CHART_I18N.get(lang, CHART_I18N["en"])
    x_label = i18n["_x_label"]
    sep_suffix = i18n["_sep_suffix"]

    # Suppress SEP overlay when the query explicitly targets a fully past date range
    current_year = datetime.datetime.now().year
    show_sep = not (end_yr and int(end_yr) < current_year)

    def resolve(ticker, fallback_name, fallback_unit):
        """Look up localized name/unit for a ticker, fall back to what the client sent."""
        if ticker in i18n:
            return i18n[ticker]
        return fallback_name, fallback_unit

    try:
        _, sep_data = get_sep_context()
        colors_main = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"]

        start_str = f"{start_yr}-01-01" if start_yr else None
        end_str   = f"{end_yr}-12-31"   if end_yr   else None

        if chart_type == "scatter_xy" and len(tickers) == 2:
            t1, fb_name1, fb_unit1 = tickers[0]
            t2, fb_name2, fb_unit2 = tickers[1]
            name1, unit1 = resolve(t1, fb_name1, fb_unit1)
            name2, unit2 = resolve(t2, fb_name2, fb_unit2)
            df1 = load_fred_data(t1, start=start_str, end=end_str)
            df2 = load_fred_data(t2, start=start_str, end=end_str)
            if df1.empty or df2.empty:
                return jsonify({"error": "No valid data to plot"}), 404

            df_combined = df1.join(df2, how="inner").dropna()

            if df_combined.empty:
                return jsonify({"error": "No valid data to plot"}), 404

            fig = go.Figure(data=go.Scatter(
                x=df_combined[t1].tolist(), y=df_combined[t2].tolist(), mode='markers',
                marker=dict(size=6, color="#3b82f6", opacity=0.6),
                name="Relationship"
            ))
            layout = PLOTLY_LAYOUT.copy()
            layout.update(
                title=dict(text=f"{name1} vs {name2}", font=dict(color="#f8fafc", size=12), x=0),
                xaxis=dict(title=dict(text=f"{name1} ({unit1})", font=dict(size=12, color="#f8fafc")), tickformat=""),
                yaxis=dict(title=dict(text=f"{name2} ({unit2})", font=dict(size=12, color="#f8fafc"))),
                hovermode="closest",
                height=320,
            )
            fig.update_layout(**layout)
            return fig.to_json()

        fig = go.Figure()

        has_data = False
        resolved_tickers = []
        for idx, ticker_info in enumerate(tickers):
            ticker, fb_name, fb_unit = ticker_info
            name, unit = resolve(ticker, fb_name, fb_unit)
            resolved_tickers.append((ticker, name, unit))

            df_combined = load_fred_data(ticker, start=start_str, end=end_str)
            if df_combined.empty:
                continue

            has_data = True

            color = colors_main[idx % len(colors_main)]
            x_vals = df_combined.index.strftime('%Y-%m-%d').tolist()

            fig.add_trace(make_trace(chart_type, x_vals, df_combined[ticker].tolist(), name, color))

            ticker_to_sep = {"GDPC1": "GDP", "UNRATE": "UNRATE", "PCEPI": "PCE", "FEDFUNDS": "FEDFUNDS"}
            sep_prefix = ticker_to_sep.get(ticker)
            if show_sep and sep_prefix and sep_data:
                try:
                    sep_date = str(sep_data.get('Date', ''))
                    if sep_date and len(sep_date) >= 4:
                        base_year = int(sep_date[:4])
                        x_proj = [f"{base_year}-12-31", f"{base_year+1}-12-31", f"{base_year+2}-12-31"]
                        y_proj = [
                            sep_data.get(f"{sep_prefix}_Year1"),
                            sep_data.get(f"{sep_prefix}_Year2"),
                            sep_data.get(f"{sep_prefix}_Year3")
                        ]
                        x_clean, y_clean = [], []
                        for x_v, y_v in zip(x_proj, y_proj):
                            if pd.notna(y_v):
                                x_clean.append(x_v)
                                y_clean.append(float(y_v))
                        if x_clean:
                            fig.add_trace(go.Scatter(
                                x=x_clean, y=y_clean,
                                name=f"{name} ({sep_suffix})",
                                mode="lines+markers",
                                line=dict(color="#ef4444", width=2, dash='dot'),
                                marker=dict(symbol="circle", size=6, color="#ef4444")
                            ))
                            sep_note = {
                                "ko": "※ 점선은 연준 SEP(경제전망 요약)에 기반한 예상 경로입니다.",
                                "en": "※ Dotted line shows the Fed's projected path based on SEP (Summary of Economic Projections).",
                                "es": "※ La línea punteada muestra la trayectoria proyectada por la Fed según el SEP.",
                            }
                            fig.add_annotation(
                                text=sep_note.get(lang, sep_note["en"]),
                                xref="paper", yref="paper",
                                x=0.0, y=-0.22,
                                showarrow=False,
                                font=dict(size=9, color="#64748b"),
                                align="left", xanchor="left"
                            )
                except Exception as e:
                    print(f"Error adding SEP trace: {e}")

        if not has_data:
            return jsonify({"error": "No valid data to plot"}), 404

        layout = PLOTLY_LAYOUT.copy()
        title_name = ", ".join([t[1] for t in resolved_tickers])
        units = ", ".join(list(set([t[2] for t in resolved_tickers])))

        layout.update(
            title=dict(text=title_name, font=dict(color="#f8fafc", size=12), x=0),
            xaxis=dict(
                title=dict(text=x_label, font=dict(size=12, color="#f8fafc")),
                showgrid=True, gridcolor="#334155", gridwidth=1,
                tickfont=dict(color="#94a3b8", size=11),
                tickformat="%Y",
                showline=True, linecolor="#475569", linewidth=1, zeroline=False,
            ),
            yaxis=dict(title=dict(text=units, font=dict(size=12, color="#f8fafc"))),
            height=320,
        )
        fig.update_layout(**layout)

        return fig.to_json()
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
