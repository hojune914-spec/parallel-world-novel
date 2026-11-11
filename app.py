# app.py
import time
import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
from prompts import SYSTEM_PROMPT

# 1. 페이지 기본 설정
st.set_page_config(page_title="나의 가능세계", page_icon="🕯️", layout="centered")

# 2. 어두운 등불 & 시네마틱 고서 테마 CSS
st.markdown("""
<style>
@import url('https://hangeul.pstatic.net/hangeul_static/css/maru-buri.css');

/* 등불 일렁임 애니메이션 */
@keyframes candleFlicker {
    0%, 100% { opacity: 0.92; transform: scale(1); filter: drop-shadow(0 0 12px rgba(212, 154, 73, 0.6)); }
    50% { opacity: 1; transform: scale(1.04); filter: drop-shadow(0 0 22px rgba(235, 175, 85, 0.9)); }
}

@keyframes fadeInSlow {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}

/* 전체 배경: 어두운 서재 + 상단 등불 후광 */
.stApp {
    background-color: #0b0907;
    background-image: 
        radial-gradient(circle at 50% 8%, rgba(212, 154, 73, 0.18) 0%, rgba(11, 9, 7, 0.97) 60%),
        repeating-linear-gradient(45deg, rgba(255,255,255,0.01) 0px, rgba(255,255,255,0.01) 2px, transparent 2px, transparent 4px);
    color: #e6dfd5;
    font-family: 'MaruBuri', serif;
}

/* 기본 타이포그래피 명조체 통일 */
h1, h2, h3, h4, p, label, .stMarkdown, .stRadio label, .stSelectbox label, .stTextInput label, .stTextArea label, .stNumberInput label, .stMultiSelect label {
    font-family: 'MaruBuri', serif !important;
    color: #e6dfd5 !important;
}

/* 입장 페이지 전체 래퍼 */
.intro-wrapper {
    background: #120f0c;
    border: 1px solid #3d3020;
    border-top: 2px solid #c8964b;
    border-radius: 8px;
    overflow: hidden;
    margin-top: 15px;
    margin-bottom: 25px;
    box-shadow: 0 25px 60px rgba(0, 0, 0, 0.9), 0 0 35px rgba(200, 150, 75, 0.08);
    animation: fadeInSlow 1.2s ease-out;
}

/* 상단 히어로 배너 이미지 (서재/등불 무드 + 하단 그라데이션 페이드) */
.hero-banner {
    position: relative;
    width: 100%;
    height: 310px;
    background-image: 
        linear-gradient(to bottom, rgba(18, 15, 12, 0.25) 0%, rgba(18, 15, 12, 0.65) 65%, #120f0c 100%),
        radial-gradient(circle at 50% 45%, rgba(225, 165, 75, 0.25) 0%, rgba(0, 0, 0, 0.7) 85%),
        url('https://images.unsplash.com/photo-1507842229356-51c61504d3ab?auto=format&fit=crop&w=1200&q=80');
    background-size: cover;
    background-position: center;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: center;
    padding-bottom: 20px;
    text-align: center;
}

.lantern-icon {
    font-size: 2.6rem;
    margin-bottom: 6px;
    animation: candleFlicker 3.5s infinite ease-in-out;
}

.intro-title {
    font-size: 2.35rem;
    font-weight: 700;
    color: #f6e7c1 !important;
    letter-spacing: 3px;
    margin-bottom: 4px;
    text-shadow: 0 4px 20px rgba(0, 0, 0, 0.95), 0 0 18px rgba(212, 154, 73, 0.5);
}

.intro-subtitle {
    font-size: 0.95rem;
    color: #c5b092 !important;
    letter-spacing: 1.5px;
    font-style: italic;
}

/* 본문 컨텐츠 영역 */
.intro-content {
    padding: 15px 38px 40px 38px;
    text-align: center;
}

/* 에피그래프(소설 서문 인용구) */
.epigraph-box {
    margin: 10px auto 30px auto;
    padding: 14px 20px;
    max-width: 88%;
    border-top: 1px solid rgba(200, 150, 75, 0.25);
    border-bottom: 1px solid rgba(200, 150, 75, 0.25);
    color: #b8a68e !important;
    font-size: 0.95rem;
    line-height: 1.85;
    font-style: italic;
}

.intro-body {
    font-size: 1.02rem;
    color: #ddd4c7 !important;
    line-height: 2.05;
    margin-bottom: 32px;
    word-break: keep-all;
}

/* 3단 비주얼 무드 카드 */
.mood-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin-bottom: 32px;
}

@media (max-width: 640px) {
    .mood-grid {
        grid-template-columns: 1fr;
    }
}

.mood-card {
    background: #191410;
    border: 1px solid #33281b;
    border-radius: 6px;
    overflow: hidden;
    text-align: left;
    transition: transform 0.25s ease, border-color 0.25s ease;
}

.mood-card:hover {
    transform: translateY(-3px);
    border-color: #9e7336;
}

.mood-img {
    width: 100%;
    height: 115px;
    object-fit: cover;
    filter: sepia(28%) contrast(105%) brightness(78%);
    border-bottom: 1px solid #2e2418;
}

.mood-text-wrap {
    padding: 12px 14px;
}

.mood-step {
    font-size: 0.75rem;
    color: #c8964b !important;
    letter-spacing: 1px;
    margin-bottom: 3px;
}

.mood-heading {
    font-size: 0.95rem;
    font-weight: 700;
    color: #efe5d5 !important;
    margin-bottom: 5px;
}

.mood-desc {
    font-size: 0.82rem;
    color: #a89984 !important;
    line-height: 1.55;
    word-break: keep-all;
}

/* 하단 안내 박스 */
.intro-guide {
    background-color: rgba(200, 150, 75, 0.06);
    border: 1px solid rgba(200, 150, 75, 0.2);
    border-left: 3px solid #c8964b;
    padding: 16px 22px;
    text-align: left;
    font-size: 0.9rem;
    color: #cbbba6 !important;
    border-radius: 4px;
    line-height: 1.8;
}

/* 입력창 다크 브라운 & 금빛 테두리 스타일링 */
input, textarea, [data-baseweb="select"] > div {
    background-color: #181410 !important;
    color: #f0e9df !important;
    border: 1px solid #3a3025 !important;
    font-family: 'MaruBuri', serif !important;
}

input:focus, textarea:focus {
    border-color: #c8964b !important;
    box-shadow: 0 0 8px rgba(200, 150, 75, 0.3) !important;
}

/* 버튼 스타일: 등불 빛깔의 앤티크 골드 */
button[kind="primary"] {
    background: linear-gradient(135deg, #b8863e 0%, #82571d 100%) !important;
    color: #fffaf0 !important;
    border: 1px solid #d4a75d !important;
    font-weight: 600 !important;
    padding: 0.65rem 1.2rem !important;
    box-shadow: 0 4px 18px rgba(184, 134, 62, 0.3) !important;
    transition: all 0.25s ease !important;
}

button[kind="primary"]:hover {
    background: linear-gradient(135deg, #cc984a 0%, #9c6b27 100%) !important;
    box-shadow: 0 6px 24px rgba(212, 167, 93, 0.5) !important;
}

button[kind="secondary"] {
    background-color: #1b1713 !important;
    color: #b8a996 !important;
    border: 1px solid #382e23 !important;
}

button[kind="secondary"]:hover {
    border-color: #8f6224 !important;
    color: #f0e6d8 !important;
}

/* 소설 출력 박스: 실제 빛바랜 소설책 종이 질감 */
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
    margin-top: 25px;
    white-space: pre-wrap;
    word-break: keep-all;
}

.novel-box * {
    color: #231e18 !important;
}
</style>
""", unsafe_allow_html=True)

# 3. 제미나이 클라이언트 연결
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# 4. 세션 상태 초기화
DEFAULT_KEYS = {
    "p0_q1": "", "p0_q2": 25, "p0_q3": None, "p0_q4_type": None,
    "p0_q4_detail": "", "p0_q5": "", "p0_q6": "", "p0_q7": "",
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

if st.session_state.scroll_to_top:
    components.html(
        "<script>window.parent.document.querySelector('section.main').scrollTo({top: 0, behavior: 'smooth'});</script>",
        height=0,
    )
    st.session_state.scroll_to_top = False

def go_to_step(step_idx):
    st.session_state.current_step = step_idx
    st.session_state.scroll_to_top = True

def reset_all():
    for k, default_val in DEFAULT_KEYS.items():
        st.session_state[k] = default_val
    st.session_state.current_step = 0
    st.session_state.novel_result = None
    st.session_state.design_note = None
    st.session_state.generate_trigger = False
    st.session_state.scroll_to_top = True

# ─────────────────────────────────────────────────────────
# [화면 A] 시네마틱 입장 페이지 (이미지 + 분위기 연출)
# ─────────────────────────────────────────────────────────
if not st.session_state.entered:
    intro_html = """
<div class="intro-wrapper">
<div class="hero-banner">
<div class="lantern-icon">🕯️</div>
<div class="intro-title">나의 가능세계</div>
<div class="intro-subtitle">The Archive of Unchosen Paths</div>
</div>
<div class="intro-content">
<div class="epigraph-box">
“가보지 못한 길은 사라지지 않는다.<br>
다만 우리가 뒤돌아보지 않는 시간 속에서 조용히 자라날 뿐이다.”
</div>
<div class="intro-body">
우리는 매일 수많은 갈림길을 지나며 살아갑니다.<br>
하나의 문을 열면 다른 문들은 소리 없이 닫히지만,<br>
닫힌 문 너머의 시간 역시 어딘가에서 계속 흐르고 있을지 모릅니다.<br><br>
이 서재는 당신의 성향과 오래된 기억, 그리고 미처 선택하지 못한 열망을 단서 삼아<br>
<b>지금의 내가 걸어갈 미래</b>와 <b>다른 선택을 했다면 존재했을 나</b>를 한 편의 단편소설로 엮어냅니다.
</div>
<div class="mood-grid">
<div class="mood-card">
<img class="mood-img" src="https://images.unsplash.com/photo-1509048191080-d2984bad6ae5?auto=format&fit=crop&w=600&q=80" alt="Object">
<div class="mood-text-wrap">
<div class="mood-step">ARCHIVE I</div>
<div class="mood-heading">기억의 사물과 흔적</div>
<div class="mood-desc">당신이 오래 간직한 물건과 버릇이 두 세계를 잇는 매개가 됩니다.</div>
</div>
</div>
<div class="mood-card">
<img class="mood-img" src="https://images.unsplash.com/photo-1455390582262-044cdead277a?auto=format&fit=crop&w=600&q=80" alt="Present">
<div class="mood-text-wrap">
<div class="mood-step">ARCHIVE II</div>
<div class="mood-heading">지금의 궤적과 다른 길</div>
<div class="mood-desc">현재의 치열한 일상과, 모든 제약을 벗어난 또 다른 가능성을 나란히 비춥니다.</div>
</div>
</div>
<div class="mood-card">
<img class="mood-img" src="https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=600&q=80" alt="Encounter">
<div class="mood-text-wrap">
<div class="mood-step">ARCHIVE III</div>
<div class="mood-heading">경계에서의 조우</div>
<div class="mood-desc">두 시간선이 스치듯 교차하며 서로에게 묻어두었던 질문을 건넵니다.</div>
</div>
</div>
</div>
<div class="intro-guide">
<b>📖 기록을 시작하기 전에</b><br>
• 총 6개 파트(23개 문항)로 구성되어 있으며, 작성에는 <b>약 5~7분</b>이 소요됩니다.<br>
• 주관식 문항에 추상적인 표현 대신 <b>구체적인 장면, 소리, 냄새, 사물의 촉감</b>을 적어주실수록 밀도 높은 소설이 완성됩니다.<br>
• 입력하신 모든 기록은 소설 집필 즉시 휘발되며 서버에 저장되지 않습니다.
</div>
</div>
</div>
"""
    st.markdown(intro_html, unsafe_allow_html=True)

    if st.button("🕯️ 등불을 켜고 서재로 들어서기", type="primary", use_container_width=True):
        st.session_state.entered = True
        st.session_state.scroll_to_top = True
        st.rerun()

# ─────────────────────────────────────────────────────────
# [화면 B] 본 설문 및 소설 생성 페이지
# ─────────────────────────────────────────────────────────
else:
    top_col1, top_col2 = st.columns([3, 1])
    with top_col1:
        st.title("🕯️ 나의 가능세계")
        st.caption("지금의 내가 계속 걸어간 미래와, 다른 선택을 했다면 존재했을 나")
    with top_col2:
        if st.button("🚪 표지로 돌아가기", use_container_width=True):
            st.session_state.entered = False
            st.session_state.scroll_to_top = True
            st.rerun()

    # BGM 플레이어 슬롯
    with st.expander("🎧 서재 배경음악 (BGM) 열기"):
        st.audio(
            "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3?filename=lofi-study-112191.mp3",
            format="audio/mp3",
        )
        st.caption("재생 버튼을 누르면 설문을 작성하는 동안 잔잔한 배경음악이 흐릅니다.")

    PART_TITLES = [
        "PART 0. 기본",
        "PART 1. 성향",
        "PART 2. 기억",
        "PART 3. 현재 미래",
        "PART 4. 다른 길",
        "PART 5. 조우",
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

    step = st.session_state.current_step

    if step == 0:
        st.subheader("PART 0. 지금의 나")
        st.text_input("1. 소설 속에서 사용할 이름 / 닉네임", placeholder="예: 이선민", key="p0_q1")
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("2. 현재 나이", min_value=10, max_value=100, key="p0_q2")
        with col2:
            st.selectbox("3. 성별", ["남성", "여성", "기타", "답하고 싶지 않음"], index=None, placeholder="선택해주세요", key="p0_q3")
        st.selectbox("4. 현재 하고 있는 일", ["대학생", "직장인", "취업준비 중", "프리랜서", "자영업", "기타"], index=None, placeholder="선택해주세요", key="p0_q4_type")
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
        st.text_input("13. [내면의 오브제] 오랫동안 간직하고 있는 물건과 그 기억은?", placeholder="예: 오래된 편지, 여행지 기념품, 낡은 카메라", key="p2_q13")
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

    # 파트 하단 이동 버튼
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if step > 0:
            if st.button("⬅️ 이전 파트로", use_container_width=True):
                go_to_step(step - 1)
                st.rerun()
    with btn_col2:
        if step < 5:
            if st.button(f"다음 파트로 이동 ({PART_TITLES[step + 1]}) ➡️", type="primary", use_container_width=True):
                go_to_step(step + 1)
                st.rerun()
        else:
            if st.button("🕯️ 나의 가능세계 기록 펼치기", type="primary", use_container_width=True):
                st.session_state.generate_trigger = True

    # 소설 생성 및 단계별 진행 표시 + 실시간 타자기 출력
    if st.session_state.generate_trigger:
        st.session_state.generate_trigger = False
        s = st.session_state

        user_data = f"""
        [PART 0] 이름: {s.p0_q1} / 나이: {s.p0_q2} / 성별: {s.p0_q3} / 현재 일: {s.p0_q4_type}({s.p0_q4_detail}) / 전공: {s.p0_q5} / 거주지: {s.p0_q6} / 현재 한 문장: {s.p0_q7}
        [PART 1] 편안한 공간(P1_Q1): {s.p1_q1} / 문제해결(P1_Q2): {s.p1_q2} / 선택기준(P1_Q3): {s.p1_q3}({s.p1_q3_reason}) / 관계모습(P1_Q4): {s.p1_q4} / 방어기제(P1_Q5): {s.p1_q5} / 핵심가치(P1_Q6): {', '.join(s.p1_q6)} / 결핍(P1_Q7): {s.p1_q7} / 열망(P1_Q8): {s.p1_q8} / 타인시선차이(P1_Q9): {s.p1_q9} / 중요한사람(P1_Q10): {s.p1_q10}({s.p1_q10_reason})
        [PART 2] 변곡점(P2_Q11): {s.p2_q11} / 성취기억(P2_Q12): {s.p2_q12} / 오브제(P2_Q13): {s.p2_q13} / 성장흔적(P2_Q14): {s.p2_q14}({s.p2_q14_reason})
        [PART 3] 현재목표(P3_Q15): {s.p3_q15} / 두려움(P3_Q16): {s.p3_q16} / 잃고싶지않은가치(P3_Q17): {s.p3_q17}
        [PART 4] 숨겨진욕망(P4_Q18): {s.p4_q18} / 제약없는선택(P4_Q19): {s.p4_q19} / 가장큰차이(P4_Q20): {s.p4_q20} / 가능세계나이(P4_Q21): {s.p4_q21}
        [PART 5] 첫질문(P5_Q22): {s.p5_q22} / 공통점(P5_Q23): {s.p5_q23}
        """

        status_box = st.status("🕯️ 등불 아래에서 가능세계의 문을 여는 중입니다...", expanded=True)
        stage_text = status_box.empty()
        stage_prog = status_box.progress(10)
        stage_text.write("🔍 **1단계:** 설문 응답을 바탕으로 내면의 성향과 기억의 조각을 분석하고 있습니다...")

        novel_area = st.empty()
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
                            stage_prog.progress(30)
                            stage_text.write("📐 **2단계:** 두 세계가 교차할 서사 구조와 목차를 설계하고 있습니다...")
                        elif "굴절" in full_text and current_stage < 3:
                            current_stage = 3
                            stage_prog.progress(55)
                            stage_text.write("🎨 **3단계:** 현실의 기억과 단어를 문학적 비유로 굴절시키는 중입니다...")
                        elif ("습관" in full_text or "무의식" in full_text) and current_stage < 4:
                            current_stage = 4
                            stage_prog.progress(75)
                            stage_text.write("👤 **4단계:** 두 세계의 나를 잇는 무의식적 습관과 캐릭터를 디자인하는 중입니다...")
                        elif ("오브제" in full_text or "엔딩" in full_text) and current_stage < 5:
                            current_stage = 5
                            stage_prog.progress(90)
                            stage_text.write(f"🕰️ **5단계:** '{s.p2_q13 or '기억의 오브제'}'에 흐른 세월과 마지막 장면을 조율하고 있습니다...")

                    if "[소설시작]" in full_text:
                        if not is_started:
                            is_started = True
                            stage_prog.progress(100)
                            stage_text.write("✍️ **집필 시작:** 오래된 원고지 위에 가능세계의 기록을 적어 내려갑니다.")
                            status_box.update(label="✍️ 등불 아래에서 소설을 집필 중입니다...", state="running", expanded=False)

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
            status_box.update(label="✨ 가능세계의 기록이 완성되었습니다.", state="complete", expanded=False)

            st.session_state.novel_result = final_novel
            st.session_state.design_note = design_note

        except Exception as e:
            status_box.update(label="⚠️ 생성 중 오류가 발생했습니다.", state="error", expanded=True)
            st.error(f"서버 응답 오류: {e}")

    elif st.session_state.novel_result:
        st.markdown(
            f'<div class="novel-box">{st.session_state.novel_result}</div>',
            unsafe_allow_html=True,
        )

    if st.session_state.novel_result:
        if st.session_state.design_note:
            with st.expander("🔍 AI 서사 설계 노트 (작성 과정 보기)"):
                st.text(st.session_state.design_note)

        st.markdown("---")
        res_col1, res_col2 = st.columns(2)
        with res_col1:
            if st.button("🔄 같은 답변으로 다른 가능세계 다시 열기", use_container_width=True):
                st.session_state.generate_trigger = True
                st.rerun()
        with res_col2:
            if st.button("🧹 모든 답변 초기화하고 처음부터 다시 하기", use_container_width=True):
                reset_all()
                st.rerun()
