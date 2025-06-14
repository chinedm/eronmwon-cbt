import streamlit as st
from utils.db import get_connection

st.title("User Registration")

with st.form("register_form"):
    full_name = st.text_input("Full Name")
    email = st.text_input("Email")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    user_class = st.text_input("Class")
    is_admin = st.checkbox("Register as Admin")
    submit = st.form_submit_button("Register")

    if submit:
        conn = get_connection()
        c = conn.cursor()
        try:
            c.execute(
                "INSERT INTO users (username, password, full_name, email, gender, class, is_admin) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (username, password, full_name, email, gender, user_class, int(is_admin))
            )
            conn.commit()
            st.success("Registration successful! You can now log in.")
        except Exception as e:
            st.error(f"Registration failed: {e}")
        conn.close()