import streamlit as st
import pandas as pd
from .utils import load_json, save_json, try_gemini

FILE = "industries.json"

def _summarize_with_ai(name, points):
    model = try_gemini()
    if not model:
        # 簡易ローカル要約
        base = f"{name}業界の要点:\n- 特徴: {points.get('特徴','')}\n- 将来性: {points.get('将来性','')}"
        return base.strip()
    prompt = f"""以下の業界について、200字程度で就活生向けに端的にまとめて：
業界名:{name}
特徴:{points.get('特徴','')}
将来性:{points.get('将来性','')}
"""
    try:
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except Exception:
        return "要約に失敗しました。"

def show():
    st.title("業界まとめ")
    items = load_json(FILE, [])
    with st.expander("業界を追加", expanded=False):
        with st.form("add_industry"):
            name = st.text_input("業界名*")
            feat = st.text_area("業界の特徴")
            future = st.text_area("将来性")
            memo = st.text_area("メモ（任意）")
            if st.form_submit_button("追加") and name:
                summary = _summarize_with_ai(name, {"特徴":feat, "将来性":future})
                items.append({"業界名":name,"特徴":feat,"将来性":future,"メモ":memo,"要約":summary})
                save_json(FILE, items)
                st.success("追加しました。")

    if not items:
        st.info("登録なし")
        return

    df = pd.DataFrame(items)
    st.subheader("一覧")
    st.dataframe(df[["業界名","要約"]], use_container_width=True)

    st.subheader("クイズ（知識チェック）")
    # 登録されている業界からランダムに1問
    import random
    target = random.choice(items)
    q = f"『{target['要約']}』これはどの業界？"
    options = random.sample([x["業界名"] for x in items], k=min(4, len(items)))
    if target["業界名"] not in options:
        options[random.randrange(len(options))] = target["業界名"]
    ans = st.radio(q, options, index=0)
    if st.button("回答する"):
        if ans == target["業界名"]:
            st.success("正解！")
        else:
            st.error(f"不正解。正しくは「{target['業界名']}」")
