import streamlit as st
import random
import json
from pathlib import Path
import google.generativeai as genai

DATA_FILE = Path("interview_questions.json")

# JSON読み込み
def load_json(file_path, default=[]):
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

# JSON保存
def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Geminiで例回答・目安時間取得
def ask_gemini(question):
    if "GEMINI_API_KEY" not in st.secrets:
        return {"estimated_time": "1-2分", "example_answer": "Gemini APIキーが設定されていません。"}

    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
以下の質問に対して、目安回答時間（分）と模範回答をJSON形式で返してください。

質問: {question}

返答形式:
{{
  "estimated_time": "x分",
  "example_answer": "模範回答"
}}
"""
        resp = model.generate_content(prompt)
        return json.loads(resp.text.strip())
    except Exception as e:
        return {"estimated_time": "1-2分", "example_answer": f"取得失敗: {e}"}

def show():
    st.title("面接対策")

    # データ読み込み
    data = load_json(DATA_FILE, [])

    # ランダム質問表示
    if data:
        st.subheader("ランダム質問")
        if st.button("質問を出す"):
            st.session_state.random_q = random.choice(data)["question"]
        random_q = st.session_state.get("random_q", random.choice(data)["question"])
        st.info(random_q)

    st.subheader("新しい質問の追加")
    question = st.text_input("質問内容")
    memo = st.text_area("メモ")
    
    if st.button("Geminiで模範回答と目安時間を取得"):
        if not question:
            st.warning("質問内容を入力してください。")
        else:
            result = ask_gemini(question)
            new_entry = {
                "question": question,
                "memo": memo,
                "estimated_time": result["estimated_time"],
                "example_answer": result["example_answer"]
            }
            data.append(new_entry)
            save_json(DATA_FILE, data)
            st.success("質問を追加しました。")
            st.json(new_entry)

    # 入力済み質問の一覧表示と編集・削除
    if data:
        st.subheader("登録済み質問一覧")
        for i, item in enumerate(data):
            st.markdown(f"**{i+1}. 質問:** {item['question']}")
            st.markdown(f"- メモ: {item.get('memo','')}")
            st.markdown(f"- 目安回答時間: {item.get('estimated_time','')}")
            st.markdown(f"- 模範回答: {item.get('example_answer','')}")
            
            col1, col2, col3 = st.columns([1,1,1])
            with col1:
                if st.button("編集", key=f"edit_{i}"):
                    st.session_state.edit_index = i
                    st.session_state.edit_question = item["question"]
                    st.session_state.edit_memo = item.get("memo","")
            with col2:
                if st.button("Gemini再取得", key=f"regen_{i}"):
                    result = ask_gemini(item["question"])
                    item["estimated_time"] = result["estimated_time"]
                    item["example_answer"] = result["example_answer"]
                    save_json(DATA_FILE, data)
                    st.success(f"{i+1}番の質問の模範回答を更新しました。")
            with col3:
                if st.button("削除", key=f"delete_{i}"):
                    data.pop(i)
                    save_json(DATA_FILE, data)
                    st.success(f"{i+1}番の質問を削除しました。")
                    st.rerun()
            st.markdown("---")

    # 編集モード
    if "edit_index" in st.session_state:
        st.subheader("質問編集")
        edit_q = st.text_input("質問内容", st.session_state.edit_question, key="edit_q")
        edit_memo = st.text_area("メモ", st.session_state.edit_memo, key="edit_memo")
        if st.button("保存", key="save_edit"):
            idx = st.session_state.edit_index
            data[idx]["question"] = edit_q
            data[idx]["memo"] = edit_memo
            save_json(DATA_FILE, data)
            st.success("質問を更新しました。")
            del st.session_state.edit_index
            del st.session_state.edit_question
            del st.session_state.edit_memo
            st.rerun()
