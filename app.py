import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 파일 경로 설정
users_path = "users.csv"
log_path = "log.csv"
comm_path = "community.csv"
comment_path = "comments.csv"

# 파일 불러오기
def load_data(path):
    if os.path.exists(path):
        return pd.read_csv(path, encoding="cp949")
    else:
        return pd.DataFrame()

user_df = load_data(users_path)
log_df = load_data(log_path)
community_df = load_data(comm_path)
comment_df = load_data(comment_path)

# 기본 정보 입력
st.markdown("<h1 style='text-align: center;'>🌙 별이 쏟아지는 오늘, 잘 자는 우리</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>(by @시너텍)</p>", unsafe_allow_html=True)
st.image("night_sky.jpg", use_column_width=True)

# 페이지 선택
page = st.sidebar.radio("페이지 선택", ["🏠 챌린지 인증", "💬 커뮤니티", "📊 마이페이지", "👤 사용자 목록 (관리자 전용)"])

today = datetime.now().strftime("%Y-%m-%d")

if page == "🏠 챌린지 인증":
    st.subheader("🙋 가입하신 적이 있나요?")
    mode = st.radio("", ["가입하지 않았습니다", "가입한 적이 있습니다"], horizontal=True)

    username = st.text_input("닉네임:", key="username")
    password = st.text_input("비밀번호 (4자리 숫자)", type="password", max_chars=4, key="pw")
    user_id = f"{username.strip()}_{password.strip()}"

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
                new_user = pd.DataFrame([[username.strip(), password.strip(), sleep_time, wake_time, today]], columns=user_df.columns)
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

if st.session_state.get("login"):
    st.sidebar.success(f"환영합니다, {username}님!")

    if page == "📊 마이페이지":
        st.subheader("📌 마이페이지")

        user_data = user_df[(user_df["이름"] == username.strip()) & (user_df["비밀번호"] == password.strip())]

        if user_data.empty:
            st.warning("사용자 정보를 불러올 수 없습니다.")
        else:
            st.markdown(f"- 수면 시간: ⏰ {user_data['수면 시간'].values[-1]}")
            st.markdown(f"- 기상 시간: 🌞 {user_data['기상 시간'].values[-1]}")
            st.markdown(f"- 챌린지 시작일: 📅 {user_data['가입일'].values[-1]}")

    if page == "🏠 챌린지 인증":
        st.subheader("📅 오늘의 루틴 인증")

        success = st.checkbox("✅ 오늘 수면 루틴을 지켰어요!")
        mood = st.radio("오늘의 기분은 어땠나요?", ["기분 좋아요", "그냥 그래요", "피곤해요"])

        if st.button("💾 오늘 루틴 인증 저장", key="save_today"):
            log_df = load_data(log_path)
            already_logged = log_df[(log_df["user_id"] == user_id) & (log_df["날짜"] == today)]

            if not already_logged.empty:
                st.warning("😴 오늘은 이미 루틴을 인증하셨어요!")
            else:
                wake_obj = datetime.strptime(user_data['기상 시간'].values[-1], "%H:%M").time()
                good_morning_success = wake_obj <= datetime.strptime("07:00", "%H:%M").time()
                status = "성공" if success and good_morning_success else "실패"

                new_log = pd.DataFrame([[today, username, user_id, status, mood]], columns=log_df.columns)
                log_df = pd.concat([log_df, new_log], ignore_index=True)
                log_df.to_csv(log_path, index=False, encoding="cp949")
                st.success(f"📝 오늘 루틴 인증이 저장되었습니다! (굿모닝 챌린지: {status})")

    if page == "💬 커뮤니티":
        st.header("💬 Zzip 커뮤니티")

        st.subheader("📌 오늘의 이야기 공유하기")
        post = st.text_area("무엇이든 자유롭게 작성해보세요!")
        if st.button("📮 게시하기"):
            if post.strip():
                new_post = pd.DataFrame([[today, username.strip(), post.strip()]], columns=community_df.columns)
                community_df = pd.concat([community_df, new_post], ignore_index=True)
                community_df.to_csv(comm_path, index=False, encoding="cp949")
                st.success("✉️ 게시물이 업로드되었습니다!")
            else:
                st.warning("내용을 작성해주세요.")

        st.subheader("📚 커뮤니티 게시판")
        for i, row in community_df[::-1].iterrows():
            st.markdown(f"**[{row['날짜']}] {row['작성자']}**")
            st.markdown(f"{row['내용']}")
            comment_input = st.text_input(f"💬 {row['작성자']}님 글에 댓글 달기", key=f"comment_{i}")
            if st.button("댓글 작성", key=f"comment_button_{i}"):
                if comment_input.strip():
                    new_comment = pd.DataFrame([[row['날짜'], row['작성자'], username.strip(), comment_input.strip()]], columns=comment_df.columns)
                    comment_df = pd.concat([comment_df, new_comment], ignore_index=True)
                    comment_df.to_csv(comment_path, index=False, encoding="cp949")
                    st.success("✅ 댓글이 등록되었습니다!")

            comments = comment_df[(comment_df["게시글작성자"] == row["작성자"]) & (comment_df["게시글날짜"] == row["날짜"])]
            for _, c in comments.iterrows():
                st.markdown(f"- 💬 **{c['댓글작성자']}**: {c['댓글내용']}")
            st.markdown("---")

    if page == "👤 사용자 목록 (관리자 전용)":
        st.header("👤 전체 사용자 보기")
        admin_pw = st.text_input("관리자 비밀번호 입력", type="password")
        if username == "짱아러버" and password == "1234" and admin_pw == "admin":
            st.success("관리자 인증 완료")
            st.subheader("✅ 사용자 목록")
            st.dataframe(user_df)

            st.subheader("📆 인증 기록")
            st.dataframe(log_df)

            st.subheader("💬 커뮤니티 게시글")
            st.dataframe(community_df)

            st.subheader("📝 댓글 목록")
            st.dataframe(comment_df)
        else:
            st.warning("비밀번호가 틀렸거나 관리자 정보가 일치하지 않습니다.")
