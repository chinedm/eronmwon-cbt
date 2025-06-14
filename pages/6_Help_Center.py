# pages/6_Help_Center.py

import streamlit as st
import os
import shutil
import sqlite3
import datetime
import pandas as pd

st.set_page_config(page_title="Help Center", layout="wide")
st.title("\U0001F4D8 Help Center")

# ----------------------------
# FAQs Section
# ----------------------------
st.header("❓ Frequently Asked Questions")

faq_items = {
    "How do I register a new user?": "Go to the Data Center → Capture Data → Users.",
    "How do I create an assignment?": "Use the Assessment Center to define titles and add questions.",
    "How do I recover lost data?": "Use the Backup/Restore tools below to manage system state.",
    "How do I view student scores?": "Visit the Reports Center → Assignment or Student reports.",
    "Can I import from Excel?": "Yes! Go to the Data Center → Import Data."
}

for question, answer in faq_items.items():
    with st.expander(question):
        st.write(answer)

# ----------------------------
# Backup Section
# ----------------------------
st.header("\U0001F4BE Backup Database")

DB_PATH = "eronmwon.db"
BACKUP_FOLDER = "backups"

if not os.path.exists(BACKUP_FOLDER):
    os.makedirs(BACKUP_FOLDER)

backup_file = f"{BACKUP_FOLDER}/backup_{st.session_state.get('user', 'manual')}.db"
shutil.copyfile(DB_PATH, backup_file)

with open(backup_file, "rb") as f:
    st.download_button("📥 Download Backup", f, file_name=os.path.basename(backup_file))

# ----------------------------
# Restore Section
# ----------------------------
st.header("\u267B\ufe0f Restore Database")

uploaded_file = st.file_uploader("Upload a SQLite database (.db) to restore", type=["db"])

if uploaded_file and st.button("⚠️ Restore Now"):
    try:
        with open(DB_PATH, "wb") as f:
            f.write(uploaded_file.read())
        st.success("✅ Database restored. Please restart the app.")
    except Exception as e:
        st.error(f"❌ Restore failed: {e}")

# ----------------------------
# Admin Reset Tool
# ----------------------------
st.header("🔐 Admin Access Reset")

admin_id = st.text_input("Admin ID", value="admin001")
first_name = st.text_input("First Name", value="System")
last_name = st.text_input("Last Name", value="Admin")
email = st.text_input("Email", value="admin@example.com")
phone = st.text_input("Phone", value="08000000000")
institution = st.text_input("Institution", value="Default Institution")
license_key = st.text_input("License Key", value="ERON-ADMIN-RESET")

if st.button("🛠️ Reset / Recreate Admin"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE user_id = ?", (admin_id,))
    exists = cursor.fetchone()[0]

    if exists:
        cursor.execute("""
            UPDATE users
            SET first_name=?, last_name=?, email=?, phone_number=?, institution=?, license_key=?
            WHERE user_id=?
        """, (first_name, last_name, email, phone, institution, license_key, admin_id))
        msg = "✅ Admin account reset successfully."
    else:
        cursor.execute("""
            INSERT INTO users (
                user_id, first_name, last_name, email, phone_number,
                gender, date_of_birth, photo, institution, license_key, registered_on
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            admin_id, first_name, last_name, email, phone,
            "M", "1980-01-01", "", institution, license_key,
            datetime.datetime.now().isoformat()
        ))
        msg = "✅ Admin account created successfully."

    conn.commit()
    conn.close()
    st.success(msg)

# ----------------------------
# Activity Log Viewer
# ----------------------------
st.header("📜 Activity Log Viewer")

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 50")
    logs = cursor.fetchall()
    log_df = pd.DataFrame(logs, columns=["log_id", "action", "actor", "timestamp"])
    st.dataframe(log_df)
except Exception as e:
    st.error(f"Log loading failed: {e}")
