import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
from .utils import load_json, save_json, today_str

FILE = "study_log.json"

def _ask():
    a = random.randint(1,99); b = random.randint(1,99)
    op = random.choice(["+","-","*","//"])
    return a,b,op

def _calc(a,b,op):
    if op == "+": return a+b
    if op == "-": return a-b
    if op == "*": return a*b
    if op == "//": return a//b

def show():
    st.title("学力試験対策")
    log = load_json(FILE, [])

    with st.expander("学習を記録", expanded=False):
        with st.form("log"):
            subject = st.text_input("学習内容（例：SPI非言語）")
            minutes = st.number_input("学習時間（分）", 0, 600, 30)
            correct = st.number_input("正答数", 0, 999, 0)
            if st.form_submit_button("保存"):
                log.append({"日付": today_str(), "学習内容": subject, "学習時間": minutes, "正答数": correct})
                save_json(FILE, log)
                st.success("保存しました。")

    st.subheader("学習履歴")
    if log:
        df = pd.DataFrame(log)
        st.dataframe(df, use_container_width=True)
        daily = df.groupby("日付")["学習時間"].sum().reset_index()
        st.bar_chart(daily.set_index("日付"))

        # ⏰ 未実施アラート
        last_day = (datetime.now()-timedelta(days=1)).strftime("%Y-%m-%d")
        if last_day not in df["日付"].values:
            st.warning(f"⚠ 昨日（{last_day}）は学習記録がありません。継続しましょう！")
    else:
        st.info("学習履歴はまだありません。")

    st.subheader("ミニ例題（四則演算）")
    if "quiz" not in st.session_state:
        st.session_state.quiz = _ask()
    a,b,op = st.session_state.quiz
    st.write(f"問題： {a} {op} {b} = ?")
    ans = st.number_input("答えを入力", step=1, value=0)
    if st.button("採点"):
        correct = _calc(a,b,op)
        if ans == correct:
            st.success("正解！")
        else:
            st.error(f"不正解。正解は {correct}")
        st.session_state.quiz = _ask()
