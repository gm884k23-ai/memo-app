import csv
import os
import uuid
from datetime import datetime

import streamlit as st

CSV_PATH = os.path.join(os.path.dirname(__file__), "memos.csv")
FIELDNAMES = ["id", "日時", "メモ"]


def load_memos():
    if not os.path.exists(CSV_PATH):
        return []
    with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        needs_migration = rows and "id" not in (reader.fieldnames or [])
    if needs_migration:
        for row in rows:
            row["id"] = uuid.uuid4().hex
        save_memos(rows)
    return rows


def save_memos(memos):
    with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(memos)


def check_password():
    if st.session_state.get("authenticated"):
        return True
    st.title("ログイン")
    password = st.text_input("パスワード", type="password")
    if st.button("ログイン"):
        if password == st.secrets.get("password", ""):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("パスワードが違います")
    return False


if not check_password():
    st.stop()

st.title("メモ保存アプリ")

memo = st.text_area("メモ")

if st.button("保存"):
    if memo.strip():
        memos = load_memos()
        memos.append({
            "id": uuid.uuid4().hex,
            "日時": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "メモ": memo,
        })
        save_memos(memos)
        st.success("保存しました")
        st.rerun()
    else:
        st.warning("メモを入力してください")

st.divider()
st.subheader("一覧")

if "editing_id" not in st.session_state:
    st.session_state.editing_id = None

memos = load_memos()

if not memos:
    st.write("まだメモがありません")
else:
    for m in reversed(memos):
        mid = m["id"]
        with st.container(border=True):
            if st.session_state.editing_id == mid:
                new_text = st.text_area("メモを編集", value=m["メモ"], key=f"edit_{mid}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("保存し直す", key=f"save_{mid}"):
                        for row in memos:
                            if row["id"] == mid:
                                row["メモ"] = new_text
                        save_memos(memos)
                        st.session_state.editing_id = None
                        st.rerun()
                with col2:
                    if st.button("キャンセル", key=f"cancel_{mid}"):
                        st.session_state.editing_id = None
                        st.rerun()
            else:
                st.caption(m["日時"])
                st.write(m["メモ"])
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("編集", key=f"editbtn_{mid}"):
                        st.session_state.editing_id = mid
                        st.rerun()
                with col2:
                    if st.button("削除", key=f"delbtn_{mid}"):
                        memos = [row for row in memos if row["id"] != mid]
                        save_memos(memos)
                        st.rerun()
