# app.py
import base64
import re
import time
import urllib.parse
import urllib.request
import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
from prompts import SYSTEM_PROMPT

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="나의 가능세계 | 가능세계 서재 - AI 평행우주 단편소설",
    page_icon="📖",
    layout="centered",
)

# 2. 숭고한(Sublime) 다크 아카이브 & 맞춤형 크로키 북커버 CSS
st.markdown("""
<style>
@import url('https://hangeul.pstatic.net/hangeul_static/css/maru-buri.css');

header[data-testid="stHeader"] {
    background: transparent !important;
}

@keyframes slowPulse {
    0%, 100% { opacity: 0.75; }
    50% { opacity: 1; }
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(14px); }
    to { opacity: 1; transform: translateY(0); }
}

/* 전체 배경: 칠흑 같은 어둠 위로 수직으로 떨어지는 한 줄기 천창(Chiaroscuro) 빛 */
.stApp {
    background-color: #070605;
    background-image: 
        radial-gradient(ellipse 38% 55% at 50% 0%, rgba(212, 175, 115, 0.14) 0%, rgba(18, 14, 10, 0.45) 55%, rgba(7, 6, 5, 1) 100%);
    color: #e6dfd5;
    font-family: 'MaruBuri', serif;
}

h1, h2, h3, h4, p, label, .stMarkdown, .stRadio label, .stSelectbox label, .stTextInput label, .stTextArea label, .stNumberInput label, .stMultiSelect label {
    font-family: 'MaruBuri', serif !important;
    color: #e6dfd5 !important;
}

/* 상단 네비게이션 버튼 '...' 잘림 완벽 방지 */
div[data-testid="stHorizontalBlock"] button {
    padding: 0.45rem 0.2rem !important;
    font-size: 0.82rem !important;
    white-space: nowrap !important;
    letter-spacing: -0.3px !important;
    min-height: 38px !important;
}

/* 좌측 상단 미니멀 고서 엠블럼 */
.top-left-book-emblem {
    position: fixed;
    top: 68px;
    left: 32px;
    z-index: 999999;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    background: rgba(14, 12, 10, 0.85);
    border: 1px solid rgba(198, 163, 106, 0.35);
    border-radius: 50%;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.85);
    pointer-events: none;
}

.top-left-book-emblem svg {
    width: 24px;
    height: 24px;
    overflow: visible;
}

@media (max-width: 1100px) {
    .top-left-book-emblem {
        position: relative;
        top: 0;
        left: 0;
        margin-top: 6px;
        margin-bottom: 12px;
    }
}

/* ─────────────────────────────────────────────────────────
   입장 페이지: 숭고한(Sublime) 모놀리스 & 건축적 여백 디자인
   ───────────────────────────────────────────────────────── */
.sublime-wrapper {
    position: relative;
    background: linear-gradient(180deg, rgba(16, 14, 12, 0.95) 0%, rgba(9, 8, 7, 0.98) 100%);
    border: 1px solid rgba(198, 163, 106, 0.28);
    padding: 10px;
    margin-top: 18px;
    margin-bottom: 28px;
    box-shadow: 0 30px 80px rgba(0, 0, 0, 0.95);
    animation: fadeInUp 1.1s ease-out;
}

.sublime-inner-frame {
    border: 1px solid rgba(198, 163, 106, 0.14);
    padding: 0 0 48px 0;
}

/* 상단 건축적 아치 & 빛의 회랑 비주얼 */
.sublime-hero {
    position: relative;
    width: 100%;
    height: 360px;
    background-image:
        linear-gradient(to bottom, rgba(7, 6, 5, 0.35) 0%, rgba(11, 9, 8, 0.72) 70%, #0b0908 100%),
        url('https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1400&q=85');
    background-size: cover;
    background-position: center;
    filter: grayscale(45%) contrast(110%);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 0 24px;
}

/* 두 궤적의 교차를 상징하는 기하학 아스트롤라베 선화 */
.sacred-geometry {
    margin-bottom: 22px;
    animation: slowPulse 5s infinite ease-in-out;
}

.sublime-kicker {
    font-size: 0.72rem;
    letter-spacing: 5px;
    color: #b89f78 !important;
    text-transform: uppercase;
    margin-bottom: 14px;
}

.sublime-title {
    font-size: 2.5rem;
    font-weight: 400;
    color: #f4ece0 !important;
    letter-spacing: 7px;
    margin-bottom: 12px;
    text-shadow: 0 10px 30px rgba(0, 0, 0, 0.9);
}

.sublime-divider {
    width: 1px;
    height: 42px;
    background: linear-gradient(to bottom, rgba(198, 163, 106, 0.7), transparent);
    margin: 18px auto;
}

.sublime-body-section {
    padding: 10px 46px 0 46px;
    text-align: center;
}

@media (max-width: 640px) {
    .sublime-body-section {
        padding: 10px 22px 0 22px;
    }
    .sublime-title {
        font-size: 1.9rem;
        letter-spacing: 4px;
    }
}

.sublime-epigraph {
    font-size: 1.02rem;
    color: #d6c8b4 !important;
    line-height: 2.1;
    letter-spacing: 0.4px;
    margin: 0 auto 36px auto;
    max-width: 520px;
    font-weight: 300;
}

.sublime-prose {
    font-size: 0.96rem;
    color: #aba090 !important;
    line-height: 2.15;
    max-width: 540px;
    margin: 0 auto 44px auto;
    word-break: keep-all;
}

/* 3단 아카이브 필러 (과장 없이 절제된 타이포그래피 그리드) */
.pillar-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
    margin: 0 auto 40px auto;
    border-top: 1px solid rgba(198, 163, 106, 0.18);
    border-bottom: 1px solid rgba(198, 163, 106, 0.18);
    padding: 28px 10px;
}

@media (max-width: 640px) {
    .pillar-grid {
        grid-template-columns: 1fr;
        gap: 22px;
    }
}

.pillar-item {
    text-align: center;
    padding: 0 8px;
}

.pillar-num {
    font-size: 0.72rem;
    letter-spacing: 3px;
    color: #b89867 !important;
    margin-bottom: 8px;
}

.pillar-title {
    font-size: 0.95rem;
    color: #ebe2d5 !important;
    margin-bottom: 8px;
    font-weight: 600;
}

.pillar-desc {
    font-size: 0.82rem;
    color: #8f8475 !important;
    line-height: 1.7;
    word-break: keep-all;
}

.sublime-notice {
    max-width: 540px;
    margin: 0 auto;
    padding: 18px 24px;
    background: rgba(255, 255, 255, 0.015);
    border-left: 2px solid rgba(198, 163, 106, 0.5);
    text-align: left;
    font-size: 0.85rem;
    color: #9e9283 !important;
    line-height: 1.85;
}

/* ─────────────────────────────────────────────────────────
   맞춤형 흑백 연필 크로키 단행본 표지 (Custom Book Cover)
   ───────────────────────────────────────────────────────── */
.book-cover-outer {
    max-width: 440px;
    margin: 28px auto 38px auto;
    background-color: #efebe1;
    background-image: 
        radial-gradient(circle at center, transparent 55%, rgba(120, 105, 82, 0.18) 100%),
        linear-gradient(90deg, rgba(60, 48, 35, 0.16) 0%, rgba(60, 48, 35, 0.03) 5%, transparent 12%);
    padding: 18px;
    border-radius: 3px 7px 7px 3px;
    border-left: 7px solid #3a3127;
    box-shadow: 0 28px 65px rgba(0, 0, 0, 0.92), 0 0 1px rgba(255, 255, 255, 0.2);
    animation: fadeInUp 1.1s ease-out;
}

.book-cover-inner {
    border: 1px solid #9c8f7a;
    padding: 28px 24px 24px 24px;
    text-align: center;
    position: relative;
}

.book-series-label {
    font-size: 0.65rem;
    letter-spacing: 3.5px;
    color: #6b5f4f !important;
    text-transform: uppercase;
    margin-bottom: 14px;
}

.book-cover-title {
    font-size: 1.55rem;
    font-weight: 700;
    color: #1f1b16 !important;
    letter-spacing: 3px;
    margin-bottom: 6px;
}

.book-cover-sub {
    font-size: 0.82rem;
    color: #5c5143 !important;
    font-style: italic;
    margin-bottom: 20px;
}

.croquis-frame {
    width: 100%;
    aspect-ratio: 3 / 3.6;
    background-color: #efeae0;
    border: 1px solid #b8ad9b;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 20px;
    position: relative;
}

.croquis-frame img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    /* 어떤 이미지든 종이 위에 그린 흑백 연필/목탄 크로키 질감으로 변환 */
    filter: grayscale(100%) contrast(135%) brightness(103%);
    mix-blend-mode: multiply;
}

.book-cover-footer {
    border-top: 1px solid #c4b9a5;
    padding-top: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.76rem;
    color: #4f4639 !important;
    letter-spacing: 0.8px;
}

/* 입력창 & 버튼 스타일 */
input, textarea, [data-baseweb="select"] > div {
    background-color: #12100d !important;
    color: #f0e9df !important;
    border: 1px solid #2e261d !important;
    font-family: 'MaruBuri', serif !important;
}

input:focus, textarea:focus {
    border-color: #b89867 !important;
    box-shadow: 0 0 8px rgba(184, 152, 103, 0.25) !important;
}

button[kind="primary"] {
    background: linear-gradient(135deg, #9e7b47 0%, #6e5023 100%) !important;
    color: #fffaf0 !important;
    border: 1px solid #c49f66 !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    padding: 0.65rem 1.2rem !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6) !important;
    transition: all 0.25s ease !important;
}

button[kind="primary"]:hover {
    background: linear-gradient(135deg, #b38d54 0%, #82602b 100%) !important;
    box-shadow: 0 6px 24px rgba(196, 159, 102, 0.35) !important;
}

button[kind="secondary"] {
    background-color: #14110e !important;
    color: #9e9181 !important;
    border: 1px solid #2b241c !important;
}

button[kind="secondary"]:hover {
    border-color: #8c6d3f !important;
    color: #ebe2d5 !important;
}

/* 소설 본문 출력 박스 */
.novel-box {
    font-family: 'MaruBuri', serif;
    background-color: #f3ecdf;
    background-image: 
        linear-gradient(90deg, rgba(120, 90, 50, 0.12) 0%, rgba(120, 90, 50, 0.02) 4%, transparent 10%),
        radial-gradient(circle at center, transparent 60%, rgba(139, 109, 70, 0.14) 100%);
    color: #231e18 !important;
    padding: 50px 42px;
    border-radius: 4px 8px 8px 4px;
    border-left: 6px solid #8c6d46;
    box-shadow: 
        inset 0 0 40px rgba(139, 105, 60, 0.15),
        0 15px 45px rgba(0, 0, 0, 0.85);
    line-height: 2.05;
    font-size: 1.06rem;
    margin-top: 15px;
    white-space: pre-wrap;
    word-break: keep-all;
}

.novel-box * {
    color: #231e18 !important;
}
</style>

<!-- 좌측 상단 미니멀 고서 픽토그램 -->
<div class="top-left-book-emblem">
    <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M32 16C25 11 14 10 6 13V49C14 46 25 47 32 52C39 47 50 46 58 49V13C50 10 39 11 32 16Z" stroke="#c8a46e" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M32 16V52" stroke="#c8a46e" stroke-width="2" stroke-linecap="round"/>
    </svg>
</div>
""", unsafe_allow_html=True)

# 3. 제미나이 클라이언트 연결
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# 4. 세션 상태 초기화
DEFAULT_KEYS = {
    "p0_q1": "", "p0_q2": 25, "p0_q3": None, "p0_q4_type": None,
    "p0_q4_custom": "", "p0_q4_detail": "", "p0_q5": "", "p0_q6": "", "p0_q7": "",
    "p1_q1": None, "p1_q2": None, "p1_q3": None, "p1_q3_reason": "",
    "p1_q4": None, "p1_q5": None, "p1_q6": [], "p1_q7": None,
    "p1_q8": "", "p1_q9": "", "p1_q10": None, "p1_q10_reason": "",
    "p2_q11": "", "p2_q12": "", "p2_q13": "", "p2_q14": None, "p2_q14_reason": "",
    "p3_q15": "", "p3_q16": None, "p3_q17": "",
    "p4_q18": "", "p4_q19": "", "p4_q20": None, "p4_q21": None,
    "p5_q22": "", "p5_q23": ""
}

for k, default_val in DEFAULT_KEYS.items():
    if k not in st.session_state:
        st.session_state[k] = default_val
    else:
        st.session_state[k] = st.session_state[k]

if "entered" not in st.session_state:
    st.session_state.entered = False
if "current_step" not in st.session_state:
    st.session_state.current_step = 0
if "scroll_to_top" not in st.session_state:
    st.session_state.scroll_to_top = False
if "generate_trigger" not in st.session_state:
    st.session_state.generate_trigger = False
if "novel_result" not in st.session_state:
    st.session_state.novel_result = None
if "design_note" not in st.session_state:
    st.session_state.design_note = None
if "cover_b64" not in st.session_state:
    st.session_state.cover_b64 = None
if "cover_meta" not in st.session_state:
    st.session_state.cover_meta = None
if "step_warning" not in st.session_state:
    st.session_state.step_warning = None

if st.session_state.scroll_to_top:
    components.html(
        "<script>window.parent.document.querySelector('section.main').scrollTo({top: 0, behavior: 'smooth'});</script>",
        height=0,
    )
    st.session_state.scroll_to_top = False


# ─────────────────────────────────────────────────────────
# 맞춤형 흑백 연필 크로키 표지 실시간 생성 함수
# ─────────────────────────────────────────────────────────
def generate_custom_croquis_cover(s):
    """사용자의 핵심 오브제(p2_q13)와 서사 분위기를 추출해 맞춤형 흑백 연필 크로키 표지를 생성"""
    raw_obj = s.p2_q13.strip() if s.p2_q13 and s.p2_q13.strip() else "오래된 회중시계와 열쇠"
    raw_mood = s.p4_q18.strip() if s.p4_q18 and s.p4_q18.strip() else "안개 낀 밤의 갈림길"
    author_name = s.p0_q1.strip() if s.p0_q1 and s.p0_q1.strip() else "무명(無名)"

    # 1. 제미나이로 사용자의 오브제를 영문 크로키 드로잉 지시문과 짧은 부제로 변환
    subject_en = "a vintage object resting on an old wooden desk by a quiet window"
    book_subtitle = f"{raw_obj[:18]}에 스민 두 개의 시간"
    try:
        meta_res = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=(
                f"사용자의 기억 속 물건은 '{raw_obj}', 다른 삶의 풍경은 '{raw_mood}'입니다.\n"
                f"1줄째에는 이 물건을 중심으로 한 정물/배경 흑백 연필 크로키용 영문 묘사(20단어 이내, 글자/텍스트 절대 제외)를 적고,\n"
                f"2줄째에는 단행본 표지에 들어갈 품격 있고 절제된 한국어 부제(15자 이내)를 적어주세요.\n"
                f"형식:\nEN: ...\nKO: ..."
            ),
        )
        for line in meta_res.text.strip().splitlines():
            if line.startswith("EN:"):
                subject_en = line.replace("EN:", "").strip()
            elif line.startswith("KO:"):
                book_subtitle = line.replace("KO:", "").strip()
    except Exception:
        pass

    croquis_prompt = (
        f"Minimalist black and white rough pencil croquis sketch on aged cream paper, "
        f"expressive graphite line drawing, fine hatching, contours and raw pencil strokes, "
        f"literary novel illustration, centered single subject with generous blank paper space, "
        f"strictly no text, no letters, no words, no signature. Subject: {subject_en}"
    )

    img_b64 = None

    # 2. 1차 시도: Google Imagen 3 API 호출
    try:
        img_res = client.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=croquis_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="3:4",
                output_mime_type="image/jpeg",
            ),
        )
        if img_res.generated_images:
            img_bytes = img_res.generated_images[0].image.image_bytes
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")
    except Exception:
        pass

    # 3. 2차 자동 폴백: Imagen 모델 권한 제한 시 즉시 크로키 스케치 엔진으로 생성
    if not img_b64:
        try:
            encoded = urllib.parse.quote(croquis_prompt)
            seed = int(time.time()) % 100000
            url = f"https://image.pollinations.ai/prompt/{encoded}?width=720&height=880&nologo=true&seed={seed}&model=flux"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                img_bytes = resp.read()
                img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        except Exception:
            img_b64 = None

    cover_meta = {
        "author": author_name,
        "object": raw_obj[:22],
        "subtitle": book_subtitle,
    }
    return img_b64, cover_meta


def render_book_cover_html(img_b64, meta):
    """생성된 맞춤형 흑백 크로키와 메타데이터를 조합해 문학 단행본 표지 HTML 렌더링"""
    if not meta:
        meta = {"author": "기록자", "object": "기억의 사물", "subtitle": "가지 않은 길의 기록"}

    if img_b64:
        img_tag = f'<img src="data:image/jpeg;base64,{img_b64}" alt="Custom Croquis Cover">'
    else:
        # 네트워크 차단 등 최후의 경우에도 깨지지 않는 미니멀 펜슬 드로잉 SVG
        img_tag = """
        <svg viewBox="0 0 200 240" width="70%" height="70%" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="100" cy="120" r="62" stroke="#3a3228" stroke-width="1" stroke-dasharray="4 3"/>
            <path d="M60 165 C85 110, 115 110, 140 75" stroke="#231e18" stroke-width="1.4"/>
            <path d="M140 165 C115 110, 85 110, 60 75" stroke="#231e18" stroke-width="0.9" stroke-opacity="0.6"/>
            <circle cx="100" cy="120" r="4" fill="#231e18"/>
        </svg>
        """

    return f"""
    <div class="book-cover-outer">
        <div class="book-cover-inner">
            <div class="book-series-label">ARCHIVE OF POSSIBLE WORLDS</div>
            <div class="book-cover-title">나의 가능세계</div>
            <div class="book-cover-sub">{meta['subtitle']}</div>
            <div class="croquis-frame">
                {img_tag}
            </div>
            <div class="book-cover-footer">
                <span>MOTIF · {meta['object']}</span>
                <span>{meta['author']}의 기록</span>
            </div>
        </div>
    </div>
    """


# ─────────────────────────────────────────────────────────
# 유효성 및 성실도(50% 이상) 검증 함수
# ─────────────────────────────────────────────────────────
def is_sincere_text(val, min_len=2):
    if not val or not isinstance(val, str):
        return False
    cleaned = val.strip()
    if len(cleaned) < min_len:
        return False
    if re.fullmatch(r"[ㄱ-ㅎㅏ-ㅣ\W_]+", cleaned):
        return False
    if len(set(cleaned.replace(" ", ""))) == 1 and len(cleaned) >= 2:
        return False
    return True


def check_part0_other_job_valid():
    if st.session_state.p0_q4_type == "기타":
        if not st.session_state.p0_q4_custom or not st.session_state.p0_q4_custom.strip():
            return False
    return True


def evaluate_survey_sincerity():
    s = st.session_state
    q4_valid = (
        is_sincere_text(s.p0_q4_custom, min_len=1)
        if s.p0_q4_type == "기타"
        else (s.p0_q4_type is not None)
    )

    part_checks = {
        "I. 기본": [
            is_sincere_text(s.p0_q1, min_len=1),
            s.p0_q3 is not None,
            q4_valid,
            is_sincere_text(s.p0_q5, min_len=2),
            is_sincere_text(s.p0_q6, min_len=2),
            is_sincere_text(s.p0_q7, min_len=3),
        ],
        "II. 성향": [
            s.p1_q1 is not None,
            s.p1_q2 is not None,
            s.p1_q3 is not None,
            s.p1_q4 is not None,
            s.p1_q5 is not None,
            len(s.p1_q6) > 0,
            s.p1_q7 is not None,
            is_sincere_text(s.p1_q8, min_len=3),
            is_sincere_text(s.p1_q9, min_len=3),
            s.p1_q10 is not None,
        ],
        "III. 기억": [
            is_sincere_text(s.p2_q11, min_len=4),
            is_sincere_text(s.p2_q12, min_len=4),
            is_sincere_text(s.p2_q13, min_len=2),
            s.p2_q14 is not None,
        ],
        "IV. 미래": [
            is_sincere_text(s.p3_q15, min_len=4),
            s.p3_q16 is not None,
            is_sincere_text(s.p3_q17, min_len=3),
        ],
        "V. 다른 길": [
            is_sincere_text(s.p4_q18, min_len=4),
            is_sincere_text(s.p4_q19, min_len=2),
            s.p4_q20 is not None,
            s.p4_q21 is not None,
        ],
        "VI. 조우": [
            is_sincere_text(s.p5_q22, min_len=3),
            is_sincere_text(s.p5_q23, min_len=2),
        ],
    }

    total_items = 0
    filled_items = 0
    weak_parts = []

    for part_name, results in part_checks.items():
        part_total = len(results)
        part_filled = sum(1 for r in results if r)
        total_items += part_total
        filled_items += part_filled
        if part_filled < (part_total / 2):
            weak_parts.append(part_name)

    ratio = filled_items / total_items if total_items > 0 else 0.0
    return ratio, filled_items, total_items, weak_parts


def go_to_step(step_idx):
    if st.session_state.current_step == 0 and step_idx > 0:
        if not check_part0_other_job_valid():
            st.session_state.step_warning = "⚠️ '4. 현재 하고 있는 일'에서 '기타'를 선택하셨습니다. 아래 칸에 현재 하고 있는 일을 직접 입력하셔야 다음 단계로 넘어갈 수 있습니다."
            return
    st.session_state.step_warning = None
    st.session_state.current_step = step_idx
    st.session_state.scroll_to_top = True


def reset_all():
    for k, default_val in DEFAULT_KEYS.items():
        st.session_state[k] = default_val
    st.session_state.current_step = 0
    st.session_state.novel_result = None
    st.session_state.design_note = None
    st.session_state.cover_b64 = None
    st.session_state.cover_meta = None
    st.session_state.generate_trigger = False
    st.session_state.step_warning = None
    st.session_state.scroll_to_top = True


# ─────────────────────────────────────────────────────────
# [화면 A] 숭고한(Sublime) 건축적 무드의 입장 페이지
# ─────────────────────────────────────────────────────────
if not st.session_state.entered:
    intro_html = """
<div class="sublime-wrapper">
<div class="sublime-inner-frame">
<div class="sublime-hero">
<div class="sacred-geometry">
<svg width="68" height="68" viewBox="0 0 68 68" fill="none" xmlns="http://www.w3.org/2000/svg">
<circle cx="34" cy="34" r="30" stroke="#c8a46e" stroke-width="0.7" stroke-opacity="0.55"/>
<circle cx="26" cy="34" r="18" stroke="#e3c998" stroke-width="0.9" stroke-opacity="0.8"/>
<circle cx="42" cy="34" r="18" stroke="#e3c998" stroke-width="0.9" stroke-opacity="0.8"/>
<line x1="34" y1="0" x2="34" y2="68" stroke="#c8a46e" stroke-width="0.7" stroke-opacity="0.6"/>
<circle cx="34" cy="21" r="2" fill="#f4ece0"/>
<circle cx="34" cy="47" r="2" fill="#f4ece0"/>
</svg>
</div>
<div class="sublime-kicker">THE ARCHIVE OF UNCHOSEN PATHS</div>
<div class="sublime-title">나의 가능세계</div>
</div>
<div class="sublime-divider"></div>
<div class="sublime-body-section">
<div class="sublime-epigraph">
“선택되지 않은 시간은 사라지지 않는다.<br>
다만 우리가 건너지 않은 강 건너편에서, 다른 이름으로 흐르고 있을 뿐이다.”
</div>
<div class="sublime-prose">
한 사람의 생은 무수한 선택의 기록이자, 동시에 그만큼의 남겨진 가능성들의 총합입니다.<br><br>
이 서재는 당신이 지나온 기억의 변곡점과 오래 간직한 사물, 그리고 미처 선택하지 않았던 열망을 바탕으로<br>
<b>지금의 내가 걸어갈 미래</b>와 <b>다른 길을 택한 나</b>의 조우를 한 권의 단편소설과 크로키 표지로 기록합니다.
</div>
<div class="pillar-grid">
<div class="pillar-item">
<div class="pillar-num">I · OBJECT</div>
<div class="pillar-title">기억의 사물</div>
<div class="pillar-desc">오래 간직한 물건과 사소한 습관이 두 세계를 잇는 고유한 표식이 됩니다.</div>
</div>
<div class="pillar-item">
<div class="pillar-num">II · DIVERGENCE</div>
<div class="pillar-title">갈라진 시간</div>
<div class="pillar-desc">현재의 연장선에 놓인 삶과, 다른 선택 너머의 삶을 나란히 비춥니다.</div>
</div>
<div class="pillar-item">
<div class="pillar-num">III · ENCOUNTER</div>
<div class="pillar-title">경계의 조우</div>
<div class="pillar-desc">두 시간선이 스치듯 교차하며 서로에게 묻어두었던 질문을 건넵니다.</div>
</div>
</div>
<div class="sublime-notice">
• 총 6개 장(23개 문항)으로 이루어져 있으며, <b>최소 절반(50%) 이상의 문항</b>을 채워주셔야 집필이 시작됩니다.<br>
• 추상적인 단어보다 <b>구체적인 사물의 형태, 계절의 공기, 공간의 소리와 촉감</b>을 적어주실수록 정교한 표지 크로키와 단편소설이 완성됩니다.<br>
• 모든 응답은 소설 생성 즉시 휘발되며 별도로 저장되지 않습니다.
</div>
</div>
</div>
</div>
"""
    st.markdown(intro_html, unsafe_allow_html=True)

    if st.button("서재로 들어서기", type="primary", use_container_width=True):
        st.session_state.entered = True
        st.session_state.scroll_to_top = True
        st.rerun()

# ─────────────────────────────────────────────────────────
# [화면 B] 본 설문 및 소설 생성 페이지
# ─────────────────────────────────────────────────────────
else:
    top_col1, top_col2 = st.columns([3, 1])
    with top_col1:
        st.title("나의 가능세계")
        st.caption("지금의 내가 계속 걸어간 미래와, 다른 선택을 했다면 존재했을 나")
    with top_col2:
        if st.button("표지로 돌아가기", use_container_width=True):
            st.session_state.entered = False
            st.session_state.scroll_to_top = True
            st.rerun()

    with st.expander("🎧 서재 배경음악 (BGM) 열기"):
        st.audio(
            "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3?filename=lofi-study-112191.mp3",
            format="audio/mp3",
        )
        st.caption("재생 버튼을 누르면 설문을 작성하는 동안 잔잔한 배경음악이 흐릅니다.")

    # 잘림 없는 로마자 네비게이션
    PART_TITLES = [
        "I. 기본",
        "II. 성향",
        "III. 기억",
        "IV. 미래",
        "V. 다른 길",
        "VI. 조우",
    ]

    nav_cols = st.columns(6)
    for idx, title in enumerate(PART_TITLES):
        with nav_cols[idx]:
            btn_type = "primary" if st.session_state.current_step == idx else "secondary"
            if st.button(title, key=f"nav_{idx}", type=btn_type, use_container_width=True):
                go_to_step(idx)
                st.rerun()

    st.progress((st.session_state.current_step + 1) / len(PART_TITLES))
    st.markdown("---")

    if st.session_state.step_warning:
        st.warning(st.session_state.step_warning)

    step = st.session_state.current_step

    if step == 0:
        st.subheader("PART 0. 지금의 나")
        st.text_input("1. 소설 속에서 사용할 이름 / 닉네임", placeholder="예: 이선민", key="p0_q1")
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("2. 현재 나이", min_value=10, max_value=100, key="p0_q2")
        with col2:
            st.selectbox("3. 성별", ["남성", "여성", "기타", "답하고 싶지 않음"], index=None, placeholder="선택해주세요", key="p0_q3")

        st.selectbox(
            "4. 현재 하고 있는 일",
            ["대학생", "직장인", "취업 준비 중", "프리랜서", "자영업", "기타"],
            index=None,
            placeholder="선택해주세요",
            key="p0_q4_type",
        )
        if st.session_state.p0_q4_type == "기타":
            st.text_input(
                "현재 하고 있는 일을 직접 입력해주세요.",
                placeholder="현재 하고 있는 일을 직접 입력해주세요.",
                key="p0_q4_custom",
            )

        st.text_input("4-1. 구체적인 일상이나 역할", placeholder="예: 학업과 취업 준비 병행 중", key="p0_q4_detail")
        st.text_input("5. 전공 또는 가장 오래 공부한 분야", placeholder="예: 경영학", key="p0_q5")
        st.text_input("6. 현재 살고 있는 곳 (국가와 도시)", placeholder="예: 대한민국 서울", key="p0_q6")
        st.text_input("7. 지금의 내 삶을 한 문장으로 표현한다면?", placeholder="예: 열심히는 하지만 약간의 회의감이 든다.", key="p0_q7")

    elif step == 1:
        st.subheader("PART 1. 나는 어떤 사람인가?")
        st.radio("1. [에너지와 쉼] 지친 하루의 끝, 가장 편안한 공간은?", [
            "A. 익숙한 사람들의 대화와 웃음소리가 들리는 거실",
            "B. 햇살과 음악이 흐르는 조용한 나만의 방",
            "C. 좋아하는 일에 몰입할 수 있는 작업실",
            "D. 낯선 풍경과 새로운 사람들을 만날 수 있는 거리"
        ], index=None, key="p1_q1")
        st.radio("2. [문제 해결 방식] 문제 발생 시 가장 먼저 하는 행동은?", [
            "A. 상황을 분석하고 해결 방법을 체계적으로 정리한다.",
            "B. 일단 행동하며 해결책을 찾아 나간다.",
            "C. 주변 사람들과 이야기하며 의견을 구한다.",
            "D. 잠시 거리를 두고 혼자 생각을 정리한다."
        ], index=None, key="p1_q2")
        st.radio("3. [선택의 기준] 두 가지 길 중 하나만 선택해야 한다면?", [
            "A. 안정적이고 예측 가능하지만 익숙한 길",
            "B. 불확실하지만 새로운 가능성이 열려 있는 길"
        ], index=None, key="p1_q3")
        st.text_input("3-1. 그 길을 선택한 이유 (선택사항)", key="p1_q3_reason")
        st.radio("4. [관계 속 나의 모습] 여러 사람과 함께 있을 때 나는?", [
            "A. 먼저 말을 꺼내고 분위기를 이끄는 사람",
            "B. 다른 사람의 이야기를 듣고 공감하는 사람",
            "C. 상황을 정리하고 방향을 제시하는 사람",
            "D. 조용히 지켜보지만 가까운 사람에게는 다른 모습을 보여주는 사람"
        ], index=None, key="p1_q4")
        st.radio("5. [감정의 방어기제] 크게 상처받거나 실망했을 때 나는?", [
            "A. 감정을 직접 표현하고 상대방과 대화한다.",
            "B. 혼자 시간을 보내며 감정을 정리한다.",
            "C. 아무렇지 않은 척하며 평소처럼 행동한다.",
            "D. 상대방과 거리를 두고 관계를 다시 생각한다."
        ], index=None, key="p1_q5")
        st.multiselect(
            "6. [삶의 가치] 가장 중요한 것 3개를 순서대로 선택해주세요.",
            ["자유와 독립성", "성취와 성장", "안정과 평온", "사랑과 깊은 유대", "인정과 명예", "새로운 경험과 자극", "경제적 풍요", "온전한 나만의 시간"],
            max_selections=3,
            placeholder="최대 3개까지 선택해주세요",
            key="p1_q6"
        )
        st.radio("7. [내면의 결핍] 타인과의 관계에서 가장 견디기 힘든 순간은?", [
            "A. 나의 선택과 자유를 통제하려 할 때",
            "B. 나의 존재나 노력이 인정받지 못할 때",
            "C. 신뢰했던 사람이 약속을 어기거나 거짓말할 때",
            "D. 소중한 사람에게 외면받거나 멀어졌다고 느낄 때",
            "E. 나의 감정이나 생각을 이해받지 못할 때"
        ], index=None, key="p1_q7")
        st.text_input("8. [내면의 열망] 가장 깊은 행복이나 뭉클함을 느끼는 순간은?", placeholder="예: 오랫동안 노력한 일이 결실을 맺었을 때", key="p1_q8")
        st.text_input("9. [타인의 시선과 진짜 나] 주변이 보는 나와 실제 나의 차이는?", placeholder="예: 겉으로는 계획적으로 보이지만 속으로는 즉흥적인 낭만을 바람", key="p1_q9")
        st.selectbox("10. [관계의 중심] 현재 삶에서 가장 중요한 사람은?", ["A. 가족", "B. 연인", "C. 친구", "D. 동료", "E. 나 자신", "F. 기타"], index=None, placeholder="선택해주세요", key="p1_q10")
        st.text_input("10-1. 그 사람이 중요한 이유", key="p1_q10_reason")

    elif step == 2:
        st.subheader("PART 2. 나를 만든 기억과 선택")
        st.text_area("11. [변곡점] 지금의 나를 만든 과거의 한 장면과 그 이후의 변화는?", key="p2_q11")
        st.text_area("12. [성취의 기억] 스스로가 가장 자랑스러웠던 순간과 그 이유는?", key="p2_q12")
        st.text_input("13. [내면의 오브제] 오랫동안 간직하고 있는 물건과 그 기억은? (표지 크로키의 모티프가 됩니다)", placeholder="예: 오래된 편지, 여행지 기념품, 낡은 필름 카메라", key="p2_q13")
        st.selectbox("14. [성장의 흔적] 과거와 비교해 가장 크게 달라진 점은?", [
            "A. 삶에서 중요하게 생각하는 가치", "B. 사람들과 관계를 맺는 방식",
            "C. 실패와 도전을 받아들이는 태도", "D. 꿈과 미래에 대한 생각", "E. 감정을 표현하고 다루는 방식"
        ], index=None, placeholder="선택해주세요", key="p2_q14")
        st.text_input("14-1. 어떤 계기로 달라졌나요?", key="p2_q14_reason")

    elif step == 3:
        st.subheader("PART 3. 지금의 내가 향하는 미래 (Future A)")
        st.text_area("15. [현재의 목표] 지금 가장 이루고 싶은 목표와 그를 위한 노력은?", key="p3_q15")
        st.radio("16. [미래의 두려움] 미래를 생각할 때 가장 두려운 것은?", [
            "A. 원하는 목표를 이루지 못하는 것", "B. 경제적으로 불안정해지는 것",
            "C. 중요한 사람들과 멀어지는 것", "D. 타인의 기대에 맞추다 나 자신을 잃는 것",
            "E. 도전하지 않은 채 후회하는 것"
        ], index=None, key="p3_q16")
        st.text_input("17. [변하지 않을 나] 시간이 흘러도 절대 잃고 싶지 않은 나의 모습은?", key="p3_q17")

    elif step == 4:
        st.subheader("PART 4. 선택하지 않은 길 (Future B)")
        st.text_area("18. [숨겨진 욕망] 현실적으로 어렵지만 한 번쯤 살아보고 싶은 삶과 그 이유는?", key="p4_q18")
        st.text_input("19. [제약 없는 선택] 모든 제약이 사라진다면 가장 먼저 무엇을 해보고 싶나요?", key="p4_q19")
        st.radio("20. [가능세계의 차이] 다른 선택을 한 삶에서 가장 크게 달라졌을 것은?", [
            "A. 직업과 사회적 역할", "B. 살아가는 장소와 환경", "C. 인간관계와 소중한 사람들",
            "D. 성격과 가치관", "E. 일상과 생활 방식"
        ], index=None, key="p4_q20")
        st.selectbox("21. [가능세계의 나이] 몇 살의 나를 만나보고 싶나요?", ["지금과 비슷한 나이", "20대 후반", "30대", "40대", "50대", "60대 이상"], index=None, placeholder="선택해주세요", key="p4_q21")

    elif step == 5:
        st.subheader("PART 5. 두 세계가 만나는 순간")
        st.text_input("22. [두 명의 나] 다른 선택을 한 나와 마주 앉는다면 가장 먼저 무엇을 물어보고 싶나요?", key="p5_q22")
        st.text_input("23. [두 세계의 공통점] 아무리 다른 삶을 살았더라도 똑같이 남아 있을 모습은?", key="p5_q23")

    st.markdown("---")

    # 파트 하단 이동 버튼 및 최종 제출 검증
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if step > 0:
            if st.button("⬅️ 이전 장으로", use_container_width=True):
                go_to_step(step - 1)
                st.rerun()
    with btn_col2:
        if step < 5:
            if st.button(f"다음 장으로 ({PART_TITLES[step + 1]}) ➡️", type="primary", use_container_width=True):
                go_to_step(step + 1)
                st.rerun()
        else:
            if st.button("📖 가능세계의 기록과 표지 펼치기", type="primary", use_container_width=True):
                if not check_part0_other_job_valid():
                    st.warning(
                        "⚠️ **PART 0의 '4. 현재 하고 있는 일'**에서 **'기타'**를 선택하셨으나 내용을 입력하지 않으셨습니다. "
                        "PART 0으로 돌아가 현재 하고 있는 일을 직접 입력해 주세요."
                    )
                else:
                    ratio, filled_cnt, total_cnt, weak_parts = evaluate_survey_sincerity()
                    if ratio < 0.5:
                        weak_str = ", ".join(weak_parts) if weak_parts else "전체 파트"
                        st.error(
                            f"**아직 가능세계의 기록을 엮기에 단서가 부족합니다.** (현재 성실 답변율: **{int(ratio * 100)}%** / 최소 **50%** 필요)\n\n"
                            f"비어 있거나 단답으로 작성된 문항이 많으면 소설이 생성되지 않습니다. "
                            f"특히 **[{weak_str}]**의 빈칸이나 짧은 답변을 조금만 더 구체적으로 채워주시길 부탁드립니다."
                        )
                    else:
                        st.session_state.generate_trigger = True

    # ─────────────────────────────────────────────────────────
    # 맞춤형 크로키 표지 생성 ➔ 실시간 소설 타자기 출력
    # ─────────────────────────────────────────────────────────
    if st.session_state.generate_trigger:
        st.session_state.generate_trigger = False
        s = st.session_state

        final_job_type = (
            s.p0_q4_custom.strip()
            if s.p0_q4_type == "기타"
            else s.p0_q4_type
        )

        user_data = f"""
        [PART 0] 이름: {s.p0_q1} / 나이: {s.p0_q2} / 성별: {s.p0_q3} / 현재 일: {final_job_type}({s.p0_q4_detail}) / 전공: {s.p0_q5} / 거주지: {s.p0_q6} / 현재 한 문장: {s.p0_q7}
        [PART 1] 편안한 공간(P1_Q1): {s.p1_q1} / 문제해결(P1_Q2): {s.p1_q2} / 선택기준(P1_Q3): {s.p1_q3}({s.p1_q3_reason}) / 관계모습(P1_Q4): {s.p1_q4} / 방어기제(P1_Q5): {s.p1_q5} / 핵심가치(P1_Q6): {', '.join(s.p1_q6)} / 결핍(P1_Q7): {s.p1_q7} / 열망(P1_Q8): {s.p1_q8} / 타인시선차이(P1_Q9): {s.p1_q9} / 중요한사람(P1_Q10): {s.p1_q10}({s.p1_q10_reason})
        [PART 2] 변곡점(P2_Q11): {s.p2_q11} / 성취기억(P2_Q12): {s.p2_q12} / 오브제(P2_Q13): {s.p2_q13} / 성장흔적(P2_Q14): {s.p2_q14}({s.p2_q14_reason})
        [PART 3] 현재목표(P3_Q15): {s.p3_q15} / 두려움(P3_Q16): {s.p3_q16} / 잃고싶지않은가치(P3_Q17): {s.p3_q17}
        [PART 4] 숨겨진욕망(P4_Q18): {s.p4_q18} / 제약없는선택(P4_Q19): {s.p4_q19} / 가장큰차이(P4_Q20): {s.p4_q20} / 가능세계나이(P4_Q21): {s.p4_q21}
        [PART 5] 첫질문(P5_Q22): {s.p5_q22} / 공통점(P5_Q23): {s.p5_q23}
        """

        status_box = st.status("🖋️ 당신의 기억과 오브제를 바탕으로 표지 크로키와 소설을 준비하고 있습니다...", expanded=True)
        stage_text = status_box.empty()
        stage_prog = status_box.progress(10)

        # 1단계: 맞춤형 흑백 연필 크로키 표지 먼저 생성 및 화면 상단 배치
        stage_text.write(f"✏️ **표지 드로잉:** 기억의 매개체('{s.p2_q13 or '오래된 사물'}')를 흑백 연필 크로키 표지로 스케치하고 있습니다...")
        cover_holder = st.empty()
        novel_area = st.empty()

        cover_b64, cover_meta = generate_custom_croquis_cover(s)
        st.session_state.cover_b64 = cover_b64
        st.session_state.cover_meta = cover_meta
        cover_holder.markdown(render_book_cover_html(cover_b64, cover_meta), unsafe_allow_html=True)

        stage_prog.progress(25)
        stage_text.write("🔍 **서사 분석:** 설문 응답을 바탕으로 내면의 성향과 기억의 조각을 분석하고 있습니다...")

        full_text = ""
        displayed_len = 0
        is_started = False
        current_stage = 1

        try:
            response_stream = client.models.generate_content_stream(
                model="gemini-3.8-flash",
                contents=user_data,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.85,
                ),
            )

            for chunk in response_stream:
                if chunk.text:
                    full_text += chunk.text

                    if not is_started:
                        if ("아키타입" in full_text or "구조" in full_text) and current_stage < 2:
                            current_stage = 2
                            stage_prog.progress(45)
                            stage_text.write("📐 **구조 설계:** 두 세계가 교차할 서사 구조와 목차를 설계하고 있습니다...")
                        elif "굴절" in full_text and current_stage < 3:
                            current_stage = 3
                            stage_prog.progress(65)
                            stage_text.write("🎨 **심상 치환:** 현실의 기억과 단어를 문학적 비유로 굴절시키는 중입니다...")
                        elif ("습관" in full_text or "무의식" in full_text) and current_stage < 4:
                            current_stage = 4
                            stage_prog.progress(80)
                            stage_text.write("👤 **인물 조형:** 두 세계의 나를 잇는 무의식적 습관과 태도를 다듬는 중입니다...")
                        elif ("오브제" in full_text or "엔딩" in full_text) and current_stage < 5:
                            current_stage = 5
                            stage_prog.progress(92)
                            stage_text.write(f"🕰️ **장면 조율:** '{s.p2_q13 or '기억의 오브제'}'에 흐른 세월과 마지막 장면을 조율하고 있습니다...")

                    if "[소설시작]" in full_text:
                        if not is_started:
                            is_started = True
                            stage_prog.progress(100)
                            stage_text.write("✍️ **집필 시작:** 표지 아래 원고지 위에 가능세계의 기록을 적어 내려갑니다.")
                            status_box.update(label="✍️ 단편소설을 집필 중입니다...", state="running", expanded=False)

                        novel_body = full_text.split("[소설시작]", 1)[1].lstrip()

                        step_chars = 3
                        while displayed_len < len(novel_body):
                            displayed_len = min(displayed_len + step_chars, len(novel_body))
                            current_view = novel_body[:displayed_len]
                            novel_area.markdown(
                                f'<div class="novel-box">{current_view}▌</div>',
                                unsafe_allow_html=True,
                            )
                            time.sleep(0.012)

            if "[소설시작]" in full_text:
                parts = full_text.split("[소설시작]", 1)
                final_novel = parts[1].strip()
                design_note = parts[0].replace("[설계도]", "").strip()
            else:
                final_novel = full_text.strip()
                design_note = ""

            novel_area.markdown(
                f'<div class="novel-box">{final_novel}</div>',
                unsafe_allow_html=True,
            )
            status_box.update(label="✨ 나만의 크로키 표지와 가능세계의 기록이 완성되었습니다.", state="complete", expanded=False)

            st.session_state.novel_result = final_novel
            st.session_state.design_note = design_note

        except Exception as e:
            status_box.update(label="⚠️ 생성 중 오류가 발생했습니다.", state="error", expanded=True)
            st.error(f"서버 응답 오류: {e}")

    # 완성된 표지와 소설 본문 유지
    elif st.session_state.novel_result:
        st.markdown(
            render_book_cover_html(st.session_state.cover_b64, st.session_state.cover_meta),
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="novel-box">{st.session_state.novel_result}</div>',
            unsafe_allow_html=True,
        )

    if st.session_state.novel_result:
        if st.session_state.design_note:
            with st.expander("🔍 서사 설계 노트 (작성 과정 보기)"):
                st.text(st.session_state.design_note)

        st.markdown("---")
        res_col1, res_col2 = st.columns(2)
        with res_col1:
            if st.button("🔄 같은 답변으로 다른 표지·가능세계 다시 열기", use_container_width=True):
                st.session_state.generate_trigger = True
                st.rerun()
        with res_col2:
            if st.button("🧹 모든 답변 초기화하고 처음부터 다시 하기", use_container_width=True):
                reset_all()
                st.rerun()
