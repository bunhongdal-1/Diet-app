import streamlit as st
import pandas as pd
import os

# 1. 초기 설정
st.set_page_config(page_title="우리들의 다이어트 챌린지", page_icon="🏃‍♀️", layout="centered")

DATA_FILE = "diet_data.csv"
USERS = ["민경", "세진", "유진"]

# 💡 여기에 세 분의 4월 1일 시작 체중을 정확히 적어주세요! (소수점 첫째 자리까지)
INITIAL_WEIGHTS = {
    "민경": 64.0, 
    "세진": 60.0, 
    "유진": 55.0
}

MAX_LOSS_LIMIT = 1.0  # 주간 최대 감량 인정치 (1kg)
BASE_POOL = 60000     # 초기 공동 회비 (2만 원 x 3명)

# 2. 데이터 불러오기 함수
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["주차", "이름", "목표감량(kg)", "실제감량(kg)", "결과"])

df = load_data()

# 3. 상단 타이틀
st.title("🔥 4~6월 다이어트 챌린지")
st.markdown("### 민경, 세진, 유진의 15만 원 환급 프로젝트 💸")
st.info(f"💡 **기본 룰:** 주간 목표 달성 시 1만 원 환급! (건강을 위해 주당 최대 {MAX_LOSS_LIMIT}kg까지만 인정)")

# 4. 기록 입력 폼
with st.form("record_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.selectbox("참가자 선택", USERS)
        week = st.number_input("주차 입력 (1~13주)", min_value=1, max_value=13, step=1)
    with col2:
        goal = st.number_input("이번 주 목표 감량 (kg)", min_value=0.0, step=0.1)
        actual = st.number_input("이번 주 실제 감량 (kg)", min_value=-2.0, max_value=5.0, step=0.1)
    
    submitted = st.form_submit_button("기록 저장하기")

    if submitted:
        if actual > MAX_LOSS_LIMIT:
            st.warning(f"🚨 앗! 주간 최대 감량치({MAX_LOSS_LIMIT}kg) 초과! 무리한 다이어트는 안 돼요. (실패 처리)")
            result = "실패"
        elif actual >= goal and goal > 0:
            st.success("🎉 목표 달성! 1만 원 환급 확정!")
            result = "성공"
        else:
            st.error("😢 아쉽게도 목표 미달성입니다. 1만 원은 공동 회비로 쏙~")
            result = "실패"
            
        new_data = pd.DataFrame([{"주차": week, "이름": name, "목표감량(kg)": goal, "실제감량(kg)": actual, "결과": result}])
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.rerun()

st.divider()

# 5. 공동 회비 현황
st.subheader("💰 공동 회비 & 환급 현황")
fail_count = len(df[df["결과"] == "실패"])
total_pool = BASE_POOL + (fail_count * 10000)
st.metric(label="현재 모인 공동 회비 (기본 6만 원 + 벌금 누적)", value=f"{total_pool:,} 원")

st.divider()

# 6. ★추가된 기능★ 개인별 누적 감량 및 현재 체중
st.subheader("🏃‍♀️ 개인별 다이어트 현황")
col_m, col_s, col_y = st.columns(3)

for i, user in enumerate(USERS):
    user_data = df[df["이름"] == user]
    total_loss = user_data["실제감량(kg)"].sum()
    current_weight = INITIAL_WEIGHTS[user] - total_loss
    
    with [col_m, col_s, col_y][i]:
        st.markdown(f"**{user}**")
        st.write(f"시작: {INITIAL_WEIGHTS[user]} kg")
        st.write(f"현재: **{current_weight:.1f} kg**")
        st.write(f"(총 **{total_loss:.1f} kg** 감량)")

st.divider()

# 7. ★업그레이드★ 기록 수정 및 삭제 ( st.data_editor )
st.subheader("✏️ 전체 기록 확인 및 수정/삭제")
st.caption("🚨 **삭제하는 법:** 맨 왼쪽 네모 빈칸을 체크하고, 표 오른쪽 위에 생기는 휴지통 아이콘을 누르면 삭제됩니다. (숫자를 터치해 바로 고칠 수도 있습니다!)")

edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

if not edited_df.equals(df):
    edited_df.to_csv(DATA_FILE, index=False)
    st.success("수정/삭제 완료! (화면이 곧 새로고침 됩니다)")
    st.rerun()
