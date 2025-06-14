# pages/5_Reports_Center.py

import streamlit as st
import pandas as pd
import sqlite3
from utils.db_access import connect_sqlite
from fpdf import FPDF
import datetime
import plotly.express as px

st.set_page_config(page_title="Reports Center", layout="wide")
st.title("\U0001F4CA Reports Center: Assignment Results")

conn = connect_sqlite()
cursor = conn.cursor()

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to access this page.")
    st.stop()

# ----------------------------
# Filter: Assignment Selection
# ----------------------------
cursor.execute("SELECT DISTINCT a.assignment_id, a.title FROM assignments a")
assignments = cursor.fetchall()

if not assignments:
    st.warning("No assignments found.")
    st.stop()

assignment_options = {a["title"]: a["assignment_id"] for a in assignments}
selected_title = st.selectbox("Select Assignment", list(assignment_options.keys()))

if selected_title:
    assignment_id = assignment_options[selected_title]

    cursor.execute("""
        SELECT r.user_id, u.first_name || ' ' || u.last_name AS student_name,
               r.total_score, r.submitted_on
        FROM results r
        LEFT JOIN users u ON r.user_id = u.user_id
        WHERE r.assignment_id = ?
    """, (assignment_id,))

    records = cursor.fetchall()
    if not records:
        st.warning("No result records for this assignment.")
        st.stop()

    df = pd.DataFrame(records, columns=["user_id", "student_name", "total_score", "submitted_on"])
    st.dataframe(df)

    # Summary Stats
    st.markdown("### \U0001F4C8 Summary")
    st.write(f"Total Students: {len(df)}")
    st.write(f"Average Score: {df['total_score'].mean():.2f}")
    st.write(f"Highest Score: {df['total_score'].max()}")
    st.write(f"Lowest Score: {df['total_score'].min()}")

    # Export Options
    st.markdown("### \U0001F4C4 Export Report")
    col1, col2 = st.columns(2)
    if col1.button("⬇️ Download as Excel"):
        excel_file = f"{selected_title}_results.xlsx"
        df.to_excel(excel_file, index=False)
        with open(excel_file, "rb") as f:
            st.download_button("📥 Click to Download Excel", f, file_name=excel_file)

    if col2.button("⬇️ Download as PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        col_width = pdf.w / (len(df.columns) + 1)

        for col in df.columns:
            pdf.cell(col_width, 10, txt=str(col), border=1)
        pdf.ln()

        for _, row in df.iterrows():
            for val in row:
                pdf.cell(col_width, 10, txt=str(val), border=1)
            pdf.ln()

        file = f"{selected_title}_results.pdf"
        pdf.output(file)
        with open(file, "rb") as f:
            st.download_button("📥 Click to Download PDF", f, file_name=file)

    # Interactive Charts
    st.markdown("## \U0001F4C8 Interactive Charts")

    # Bar chart: Student Scores
    bar_fig = px.bar(df, x='user_id', y='total_score', title='Scores by Student',
                     hover_data=['student_name'], labels={'user_id': 'Student ID', 'total_score': 'Score'})
    st.plotly_chart(bar_fig, use_container_width=True)

    # Pie chart: Performance Distribution
    df['performance'] = pd.cut(df['total_score'],
                               bins=[0, 39, 59, 69, 100],
                               labels=['Fail', 'Pass', 'Merit', 'Distinction'])
    pie_fig = px.pie(df, names='performance', title='Performance Distribution',
                     color_discrete_sequence=px.colors.qualitative.Set3)
    st.plotly_chart(pie_fig, use_container_width=True)

    # Line chart: Scores Over Time
    df['submitted_on'] = pd.to_datetime(df['submitted_on'])
    line_fig = px.line(df.sort_values('submitted_on'), x='submitted_on', y='total_score',
                       markers=True, title='Score Trend Over Time')
    st.plotly_chart(line_fig, use_container_width=True)

# ----------------------------
# Subject-Wise Performance Summary
# ----------------------------
st.markdown("---")
st.header("\U0001F4DA Subject-Wise Performance Summary")

cursor.execute("""
    SELECT a.subject_id, s.subject_title, COUNT(r.result_id) AS student_count,
           AVG(r.total_score) AS avg_score,
           MAX(r.total_score) AS max_score,
           MIN(r.total_score) AS min_score
    FROM results r
    JOIN assignments a ON r.assignment_id = a.assignment_id
    JOIN subjects s ON a.subject_id = s.subject_id
    GROUP BY a.subject_id
""")
rows = cursor.fetchall()

if rows:
    sub_df = pd.DataFrame(rows, columns=["subject_id", "subject_title", "student_count", "avg_score", "max_score", "min_score"])
    st.dataframe(sub_df)

    col1, col2 = st.columns(2)
    if col1.button("⬇️ Download Subject Summary (Excel)"):
        file = "subject_summary.xlsx"
        sub_df.to_excel(file, index=False)
        with open(file, "rb") as f:
            st.download_button("📥 Download Excel", f, file_name=file)

    if col2.button("⬇️ Download Subject Summary (PDF)"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        col_width = pdf.w / (len(sub_df.columns) + 1)
        for col in sub_df.columns:
            pdf.cell(col_width, 10, txt=str(col), border=1)
        pdf.ln()
        for _, row in sub_df.iterrows():
            for val in row:
                pdf.cell(col_width, 10, txt=str(val), border=1)
            pdf.ln()
        file = "subject_summary.pdf"
        pdf.output(file)
        with open(file, "rb") as f:
            st.download_button("📥 Download PDF", f, file_name=file)

    st.markdown("### \U0001F4CA Subject Averages")
    bar_fig = px.bar(sub_df, x='subject_title', y='avg_score',
                     title='Average Score per Subject',
                     labels={'subject_title': 'Subject', 'avg_score': 'Avg Score'},
                     color='avg_score')
    st.plotly_chart(bar_fig, use_container_width=True)

# ----------------------------
# Student-Specific Reports
# ----------------------------
st.markdown("---")
st.header("\U0001F464 Student-Specific Reports")

cursor.execute("""
    SELECT DISTINCT r.user_id, u.first_name || ' ' || u.last_name AS full_name
    FROM results r
    LEFT JOIN users u ON r.user_id = u.user_id
""")
students = cursor.fetchall()

if students:
    student_map = {s['full_name']: s['user_id'] for s in students}
    selected_student = st.selectbox("Select Student", list(student_map.keys()))

    if selected_student:
        user_id = student_map[selected_student]
        cursor.execute("""
            SELECT a.title AS assignment_title, r.total_score, r.submitted_on
            FROM results r
            JOIN assignments a ON r.assignment_id = a.assignment_id
            WHERE r.user_id = ?
            ORDER BY r.submitted_on ASC
        """, (user_id,))
        results = cursor.fetchall()

        if results:
            student_df = pd.DataFrame(results, columns=["assignment_title", "score", "date"])
            st.dataframe(student_df)

            st.markdown("### \U0001F4C8 Performance Summary")
            st.write(f"Total Assignments: {len(student_df)}")
            st.write(f"Average Score: {student_df['score'].mean():.2f}")
            st.write(f"Best Score: {student_df['score'].max()}")
            st.write(f"Lowest Score: {student_df['score'].min()}")

            col1, col2 = st.columns(2)
            if col1.button("⬇️ Download Report (Excel)"):
                excel_file = f"{user_id}_report.xlsx"
                student_df.to_excel(excel_file, index=False)
                with open(excel_file, "rb") as f:
                    st.download_button("📥 Download Excel", f, file_name=excel_file)

            if col2.button("⬇️ Download Report (PDF)"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=10)
                pdf.cell(190, 10, txt=f"Report for {selected_student}", ln=1)
                col_width = pdf.w / (len(student_df.columns) + 1)
                for col in student_df.columns:
                    pdf.cell(col_width, 10, txt=str(col), border=1)
                pdf.ln()
                for _, row in student_df.iterrows():
                    for val in row:
                        pdf.cell(col_width, 10, txt=str(val), border=1)
                    pdf.ln()
                file = f"{user_id}_report.pdf"
                pdf.output(file)
                with open(file, "rb") as f:
                    st.download_button("📥 Download PDF", f, file_name=file)

            st.markdown("### \U0001F4CA Performance Over Time")
            student_df['date'] = pd.to_datetime(student_df['date'])
            chart = px.line(student_df, x="date", y="score", markers=True,
                            title=f"Score Trend for {selected_student}")
            st.plotly_chart(chart, use_container_width=True)
else:
    st.warning("No student results available.")
