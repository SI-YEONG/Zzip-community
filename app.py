import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime

# ✅ 파일 경로 설정
os.makedirs("data", exist_ok=True)
users_path = "data/users.csv"
log_path = "data/log.csv"

# ✅ 파일 초기화
for path, cols in [
    (users_path, ["이름", "비밀번호", "수면시간", "기상시간", "가입일"]),
    (log_path, ["날짜", "이름", "user_id", "성공여부", "기분"])
]:
    if not os.path.exists(path):
        pd.DataFrame(columns=cols).to_csv(path, index=False, encoding="cp949")

# ✅ 파일 로드
user_df = pd.read_csv(users_path, encoding="cp949")
log_df = pd.read_csv(log_path, encoding="cp949")

# ✅ 배경 이미지 적용
try:
    with open("night_sky.jpg", "rb") as f:
        bg_image = base64.b64encode(f.read()).decode()
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{bg_image}");
            background-size: cover;
            background-position: center;
        }}
        </style>
    """, unsafe_allow_html=True)
except:
    pass

# ✅ 페이지 설정
st.set_page_config(page_title="Zzip 3.0", layout="centered")
st.title("🌙 Zzip – 잠드는 습관을 모아주는 커뮤니티형 수면 루틴 서비스")

page = st.sidebar.radio("페이지 선택", ["🏠 챌린지 인증", "📊 마이페이지", "👤 사용자 목록 (관리자)"])

today = datetime.now().strftime("%Y-%m-%d")

# ✅ 챌린지 인증 페이지
if page == "🏠 챌린지 인증":
    st.header("🏠 오늘의 루틴 인증")
    mode = st.radio("가입하신 적이 있나요?", ["가입하지 않았습니다", "가입한 적이 있습니다"], horizontal=True)

    username = st.text_input("닉네임")
    password = st.text_input("비밀번호 (4자리 숫자)", type="password", max_chars=4)
    user_id = f"{username.strip()}_{password.strip()}"

    def is_valid_time(t):
        return pd.notna(t) and isinstance(t, str) and len(t) == 5 and ":" in t

    if mode == "가입하지 않았습니다":
        sleep = st.text_input("잠드는 시간 (00:00)", placeholder="23:30")
        wake = st.text_input("기상 시간 (00:00)", placeholder="07:30")
        if st.button("회원가입 후 저장"):
            if user_id in user_df.apply(lambda r: f"{r['이름'].strip()}_{str(r['비밀번호']).strip()}", axis=1).values:
                st.error("이미 가입된 사용자입니다.")
            elif not is_valid_time(sleep) or not is_valid_time(wake):
                st.warning("시간 형식이 올바르지 않습니다. 예: 23:30")
            else:
                new = pd.DataFrame([[username, password, sleep, wake, today]], columns=user_df.columns)
                user_df = pd.concat([user_df, new], ignore_index=True)
                user_df.to_csv(users_path, index=False, encoding="cp949")
                st.success("🎉 회원가입 완료! 다시 로그인 해주세요.")

    elif mode == "가입한 적이 있습니다":
        if st.button("로그인"):
            user_df["user_id"] = user_df["이름"].astype(str).str.strip() + "_" + user_df["비밀번호"].astype(str).str.strip()
            matched = user_df["user_id"] == user_id
            if matched.any():
                st.session_state["login"] = True
                st.session_state["username"] = username
                st.session_state["user_id"] = user_id
                st.success(f"{username}님, 환영합니다!")
            else:
                st.error("닉네임 또는 비밀번호가 일치하지 않습니다.")

    if st.session_state.get("login"):
        st.subheader(f"🌟 {st.session_state['username']}님, 루틴 인증을 시작하세요!")
        mood = st.radio("기분 어땠나요?", ["기분 좋아요", "그냥 그래요", "피곤해요"])
        success = st.checkbox("✅ 수면 루틴을 지켰어요!")

        already = log_df[(log_df["user_id"] == st.session_state["user_id"]) & (log_df["날짜"] == today)]

        if not already.empty:
            st.info("오늘은 이미 루틴을 인증하셨습니다!")
        else:
            if st.button("💾 오늘 루틴 인증 저장"):
                result = "성공" if success else "실패"
                new_log = pd.DataFrame([[today, st.session_state['username'], st.session_state['user_id'], result, mood]],
                                       columns=log_df.columns)
                log_df = pd.concat([log_df, new_log], ignore_index=True)
                log_df.to_csv(log_path, index=False, encoding="cp949")
                st.success(f"오늘 인증이 저장되었습니다. ({result})")

# ✅ 마이페이지
elif page == "📊 마이페이지":
    st.header("📊 내 인증 이력 확인")
    name = st.text_input("닉네임 입력")
    pw = st.text_input("비밀번호 (4자리 숫자)", type="password")
    uid = f"{name.strip()}_{pw.strip()}"

    if st.button("조회"):
        logs = log_df[log_df["user_id"] == uid]
        if logs.empty:
            st.info("해당 사용자의 인증 기록이 없습니다.")
        else:
            st.dataframe(logs)

# ✅ 관리자 사용자 목록
elif page == "👤 사용자 목록 (관리자)":
    st.header("👤 전체 사용자 보기")
    admin_pw = st.text_input("관리자 비밀번호 입력", type="password")
    if admin_pw == "admin":
        st.success("관리자 인증 완료")
        st.subheader("✅ 사용자 목록")
        st.dataframe(user_df)

        st.subheader("📆 인증 기록")
        st.dataframe(log_df)
    else:
        st.warning("비밀번호가 틀렸습니다.")
