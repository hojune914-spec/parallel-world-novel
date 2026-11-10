# app.py
import streamlit as st
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
    margin-top: 25px;
}
</style>
""", unsafe_allow_html=True)

# 2. 제미나이 클라이언트 연결
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.title("📖 나의 가능세계")
st.caption("지금의 내가 계속 걸어간 미래와, 다른 선택을 했다면 존재했을 나")

# 3. 설문 폼 구성
with st.form("parallel_world_survey"):
    tabs = st.tabs(["PART 0. 기본", "PART 1. 성향", "PART 2. 기억", "PART 3. 현재 미래", "PART 4. 다른 길", "PART 5. 조우"])

    with tabs[0]:
        st.subheader("PART 0. 지금의 나")
        p0_q1 = st.text_input("1. 소설 속에서 사용할 이름 / 닉네임", placeholder="예: 이선민")
        col1, col2 = st.columns(2)
        with col1:
            p0_q2 = st.number_input("2. 현재 나이", min_value=10, max_value=100, value=25)
        with col2:
            p0_q3 = st.selectbox("3. 성별", ["남성", "여성", "기타", "답하고 싶지 않음"])
        p0_q4_type = st.selectbox("4. 현재 하고 있는 일", ["대학생", "직장인", "취업준비 중", "프리랜서", "자영업", "기타"])
        p0_q4_detail = st.text_input("4-1. 구체적인 일상이나 역할", placeholder="예: 학업과 취업 준비 병행 중")
        p0_q5 = st.text_input("5. 전공 또는 가장 오래 공부한 분야", placeholder="예: 경영학")
        p0_q6 = st.text_input("6. 현재 살고 있는 곳 (국가와 도시)", placeholder="예: 대한민국 서울")
        p0_q7 = st.text_input("7. 지금의 내 삶을 한 문장으로 표현한다면?", placeholder="예: 열심히는 하지만 약간의 회의감이 든다.")

    with tabs[1]:
        st.subheader("PART 1. 나는 어떤 사람인가?")
        p1_q1 = st.radio("1. [에너지와 쉼] 지친 하루의 끝, 가장 편안한 공간은?", [
            "A. 익숙한 사람들의 대화와 웃음소리가 들리는 거실",
            "B. 햇살과 음악이 흐르는 조용한 나만의 방",
            "C. 좋아하는 일에 몰입할 수 있는 작업실",
            "D. 낯선 풍경과 새로운 사람들을 만날 수 있는 거리"
        ])
        p1_q2 = st.radio("2. [문제 해결 방식] 문제 발생 시 가장 먼저 하는 행동은?", [
            "A. 상황을 분석하고 해결 방법을 체계적으로 정리한다.",
            "B. 일단 행동하며 해결책을 찾아 나간다.",
            "C. 주변 사람들과 이야기하며 의견을 구한다.",
            "D. 잠시 거리를 두고 혼자 생각을 정리한다."
        ])
        p1_q3 = st.radio("3. [선택의 기준] 두 가지 길 중 하나만 선택해야 한다면?", [
            "A. 안정적이고 예측 가능하지만 익숙한 길",
            "B. 불확실하지만 새로운 가능성이 열려 있는 길"
        ])
        p1_q3_reason = st.text_input("3-1. 그 길을 선택한 이유 (선택사항)")
        p1_q4 = st.radio("4. [관계 속 나의 모습] 여러 사람과 함께 있을 때 나는?", [
            "A. 먼저 말을 꺼내고 분위기를 이끄는 사람",
            "B. 다른 사람의 이야기를 듣고 공감하는 사람",
            "C. 상황을 정리하고 방향을 제시하는 사람",
            "D. 조용히 지켜보지만 가까운 사람에게는 다른 모습을 보여주는 사람"
        ])
        p1_q5 = st.radio("5. [감정의 방어기제] 크게 상처받거나 실망했을 때 나는?", [
            "A. 감정을 직접 표현하고 상대방과 대화한다.",
            "B. 혼자 시간을 보내며 감정을 정리한다.",
            "C. 아무렇지 않은 척하며 평소처럼 행동한다.",
            "D. 상대방과 거리를 두고 관계를 다시 생각한다."
        ])
        p1_q6 = st.multiselect("6. [삶의 가치] 가장 중요한 것 3개를 순서대로 선택해주세요.", 
            ["자유와 독립성", "성취와 성장", "안정과 평온", "사랑과 깊은 유대", "인정과 명예", "새로운 경험과 자극", "경제적 풍요", "온전한 나만의 시간"],
            max_selections=3
        )
        p1_q7 = st.radio("7. [내면의 결핍] 타인과의 관계에서 가장 견디기 힘든 순간은?", [
            "A. 나의 선택과 자유를 통제하려 할 때",
            "B. 나의 존재나 노력이 인정받지 못할 때",
            "C. 신뢰했던 사람이 약속을 어기거나 거짓말할 때",
            "D. 소중한 사람에게 외면받거나 멀어졌다고 느낄 때",
            "E. 나의 감정이나 생각을 이해받지 못할 때"
        ])
        p1_q8 = st.text_input("8. [내면의 열망] 가장 깊은 행복이나 뭉클함을 느끼는 순간은?", placeholder="예: 오랫동안 노력한 일이 결실을 맺었을 때")
        p1_q9 = st.text_input("9. [타인의 시선과 진짜 나] 주변이 보는 나와 실제 나의 차이는?", placeholder="예: 겉으로는 계획적으로 보이지만 속으로는 즉흥적인 낭만을 바람")
        p1_q10 = st.selectbox("10. [관계의 중심] 현재 삶에서 가장 중요한 사람은?", ["A. 가족", "B. 연인", "C. 친구", "D. 동료", "E. 나 자신", "F. 기타"])
        p1_q10_reason = st.text_input("10-1. 그 사람이 중요한 이유")

    with tabs[2]:
        st.subheader("PART 2. 나를 만든 기억과 선택")
        p2_q11 = st.text_area("11. [변곡점] 지금의 나를 만든 과거의 한 장면과 그 이후의 변화는?")
        p2_q12 = st.text_area("12. [성취의 기억] 스스로가 가장 자랑스러웠던 순간과 그 이유는?")
        p2_q13 = st.text_input("13. [내면의 오브제] 오랫동안 간직하고 있는 물건과 그 기억은?", placeholder="예: 오래된 편지, 여행지 기념품, 낡은 카메라")
        p2_q14 = st.selectbox("14. [성장의 흔적] 과거와 비교해 가장 크게 달라진 점은?", [
            "A. 삶에서 중요하게 생각하는 가치", "B. 사람들과 관계를 맺는 방식", 
            "C. 실패와 도전을 받아들이는 태도", "D. 꿈과 미래에 대한 생각", "E. 감정을 표현하고 다루는 방식"
        ])
        p2_q14_reason = st.text_input("14-1. 어떤 계기로 달라졌나요?")

    with tabs[3]:
        st.subheader("PART 3. 지금의 내가 향하는 미래 (Future A)")
        p3_q15 = st.text_area("15. [현재의 목표] 지금 가장 이루고 싶은 목표와 그를 위한 노력은?")
        p3_q16 = st.radio("16. [미래의 두려움] 미래를 생각할 때 가장 두려운 것은?", [
            "A. 원하는 목표를 이루지 못하는 것", "B. 경제적으로 불안정해지는 것",
            "C. 중요한 사람들과 멀어지는 것", "D. 타인의 기대에 맞추다 나 자신을 잃는 것",
            "E. 도전하지 않은 채 후회하는 것"
        ])
        p3_q17 = st.text_input("17. [변하지 않을 나] 시간이 흘러도 절대 잃고 싶지 않은 나의 모습은?")

    with tabs[4]:
        st.subheader("PART 4. 선택하지 않은 길 (Future B)")
        p4_q18 = st.text_area("18. [숨겨진 욕망] 현실적으로 어렵지만 한 번쯤 살아보고 싶은 삶과 그 이유는?")
        p4_q19 = st.text_input("19. [제약 없는 선택] 모든 제약이 사라진다면 가장 먼저 무엇을 해보고 싶나요?")
        p4_q20 = st.radio("20. [가능세계의 차이] 다른 선택을 한 삶에서 가장 크게 달라졌을 것은?", [
            "A. 직업과 사회적 역할", "B. 살아가는 장소와 환경", "C. 인간관계와 소중한 사람들",
            "D. 성격과 가치관", "E. 일상과 생활 방식"
        ])
        p4_q21 = st.selectbox("21. [가능세계의 나이] 몇 살의 나를 만나보고 싶나요?", ["지금과 비슷한 나이", "20대 후반", "30대", "40대", "50대", "60대 이상"])

    with tabs[5]:
        st.subheader("PART 5. 두 세계가 만나는 순간")
        p5_q22 = st.text_input("22. [두 명의 나] 다른 선택을 한 나와 마주 앉는다면 가장 먼저 무엇을 물어보고 싶나요?")
        p5_q23 = st.text_input("23. [두 세계의 공통점] 아무리 다른 삶을 살았더라도 똑같이 남아 있을 모습은?")
        st.markdown("---")
        submit_btn = st.form_submit_button("✨ 나의 가능세계 기록 펼치기", use_container_width=True)

# 4. 제출 시 소설 생성
if submit_btn:
    user_data = f"""
    [PART 0] 이름: {p0_q1} / 나이: {p0_q2} / 성별: {p0_q3} / 현재 일: {p0_q4_type}({p0_q4_detail}) / 전공: {p0_q5} / 거주지: {p0_q6} / 현재 한 문장: {p0_q7}
    [PART 1] 편안한 공간(P1_Q1): {p1_q1} / 문제해결(P1_Q2): {p1_q2} / 선택기준(P1_Q3): {p1_q3}({p1_q3_reason}) / 관계모습(P1_Q4): {p1_q4} / 방어기제(P1_Q5): {p1_q5} / 핵심가치(P1_Q6): {', '.join(p1_q6)} / 결핍(P1_Q7): {p1_q7} / 열망(P1_Q8): {p1_q8} / 타인시선차이(P1_Q9): {p1_q9} / 중요한사람(P1_Q10): {p1_q10}({p1_q10_reason})
    [PART 2] 변곡점(P2_Q11): {p2_q11} / 성취기억(P2_Q12): {p2_q12} / 오브제(P2_Q13): {p2_q13} / 성장흔적(P2_Q14): {p2_q14}({p2_q14_reason})
    [PART 3] 현재목표(P3_Q15): {p3_q15} / 두려움(P3_Q16): {p3_q16} / 잃고싶지않은가치(P3_Q17): {p3_q17}
    [PART 4] 숨겨진욕망(P4_Q18): {p4_q18} / 제약없는선택(P4_Q19): {p4_q19} / 가장큰차이(P4_Q20): {p4_q20} / 가능세계나이(P4_Q21): {p4_q21}
    [PART 5] 첫질문(P5_Q22): {p5_q22} / 공통점(P5_Q23): {p5_q23}
    """

    st.markdown("---")
    st.info("✍️ 두 세계의 기록을 실시간으로 적어 내려가는 중입니다...")

    novel_area = st.empty()
    full_text = ""

    try:
        # 스트리밍 호출
        response_stream = client.models.generate_content_stream(
            model="gemini-3.8-flash",
            contents=user_data,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.85,
            ),
        )

        # 들어오는 즉시 글자를 그대로 화면에 표시 (중간에 멈추는 일 방지)
        for chunk in response_stream:
            if chunk.text:
                full_text += chunk.text
                novel_area.markdown(
                    f'<div class="novel-box">{full_text}</div>',
                    unsafe_allow_html=True,
                )

        st.success("✨ 가능세계의 기록이 완성되었습니다.")

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
