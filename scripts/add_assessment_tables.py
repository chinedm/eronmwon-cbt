import sqlite3

conn = sqlite3.connect("eronmwon.db")
cursor = conn.cursor()

# Assignments table
cursor.execute("""
CREATE TABLE IF NOT EXISTS assignments (
    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id TEXT,
    owner_id TEXT,
    title TEXT,
    description TEXT,
    assignment_type TEXT,
    duration_minutes INTEGER,
    created_on TEXT
)
""")

# Questions table
cursor.execute("""
CREATE TABLE IF NOT EXISTS assignmentqa (
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    assignment_id INTEGER,
    question_type TEXT,
    question_text TEXT,
    option_a TEXT,
    option_b TEXT,
    option_c TEXT,
    option_d TEXT,
    correct_answer TEXT,
    marks_allocated INTEGER
)
""")

# Results table
cursor.execute("""
CREATE TABLE IF NOT EXISTS results (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    assignment_id INTEGER,
    user_id TEXT,
    submitted_on TEXT,
    total_score INTEGER
)
""")

# Add a sample assignment
cursor.execute("""
INSERT INTO assignments (subject_id, owner_id, title, description, assignment_type, duration_minutes, created_on)
VALUES ('MTH101', 'admin001', 'Intro to Algebra Quiz', 'Test your basic algebra skills', 'Single Selection Objective', 10, '2025-01-01')
""")

# Add sample questions
assignment_id = cursor.lastrowid
sample_questions = [
    (assignment_id, 'Single Selection Objective', 'What is 2 + 2?', '3', '4', '5', '6', 'B', 5),
    (assignment_id, 'Single Selection Objective', 'What is x if x + 3 = 5?', '1', '2', '3', '4', 'B', 5)
]

cursor.executemany("""
INSERT INTO assignmentqa (assignment_id, question_type, question_text, option_a, option_b, option_c, option_d, correct_answer, marks_allocated)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", sample_questions)

conn.commit()
conn.close()
print("✅ Assessment tables and sample data added.")
