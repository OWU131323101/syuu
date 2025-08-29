import streamlit as st
import pandas as pd
from .utils import load_json

def show():
    st.title("カレンダー")
    data = load_json("job_data.json", [])
    if not data:
        st.info("企業データがありません。『企業まとめ』で追加してください。")
        return
    df = pd.DataFrame(data)
    if "日付" not in df or df["日付"].isna().all():
        st.info("イベント日付が登録されていません。")
        return

    df["日付"] = pd.to_datetime(df["日付"], errors="coerce")
    df = df.dropna(subset=["日付"]).sort_values("日付")
    st.subheader("直近イベント一覧")
    for _, r in df.iterrows():
        st.write(f"🗓️ {r['日付'].date()}：**{r['企業名']}** - {r.get('直近イベント','')}")
    st.caption("※ 簡易表示（必要に応じて本格カレンダーへ拡張可能）")
