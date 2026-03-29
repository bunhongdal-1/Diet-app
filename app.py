import streamlit as st
import pandas as pd
import os
from datetime import date

# 1. 초기 설정 및 데이터 파일 정의
st.set_page_config(page_title="우리들의 다이어트 챌린지", page_icon="🏃‍♀️", layout="centered")

DIET_DATA_FILE = "diet_data.csv"
WEIGHTS_FILE = "initial_weights.csv"
USERS = ["민경", "세진", "유진"]

# 관리자 비밀번호 (시작 몸무게 수정용)
ADMIN_PASSWORD = "1234" 

# --- [추가된 기능] D-Day 계산 ---
today = date.today()
target_date = date(today.year, 6, 30) # 6월 30일 종료
start_date = date(today.year, 4, 1)   # 4월 1일 시작

d_day = (target_date - today).days

if d_day > 0:
    d_day_text = f"⏳ D-{d_day}"
elif d_day == 0:
    d_day_text = "🎉 D-Day (종료일)!"
else:
    d_day_text = "🏁 챌린지 종료"

# 2. 데이터 불러오기 함수 
def load_data(file_name, columns):
    if os.path.exists(file_name):
        return pd.read_csv(file_name)
    else:
        return pd.DataFrame(columns=columns)

df = load_data(DIET_DATA_FILE, ["주차", "이름", "목표감량(kg)", "실제감량(kg)", "결과"])
weights_df = load_data(WEIGHTS_FILE, ["이름", "시작몸무게(kg)"])

# 3. 메인 타이틀
st.title("🔥 4~6월 다이어트 챌린지")
st.markdown("### 민경, 세진, 유진의 13만 원 환급 프로젝트 💸")

# 디데이 알림창 추가
st.info(f"**진행 기간:** 4월 1일 ~ 6월 30일\n\n**현재 남은 시간:** {d_day_text}")
st.divider()

# 4. [설정 단계] 시작 몸무게 입력 여부 확인
configured_users = weights_df["이름"].tolist()
missing_users = [user for user in USERS if user not in configured_users]

if missing_users:
    st.subheader("🛠️ 4월 1일 시작 몸무게 설정 (최초 1회)")
    st.warning("아직 시작 몸무게를 입력하지 않은 참가자가 있습니다. 먼저 입력해 주세요!")
    
    with st.form("weight_setting_form"):
        col1, col2 = st.columns([1, 2])
        with col1:
            setup_name = st.selectbox("참가자 선택", missing_users)
        with col2:
            setup_weight = st.number_input("4월 1일 몸무게 (kg)", min_value=0.0, step=0.1)
        
        save_btn = st.form_submit_button("시작 몸무게 저장하기")
        
        if save_btn:
            if setup_weight > 0:
                new_weight = pd.DataFrame([{"이름": setup_name, "시작몸무게(kg)": setup_weight}])
                weights_df = pd.concat([weights_df, new_weight], ignore_index=True)
                weights_df.to_csv(WEIGHTS_FILE, index=False)
                st.success(f"{setup_name}님, 시작 몸무게 {setup_weight}kg 설정 완료!")
                st.rerun()
            else:
                st.error("정확한 몸무게를 입력해 주세요.")
    
    st.divider()
    st.stop() 

# --- 이하 메인 앱 기능 ---

# 5. 주간 기록 입력 폼
st.subheader("✍️ 이번 주 다이어트 기록")
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
        # 주간 최대 감량 제한 로직 삭제됨
        if actual >= goal and goal > 0:
            st.success("🎉 목표 달성! 1만 원 환급 확정!")
            result = "성공"
        else:
            st.error("😢 아쉽게도 목표 미달성입니다. 1만 원은 공동 회비로 쏙~")
            result = "실패"
            
        new_data = pd.DataFrame([{"주차": week, "이름": name, "목표감량(kg)": goal, "실제감량(kg)": actual, "결과": result}])
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(DIET_DATA_FILE, index=False)
        st.rerun()

st.divider()

# 6. 공동 회비 & 개인별 현황 대시보드
col_money, col_status = st.columns([1, 2])

with col_money:
    st.subheader("💰 공동 회비")
    fail_count = len(df[df["결과"] == "실패"])
    total_pool = fail_count * 10000 
    st.metric(label="현재 모인 벌금 총액", value=f"{total_pool:,} 원")
    st.caption("목표 미달성으로 쌓인 회비! 6월 파티 비용 🥳")

with col_status:
    st.subheader("🏃‍♀️ 누적 감량 현황")
    init_weights = weights_df.set_index("이름")["시작몸무게(kg)"].to_dict()
    
    col_m, col_s, col_y = st.columns(3)
    for i, user in enumerate(USERS):
        user_data = df[df["이름"] == user]
        total_loss = user_data["실제감량(kg)"].sum()
        current_weight = init_weights[user] - total_loss
        
        with [col_m, col_s, col_y][i]:
            st.markdown(f"**{user}**")
            st.caption(f"시작: {init_weights[user]} kg")
            st.write(f"현재: **{current_weight:.1f} kg**")
            st.write(f"(총 **{total_loss:.1f} kg** 감량)")

st.divider()

# 7. 기록 수정 및 삭제 
st.subheader("✏️ 지난 기록 수정 및 삭제")
st.caption("🚨 **삭제 방법:** 왼쪽 네모 체크 ➡️ 표 위 휴지통 아이콘 클릭")

edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="data_editor")

if not edited_df.equals(df):
    edited_df.to_csv(DIET_DATA_FILE, index=False)
    st.success("기록 수정 완료! (화면이 곧 새로고침 됩니다)")
    st.rerun()

st.divider()

# 8. 시작 몸무게 수정 (관리자용)
with st.expander("🛠️ 시작 몸무게 수정 (비밀번호 필요)"):
    pwd = st.text_input("관리자 비밀번호를 입력하세요", type="password")
    if pwd == ADMIN_PASSWORD:
        st.info("시작 몸무게를 고치거나 삭제할 수 있습니다.")
        edited_weights_df = st.data_editor(weights_df, num_rows="dynamic", use_container_width=True)
        if not edited_weights_df.equals(weights_df):
            edited_weights_df.to_csv(WEIGHTS_FILE, index=False)
            st.success("시작 몸무게 수정 완료! (화면이 곧 새로고침 됩니다)")
            st.rerun()
    elif pwd:
        st.error("비밀번호가 틀렸습니다.")

st.divider()
st.caption("💡 수정 및 삭제는 4월 1일 전 테스트 기간 동안 마음껏 해보세요!")
