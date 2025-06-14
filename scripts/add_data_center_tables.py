# pages/3_Data_Center.py

import streamlit as st
import sqlite3
from utils.db_access import connect_sqlite
import datetime

st.set_page_config(page_title="Data Center", layout="wide")
st.title("🗃️ Data Center: Capture, Edit, and Manage Data")

conn = connect_sqlite()
cursor = conn.cursor()

menu = st.sidebar.radio("Choose Table", ["Subjects", "Users"])

# -----------------------------
# SUBJECTS FORM
# -----------------------------
if menu == "Subjects":
    st.subheader("📚 Add New Subject")

    subject_id = st.text_input("Subject ID (e.g., MTH101)")
    subject_title = st.text_input("Subject Title")
    owner_id = st.text_input("Owner ID (e.g., admin001)", value="admin001")

    if st.button("➕ Add Subject"):
        if subject_id and subject_title:
            cursor.execute("""
                INSERT INTO subjects (subject_id, owner_id, subject_title, created_on)
                VALUES (?, ?, ?, ?)
            """, (subject_id, owner_id, subject_title, datetime.datetime.now().isoformat()))
            conn.commit()
            st.success(f"✅ Subject '{subject_title}' added successfully.")
            st.rerun()
        else:
            st.error("Subject ID and Title are required.")

    # Show and manage existing subjects
    st.markdown("### 📋 Manage Subjects")
    cursor.execute("SELECT * FROM subjects")
    subjects = cursor.fetchall()

    for sub in subjects:
        with st.expander(f"📘 {sub['subject_id']} – {sub['subject_title']}"):
            new_title = st.text_input(f"Edit Title for {sub['subject_id']}", sub['subject_title'], key=f"edit_title_{sub['subject_id']}")
            new_owner = st.text_input(f"Edit Owner ID", sub['owner_id'], key=f"edit_owner_{sub['subject_id']}")

            col1, col2 = st.columns(2)
            if col1.button("✏️ Update", key=f"update_subject_{sub['subject_id']}"):
                cursor.execute("""
                    UPDATE subjects
                    SET subject_title = ?, owner_id = ?
                    WHERE subject_id = ?
                """, (new_title, new_owner, sub['subject_id']))
                conn.commit()
                st.success(f"✅ Subject '{sub['subject_id']}' updated.")
                st.rerun()

            if col2.button("🗑️ Delete", key=f"delete_subject_{sub['subject_id']}"):
                cursor.execute("DELETE FROM subjects WHERE subject_id = ?", (sub['subject_id'],))
                conn.commit()
                st.warning(f"❌ Subject '{sub['subject_id']}' deleted.")
                st.rerun()

# -----------------------------
# USERS FORM
# -----------------------------
elif menu == "Users":
    st.subheader("👤 Register New User")

    user_id = st.text_input("User ID")
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    gender = st.selectbox("Gender", ["M", "F"])
    dob = st.date_input("Date of Birth")
    institution = st.text_input("Institution")
    license_key = st.text_input("License Key")
    photo_path = st.text_input("Photo Path (optional)")
    registered_on = datetime.datetime.now().isoformat()

    if st.button("➕ Register User"):
        if user_id and first_name and last_name:
            cursor.execute("""
                INSERT INTO users (
                    user_id, first_name, last_name, email, phone_number,
                    gender, date_of_birth, photo, institution, license_key, registered_on
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, first_name, last_name, email, phone,
                gender, dob.isoformat(), photo_path, institution, license_key, registered_on
            ))
            conn.commit()
            st.success(f"✅ User '{first_name} {last_name}' registered successfully.")
            st.rerun()
        else:
            st.error("User ID, First Name, and Last Name are required.")

    # Show and manage existing users
    st.markdown("### 👥 Manage Users")
    cursor.execute("SELECT * FROM users ORDER BY registered_on DESC LIMIT 10")
    users = cursor.fetchall()

    for u in users:
        with st.expander(f"{u['user_id']}: {u['first_name']} {u['last_name']}"):
            new_first = st.text_input("First Name", u['first_name'], key=f"ufn_{u['user_id']}")
            new_last = st.text_input("Last Name", u['last_name'], key=f"uln_{u['user_id']}")
            new_email = st.text_input("Email", u['email'], key=f"uem_{u['user_id']}")
            new_phone = st.text_input("Phone", u['phone_number'], key=f"uph_{u['user_id']}")
            new_inst = st.text_input("Institution", u['institution'], key=f"uin_{u['user_id']}")
            new_license = st.text_input("License Key", u['license_key'], key=f"ulk_{u['user_id']}")

            col1, col2 = st.columns(2)
            if col1.button("✏️ Update", key=f"update_user_{u['user_id']}"):
                cursor.execute("""
                    UPDATE users
                    SET first_name = ?, last_name = ?, email = ?, phone_number = ?, institution = ?, license_key = ?
                    WHERE user_id = ?
                """, (new_first, new_last, new_email, new_phone, new_inst, new_license, u['user_id']))
                conn.commit()
                st.success("✅ User updated.")
                st.rerun()

            if col2.button("🗑️ Delete", key=f"delete_user_{u['user_id']}"):
                cursor.execute("DELETE FROM users WHERE user_id = ?", (u['user_id'],))
                conn.commit()
                st.warning("❌ User deleted.")
                st.rerun()
