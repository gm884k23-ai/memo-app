import csv
import os
import uuid
from datetime import datetime

import streamlit as st

CSV_PATH = os.path.join(os.path.dirname(__file__), "memos.csv")
FIELDNAMES = ["id", "日時", "メモ", "owner"]

st.set_page_config(page_title="メモ保存アプリ", page_icon="📝", layout="centered")


def load_memos():
    if not os.path.exists(CSV_PATH):
        return []
    with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader if (row.get("メモ") or "").strip()]
    changed = False
    for row in rows:
        if not row.get("id"):
            row["id"] = uuid.uuid4().hex
            changed = True
        if row.get("owner") is None:
            row["owner"] = ""
            changed = True
    if changed:
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
    st.title("📝 メモ保存アプリ")
    st.caption("クロードコード部メンバー専用です。ログインしてください。")
    with st.form("login_form"):
        username = st.text_input("ユーザー名")
        password = st.text_input("パスワード", type="password")
        submitted = st.form_submit_button("ログイン", use_container_width=True)
    if submitted:
        if not username.strip() or not password:
            st.warning("ユーザー名とパスワードを入力してください")
        else:
            users = st.secrets.get("users", {})
            if users.get(username) == password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("ユーザー名またはパスワードが違います")
    return False


if not check_password():
    st.stop()

username = st.session_state.username

with st.sidebar:
    st.subheader("📝 メモ保存アプリ")
    st.write(f"ログイン中: **{username}**")
    if st.button("ログアウト", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()

st.title("📝 メモ保存アプリ")

memo = st.text_area("メモ", placeholder="ここにメモを入力…")

if st.button("保存", type="primary", use_container_width=True):
    if memo.strip():
        memos = load_memos()
        memos.append({
            "id": uuid.uuid4().hex,
            "日時": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "メモ": memo,
            "owner": username,
        })
        save_memos(memos)
        st.success("保存しました")
        st.rerun()
    else:
        st.warning("メモを入力してください")

st.divider()

if "editing_id" not in st.session_state:
    st.session_state.editing_id = None
if "confirm_delete_id" not in st.session_state:
    st.session_state.confirm_delete_id = None

all_memos = load_memos()
my_memos = [m for m in all_memos if m.get("owner") == username]

st.subheader(f"一覧({len(my_memos)}件)")

if not my_memos:
    st.info("まだメモがありません。上のフォームから最初のメモを保存してみましょう。")
else:
    for m in reversed(my_memos):
        mid = m["id"]
        with st.container(border=True):
            if st.session_state.editing_id == mid:
                new_text = st.text_area("メモを編集", value=m.get("メモ", ""), key=f"edit_{mid}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("保存し直す", key=f"save_{mid}", type="primary", use_container_width=True):
                        if not new_text.strip():
                            st.warning("メモを入力してください")
                        else:
                            for row in all_memos:
                                if row["id"] == mid:
                                    row["メモ"] = new_text
                            save_memos(all_memos)
                            st.session_state.editing_id = None
                            st.rerun()
                with col2:
                    if st.button("キャンセル", key=f"cancel_{mid}", use_container_width=True):
                        st.session_state.editing_id = None
                        st.rerun()
            elif st.session_state.confirm_delete_id == mid:
                st.write(m.get("メモ", ""))
                st.warning("このメモを削除します。元に戻せません。よろしいですか?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("削除する", key=f"confirm_{mid}", type="primary", use_container_width=True):
                        all_memos = [row for row in all_memos if row["id"] != mid]
                        save_memos(all_memos)
                        st.session_state.confirm_delete_id = None
                        st.rerun()
                with col2:
                    if st.button("キャンセル", key=f"cancelconfirm_{mid}", use_container_width=True):
                        st.session_state.confirm_delete_id = None
                        st.rerun()
            else:
                st.caption(m.get("日時", ""))
                st.write(m.get("メモ", ""))
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✏️ 編集", key=f"editbtn_{mid}", use_container_width=True):
                        st.session_state.editing_id = mid
                        st.rerun()
                with col2:
                    if st.button("🗑️ 削除", key=f"delbtn_{mid}", use_container_width=True):
                        st.session_state.confirm_delete_id = mid
                        st.rerun()
