import streamlit as st
import pandas as pd
from .utils import load_json, save_json

FILE = "agents.json"

def show():
    st.title("エージェントまとめ")
    agents = load_json(FILE, [])
    with st.form("add_agent"):
        c1,c2,c3 = st.columns(3)
        with c1: name = st.text_input("エージェント名*")
        with c2: pic = st.text_input("担当者")
        with c3: contact = st.text_input("連絡先")
        memo = st.text_area("メモ")
        if st.form_submit_button("追加") and name:
            agents.append({"エージェント名":name,"担当者":pic,"連絡先":contact,"メモ":memo})
            save_json(FILE, agents)
            st.success("追加しました。")

    if not agents:
        st.info("登録なし")
        return
    df = pd.DataFrame(agents)
    st.dataframe(df, use_container_width=True)
