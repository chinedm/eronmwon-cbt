# main.py

import streamlit as st
import os
from utils.db import create_tables

create_tables()

st.set_page_config(page_title="Eronmwon App", layout="wide")


if st.button("🔑 Login"):
    st.switch_page("pages/0_Login.py")

if st.button("📝 Register", key="register_main"):
    st.switch_page("pages/0_Register.py")

with st.sidebar:
    if st.session_state.get("logged_in", False):
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.success("You have been logged out.")
            st.rerun()


# -------------------------------
# Sidebar Navigation (Modern)
# -------------------------------
with st.sidebar:
    st.title("📚 Eronmwon Navigation")

    if st.button("🏠 Home"):
        st.switch_page("main")

    if st.button("📖 eReading Center"):
        st.switch_page("pages/1_eReading.py")

    if st.button("🗂️ Data Center"):
        st.switch_page("pages/3_Data_Center.py")

    if st.button("📝 Assessment Center"):
        st.switch_page("pages/4_Assessment_Center.py")

    if st.button("📊 Reports Center"):
        st.switch_page("pages/5_Reports_Center.py")

    if st.button("🔧 Admin Tools"):
        st.switch_page("pages/6_Admin_Tools.py")

    if st.button("🆘 Help Center"):
        st.switch_page("pages/6_Help_Center.py")

    if st.button("📝 Register", key="register_sidebar"):
        st.switch_page("pages/0_Register.py")
        

# -------------------------------
# Main Page Content
# -------------------------------
st.markdown("<h1 style='text-align: center; color: #4B8BBE;'>Welcome to Eronmwon</h1>", unsafe_allow_html=True)

if os.path.exists("static/media/intro.mp4"):
    st.video("static/media/intro.mp4")
else:
    st.warning("Intro video not found.")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚀 Proceed to eReading Center", key="proceed_button"):
        st.switch_page("pages/1_eReading.py")
