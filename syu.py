import streamlit as st
from components import company, calendar, agent, industry, es, study, interview

st.set_page_config(page_title="就活まとめアプリ", layout="wide")

PAGES = {
    "企業まとめ": company.show,
    "カレンダー": calendar.show,
    "エージェントまとめ": agent.show,
    "業界まとめ": industry.show,
    "ES管理": es.show,
    "学力試験対策": study.show,
    "面接対策": interview.show,
}

with st.sidebar:
    st.title("就活まとめアプリ")
    page = st.radio("ページ選択", list(PAGES.keys()))

PAGES[page]()
