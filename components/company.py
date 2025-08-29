import streamlit as st 
import pandas as pd
from datetime import date
from .utils import load_json, save_json, text_badge, try_gemini

FILE = "job_data.json"  # data/job_data.json
AGENT_FILE = "agents.json"

# --- 初期化 ---
def _init_state():
    if "companies" not in st.session_state:
        st.session_state.companies = load_json(FILE, [])

# --- フィルタ ---
def _filters(df):
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        status = st.multiselect("選考状況", sorted(df["選考状況"].dropna().unique().tolist()))
    with c2:
        priority = st.multiselect("志望度", sorted(df["志望度"].dropna().unique().tolist()))
    with c3:
        industry = st.multiselect("業界", sorted(df["業界"].dropna().unique().tolist()))
    with c4:
        agent = st.multiselect("エージェント", sorted(df["エージェント"].dropna().unique().tolist()))
    mask = pd.Series([True]*len(df))
    if status:   mask &= df["選考状況"].isin(status)
    if priority: mask &= df["志望度"].isin(priority)
    if industry: mask &= df["業界"].isin(industry)
    if agent:    mask &= df["エージェント"].isin(agent)
    return df[mask]

# --- 志望動機AI改善 ---
def _ai_improve_motive(name, industry, motive, url=None):
    model = try_gemini()
    if not model:
        return "AI未接続：文章を具体的に・成果や学びを含めるとより良くなります。"
    
    url_info = f"企業URL: {url}" if url else ""
    
    prompt = f"""
企業名: {name}
業界: {industry}
{url_info}
志望動機: {motive}

上記の志望動機を採用担当者に伝わりやすい形に改善してください。
- 結論を先に述べる
- 自分の経験や強みを結びつける
- 200字程度に整える
"""
    try:
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except Exception:
        return "AI改善に失敗しました。"

# --- 企業詳細取得 ---
def _get_company_details(name, url=None):
    model = try_gemini()
    if not model:
        return "AI未接続のため企業詳細は取得できません。"

    url_info = f"企業URL: {url}" if url else ""

    prompt = f"""
企業名: {name}
{url_info}

上記企業について、就活生向けに以下の情報をまとめてください：
- 業界の位置づけ
- 事業内容・理念
- 最近のニュースや動向
- 求めている人材像
200字程度でお願いします。
"""
    try:
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except Exception:
        return "企業情報の取得に失敗しました。"

# --- メイン表示 ---
def show():
    _init_state()
    st.title("企業まとめ")

    # --- エージェントリスト ---
    agents_list = [a["エージェント名"] for a in load_json(AGENT_FILE, [])]

    # --- 企業追加フォーム ---
    with st.expander("企業を追加", expanded=False):
        with st.form("add_company"):
            c1,c2,c3 = st.columns(3)
            with c1: name = st.text_input("企業名*")
            with c2: status = st.selectbox("選考状況", ["エントリー","説明会","一次選考","二次選考","最終選考","内定","辞退"])
            with c3: priority = st.selectbox("志望度", ["第一志望群","第二志望群","その他"])
            c4,c5,c6 = st.columns(3)
            with c4: industry = st.text_input("業界（例：SIer、メーカー等）")
            with c5: event = st.text_input("直近イベント（例：一次面接）")
            with c6: date_v = st.date_input("イベント日付", value=date.today())
            motive = st.text_area("志望動機（任意）")
            c7,c8 = st.columns(2)
            with c7:
                if agents_list:
                    agent = st.selectbox("エージェント（任意）", [""] + agents_list)
                else:
                    agent = st.text_input("エージェント（任意）")
            with c8: url = st.text_input("企業URL（任意）")
            memo = st.text_area("メモ（任意）")  # 新規メモ欄
            c9,c10 = st.columns(2)
            with c9: entry_id = st.text_input("エントリーページID", value="")
            with c10: entry_pw = st.text_input("エントリーページPW", value="", type="password")
            submitted = st.form_submit_button("追加")
            if submitted and name:
                st.session_state.companies.append({
                    "企業名": name, "選考状況": status, "志望度": priority,
                    "業界": industry, "直近イベント": event, "日付": str(date_v),
                    "エージェント": agent, "URL": url,
                    "ID": entry_id, "PW": entry_pw,
                    "志望動機": motive,
                    "メモ": memo
                })
                save_json(FILE, st.session_state.companies)
                st.success("追加しました。")
                st.experimental_rerun()

    # --- DataFrame 作成 ---
    df = pd.DataFrame(st.session_state.companies)
    if df.empty:
        st.info("まだ企業がありません。上のフォームから追加してください。")
        return

    # --- フィルタ ---
    st.subheader("フィルタ")
    fdf = _filters(df)
    c1,c2 = st.columns(2)
    with c1: st.metric("登録数", len(df))
    with c2: st.metric("表示件数", len(fdf))

    # --- 詳細と編集 ---
    st.subheader("詳細と編集")
    for idx, row in fdf.reset_index().iterrows():
        with st.expander(f"{row['企業名']}/{row['業界']}", expanded=False):
            b1,b2,b3,b4 = st.columns(4)
            with b1: text_badge("直近イベント", row.get("直近イベント","-"))
            with b2: text_badge("日付", str(row.get("日付","-")))
            with b3: text_badge("エージェント", row.get("エージェント","-"))
            with b4: text_badge("エントリーID", row.get("ID","-"))

            st.write("### 志望動機")
            st.write(row.get("志望動機","（未記入）"))

            st.write("### メモ")
            st.write(row.get("メモ","（未記入）"))

            st.write("### Gemini取得企業情報")
            details = _get_company_details(row["企業名"], row.get("URL"))
            st.info(details)

            # --- 編集欄 ---
            st.write("### 編集")
            new_status = st.selectbox("選考状況を変更", ["エントリー","説明会","一次選考","二次選考","最終選考","内定","辞退"],
                                      index=["エントリー","説明会","一次選考","二次選考","最終選考","内定","辞退"].index(row["選考状況"]),
                                      key=f"edit_status_{idx}")
            new_priority = st.selectbox("志望度を変更", ["第一志望群","第二志望群","その他"],
                                        index=["第一志望群","第二志望群","その他"].index(row["志望度"]),
                                        key=f"edit_priority_{idx}")
            new_agent = st.selectbox("エージェントを変更", [""] + agents_list,
                                     index=(agents_list.index(row["エージェント"]) if row["エージェント"] in agents_list else 0),
                                     key=f"edit_agent_{idx}")
            new_memo = st.text_area("メモを変更", value=row.get("メモ",""), key=f"edit_memo_{idx}")

            col1,col2,col3 = st.columns(3)
            with col1:
                if st.button("更新", key=f"update_{idx}"):
                    st.session_state.companies[idx]["選考状況"] = new_status
                    st.session_state.companies[idx]["志望度"] = new_priority
                    st.session_state.companies[idx]["エージェント"] = new_agent
                    st.session_state.companies[idx]["メモ"] = new_memo
                    save_json(FILE, st.session_state.companies)
                    st.success("更新しました。")
                    st.experimental_rerun()
            with col2:
                if st.button("削除", key=f"del_{idx}"):
                    st.session_state.companies.pop(idx)
                    save_json(FILE, st.session_state.companies)
                    st.warning("削除しました。")
                    st.experimental_rerun()
            with col3:
                if st.button("志望動機AI改善", key=f"motive_ai_{idx}"):
                    improved = _ai_improve_motive(row["企業名"], row.get("業界",""), row.get("志望動機",""), row.get("URL"))
                    st.info(improved)
                    st.session_state.companies[idx]["志望動機_改善案"] = improved
                    save_json(FILE, st.session_state.companies)

    # --- 一覧表示 ---
    st.subheader("一覧（主要項目のみ）")
    st.dataframe(df[["企業名","選考状況","志望度","業界"]], use_container_width=True)
