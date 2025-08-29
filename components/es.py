import streamlit as st
import pandas as pd
import numpy as np
from .utils import load_json, save_json, try_gemini

FILE = "es_data.json"

def _ai_review(text):
    model = try_gemini()
    if not model:
        tips = []
        if len(text) < 200: tips.append("文章量が少ないかも（200文字以上推奨）")
        if "私は" not in text: tips.append("主語が曖昧。結論/成果/根拠を整理")
        return " / ".join(tips) or "OK"
    prompt = f"以下のESを就活選考向けに要約し、改善点を3つ提案してください：\n{text}"
    try:
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except Exception:
        return "添削に失敗しました。"

def _embed(text):
    model = try_gemini()
    if not model:
        return np.random.rand(1,256)  # 疑似ベクトル
    try:
        emb = model.embed_content(content=text, model="models/text-embedding-004")
        return np.array(emb["embedding"]).reshape(1,-1)
    except Exception:
        return np.random.rand(1,256)

def show():
    st.title("ES管理")
    data = load_json(FILE, [])

    # 新規追加
    with st.expander("新規作成", expanded=False):
        with st.form("add_es"):
            title = st.text_input("質問内容名 / タイトル*")
            body = st.text_area("本文（文字数カウンタあり）", height=240)
            st.write(f"文字数：{len(body)}")
            if st.form_submit_button("保存") and title:
                review = _ai_review(body)
                emb = _embed(body).tolist()
                data.append({"タイトル":title,"本文":body,"添削":review,"embedding":emb})
                save_json(FILE, data)
                st.success("保存しました。")

    if not data:
        st.info("まだESがありません。")
        return

    df = pd.DataFrame(data)
    st.subheader("一覧")
    st.dataframe(df[["タイトル"]])

    # 詳細表示
    st.subheader("詳細と操作")
    for i, row in enumerate(data):
        with st.expander(row["タイトル"]):
            st.text_area("本文", row["本文"], height=220, key=f"es_{i}")
            st.write("添削（AI/ローカル）")
            st.write(row.get("添削",""))

            # 📋 コピーボタン（pyperclip不要）
            if st.button("コピー", key=f"copy_{i}"):
                st.experimental_set_query_params()  # ダミーでクリック反応を強制
                st.session_state.copied_text = row["本文"]
                st.success("クリップボードにコピーしてください（右クリック → コピー / Ctrl+C）")
