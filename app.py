# app.py
import time
import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
from prompts import SYSTEM_PROMPT

# 1. 페이지 설정 및 명조체 스타일
st.set_page_config(page_title="나의 가능세계", page_icon="📖", layout="centered")

st.markdown("""
<style>
@import url('https://hangeul.pstatic.net/hangeul_static/css/maru-buri.css');
.novel-box {
    font-family: 'MaruBuri', serif;
    background-color: #fcfaf2;
    color: #2b2b2b;
    padding: 40px 35px;
    border-radius: 8px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    line-height: 1.95;
    font-size: 1.05rem;
    margin-top: 20px;
    white-space: pre-wrap;
}
.step-indicator {
    font-size: 0.9rem;
    color: #666;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# 2. 제미나이 클라이언트 연결
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# 3. 세션 상태(Session State) 초기화 및 파트 이동 시 입력값 증발 방지
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
        st.session_state[k] = st.session_state[k]  # 파트 이동 시 값 유지

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

# 화면 상단 자동 스크롤 처리
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

# 4. 상단 타이틀 및 파트 네비게이션 바
st.title("📖 나의 가능세계")
st.caption("지금의 내가 계속 걸어간 미래와, 다른 선택을 했다면 존재했을 나")

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

# 5. 단계별 설문 화면 렌더링 (엔터 키 제출 방지를 위해 form 미사용)
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

# 6. 각 파트 하단 이동 버튼 (이전 파트 / 다음 파트 / 최종 제출)
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
        if st.button("✨ 나의 가능세계 기록 펼치기", type="primary", use_container_width=True):
            st.session_state.generate_trigger = True

# 7. 소설 생성 및 단계별 진행 표시 + 실시간 타자기 출력
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

    status_box = st.status("🌌 가능세계의 문을 여는 중입니다...", expanded=True)
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
            model="gemini-3.8-flash",  # 유료 전환 후 "gemini-2.5-pro" 등으로 변경 가능
            contents=user_data,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.85,
            ),
        )

        for chunk in response_stream:
            if chunk.text:
                full_text += chunk.text

                # [소설시작] 전: 설계도가 작성되는 동안 단계별 진행 상황을 실시간 표시
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

                # [소설시작] 등장 이후: 본문을 타자기(타이핑) 효과로 부드럽게 출력
                if "[소설시작]" in full_text:
                    if not is_started:
                        is_started = True
                        stage_prog.progress(100)
                        stage_text.write("✍️ **집필 시작:** 설계가 완료되어 가능세계의 기록을 실시간으로 적어 내려갑니다.")
                        status_box.update(label="✍️ 가능세계의 기록을 집필 중입니다...", state="running", expanded=False)

                    novel_body = full_text.split("[소설시작]", 1)[1].lstrip()

                    # 새로 들어온 글자들을 3글자씩 끊어 커서(▌)와 함께 타이핑 연출
                    step_chars = 3
                    while displayed_len < len(novel_body):
                        displayed_len = min(displayed_len + step_chars, len(novel_body))
                        current_view = novel_body[:displayed_len]
                        novel_area.markdown(
                            f'<div class="novel-box">{current_view}▌</div>',
                            unsafe_allow_html=True,
                        )
                        time.sleep(0.012)

        # 완료 후 커서(▌) 제거 및 결과 저장
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

# 8. 생성된 소설 유지 및 하단 초기화 / 재생성 버튼
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
