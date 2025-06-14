# pages/1_eReading.py

import streamlit as st
import os
from utils.db_access import connect_sqlite

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to access this page.")
    st.stop()

st.set_page_config(page_title="eReading Center", layout="wide")

# Sidebar for subject and topic selection
st.sidebar.title("eReading Navigation")

conn = connect_sqlite()
if not conn:
    st.stop()

cursor = conn.cursor()

# Fetch Subjects
cursor.execute("SELECT id, name FROM subjects")
subjects = cursor.fetchall()

subject_dict = {row['name']: row['id'] for row in subjects}
subject_choice = st.sidebar.selectbox("Select a Subject", list(subject_dict.keys()))

if subject_choice:
    subject_id = subject_dict[subject_choice]

    # Fetch Topics
    cursor.execute("SELECT ereader_id, topic FROM eReader WHERE subject_id = ?", (subject_id,))
    topics = cursor.fetchall()
    topic_dict = {t['topic']: t['ereader_id'] for t in topics}

    topic_choice = st.sidebar.selectbox("Select a Topic", list(topic_dict.keys()))

    if topic_choice:
        ereader_id = topic_dict[topic_choice]
        cursor.execute("SELECT * FROM eReader WHERE ereader_id = ?", (ereader_id,))
        topic = cursor.fetchone()

        st.markdown(f"## {topic['topic']}")
        st.markdown(topic['content'], unsafe_allow_html=True)

        # Show media (with existence checks)
        col1, col2, col3 = st.columns([1,1,1])

        # GRAPHICS (image)
        if topic['graphics']:
            image_file = topic['graphics'].strip()
            image_path = os.path.join("static", "media", image_file)
            if os.path.exists(image_path):
                col1.image(image_path, caption="Graphics", use_column_width=True)
            else:
                col1.warning(f"Image not found: {image_file}")

        # AUDIO
        if topic['audio']:
            audio_file = topic['audio'].strip()
            audio_path = os.path.join("static", "media", audio_file)
            if os.path.exists(audio_path):
                col2.audio(audio_path)
            else:
                col2.warning(f"Audio not found: {audio_file}")

        # VIDEO
        if topic['video']:
            video_file = topic['video'].strip()
            video_path = os.path.join("static", "media", video_file)
            if os.path.exists(video_path):
                col3.video(video_path)
            else:
                col3.warning(f"Video not found: {video_file}")
