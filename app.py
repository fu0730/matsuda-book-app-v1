import streamlit as st
import pandas as pd
from urllib.parse import quote_plus
import numpy as np
import html
import requests
import io

st.set_page_config(
    page_title="📘 そっとよりそう本さがし",
    page_icon="📘",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    /* Base spacing */
    .main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

    /* Headings readability */
    h1, h2, h3 { line-height: 1.3; }

    /* Make the main content column comfortably narrow on large screens */
    @media (min-width: 1024px) {
      .main .block-container { max-width: 940px; }
    }

    /* Mobile tweaks */
    @media (max-width: 640px) {
      .stButton>button { width: 100%; }
      .stRadio, .stSelectbox { font-size: 0.95rem; }
      .stMarkdown p { font-size: 0.98rem; line-height: 1.7; }
    }

    /* Cards & grid for desktop/mobile */
    .hero-card, .book-card {
      background: var(--card-bg, #fff);
      border: 1px solid var(--card-border, #e6e6e6);
      border-radius: 12px;
      padding: 16px 18px;
      box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }
    .hero-card { border-width: 2px; }
    .hero-title, .book-title { font-weight: 700; margin-bottom: 6px; font-size: 1.12rem; line-height: 1.5; }
    .hero-desc, .book-desc { margin: 8px 0 12px; line-height: 1.7; overflow-wrap: anywhere; }

    .book-grid { display: grid; gap: 12px; }
    @media (min-width: 768px) { .book-grid { grid-template-columns: 1fr 1fr; } }

    /* Link button */
    .link-btn { display:inline-block; padding: 9px 14px; border-radius: 8px; text-decoration:none; border:1px solid #ddd; background:#eef2ff; color:#1d4ed8; border-color:#c7d2fe; font-size:1rem; }
    .link-btn:hover { background:#e0e7ff; }

    /* Dark mode friendly defaults */
    @media (prefers-color-scheme: dark) {
      :root { --card-bg: #111418; --card-border: #242a31; }
      .link-btn { border-color:#333; }
      .link-btn:hover { background:#1c222b; }
    }

    /* Typography & base */
    html, body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji"; }
    body { -webkit-font-smoothing: antialiased; }

    /* Section spacing */
    .section { margin: 24px 0; }

    /* Improve label wrapping */
    .stSelectbox label, .stRadio label { white-space: normal; line-height: 1.5; }

    /* Clamp long descriptions on mobile */
    @media (max-width: 640px) {
      .book-desc { display: -webkit-box; -webkit-line-clamp: 5; -webkit-box-orient: vertical; overflow: hidden; }
    }

    /* details/summary styling */
    details { margin-top: 6px; }
    details summary { cursor: pointer; color: #3366cc; outline: none; }
    details[open] summary { color: #555; }

    /* Larger touch targets on mobile */
    @media (max-width: 640px) {
      .link-btn { width: 100%; text-align: center; padding: 12px 14px; }
    }

    /* Sections / dividers */
    .section { margin: 24px 0; }
    .section-hero { margin-bottom: 28px; }
    .section-others { margin-top: 14px; }
    .divider { height: 1px; background: var(--card-border, #e6e6e6); margin: 14px 0; }

    /* 見出しサイズを少し抑える */
    h1 { font-size: 1.4rem !important; }
    h2 { font-size: 1.15rem !important; }

    /* 本文や説明はほんの少し大きく */
    .stMarkdown p, .book-desc {
      font-size: 1.02rem;
      line-height: 1.65;
    }

    /* Headings spacing/weight (控えめに) */
    h1 { margin: 0.2rem 0 1.0rem; font-weight: 700; }
    h2 { margin: 0.8rem 0 0.6rem; font-weight: 650; }

    /* Success alert: 少し控えめに */
    .stAlert { border-radius: 10px; margin: 8px 0 10px; }
    .stAlert > div { padding: 8px 10px; font-size: 0.9rem; }

    /* Radio/Select の行間とタップしやすさ */
    .stRadio label, .stSelectbox label { margin-bottom: 4px; }
    .stRadio [role="radiogroup"] label { padding: 4px 2px; }

    /* Amazonリンクをボタン風に（色弱でも見やすいコントラスト） */
    .link-btn { background:#eef2ff; color:#1d4ed8; border-color:#c7d2fe; font-size:1rem; padding:9px 14px; }
    .link-btn:hover { background:#e0e7ff; }

    /* カード間の余白をやや広く（PC） */
    @media (min-width: 1024px) {
      .book-grid { gap: 16px; }
    }

    /* Desktop typography boost */
    @media (min-width: 768px) {
      h1 { font-size: 1.6rem !important; }
      h2 { font-size: 1.25rem !important; }
      .stMarkdown p, .book-desc { font-size: 1.05rem; line-height: 1.7; }
      .stRadio, .stSelectbox { font-size: 1rem; }
      .hero-title { font-size: 1.1rem; }
      .book-title { font-size: 1.05rem; }
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
    for col in ["title", "description", "amazon_url", "keywords"]:
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

st.title("📘 今日のあなたに、そっとよりそう本を探しましょう")

# 質問
interest = st.selectbox("テーマを選んでください", (
    "自己理解・内省",
    "習慣・ライフスタイル",
    "仕事・キャリア",
    "人間関係・コミュニケーション",
    "恋愛・パートナーシップ",
    "子育て・教育",
    "死生観・人生の意味"
))

feeling = st.radio("今の気持ちに近いものを教えてください", (
    "前向きになりたい",
    "迷いを整理したい",
    "自分の軸を確かめたい",
    "人間関係を整えたい",
    "小さく動き出したい",
))

# 追加の一問（読み方/アプローチ軸）：精度を少し高める
extra = st.radio(
    "今回はどんな読み方がしっくりきますか？",
    (
        "さらっと読みたい",
        "じっくり考えたい",
        "具体的に実践したい",
    ),
)

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

INTEREST_PENALTY = {
    "自己理解・内省": ["恋愛", "パートナー", "夫婦", "子育て", "教育", "マーケティング", "起業", "ビジネス"],
    "習慣・ライフスタイル": ["恋愛", "子育て", "マーケティング", "起業"],
    "仕事・キャリア": ["恋愛", "子育て", "死", "死生観"],
    "人間関係・コミュニケーション": ["起業", "マーケティング", "マンダラ", "時間術"],
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

if st.button("📖 本をえらぶ"):
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

    if len(cand_sorted) >= 3:
        # Prefer items that clearly match the selected theme
        theme_regex = "|".join(INTEREST_TO_KEYWORDS.get(interest, []))
        theme_mask_sorted = cand_sorted["_keys"].str.contains(theme_regex, case=False, na=False) | \
                            cand_sorted["_title"].str.contains(theme_regex, case=False, na=False)
        preferred = cand_sorted[theme_mask_sorted]
        if len(preferred) >= 3:
            picks = preferred.head(3)
        else:
            need = 3 - len(preferred)
            others = cand_sorted[~theme_mask_sorted]
            picks = pd.concat([preferred, others.head(need)], ignore_index=True)
    elif len(cand_sorted) >= 1:
        need = 3 - len(cand_sorted)
        # 補完候補：既に選んだものを除き、同じスコア計算を使えるように一時結合
        rest = books.drop(cand_sorted.index, errors="ignore").copy()
        if "keywords" in rest.columns:
            # Recompute weighted scoring for rest, matching filter_books
            rest["_title"] = rest["title"].astype(str).str.lower()
            rest["_desc"]  = rest["description"].astype(str).str.lower()
            rest["_keys"]  = rest["keywords"].astype(str).str.lower()
            rest["mi_keys"] = rest["_keys"].apply(lambda s: _match_any_keyword(s, INTEREST_TO_KEYWORDS.get(interest, [])))
            rest["mi_title"] = rest["_title"].apply(lambda s: _match_any_keyword(s, INTEREST_TO_KEYWORDS.get(interest, [])))
            rest["mi_desc"] = rest["_desc"].apply(lambda s: _match_any_keyword(s, INTEREST_TO_KEYWORDS.get(interest, [])))
            rest["mf_keys"] = rest["_keys"].apply(lambda s: _match_any_keyword(s, FEELING_TO_KEYWORDS.get(feeling, [])))
            rest["mf_desc"] = rest["_desc"].apply(lambda s: _match_any_keyword(s, FEELING_TO_KEYWORDS.get(feeling, [])))
            rest["mx_keys"] = rest["_keys"].apply(lambda s: _match_any_keyword(s, EXTRA_TO_KEYWORDS.get(extra, [])))
            rest["penalty"] = rest["_keys"].apply(lambda s: _match_any_keyword(s, INTEREST_PENALTY.get(interest, [])))
            rest["score"] = (
                (rest["mi_keys"].astype(int) * 3)
                + (rest["mi_title"].astype(int) * 2)
                + (rest["mi_desc"].astype(int) * 1)
                + (rest["mf_keys"].astype(int) * 2)
                + (rest["mf_desc"].astype(int) * 1)
                + (rest["mx_keys"].astype(int) * 1)
                - (rest["penalty"].astype(int) * 1)
            )
            if (interest, feeling) in {
                ("仕事・キャリア", "小さく動き出したい"),
                ("自己理解・内省", "自分の軸を確かめたい"),
                ("人間関係・コミュニケーション", "人間関係を整えたい"),
                ("恋愛・パートナーシップ", "人間関係を整えたい"),
                ("習慣・ライフスタイル", "前向きになりたい"),
                ("習慣・ライフスタイル", "小さく動き出したい"),
                ("死生観・人生の意味", "迷いを整理したい"),
            }:
                rest["score"] = rest["score"] + 1
            rest["_rand"] = np.random.rand(len(rest))
            rest = rest.sort_values(["score", "_rand"], ascending=[False, True])
        picks = pd.concat([cand_sorted, rest.head(need)], ignore_index=True)
        # Re-order picks to prefer theme matches
        theme_regex = "|".join(INTEREST_TO_KEYWORDS.get(interest, []))
        tmask = picks["_keys"].str.contains(theme_regex, case=False, na=False) | \
                picks["_title"].str.contains(theme_regex, case=False, na=False)
        if tmask.any():
            picks = pd.concat([picks[tmask], picks[~tmask]]).head(3)
    else:
        # フォールバック：全体からランダム
        picks = books.sample(3)
        theme_regex = "|".join(INTEREST_TO_KEYWORDS.get(interest, []))
        picks["_title"] = picks["title"].astype(str).str.lower()
        picks["_keys"]  = picks["keywords"].astype(str).str.lower()
        tmask = picks["_keys"].str.contains(theme_regex, case=False, na=False) | \
                picks["_title"].str.contains(theme_regex, case=False, na=False)
        if tmask.any():
            picks = pd.concat([picks[tmask], picks[~tmask]]).head(3)

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
    hero_html = f"""
<div class="hero-card">
  <div class="hero-title">『{esc_title}』</div>
  <p class="hero-desc">{esc_desc}</p>
  <a class="link-btn" href="{hero_link}" target="_blank" rel="noopener" aria-label="Amazonで{esc_title}を検索">📦 Amazonで見る</a>
</div>
"""
    st.markdown("<div class='section section-hero'>" + hero_html + "</div>", unsafe_allow_html=True)

    st.markdown("## 📖 こちらも手にとってみませんか")
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    # 次点の2冊（グリッドで横並び／スマホは縦）
    cards_html = []
    for _, book in picks.iloc[1:].iterrows():
        esc_t = html.escape(str(book["title"]))
        esc_d = html.escape(str(book["description"]))
        link = build_amazon_link(book['title'], guess_author_from_keywords(book.get('keywords', '')))
        card_html = f"""
<div class="book-card">
  <div class="book-title">『{esc_t}』</div>
  <p class="book-desc">{esc_d}</p>
  <a class="link-btn" href="{link}" target="_blank" rel="noopener" aria-label="Amazonで{esc_t}を検索">📦 Amazonで見る</a>
</div>
"""
        cards_html.append(card_html)
    st.markdown("<div class='section section-others'><div class='book-grid'>" + "".join(cards_html) + "</div></div>", unsafe_allow_html=True)