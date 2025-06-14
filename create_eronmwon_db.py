import sqlite3

conn = sqlite3.connect("eronmwon.db")
cursor = conn.cursor()

# Drop old tables to avoid schema conflicts
cursor.execute("DROP TABLE IF EXISTS eReader")
cursor.execute("DROP TABLE IF EXISTS subjects")

# Create subjects table (match utils/db.py)
cursor.execute("""
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    description TEXT
)
""")

# Create eReader table (subject_id is INTEGER, FK to subjects.id)
cursor.execute("""
CREATE TABLE IF NOT EXISTS eReader (
    ereader_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER,
    owner_id TEXT,
    topic_no INTEGER,
    topic TEXT,
    content TEXT,
    graphics TEXT,
    video TEXT,
    audio TEXT,
    created_on TEXT,
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
)
""")

# Insert sample subject
cursor.execute("""
INSERT INTO subjects (name, description)
VALUES ('Mathematics 101', 'Basic Mathematics')
""")

# Get the subject id for the inserted subject
cursor.execute("SELECT id FROM subjects WHERE name='Mathematics 101'")
subject_id = cursor.fetchone()[0]

# Insert sample topic
cursor.execute("""
INSERT INTO eReader (subject_id, owner_id, topic_no, topic, content, graphics, video, audio, created_on)
VALUES (?, 'admin001', 1, 'Introduction to Algebra',
'This is an introduction to algebra...', 'algebra.png', 'algebra.mp4', 'algebra.mp3', '2025-01-01')
""", (subject_id,))

conn.commit()
conn.close()
print("SQLite database created with sample data.")