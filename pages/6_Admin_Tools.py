import streamlit as st
from utils.db import get_connection

st.set_page_config(page_title="Admin Tools", layout="wide")
st.title("🛠️ Admin Tools")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to access this page.")
    st.stop()

if not st.session_state.user or not st.session_state.user.get("is_admin"):
    st.warning("You must be an admin to access this page.")
    st.stop()

st.header("Add New Subject")
with st.form("add_subject_form"):
    subject_name = st.text_input("Subject Name")
    subject_desc = st.text_area("Description")
    submit = st.form_submit_button("Add Subject")
    if submit:
        conn = get_connection()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO subjects (name, description) VALUES (?, ?)", (subject_name, subject_desc))
            conn.commit()
            st.success("Subject added successfully!")
        except Exception as e:
            st.error(f"Failed to add subject: {e}")
        conn.close()