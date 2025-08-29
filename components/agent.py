import streamlit as st
import pandas as pd
from .utils import load_json, save_json

FILE = "agents.json"

def show():
    st.title("エージェントまとめ")
    agents = load_json(FILE, [])

    #-- 新規追加
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
            st.experimental_rerun()

    if not agents:
        st.info("登録なし")
        return
    
    #-- 一覧表示
    df = pd.DataFrame(agents)
    st.subheader("登録済みエージェント")
    for idx, row in df.iterrows():
        with st.expander(row["エージェント名"], expanded=False):
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.text_input("エージェント名", value=row["エージェント名"], key=f"name_{idx}")
            with c2: st.text_input("担当者", value=row["担当者"], key=f"pic_{idx}")
            with c3: st.text_input("連絡先", value=row["連絡先"], key=f"contact_{idx}")
            with c4: st.text_area("メモ", value=row["メモ"], key=f"memo_{idx}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("更新", key=f"update_{idx}"):
                    agents[idx]["エージェント名"] = st.session_state[f"name_{idx}"]
                    agents[idx]["担当者"] = st.session_state[f"pic_{idx}"]
                    agents[idx]["連絡先"] = st.session_state[f"contact_{idx}"]
                    agents[idx]["メモ"] = st.session_state[f"memo_{idx}"]
                    save_json(FILE, agents)
                    st.success("更新しました。")
                    st.rerun()
            with col2:
                if st.button("削除", key=f"del_{idx}"):
                    agents.pop(idx)
                    save_json(FILE, agents)
                    st.warning("削除しました。")
                    st.rerun()
