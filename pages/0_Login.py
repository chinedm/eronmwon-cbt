import streamlit as st
from utils.db import get_connection

st.title("🔐 Login")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submit = st.form_submit_button("Login")

    if submit:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            st.session_state.logged_in = True
            st.session_state.user = {
                "id": user[0],
                "username": user[1],
                "full_name": user[3],
                "is_admin": user[7]
            }
            st.success(f"Welcome, {user[3]}!")
            st.rerun()
        else:
            st.error("Invalid username or password.")