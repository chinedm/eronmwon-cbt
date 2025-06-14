# pages/4_Assessment_Center.py

import streamlit as st
from utils.db_access import connect_sqlite
import datetime
import time

st.set_page_config(page_title="Assessment Center", layout="wide")
st.title("📝 Assessment Center")

conn = connect_sqlite()
cursor = conn.cursor()

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to access this page.")
    st.stop()
    
# Fetch all assignments
cursor.execute("SELECT * FROM assignments")
assignments = cursor.fetchall()

if not assignments:
    st.warning("No assignments found.")
    st.stop()

# Assignment selection
titles = {a['title']: a['assignment_id'] for a in assignments}
selected_title = st.selectbox("Select an Assignment", list(titles.keys()))

if selected_title:
    assignment_id = titles[selected_title]
    st.session_state['assignment_id'] = assignment_id

    # Load assignment duration
    cursor.execute("SELECT duration_minutes FROM assignments WHERE assignment_id = ?", (assignment_id,))
    duration_minutes = cursor.fetchone()['duration_minutes']

    # Initialize timer
    if 'start_time' not in st.session_state:
        st.session_state.start_time = time.time()
    remaining = duration_minutes * 60 - (time.time() - st.session_state.start_time)

    if remaining <= 0:
        st.warning("⏰ Time's up! Auto-submitting your answers...")
        st.session_state.auto_submit = True
        remaining = 0

    # Display timer
    mins, secs = divmod(int(remaining), 60)
    st.info(f"⏳ Time left: {mins:02d}:{secs:02d}")

    # Load questions
    cursor.execute("SELECT * FROM assignmentqa WHERE assignment_id = ?", (assignment_id,))
    questions = cursor.fetchall()

    if 'q_index' not in st.session_state:
        st.session_state.q_index = 0
        st.session_state.answers = {}
        st.session_state.auto_submit = False

    question = questions[st.session_state.q_index]
    st.markdown(f"**Question {st.session_state.q_index + 1}:** {question['question_text']}")

    qid = question['question_id']
    qtype = question['question_type']

    # Render input based on question type
    if qtype == 'Single Selection Objective':
        options = {
            'A': question['option_a'],
            'B': question['option_b'],
            'C': question['option_c'],
            'D': question['option_d']
        }
        selected = st.radio("Choose an answer:", options.items(), 
                            format_func=lambda x: f"{x[0]}. {x[1]}",
                            key=f"mcq_{qid}")
        st.session_state.answers[qid] = selected[0]

    elif qtype == 'True/False':
        selected = st.radio("Choose:", ['True', 'False'], key=f"tf_{qid}")
        st.session_state.answers[qid] = selected

    elif qtype == 'Yes/No':
        selected = st.radio("Choose:", ['Yes', 'No'], key=f"yn_{qid}")
        st.session_state.answers[qid] = selected

    elif qtype == 'Fill in the gap':
        answer = st.text_input("Your Answer:", key=f"fib_{qid}")
        st.session_state.answers[qid] = answer.strip()

    elif qtype == 'Theory':
        answer = st.text_area("Your Answer:", key=f"essay_{qid}")
        st.session_state.answers[qid] = answer.strip()

    # Navigation buttons
    col1, col2 = st.columns(2)
    if col1.button("⬅️ Previous", disabled=st.session_state.q_index == 0):
        st.session_state.q_index -= 1
        st.rerun()

    if col2.button("➡️ Next", disabled=st.session_state.q_index == len(questions) - 1):
        st.session_state.q_index += 1
        st.rerun()

    # Submission logic
    if (st.session_state.q_index == len(questions) - 1 and
       (st.button("✅ Submit Answers") or st.session_state.auto_submit)):

        total_score = 0
        for q in questions:
            qid = q['question_id']
            correct = q['correct_answer']
            user_ans = st.session_state.answers.get(qid, "").strip()

            if q['question_type'] == 'Single Selection Objective' and user_ans == correct:
                total_score += q['marks_allocated']
            elif q['question_type'] in ['True/False', 'Yes/No'] and user_ans.lower() == correct.lower():
                total_score += q['marks_allocated']
            elif q['question_type'] == 'Fill in the gap' and user_ans.lower() == correct.lower():
                total_score += q['marks_allocated']
            # Theory is not auto-graded

        max_score = sum(q['marks_allocated'] for q in questions if q['question_type'] != 'Theory')

        # Save result
        cursor.execute("""
            INSERT INTO results (assignment_id, user_id, submitted_on, total_score)
            VALUES (?, ?, ?, ?)
        """, (assignment_id, "student001", datetime.datetime.now().isoformat(), total_score))
        conn.commit()

        st.success(f"🎉 You scored {total_score} out of {max_score}!")

        # Reset session state
        st.session_state.q_index = 0
        st.session_state.answers = {}
        st.session_state.auto_submit = False
        st.session_state.start_time = None
