import streamlit as st
import pandas as pd
import os

# 1. 초기 설정
st.set_page_config(page_title="우리들의 다이어트 챌린지", page_icon="🏃‍♀️", layout="centered")

# 2. 기본 데이터 설정
DATA_FILE = "diet_data.csv"
USERS = ["민경", "세진", "유진"]
MAX_LOSS_LIMIT = 1.0  # 주간 최대 감량 인정치 (1kg)
BASE_POOL = 60000     # 초기 공동 회비 (2만 원 x 3명)

# 3. 데이터 불러오기 함수
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["주차", "이름", "목표감량(kg)", "실제감량(kg)", "결과"])

df = load_data()

# 4. 화면 구성
st.title("🔥 4~6월 다이어트 챌린지")
st.markdown("### 민경, 세진, 유진의 15만 원 환급 프로젝트 💸")
st.info(f"💡 **기본 룰:** 주간 목표 달성 시 1만 원 환급! (건강을 위해 주당 최대 {MAX_LOSS_LIMIT}kg까지만 인정)")

# 5. 기록 입력 폼
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
            
        # 입력된 데이터를 표에 추가
        new_data = pd.DataFrame([{"주차": week, "이름": name, "목표감량(kg)": goal, "실제감량(kg)": actual, "결과": result}])
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.rerun()

# 6. 결과 대시보드
st.divider()
st.subheader("💰 공동 회비 & 환급 현황")

# 누적 벌금 계산
fail_count = len(df[df["결과"] == "실패"])
total_pool = BASE_POOL + (fail_count * 10000)

st.metric(label="현재 모인 공동 회비 (기본 6만 원 + 벌금 누적)", value=f"{total_pool:,} 원")
st.caption("모인 돈은 6월에 맛있는 식사나 축하 파티 비용으로 사용됩니다! 🥳")

st.divider()
st.subheader("📊 주차별 기록 확인")
st.dataframe(df, use_container_width=True)
