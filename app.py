import streamlit as st
import pandas as pd
from urllib.parse import quote_plus
from urllib.parse import quote as urlquote
import numpy as np
import html
import requests
import io
import re
import difflib
import textwrap
import streamlit.components.v1 as components

st.set_page_config(
    page_title="📘 そっとよりそう本さがし",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
      --brand-bg: #F5F7FA;            /* neutral light */
      --brand-card: #FFFFFF;
      --brand-accent: #1D4ED8;        /* blue accent */
      --brand-accent-weak: #EEF2FF;   /* pale blue */
      --brand-text: #374151;          /* neutral dark */
      --brand-border: #E6E6E6;        /* soft gray border */
      --focus: #A5B4FC;               /* focus ring */
    }
    body { background: var(--brand-bg); }
    /* Base spacing */
    .main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

    /* Font family: 魔法の質問風・温かみある角丸/丸ゴシック */
    html, body {
      font-family: "Hiragino Sans", "Noto Sans JP", "Yu Gothic", sans-serif;
      -webkit-font-smoothing: antialiased;
      color: var(--brand-text);
    }

    /* Headings readability and brand style */
    h1, h2, h3 {
      line-height: 1.35;
      font-family: "Noto Serif JP", "Hiragino Mincho ProN", "Yu Mincho", serif;
      letter-spacing: 0.02em;
    }

    /* Headings sizes and weight */
    h1 {
      font-size: 1.55rem !important;
      font-weight: 700;
      color: var(--brand-text);
      margin: 0.2rem 0 0.85rem;
      letter-spacing: 0.02em;
      padding-bottom: 8px;
      border-bottom: 3px solid var(--brand-border);
    }
    h2 {
      font-size: 1.4rem !important;
      font-weight: 700;
      color: var(--brand-text);
      margin: 1rem 0 0.7rem;
      letter-spacing: 0.02em;
    }
    h3 {
      font-size: 1.15rem !important;
      font-weight: 500;
      color: var(--brand-text);
    }

    /* Make the main content column comfortably narrow on large screens */
    @media (min-width: 1024px) {
      .main .block-container { max-width: 1040px; }
    }

    /* Mobile tweaks */
    @media (max-width: 640px) {
      .stButton>button { width: 100%; }
      .stRadio, .stSelectbox { font-size: 0.98rem; }
      .stMarkdown p { font-size: 1.08rem; line-height: 1.7; }
    }

    /* Cards & grid for desktop/mobile */
    .hero-card, .book-card {
      background: var(--brand-card);
      border: 1px solid var(--brand-border);
      border-radius: 10px;
      padding: 16px 18px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    /* Form card wrapper */
    .form-card {
      background: var(--brand-card);
      border: 1px solid var(--brand-border);
      border-radius: 12px;
      padding: 16px 18px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.05);
      margin-bottom: 18px;
    }
    .hero-card { border-width: 2px; }
    .hero-title, .book-title {
      font-weight: 700;
      margin-bottom: 6px;
      font-size: 1.18rem;
      line-height: 1.5;
      color: var(--brand-text);
      font-family: "Hiragino Sans", "Noto Sans JP", "Yu Gothic", sans-serif;
      letter-spacing: 0.01em;
    }
    .hero-desc, .book-desc {
      margin: 8px 0 12px;
      line-height: 1.7;
      overflow-wrap: anywhere;
      color: var(--brand-text);
      font-size: 1.1rem;
      font-family: "Hiragino Sans", "Noto Sans JP", "Yu Gothic", sans-serif;
    }

    .book-grid { display: grid; gap: 12px; }
    @media (min-width: 768px) { .book-grid { grid-template-columns: 1fr 1fr; } }

    /* Link button (neutral/blue style) */
    .link-btn {
      display: inline-block;
      padding: 8px 18px;
      border-radius: 6px;
      text-decoration: none;
      background: var(--brand-accent-weak);
      color: var(--brand-accent);
      border: 1px solid #c7d2fe;
      box-shadow: none;
      font-size: 1rem;
      font-weight: 600;
      transition: background 0.15s;
      width: auto;
      white-space: nowrap;
      letter-spacing: 0.03em;
    }
    .link-btn:hover { background: #e0e7ff; color: var(--brand-accent); }

    /* Primary button style */
    .stButton>button {
      background: var(--brand-accent-weak);
      color: var(--brand-accent);
      border: 1px solid #c7d2fe;
      padding: 10px 18px;
      border-radius: 8px;
      font-weight: 600;
      letter-spacing: 0.02em;
      box-shadow: none;
      transition: background 0.15s ease, color 0.15s ease;
      max-width: 360px;
    }
    .stButton>button:hover { background: #e0e7ff; color: var(--brand-accent); }

    /* Focus ring for accessibility */
    .link-btn:focus { outline: 3px solid var(--focus); outline-offset: 2px; }
    .stButton>button:focus { outline: 3px solid var(--focus); outline-offset: 2px; }

    /* Dark mode friendly defaults */
    @media (prefers-color-scheme: dark) {
      :root { --card-bg: #111418; --card-border: #242a31; }
      .link-btn { border-color: #333; }
      .link-btn:hover { background: #1c222b; }
    }

    /* Section spacing */
    .section { margin: 24px 0; }

    /* Improve label wrapping & readability */
    .stSelectbox label, .stRadio label {
      white-space: normal;
      line-height: 1.6;
      font-size: 1.12rem;
      font-weight: 600;
      margin-bottom: 8px;
      color: var(--brand-text);
      font-family: "Hiragino Sans", "Noto Sans JP", "Yu Gothic", sans-serif;
      letter-spacing: 0.01em;
    }

    /* Custom form labels (to avoid Streamlit default label sizing) */
    .form-label {
      font-size: 1.2rem;
      font-weight: 700;
      margin: 14px 0 10px;
      color: var(--brand-text);
      font-family: "Hiragino Sans", "Noto Sans JP", "Yu Gothic", sans-serif;
      letter-spacing: 0.01em;
    }
    @media (min-width: 768px) { .form-label { font-size: 1.25rem; } }

    /* Clamp long descriptions on mobile */
    @media (max-width: 640px) {
      .book-desc { display: block; -webkit-line-clamp: initial; -webkit-box-orient: initial; overflow: visible; }
    }

    /* details/summary styling */
    details { margin-top: 6px; }
    details summary { cursor: pointer; color: #3366cc; outline: none; }
    details[open] summary { color: #555; }

    /* 補足ラベル（補完本の注釈） */
    .sub-label{ font-size: 0.92rem; color:#6b7280; margin:4px 0 6px; font-style: italic; }

    /* Card grid for cover + body */
    .card-grid { display: grid; grid-template-columns: 1fr; gap: 14px; align-items: start; }
    @media (min-width: 768px) { .card-grid { grid-template-columns: 130px 1fr; } }
    @media (min-width: 768px) { .hero-card .card-grid { grid-template-columns: 160px 1fr; } }
    .card-cover img { width: 100%; height: auto; max-height: 200px; object-fit: contain; background: #fafafa; border: 1px solid #eee; border-radius: 8px; padding: 8px; }
    .card-body { display: flex; flex-direction: column; gap: 8px; justify-content: space-between; }
    /* Keep link button aligned */
    .card-body .link-btn {
      align-self: flex-start;
    }

    /* PCでは右下寄せ */
    @media (min-width: 768px) {
      .card-body { flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }
      .card-body .link-btn { align-self: flex-end; }
    }

    /* Larger touch targets on mobile */
    @media (max-width: 640px) {
      .link-btn { width: 100%; text-align: center; padding: 14px 16px; }
    }

    /* Sections / dividers */
    .section { margin: 24px 0; }
    .section-hero { margin-bottom: 28px; }
    .section-others { margin-top: 14px; }
    .divider { height: 1px; background: var(--brand-border); margin: 14px 0; }

    /* 本文や説明は大きく温かく */
    .stMarkdown p, .book-desc {
      font-size: 1.12rem;
      line-height: 1.85;
      font-family: "Hiragino Sans", "Noto Sans JP", "Yu Gothic", sans-serif;
      color: var(--brand-text);
      letter-spacing: 0.01em;
    }

    /* Success alert: 少し控えめに */
    .stAlert { border-radius: 10px; margin: 8px 0 10px; }
    .stAlert > div { padding: 8px 10px; font-size: 0.94rem; }

    /* Radio/Select の行間とタップしやすさ */
    .stRadio [role="radiogroup"] label { padding: 4px 2px; }

    /* カード間の余白をやや広く（PC） */
    @media (min-width: 1024px) {
      .book-grid { gap: 16px; }
    }

    /* Desktop typography boost */
    @media (min-width: 768px) {
      h1 { font-size: 1.8rem !important; }
      h2 { font-size: 1.55rem !important; }
      .stMarkdown p, .book-desc { font-size: 1.2rem; line-height: 1.9; }
      .stRadio, .stSelectbox { font-size: 1.1rem; }
      .hero-title { font-size: 1.26rem; }
      .book-title { font-size: 1.16rem; }
      .stSelectbox label, .stRadio label { font-size: 1.2rem; }
    }
    /* Two-column form: stack on mobile */
    @media (max-width: 768px){
      div[data-testid="column"]{ width:100% !important; flex: 1 0 100% !important; }
      div[data-testid="stHorizontalBlock"]{ gap: 0.75rem !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# データ読み込み（キャッシュつき & フォールバック）
@st.cache_data(show_spinner=False, ttl=60 * 10)
def load_books() -> pd.DataFrame:
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRrOkycGi4nVcR_f2HES6pkm4Yz8BiwFr2L9t3Zf0_j0c_eRy0g2pM9cxZj6fRfsUM20urikULvOqub/pub?output=csv"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; matsuda-book-app-v1/1.0)"}
    text = None
    # Try up to 3 times with backoff
    for i in range(3):
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            try:
                text = resp.content.decode("utf-8-sig", errors="replace")
            except Exception:
                text = resp.content.decode("cp932", errors="replace")
            break
        except Exception:
            pass
    if text is None:
        st.error("データの取得に失敗しました。時間をおいて再度お試しください。")
        return pd.DataFrame(columns=["title", "description", "amazon_url", "keywords"])  # safe empty

    df = pd.read_csv(io.StringIO(text))
    # 標準化
    df.columns = df.columns.str.strip().str.replace('"', "").str.replace("\n", "", regex=False)
    # 期待カラム名への寄せ
    rename_map: dict[str, str] = {}
    for c in df.columns:
        lc = c.lower()
        if "title" in lc and " " not in lc:
            rename_map[c] = "title"
        if "amazon" in lc:
            rename_map[c] = "amazon_url"
        if "keyword" in lc:
            rename_map[c] = "keywords"
        if "description" in lc:
            rename_map[c] = "description"
    df = df.rename(columns=rename_map)
    # 欠損カラムの安全対策
    for col in ["title", "description", "amazon_url", "keywords", "isbn"]:
        if col not in df.columns:
            df[col] = ""
    # 前後空白の除去
    for col in ["title", "description", "amazon_url", "keywords"]:
        df[col] = df[col].astype(str).str.strip()
    # 重複排除（タイトルで一意に）
    if "title" in df.columns:
        df = df.drop_duplicates(subset=["title"]).reset_index(drop=True)
    return df




books = load_books()

# タイトル補正（シート側を修正したため現状は未使用）
TITLE_OVERRIDE: dict[str, str] = {}

# プレースホルダー（SVG）を生成
def build_placeholder_cover(bg: str = "#F2F4F7", fg: str = "#667085") -> str:
    """大きなはてなマークと日本語テキストのプレースホルダー画像を返す。"""
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="320" height="450" viewBox="0 0 320 450">
<rect width="100%" height="100%" fill="{bg}"/>
<text x="50%" y="45%" dominant-baseline="middle" text-anchor="middle" font-size="160" font-weight="700" fill="{fg}">？</text>
<text x="50%" y="70%" dominant-baseline="middle" text-anchor="middle" font-size="24" font-weight="700" fill="{fg}">表紙画像が</text>
<text x="50%" y="84%" dominant-baseline="middle" text-anchor="middle" font-size="24" font-weight="700" fill="{fg}">見つかりませんでした</text>
</svg>'''
    return "data:image/svg+xml;utf8," + urlquote(svg)

NO_COVER_IMG = build_placeholder_cover()

def needs_placeholder(title: str) -> bool:
    t = (title or "")
    return "子どもの" in t and "考える力" in t and "魔法の質問" in t

# 任意: タイトル→ISBN の手動オーバーライド（必要に応じて追記）
ISBN_OVERRIDE: dict[str, str] = {
    # "朝1分30の習慣": "",  # 例: "978429..."
    # "愛と怖れの法則": "",
    # "子どもの「考える力」が伸びる魔法の質問": "",
}

# --- v2: 表紙画像の表示ON/OFF ---
SHOW_COVERS: bool = True


@st.cache_data(ttl=60*60)
def get_cover_url(isbn: str | None, title: str, author: str | None = None) -> str | None:
    """
    表紙取得（OpenBD→Google Books）。Google Books は題名の類似度と著者確認で誤ヒットを防ぐ。
    """
    # タイトルに対する手動ISBNがあれば OpenBD を最優先
    if title in ISBN_OVERRIDE and ISBN_OVERRIDE.get(title):
        try:
            ob = f"https://api.openbd.jp/v1/cover/{ISBN_OVERRIDE[title]}.jpg"
            r = requests.get(ob, timeout=6)
            if r.status_code == 200 and (r.headers.get("Content-Type", "").startswith("image/") or r.content[:2] == b"\xff\xd8"):
                return ob
        except Exception:
            pass

    headers = {"User-Agent": "Mozilla/5.0 (compatible; matsuda-book-app/2.0)"}
    def clean_author_string(s: str) -> str:
        """Remove role annotations like 監修/編/著 and any parentheses, and collapse spaces (incl. full-width)."""
        s = s or ""
        # remove parentheses content e.g., （監修）, (Ed.), etc.
        s = re.sub(r"[（(][^）)]*[)）]", "", s)
        # remove common role markers
        for mark in ("監修", "編", "著"):
            s = s.replace(mark, "")
        # collapse spaces (half/full width)
        return s.replace(" ", "").replace("　", "")

    def author_variants(a: str | None) -> list[str]:
        if not a:
            return []
        a = a.strip()
        # normalize both half-width and full-width spaces for variant generation
        a_no_space = a.replace(" ", "").replace("　", "")
        if a in ("マツダミヒロ", "マツダ ミヒロ", "松田充弘", "松田 充弘", "松田　充弘", "Mihiro", "Matsuda"):
            return [
                "マツダミヒロ", "マツダ ミヒロ",
                "松田充弘", "松田 充弘", "松田　充弘",
                "Mihiro", "Mihiro Matsuda", "Matsuda Mihiro", "Matsuda",
            ]
        if a in ("WAKANA", "ワカナ", "わかな"):
            return ["WAKANA", "ワカナ", "わかな"]
        # fallback: return original + no-space variants
        return [a, a_no_space]

    def norm(s: str) -> str:
        """Normalize title for fuzzy match: keep Japanese letters, drop spaces & punctuation only."""
        s = (s or "").lower().strip()
        # remove common spaces and punctuation but KEEP CJK characters
        remove_chars = " 　\t\n\r・:：、。!！?？『』「」（）()[]【】〈〉《》—–‐-／/,."  # extend as needed
        table = str.maketrans({ch: "" for ch in remove_chars})
        return s.translate(table)

    # 1) OpenBD（ISBNがあれば高確度）
    try:
        clean_isbn = None
        if isinstance(isbn, str):
            digits = "".join(ch for ch in isbn if ch.isdigit())
            clean_isbn = digits if digits else None
        if clean_isbn:
            ob = f"https://api.openbd.jp/v1/cover/{clean_isbn}.jpg"
            r = requests.get(ob, headers=headers, timeout=6)
            if r.status_code == 200 and (
                r.headers.get("Content-Type", "").startswith("image/") or r.content[:2] == b"\xff\xd8"
            ):
                return ob
    except Exception:
        pass

    # 2) Google Books（タイトル検索フォールバック）
    GB_URL = "https://www.googleapis.com/books/v1/volumes"
    # タイトル補正
    query_title = TITLE_OVERRIDE.get(title, title)
    # 検索クエリ候補（著者ゆらぎ＋素のタイトル）
    queries = [
        f'intitle:"{query_title}" inauthor:マツダミヒロ',
        f'intitle:{query_title} inauthor:"マツダ ミヒロ"',
        f'intitle:{query_title} inauthor:WAKANA',
        f'intitle:{query_title} inauthor:"塩沢節子"',
        f'intitle:{query_title}',
        query_title,
    ]
    # 著者が分かっている場合は先頭に著者指定クエリを積む
    if author:
        queries.insert(0, f'intitle:"{query_title}" inauthor:{author}')

    allowed_authors = [
        "マツダミヒロ", "マツダ ミヒロ",
        "松田充弘", "松田 充弘", "松田　充弘",
        "Mihiro", "Mihiro Matsuda", "Matsuda Mihiro", "Matsuda",
        "WAKANA", "ワカナ", "わかな",
        # よく出る共著者
        "塩沢節子", "日小田正人", "小田正人", "Oda", "Shiozawa"
    ]
    want_title = norm(query_title)

    for q in queries:
        try:
            params = {"q": q, "maxResults": 5, "printType": "books", "projection": "lite", "langRestrict": "ja"}
            g = requests.get(GB_URL, params=params, headers=headers, timeout=8)
            data = g.json() if g.ok else {}
            for it in data.get("items", []) or []:
                info = (it.get("volumeInfo") or {})
                api_title = info.get("title", "")
                raw_authors = ", ".join(info.get("authors", []) or [])
                api_authors = clean_author_string(raw_authors)
                api_norm = norm(api_title)
                # 題名類似度（0〜1）と部分一致
                ratio = difflib.SequenceMatcher(None, want_title, api_norm).ratio()
                title_ok = False
                if want_title and api_norm:
                    title_ok = (want_title in api_norm) or (api_norm in want_title) or (ratio >= 0.60)

                # 著者チェック：与えた著者はゆらぎを広げて判定。未指定なら既知リスト。
                author_ok = True
                if author:
                    variants = author_variants(author)
                    author_ok = any(v in api_authors for v in variants)
                else:
                    author_ok = any(tok in api_authors for tok in allowed_authors)

                # 通常判定
                if title_ok and author_ok:
                    links = info.get("imageLinks") or {}
                    url = links.get("thumbnail") or links.get("smallThumbnail")
                    if url:
                        return url.replace("http://", "https://")

                # フォールバック：タイトル強一致のみ（類似度が十分高い場合は著者不一致でも採用）
                if ratio >= 0.72:
                    links = info.get("imageLinks") or {}
                    url = links.get("thumbnail") or links.get("smallThumbnail")
                    if url:
                        return url.replace("http://", "https://")
        except Exception:
            continue

    return None

# フォーム（テーマ:全幅, 気持ち/読み方:2カラム横並び）
st.title("📘 今日のあなたに、そっとよりそう本を探しましょう")


# テーマ選択（全幅）
st.markdown("<div class='form-label'>テーマを選んでください</div>", unsafe_allow_html=True)
interest = st.selectbox(
    "",
    (
        "自己理解・内省",
        "習慣・ライフスタイル",
        "仕事・キャリア",
        "人間関係・コミュニケーション",
        "恋愛・パートナーシップ",
        "子育て・教育",
        "死生観・人生の意味",
    ),
    label_visibility="collapsed",
    key="k_interest",
)

# 気持ち/読み方: 2カラム横並び
col1, col2 = st.columns(2, gap="large")
with col1:
    st.markdown("<div class='form-label'>今の気持ちに近いものを教えてください</div>", unsafe_allow_html=True)
    feeling = st.radio(
        "",
        (
            "前向きになりたい",
            "迷いを整理したい",
            "自分の軸を確かめたい",
            "人間関係を整えたい",
            "小さく動き出したい",
        ),
        label_visibility="collapsed",
        key="k_feeling",
    )
with col2:
    st.markdown("<div class='form-label'>今回はどんな読み方がしっくりきますか？</div>", unsafe_allow_html=True)
    extra = st.radio(
        "",
        (
            "さらっと読みたい",
            "じっくり考えたい",
            "具体的に実践したい",
        ),
        label_visibility="collapsed",
        key="k_extra",
    )


# 実行ボタン（フォームカード下・左寄せ）
go = st.button("📖 本をえらぶ")
st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# --- 推薦ロジック用キーワード辞書 ---
INTEREST_TO_KEYWORDS = {
    "自己理解・内省": ["自己理解", "自分探し", "内省", "価値観", "自分軸", "問い", "質問"],
    "習慣・ライフスタイル": ["習慣", "ルーティン", "時間術", "ライフスタイル", "朝活", "手放す"],
    "仕事・キャリア": ["仕事", "キャリア", "ビジネス", "仕事術", "会社", "上司", "起業"],
    "人間関係・コミュニケーション": ["人間関係", "コミュニケーション", "聞く", "会話", "傾聴", "質問力"],
    "恋愛・パートナーシップ": ["恋愛", "パートナー", "夫婦", "関係", "愛"],
    "子育て・教育": ["子育て", "教育", "親子", "先生", "学校", "子ども"],
    "死生観・人生の意味": ["死", "人生の意味", "生き方", "幸福", "哲学"],
}

FEELING_TO_KEYWORDS = {
    "前向きになりたい": ["モチベーション", "前向き", "元気", "情熱", "やる気", "ポジティブ", "勇気", "こころ"],
    "迷いを整理したい": ["モヤモヤ", "悩み", "整理", "手放す", "やめる", "断捨離", "不安", "整理する"],
    "自分の軸を確かめたい": ["自分軸", "価値観", "強み", "理想"],
    "人間関係を整えたい": ["人間関係", "コミュニケーション", "傾聴", "会話", "上司", "部下", "パートナー", "恋愛"],
    "小さく動き出したい": ["一歩", "背中を押す", "きっかけ", "スモールステップ"],
}

EXTRA_TO_KEYWORDS = {
    # フォーマット/読み口を示す語に寄せる（テーマ語とは被らない）
    "さらっと読みたい": [
        "短編", "コラム", "要点", "まとめ", "Q&A", "箇条書き", "図解", "見開き", "マンガ", "読みやすい"
    ],
    "じっくり考えたい": [
        "論考", "解説", "長文", "考察", "読み応え", "章末", "問いかけ", "エッセイ"
    ],
    "具体的に実践したい": [
        "ワーク", "演習", "シート", "テンプレート", "チェックリスト", "ステップ", "手順", "実践ガイド"
    ],
}


# 補足テーマ（不足時の関連ジャンル）
RELATED_THEME = {
    "恋愛・パートナーシップ": "人間関係・コミュニケーション",
    "子育て・教育": "人間関係・コミュニケーション",
    "死生観・人生の意味": "自己理解・内省",
    "習慣・ライフスタイル": "自己理解・内省",
    "仕事・キャリア": "人間関係・コミュニケーション",
}

# 補足ラベル（やさしい注釈）
RELATED_THEME_LABELS = {
    "恋愛・パートナーシップ": "ちょっと毛色は違いますが、人間関係のヒントになるかもしれませんね。",
    "子育て・教育": "少し視点を変えて、教育の観点からも役立つかもしれませんね。",
    "死生観・人生の意味": "自己理解のヒントとしても読めるかもしれませんね。",
    "習慣・ライフスタイル": "日々に取り入れやすい小さな気づきになるかもしれませんね。",
    "仕事・キャリア": "人との関わりの観点からも役立つかもしれませんね。",
}

# テーマから遠い語のペナルティ
INTEREST_PENALTY = {
    "自己理解・内省": ["恋愛", "パートナー", "夫婦", "子育て", "教育", "マーケティング", "起業", "ビジネス"],
    "習慣・ライフスタイル": ["恋愛", "子育て", "マーケティング", "起業"],
    "仕事・キャリア": ["恋愛", "子育て", "死", "死生観"],
    "人間関係・コミュニケーション": ["起業", "マーケティング", "マンダラ", "時間術", "子育て", "教育", "親子", "学校"],
    "恋愛・パートナーシップ": ["起業", "マーケティング", "仕事術"],
    "子育て・教育": ["恋愛", "マーケティング", "起業"],
    "死生観・人生の意味": ["マーケティング", "起業", "恋愛", "子育て"],
}

# Amazon検索リンクの生成（タイトル + 著者）
AUTHOR_TOKENS = ["マツダミヒロ", "松田充弘", "WAKANA"]

def guess_author_from_keywords(kw: str) -> str | None:
    if not isinstance(kw, str):
        return None
    if any(tok in kw for tok in ["WAKANA", "ワカナ", "わかな"]):
        return "WAKANA"
    # デフォルトはマツダミヒロ系
    return "マツダミヒロ"


def build_amazon_link(title: str, author: str | None = None) -> str:
    """Amazonの検索URLを作る（直接URLは使わず検索ページに統一）。"""
    if author and isinstance(author, str):
        query = quote_plus(f"{title} {author}")
    else:
        # 著者不明なら既知の著者候補を含めて検索
        query = quote_plus(f"{title} " + " OR ".join(AUTHOR_TOKENS))
    return f"https://www.amazon.co.jp/s?k={query}"

def _match_any_keyword(cell: str, kw_list: list[str]) -> bool:
    if not isinstance(cell, str):
        return False
    text = cell.lower()
    return any(k.lower() in text for k in kw_list)

# Helper: normalize and concatenate text parts
def _normalize_text(*parts: str) -> str:
    return "\n".join([(p or "").lower().strip() for p in parts])

def filter_books(df: pd.DataFrame, interest_choice: str, feeling_choice: str, extra_choice: str = "") -> pd.DataFrame:
    # 1) テーマ・気持ち 両方のキーワードを結合
    interest_kw = INTEREST_TO_KEYWORDS.get(interest_choice, [])
    feeling_kw = FEELING_TO_KEYWORDS.get(feeling_choice, [])
    combined_kw = list(dict.fromkeys(interest_kw + feeling_kw))  # 重複除去・順序維持

    penalty_kw = INTEREST_PENALTY.get(interest_choice, [])
    extra_kw = EXTRA_TO_KEYWORDS.get(extra_choice, [])

    # 2) キーワード欄が存在しない場合は全件
    if "keywords" not in df.columns:
        return df.copy()

    # 3) Weighted scoring using title/description/keywords
    df = df.copy()
    # precompute lowercase fields
    df["_title"] = df["title"].astype(str).str.lower()
    df["_desc"]  = df["description"].astype(str).str.lower()
    df["_keys"]  = df["keywords"].astype(str).str.lower()

    # boolean matches
    df["mi_keys"] = df["_keys"].apply(lambda s: _match_any_keyword(s, interest_kw))
    df["mi_title"] = df["_title"].apply(lambda s: _match_any_keyword(s, interest_kw))
    df["mi_desc"] = df["_desc"].apply(lambda s: _match_any_keyword(s, interest_kw))

    df["mf_keys"] = df["_keys"].apply(lambda s: _match_any_keyword(s, feeling_kw))
    df["mf_desc"] = df["_desc"].apply(lambda s: _match_any_keyword(s, feeling_kw))

    df["mx_keys"] = df["_keys"].apply(lambda s: _match_any_keyword(s, extra_kw))

    df["penalty"] = df["_keys"].apply(lambda s: _match_any_keyword(s, penalty_kw))

    # weighted score
    df["score"] = (
        (df["mi_keys"].astype(int) * 3)
        + (df["mi_title"].astype(int) * 2)
        + (df["mi_desc"].astype(int) * 1)
        + (df["mf_keys"].astype(int) * 2)
        + (df["mf_desc"].astype(int) * 1)
        + (df["mx_keys"].astype(int) * 1)
        - (df["penalty"].astype(int) * 1)
    )

    # 軽いテーマ×気持ち ボーナス（+1）
    BONUS_MAP = {
        ("仕事・キャリア", "小さく動き出したい"),
        ("自己理解・内省", "自分の軸を確かめたい"),
        ("人間関係・コミュニケーション", "人間関係を整えたい"),
        ("恋愛・パートナーシップ", "人間関係を整えたい"),
        ("習慣・ライフスタイル", "前向きになりたい"),
        ("習慣・ライフスタイル", "小さく動き出したい"),
        ("死生観・人生の意味", "迷いを整理したい"),
    }
    if (interest_choice, feeling_choice) in BONUS_MAP:
        df["score"] = df["score"] + 1

    # Tiered selection based on weighted scores
    strong = df[df["score"] >= 4]
    medium = df[(df["score"] >= 2) & (df["score"] < 4)]
    if len(strong) >= 3:
        return strong
    elif len(strong) + len(medium) >= 3:
        return pd.concat([strong, medium]).head(30)
    else:
        # 最後の手として combined_kw のどれかにマッチ
        loose = df[df["_keys"].apply(lambda s: _match_any_keyword(s, combined_kw)) | df["_desc"].apply(lambda s: _match_any_keyword(s, combined_kw))]
        merged = pd.concat([strong, medium, loose]).drop_duplicates()
        if len(merged) >= 3:
            return merged.head(30)
        # それでも足りなければ全体
        return df

if 'go' in locals() and go:
    candidates = filter_books(books, interest, feeling, extra)

    if len(candidates) == 0:
        st.info("条件にぴったりの本が少なかったため、全体からもおすすめを選びました。")

    # スコア高い順に並べ、足りなければ全体から補完（補完側もスコア優先）
    cols_for_sort = [c for c in ["score"] if c in candidates.columns]
    if len(candidates) >= 1 and cols_for_sort:
        candidates["_rand"] = np.random.rand(len(candidates))
        cand_sorted = candidates.sort_values(["score", "_rand"], ascending=[False, True])
    else:
        cand_sorted = candidates

    # --- 補完本タイトル追跡 ---
    supplemented_titles = set()

    if len(cand_sorted) >= 3:
        # 1冊目：ドンピシャ（最上位）
        pick1 = cand_sorted.iloc[0:1]
        # 2冊目：次点（2番目）
        pick2 = cand_sorted.iloc[1:2]
        # 3冊目：探索枠（残りからランダム1冊）
        remaining = cand_sorted.iloc[2:]
        if len(remaining) >= 1:
            pick3 = remaining.sample(1, random_state=np.random.randint(1_000_000_000))
            # pick3は補完ではない（同じテーマ内）
        else:
            rest = books.drop(cand_sorted.index, errors="ignore")
            pick3 = rest.sample(1, random_state=np.random.randint(1_000_000_000))
            # pick3は補完本
            supplemented_titles.update(pick3["title"].tolist())
        picks = pd.concat([pick1, pick2, pick3], ignore_index=True)
    elif len(cand_sorted) == 2:
        rest = books.drop(cand_sorted.index, errors="ignore")
        pick3 = rest.sample(1, random_state=np.random.randint(1_000_000_000))
        picks = pd.concat([cand_sorted, pick3], ignore_index=True)
        supplemented_titles.update(pick3["title"].tolist())
    elif len(cand_sorted) == 1:
        rest = books.drop(cand_sorted.index, errors="ignore")
        supplement = rest.sample(2, random_state=np.random.randint(1_000_000_000))
        picks = pd.concat([cand_sorted, supplement], ignore_index=True)
        supplemented_titles.update(supplement["title"].tolist())
    else:
        # フォールバック：全体からランダム
        picks = books.sample(3, random_state=np.random.randint(1_000_000_000))
        supplemented_titles.update(picks["title"].tolist())

    # 不要な_rand列を削除
    if "_rand" in picks.columns:
        picks = picks.drop(columns=["_rand"])
    if "_rand" in candidates.columns:
        candidates = candidates.drop(columns=["_rand"])
    if 'rest' in locals() and "_rand" in rest.columns:
        rest = rest.drop(columns=["_rand"])

    # st.success("おすすめの本はこちらです！")
    st.markdown("## 🌟 特におすすめの1冊")
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # 最優先の1冊（カード表示）
    pick = picks.iloc[0]
    esc_title = html.escape(str(pick["title"]))
    esc_desc = html.escape(str(pick["description"]))
    hero_link = build_amazon_link(pick['title'], guess_author_from_keywords(pick.get('keywords', '')))
    cover_html = ""
    if SHOW_COVERS:
        cover_url = get_cover_url(pick.get("isbn"), pick["title"], guess_author_from_keywords(pick.get("keywords", "")))
        if cover_url:
            cover_html = f'<img src="{html.escape(cover_url)}" alt="表紙" loading="lazy" decoding="async" />'
        else:
            cover_html = f'<img src="{NO_COVER_IMG}" alt="表紙画像が見つかりませんでした" />'

    # --- 補足ラベル（補完本の場合のみ） ---
    note_html = ""
    if esc_title in supplemented_titles:
        note = RELATED_THEME_LABELS.get(interest, "")
        if note:
            note_html = f"<div class='sub-label'>{html.escape(note)}</div>"

    if cover_html:
        hero_html = f"""
<div class="hero-card">
  <div class="card-grid">
    <div class="card-cover">{cover_html}</div>
    <div class="card-body">
      <div class="hero-title">『{esc_title}』</div>
      {note_html}
      <p class="hero-desc">{esc_desc}</p>
      <a class="link-btn" href="{hero_link}" target="_blank" rel="noopener" aria-label="Amazonで{esc_title}を検索">📦 Amazonで見る</a>
    </div>
  </div>
</div>
"""
        hero_html = textwrap.dedent(hero_html).lstrip()
    else:
        hero_html = f"""
<div class="hero-card">
  <div class="card-grid">
    <div class="card-body">
      <div class="hero-title">『{esc_title}』</div>
      {note_html}
      <p class="hero-desc">{esc_desc}</p>
      <a class="link-btn" href="{hero_link}" target="_blank" rel="noopener" aria-label="Amazonで{esc_title}を検索">📦 Amazonで見る</a>
    </div>
  </div>
</div>
"""
        hero_html = textwrap.dedent(hero_html).lstrip()
    hero_full = f"""
<html><head><meta charset='utf-8'><style>
body{{margin:0;font-family:'Hiragino Sans','Noto Sans JP','Yu Gothic',sans-serif;color:#374151;}}
.hero-card,.book-card{{background:#fff;border:1px solid #E6E6E6;border-radius:10px;padding:16px 18px;box-shadow:0 2px 6px rgba(0,0,0,.05);}}
.card-grid{{display:grid;grid-template-columns:170px 1fr;gap:18px;align-items:start}}
.card-cover img{{width:100%;height:auto;max-height:200px;object-fit:contain;background:#fafafa;border:1px solid #eee;border-radius:8px;padding:8px;box-sizing:border-box}}
.hero-title{{font-weight:700;margin-bottom:6px;font-size:18px;line-height:1.5}}
.hero-desc{{margin:8px 0 12px;line-height:1.7;font-size:16px;color:#374151}}
.link-btn{{display:inline-block;padding:8px 18px;border-radius:6px;text-decoration:none;background:#EEF2FF;color:#1D4ED8;border:1px solid #c7d2fe;font-weight:600;}}
.card-body{{display:flex;flex-direction:column;gap:8px;justify-content:space-between}}
.card-body .link-btn{{align-self:flex-end}}
@media (max-width:640px){{ .card-body .link-btn{{align-self:stretch;text-align:center;width:100%}} }}
</style></head><body>{hero_html}</body></html>
"""
    components.html(hero_full, height=380, scrolling=False)

    st.markdown("## 📖 こちらも手にとってみませんか")
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    # 次点の2冊（グリッドで横並び／スマホは縦）
    cards_html = []
    for _, book in picks.iloc[1:].iterrows():
        esc_t = html.escape(str(book["title"]))
        esc_d = html.escape(str(book["description"]))
        link = build_amazon_link(book['title'], guess_author_from_keywords(book.get('keywords', '')))
        cover2 = ""
        if SHOW_COVERS:
            c2 = get_cover_url(book.get("isbn"), book["title"], guess_author_from_keywords(book.get("keywords", "")))
            if c2:
                cover2 = f'<img src="{html.escape(c2)}" alt="表紙" loading="lazy" decoding="async" />'
            else:
                cover2 = f'<img src="{NO_COVER_IMG}" alt="表紙画像が見つかりませんでした" />'

        # --- 補足ラベル（補完本の場合のみ） ---
        note_html = ""
        if esc_t in supplemented_titles:
            note = RELATED_THEME_LABELS.get(interest, "")
            if note:
                note_html = f"<div class='sub-label'>{html.escape(note)}</div>"

        if cover2:
            card_html = f"""
<div class="book-card">
  <div class="card-grid">
    <div class="card-cover">{cover2}</div>
    <div class="card-body">
      <div class="book-title">『{esc_t}』</div>
      {note_html}
      <p class="book-desc">{esc_d}</p>
      <a class="link-btn" href="{link}" target="_blank" rel="noopener" aria-label="Amazonで{esc_t}を検索">📦 Amazonで見る</a>
    </div>
  </div>
</div>
"""
            card_html = textwrap.dedent(card_html).lstrip()
        else:
            card_html = f"""
<div class="book-card">
  <div class="card-grid">
    <div class="card-body">
      <div class="book-title">『{esc_t}』</div>
      {note_html}
      <p class="book-desc">{esc_d}</p>
      <a class="link-btn" href="{link}" target="_blank" rel="noopener" aria-label="Amazonで{esc_t}を検索">📦 Amazonで見る</a>
    </div>
  </div>
</div>
"""
            card_html = textwrap.dedent(card_html).lstrip()
        cards_html.append(card_html)
    grid_full = f"""
<html><head><meta charset='utf-8'><style>
body{{margin:0;font-family:'Hiragino Sans','Noto Sans JP','Yu Gothic',sans-serif;color:#374151;}}
.book-grid{{display:grid;gap:16px;}}
@media (min-width:768px){{ .book-grid{{grid-template-columns:1fr 1fr;}} }}
.book-card{{background:#fff;border:1px solid #E6E6E6;border-radius:10px;padding:16px 18px;box-shadow:0 2px 6px rgba(0,0,0,.05);}}
.card-grid{{display:grid;grid-template-columns:140px 1fr;gap:16px;align-items:start}}
.card-cover img{{width:100%;height:auto;max-height:200px;object-fit:contain;background:#fafafa;border:1px solid #eee;border-radius:8px;padding:8px;box-sizing:border-box}}
.book-title{{font-weight:700;margin-bottom:6px;font-size:17px;line-height:1.5}}
.book-desc{{margin:8px 0 12px;line-height:1.7;font-size:15px;color:#374151}}
.link-btn{{display:inline-block;padding:8px 18px;border-radius:6px;text-decoration:none;background:#EEF2FF;color:#1D4ED8;border:1px solid #c7d2fe;font-weight:600;}}
.sub-label{{ font-size: 14px; color:#6b7280; margin:4px 0 6px; font-style: italic; }}
.card-body{{display:flex;flex-direction:column;gap:8px;justify-content:space-between}}
.card-body .link-btn{{align-self:flex-end}}
@media (max-width:640px){{ .card-body .link-btn{{align-self:stretch;text-align:center;width:100%}} }}
</style></head><body><div class='book-grid'>{"".join(cards_html)}</div></body></html>
"""
    components.html(grid_full, height=900, scrolling=True)