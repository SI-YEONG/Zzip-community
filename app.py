import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 파일 경로 설정
users_path = "data/users.csv"
log_path = "data/log.csv"
comm_path = "data/community.csv"
comment_path = "data/comments.csv"

# 초기 파일 생성
for path, columns in [
    (users_path, ["이름", "비밀번호", "수면시간", "기상시간", "가입일"]),
    (log_path, ["날짜", "이름", "user_id", "성공여부", "기분"]),
    (comm_path, ["날짜", "이름", "내용"]),
    (comment_path, ["날짜", "이름", "댓글대상", "댓글내용"]),
]:
    if not os.path.exists(path):
        pd.DataFrame(columns=columns).to_csv(path, index=False, encoding="cp949")

# 파일 불러오기
user_df = pd.read_csv(users_path, encoding="cp949")
log_df = pd.read_csv(log_path, encoding="cp949")
community_df = pd.read_csv(comm_path, encoding="cp949")
comment_df = pd.read_csv(comment_path, encoding="cp949")

st.set_page_config(page_title="Zzip 3.0", layout="wide")
st.title("🌙 Zzip – 잠드는 습관을 모아주는 커뮤니티형 수면 루틴 서비스")

# 페이지 선택
page = st.sidebar.radio("페이지 선택", ["🏠 챌린지 인증", "💬 커뮤니티", "📊 마이페이지", "👤 사용자 목록 (관리자 전용)"])

if page == "🏠 챌린지 인증":
    st.header("🏠 Zzip – 수면 루틴 챌린지")

    st.subheader("🙋 가입하신 적이 있나요?")
    mode = st.radio("", ["가입하지 않았습니다", "가입한 적이 있습니다"], horizontal=True)

    username = st.text_input("닉네임:", key="username")
    password = st.text_input("비밀번호 (4자리 숫자)", type="password", max_chars=4, key="pw")
    user_id = f"{username.strip()}_{password.strip()}"
    today = datetime.now().strftime("%Y-%m-%d")

    def is_valid_time_format(t):
        return pd.notna(t) and isinstance(t, str) and len(t) == 5 and ":" in t

    if mode == "가입하지 않았습니다":
        sleep_time = st.text_input("잠드는 시간 (00:00 형식)", placeholder="예: 23:30", key="sleep_input")
        wake_time = st.text_input("기상 시간 (00:00 형식)", placeholder="예: 07:30", key="wake_input")

        if st.button("회원가입 후 루틴 저장"):
            if len(password.strip()) != 4 or not password.strip().isdigit():
                st.warning("비밀번호는 4자리 숫자여야 합니다.")
            elif not is_valid_time_format(sleep_time) or not is_valid_time_format(wake_time):
                st.warning("수면/기상 시간은 반드시 00:00 형식으로 입력해주세요.")
            elif user_id in user_df.apply(lambda r: f"{r['이름'].strip()}_{str(r['비밀번호']).strip()}", axis=1).values:
                st.error("이미 존재하는 사용자입니다.")
            else:
                new_user = pd.DataFrame([[username.strip(), password.strip(), sleep_time, wake_time, today]],
                                        columns=user_df.columns)
                user_df = pd.concat([user_df, new_user], ignore_index=True)
                user_df.to_csv(users_path, index=False, encoding="cp949")
                st.success("🎉 회원가입 완료! 다시 로그인 해주세요.")
    elif mode == "가입한 적이 있습니다":
        login_button = st.button("로그인")
        matched = (
            user_df["이름"].astype(str).str.strip() == username.strip()
        ) & (
            user_df["비밀번호"].astype(str).str.strip() == password.strip()
        )

        if login_button:
            if matched.any():
                st.session_state["login"] = True
                st.session_state["user_id"] = user_id
                st.success(f"🌙 {username}님 환영합니다.")
            else:
                st.error("닉네임 또는 비밀번호가 일치하지 않습니다.")

    if "login" in st.session_state and st.session_state["login"]:
        st.markdown("### 🌅 오늘 루틴 인증")

        sleep_time = user_df[user_df["이름"] == username]["수면시간"].values[0]
        wake_time = user_df[user_df["이름"] == username]["기상시간"].values[0]
        mood = st.selectbox("기상 후 기분은 어떤가요?", ["😊", "😐", "😴", "😡", "😭"])
        success = st.checkbox("🛏️ 어제 설정한 시간에 맞춰 잠들었나요?")

        if st.button("💾 오늘 루틴 인증 저장"):
            today = datetime.now().strftime("%Y-%m-%d")
            already_logged = log_df[
                (log_df["user_id"] == user_id) & (log_df["날짜"] == today)
            ]

            if not already_logged.empty:
                st.warning("😴 오늘은 이미 루틴을 인증하셨어요!")
            else:
                try:
                    wake_obj = datetime.strptime(wake_time, "%H:%M").time()
                except:
                    st.error("기상 시간 형식 오류")
                    wake_obj = None

                good_morning_success = wake_obj and wake_obj <= datetime.strptime("07:00", "%H:%M").time()
                status = "성공" if success and good_morning_success else "실패"

                new_log = pd.DataFrame(
                    [[today, username, user_id, status, mood]],
                    columns=log_df.columns
                )
                log_df = pd.concat([log_df, new_log], ignore_index=True)
                log_df.to_csv(log_path, index=False, encoding="cp949")
                st.success(f"📝 오늘 루틴 인증이 저장되었습니다! (굿모닝 챌린지: {status})")

        # 관리자 전용 로그 확인
        if username.strip() == "짱아러버":
            st.markdown("### 📂 전체 사용자 log.csv 기록 보기 (관리자용)")
            if st.checkbox("모든 사용자 인증 기록 보기"):
                try:
                    log_df = pd.read_csv(log_path, encoding="cp949")
                    st.dataframe(log_df)
                except FileNotFoundError:
                    st.warning("log.csv 파일이 아직 없습니다.")
elif page == "💬 커뮤니티":
    st.header("💬 수면 루틴 커뮤니티")
    new_post = st.text_area("📝 커뮤니티에 글을 작성해보세요!", placeholder="내용을 입력하세요")
    author = st.text_input("작성자 이름", key="comm_name")
    if st.button("게시글 등록"):
        if new_post.strip() and author.strip():
            today = datetime.now().strftime("%Y-%m-%d")
            new_entry = pd.DataFrame([[today, author, new_post]], columns=community_df.columns)
            community_df = pd.concat([community_df, new_entry], ignore_index=True)
            community_df.to_csv(comm_path, index=False, encoding="cp949")
            st.success("게시글이 등록되었습니다!")
        else:
            st.warning("모든 항목을 입력해주세요.")

    st.subheader("📃 커뮤니티 피드")
    for idx, row in community_df.iterrows():
        st.markdown(f"**{row['이름']}** ({row['날짜']}): {row['내용']}")
        comment_text = st.text_input(f"💬 {row['이름']}님 글에 댓글 달기", key=f"comment_{idx}")
        commenter = st.text_input("댓글 작성자 이름", key=f"commenter_{idx}")
        if st.button("댓글 등록", key=f"submit_{idx}"):
            if comment_text.strip() and commenter.strip():
                today = datetime.now().strftime("%Y-%m-%d")
                new_comment = pd.DataFrame([[today, commenter, row['이름'], comment_text]], columns=comment_df.columns)
                comment_df = pd.concat([comment_df, new_comment], ignore_index=True)
                comment_df.to_csv(comment_path, index=False, encoding="cp949")
                st.success("댓글이 등록되었습니다.")
            else:
                st.warning("댓글과 이름을 모두 입력해주세요.")
elif page == "📊 마이페이지":
    st.header("📊 마이페이지")

    name = st.text_input("닉네임 입력", key="mypage_name")
    pw = st.text_input("비밀번호 입력 (4자리 숫자)", type="password", key="mypage_pw")
    uid = f"{name.strip()}_{pw.strip()}"

    if st.button("조회하기"):
        if uid not in user_df.apply(lambda r: f"{r['이름'].strip()}_{str(r['비밀번호']).strip()}", axis=1).values:
            st.warning("회원 정보가 없습니다. 닉네임과 비밀번호를 다시 확인해주세요.")
        else:
            st.success(f"{name}님의 루틴과 인증 현황입니다.")
            st.markdown("#### 🛌 루틴 정보")
            selected = user_df[user_df["이름"] == name]
            st.dataframe(selected[["수면시간", "기상시간"]])

            st.markdown("#### 📆 인증 이력")
            log_data = log_df[log_df["user_id"] == uid]
            if log_data.empty:
                st.info("아직 인증한 기록이 없습니다.")
            else:
                st.dataframe(log_data)

elif page == "👤 사용자 목록 (관리자 전용)":
    st.header("👤 전체 사용자 목록 (관리자 전용)")

    if st.text_input("관리자 비밀번호", type="password", key="admin_pw") == "admin":
        st.success("관리자 인증 완료!")
        st.subheader("회원 정보")
        st.dataframe(user_df)

        st.subheader("루틴 인증 기록")
        st.dataframe(log_df)

        st.subheader("커뮤니티 글")
        st.dataframe(community_df)

        st.subheader("댓글 목록")
        st.dataframe(comment_df)
    else:
        st.warning("비밀번호가 틀렸거나 입력되지 않았습니다.")


