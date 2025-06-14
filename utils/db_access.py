import sqlite3
import streamlit as st

@st.cache_resource
def connect_sqlite():
    try:
        conn = sqlite3.connect("eronmwon.db", check_same_thread=False)
        conn.row_factory = sqlite3.Row  # enable dict-like access
        return conn
    except Exception as e:
        st.error(f"SQLite connection failed: {e}")
        return None
