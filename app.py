import streamlit as st
import pandas as pd
import os
from datetime import datetime, time
import matplotlib.pyplot as plt
import matplotlib
import base64

# 기본 설정
st.set_page_config(page_title="Zzip - 잠드는 습관", layout="wide")

# 파일 경로
users_path = "data/users.csv"
log_path = "data/log.csv"
comm_path = "data/community.csv"
comment_path = "data/comment.csv"

# 디렉토리 생성
os.makedirs("data", exist_ok=True)
for path, columns in [
    (users_path, ["이름", "비밀번호", "수면시간", "기상시간", "챌린지시작일"]),
    (log_path, ["날짜", "이름", "user_id", "성공여부", "기분"]),
    (comm_path, ["글ID", "닉네임", "날짜", "내용"]),
    (comment_path, ["글ID", "닉네임", "날짜", "내용"])
]:
    if not os.path.exists(path):
        pd.DataFrame(columns=columns).to_csv(path, index=False, encoding="cp949")

# 파일 불러오기
user_df = pd.read_csv(users_path, encoding="cp949")
log_df = pd.read_csv(log_path, encoding="cp949")
community_df = pd.read_csv(comm_path, encoding="cp949")
comment_df = pd.read_csv(comment_path, encoding="cp949")

# 🌌 배경 설정
with open("night_sky.jpg", "rb") as img_file:
    img_base64 = base64.b64encode(img_file.read()).decode()

# 사이드바 배경 이미지 불러오기
with open("the_galaxy.jpg", "rb") as f:
    sidebar_base64 = base64.b64encode(f.read()).decode()
st.markdown(
    f"""
    <style>
    /* 전체 앱 배경 */
    .stApp {{
        background-image: url("data:image/jpeg;base64,{img_base64}");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        color: white !important;
    }}

    /* 사이드바 배경 */
    section[data-testid="stSidebar"] {{
        background-image: url("data:image/jpeg;base64,{sidebar_base64}");
        background-size: cover;
        background-position: center;
        color: white !important;
    }}

    /* 라벨 및 헤더 텍스트 흰색 */
    label, h1, h2, h3, h4, h5, h6, p, div, .css-16idsys, .css-qrbaxs {{
        color: white !important;
    }}

    /* 체크박스 및 라디오 텍스트 흰색 */
    .stRadio > label, .stCheckbox > label {{
        color: white !important;
    }}

    /* 입력창(닉네임 등) 내부 텍스트 검정색 */
    input, textarea {{
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: black !important;
    }}

    /* ✅ 시간 입력창 텍스트 검정색 */
    .stTimeInput input {{
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: black !important;
    }}

    /* ✅ 드롭다운 항목도 검정 텍스트 */
    div[role="listbox"] span {{
        color: black !important;
        font-weight: 600;
    }}

    /* 버튼 스타일 */
    .stButton > button {{
        color: white !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid white !important;
    }}
    .stButton > button:hover {{
        color: #ffffdd !important;
        border-color: #ffffdd !important;
        background-color: rgba(255, 255, 255, 0.2) !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)


# 감성 문구
st.markdown(
    """
    <div style="
        background-color: rgba(0, 0, 0, 0.5);
        padding: 1rem;
        border-radius: 1rem;
        margin-top: -30px;
        margin-bottom: 20px;
        text-align: center;
        font-size: 20px;
        font-weight: 500;
        color: #ffffff;
    ">
        🌠 별이 쏟아지는 오늘, 잘 자는 우리<br><span style='font-size:14px; opacity: 0.8;'>(by @시너텍)</span>
    </div>
    """,
    unsafe_allow_html=True
)

# 페이지 분리
page = st.sidebar.radio("페이지 선택", ["🏠 챌린지 인증", "💬 커뮤니티"])

if page == "🏠 챌린지 인증":
    st.header("🏠 Zzip – 수면 루틴 챌린지")

    st.subheader("🙋 가입하신 적이 있나요?")
    mode = st.radio("", ["가입하지 않았습니다", "가입한 적이 있습니다"], horizontal=True)

    username = st.text_input("닉네임:", key="username")
    password = st.text_input("비밀번호 (4자리 숫자)", type="password", max_chars=4, key="pw")

    user_id = f"{username.strip()}_{password.strip()}"
    today = datetime.now().strftime("%Y-%m-%d")

    if mode == "가입하지 않았습니다":
        sleep_time = st.time_input("잠드는 시간:")
        wake_time = st.time_input("기상 시간:")

        if st.button("회원가입 후 루틴 저장"):
            if len(password.strip()) != 4 or not password.strip().isdigit():
                st.warning("비밀번호는 4자리 숫자여야 합니다.")
            elif user_id in user_df.apply(lambda r: f"{r['이름'].strip()}_{str(r['비밀번호']).strip()}", axis=1).values:
                st.error("이미 존재하는 사용자입니다.")
            else:
                new_user = pd.DataFrame([[username.strip(), password.strip(),
                                          sleep_time.strftime("%H:%M"), wake_time.strftime("%H:%M"), today]],
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

    # 로그인한 경우
    if st.session_state.get("login"):
        user_id = st.session_state["user_id"]
        username = user_id.split("_")[0]
        u_row = user_df[user_df["이름"].astype(str).str.strip() == username].iloc[0]
        sleep_time = datetime.strptime(u_row["수면시간"], "%H:%M").time()
        wake_time = datetime.strptime(u_row["기상시간"], "%H:%M").time()
        start_date = u_row["챌린지시작일"]

        def get_group(bed, wake):
            if bed >= time(0, 0) and wake >= time(9, 0):
                return "올빼미형 그룹", "한밤중에 자고 늦게 일어나는 패턴입니다."
            elif bed <= time(23, 0) and wake <= time(7, 0):
                return "아침형 그룹", "일찍 자고 일찍 일어나는 패턴입니다."
            else:
                return "유연한 수면 그룹", "고정된 수면 루틴보단 유동적인 패턴입니다."

        group, desc = get_group(sleep_time, wake_time)
        st.info(f"🧭 당신은 **{group}**에 속합니다!\n\n📝 {desc}")

        st.subheader("📅 오늘의 루틴 인증")
        success = st.checkbox("✅ 오늘 수면 루틴을 지켰어요!", key="success_today")
        mood = st.radio("오늘의 기분은 어땠나요?", ["기분 좋아요", "그냥 그래요", "피곤해요"], key="mood_radio")
        if st.button("💾 오늘 루틴 인증 저장", key="save_today"):
            good_morning_success = wake_time <= time(7, 0)
            status = "성공" if success and good_morning_success else "실패"

            new_log = pd.DataFrame([[today, username, user_id, status, mood]],
                                   columns=log_df.columns)
            log_df = pd.concat([log_df, new_log], ignore_index=True)
            log_df.to_csv(log_path, index=False, encoding="cp949")
            st.success(f"📝 오늘 루틴 인증이 저장되었습니다! (굿모닝 챌린지: {status})")
        # 마이페이지 + 통계
        st.subheader("📌 마이페이지")
        st.markdown(f"""
        - 수면 시간: ⏰ **{u_row['수면시간']}**
        - 기상 시간: ☀️ **{u_row['기상시간']}**
        - 챌린지 시작일: 📅 **{u_row['챌린지시작일']}**
        """)

        st.subheader("📊 챌린지 통계")
        my_logs = log_df[(log_df["user_id"] == user_id) & (log_df["날짜"] >= start_date)]
        if not my_logs.empty:
            st.write("### ✅ 성공/실패")
            fig1, ax1 = plt.subplots()
            my_logs["성공여부"].value_counts().plot(kind="bar", ax=ax1, color=["green", "red"])
            st.pyplot(fig1)

            st.write("### 😊 기분 통계")
            fig2, ax2 = plt.subplots()
            my_logs["기분"].value_counts().plot(kind="pie", ax=ax2, autopct="%1.1f%%")
            ax2.axis("equal")
            st.pyplot(fig2)
        else:
            st.info("아직 인증 기록이 없습니다.")

        st.subheader("📂 오늘 다른 사람들의 인증")
        today_logs = log_df[log_df["날짜"] == today]
        if not today_logs.empty:
            st.dataframe(today_logs[["이름", "성공여부", "기분"]])
        else:
            st.info("오늘 인증한 사용자가 아직 없습니다.")

elif page == "💬 커뮤니티":
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")

    st.header("💬 Zzip 커뮤니티 – 오늘의 수면 이야기")
    st.write("수면에 관한 고민이나 꿀팁을 자유롭게 나눠보세요.")

    username = st.text_input("닉네임", key="comm_user")
    post = st.text_area("✍️ 글을 작성하세요 (최대 200자)", max_chars=200, key="comm_text")

    if st.button("📝 커뮤니티에 남기기", key="submit_post"):
        if username and post:
            post_id = len(community_df)
            new_post = pd.DataFrame([{
                "글ID": post_id,
                "닉네임": username,
                "날짜": today,
                "내용": post
            }])
            community_df = pd.concat([community_df, new_post], ignore_index=True)
            community_df.to_csv(comm_path, index=False, encoding="cp949")
            st.success("✅ 글이 등록되었습니다!")
        else:
            st.warning("닉네임과 내용을 모두 입력하세요.")

    st.subheader("📚 최근 커뮤니티 글")
    for _, row in community_df.sort_values(by="날짜", ascending=False).tail(10).iloc[::-1].iterrows():
        if "글ID" not in row:
            st.warning("⚠️ 글ID가 없는 행이 있어 건너뜁니다.")
            continue

        st.markdown(f"**📝 {row['닉네임']}** ({row['날짜']}): {row['내용']}")

        # 댓글 표시
        cmt = comment_df[comment_df["글ID"] == row["글ID"]]
        if not cmt.empty:
            for _, c in cmt.iterrows():
                st.markdown(f"➡️ {c['닉네임']} ({c['날짜']}): {c['내용']}")

        # 댓글 입력
        with st.form(f"댓글_{row['글ID']}"):
            commenter = st.text_input("댓글 닉네임", key=f"c_user_{row['글ID']}")
            comment = st.text_input("댓글 내용", key=f"c_text_{row['글ID']}")
            submitted = st.form_submit_button("💬 댓글 남기기")
            if submitted and commenter and comment:
                new_comment = pd.DataFrame([{
                    "글ID": row["글ID"],
                    "닉네임": commenter,
                    "날짜": today,
                    "내용": comment
                }])
                comment_df = pd.concat([comment_df, new_comment], ignore_index=True)
                comment_df.to_csv(comment_path, index=False, encoding="cp949")
                st.success("💬 댓글이 등록되었습니다!")
