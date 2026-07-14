import streamlit as st
import datetime
import pandas as pd
from utils.database import get_all_students, add_student, update_student, delete_student
from utils.helpers import load_custom_css, is_valid_email, render_card

# Load styles
load_custom_css()

# Render success notification if stored in session state
if "student_success_message" in st.session_state:
    st.success(st.session_state.student_success_message)
    del st.session_state.student_success_message

st.markdown("<h1>👥 Student Management</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748B;'>Search, add, update, and manage student enrollment records.</p>", unsafe_allow_html=True)

# Check user role for authorization
user_role = st.session_state.user.get("role") if st.session_state.user else "Student"
is_privileged = user_role in ["Admin", "Faculty"]

# Prepare tab list based on permissions
if is_privileged:
    tab_list = ["🔍 Student Directory", "➕ Add Student", "✏️ Edit / Delete Student"]
else:
    tab_list = ["🔍 Student Directory"]

tabs = st.tabs(tab_list)

students = get_all_students()

# ----------------------------------------------------
# TAB 1: STUDENT DIRECTORY
# ----------------------------------------------------
with tabs[0]:
    st.markdown("### Campus Student Directory")
    
    if not students:
        st.info("No student records found in the system.")
    else:
        # Search & Filter Controls
        col_search, col_dept, col_year = st.columns([2, 1, 1])
        
        with col_search:
            search_query = st.text_input("Search Students", placeholder="Type Name, Email, or Student ID...")
            
        with col_dept:
            depts = ["All Departments"] + list(sorted(list(set(s.get("department") for s in students))))
            selected_dept = st.selectbox("Filter by Department", depts)
            
        with col_year:
            years = ["All Years", "1st Year", "2nd Year", "3rd Year", "4th Year"]
            selected_year = st.selectbox("Filter by Year", years)
            
        # Filter logic
        filtered_students = students
        
        if search_query.strip():
            q = search_query.lower().strip()
            filtered_students = [
                s for s in filtered_students
                if q in s.get("name").lower() or q in s.get("email").lower() or q in s.get("id").lower()
            ]
            
        if selected_dept != "All Departments":
            filtered_students = [s for s in filtered_students if s.get("department") == selected_dept]
            
        if selected_year != "All Years":
            filtered_students = [s for s in filtered_students if s.get("year") == selected_year]
            
        # Display student list
        if not filtered_students:
            st.warning("No students matched your search criteria.")
        else:
            df = pd.DataFrame(filtered_students)
            # Reorder for display
            df_display = df[["id", "name", "email", "department", "year", "phone", "enrollment_date"]].copy()
            df_display.columns = ["Student ID", "Full Name", "Email", "Department", "Academic Year", "Phone", "Enrollment Date"]
            
            # Interactive selection
            st.dataframe(df_display, hide_index=True, use_container_width=True)
            
            st.markdown("#### 👤 Student Profile Viewer")
            selected_id = st.selectbox("Select a Student to view detailed profile:", [s.get("id") for s in filtered_students])
            
            profile = next((s for s in filtered_students if s.get("id") == selected_id), None)
            if profile:
                col_pic, col_details = st.columns([1, 3])
                with col_pic:
                    st.markdown(
                        f"""
                        <div style="
                            background-color: #E2E8F0;
                            border-radius: 50%;
                            width: 120px;
                            height: 120px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 3rem;
                            color: #475569;
                            border: 3px solid #2563EB;
                        ">
                            👨‍🎓
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with col_details:
                    details_html = f"""
                    <table style="width: 100%; font-size: 0.95rem;">
                        <tr><td style="font-weight: 600; width: 30%; color: #64748B;">Student ID:</td><td style="color:#1E293B; font-weight:700;">{profile.get('id')}</td></tr>
                        <tr><td style="font-weight: 600; color: #64748B;">Full Name:</td><td style="color:#1E293B;">{profile.get('name')}</td></tr>
                        <tr><td style="font-weight: 600; color: #64748B;">Email Address:</td><td style="color:#1E293B;">{profile.get('email')}</td></tr>
                        <tr><td style="font-weight: 600; color: #64748B;">Department:</td><td style="color:#1E293B;">{profile.get('department')}</td></tr>
                        <tr><td style="font-weight: 600; color: #64748B;">Academic Year:</td><td style="color:#2563EB; font-weight:600;">{profile.get('year')}</td></tr>
                        <tr><td style="font-weight: 600; color: #64748B;">Phone:</td><td style="color:#1E293B;">{profile.get('phone')}</td></tr>
                        <tr><td style="font-weight: 600; color: #64748B;">Enrollment Date:</td><td style="color:#1E293B;">{profile.get('enrollment_date')}</td></tr>
                    </table>
                    """
                    render_card(f"{profile.get('name')}'s Academic Profile", details_html)

# ----------------------------------------------------
# TAB 2: ADD STUDENT (ADMIN / FACULTY ONLY)
# ----------------------------------------------------
if is_privileged:
    with tabs[1]:
        st.markdown("### Add New Student to Campus Roll")
        
        # Calculate Next Student ID
        if students:
            ids = [int(s.get("id")[1:]) for s in students if s.get("id").startswith("S") and s.get("id")[1:].isdigit()]
            next_id = f"S{max(ids) + 1}" if ids else "S1001"
        else:
            next_id = "S1001"
            
        with st.form("add_student_form"):
            col_id, col_name = st.columns([1, 3])
            with col_id:
                st.text_input("Generated ID", value=next_id, disabled=True)
            with col_name:
                name = st.text_input("Full Name", placeholder="Jane Doe")
                
            email = st.text_input("Email Address", placeholder="jane.doe@campus.edu")
            
            col_dep, col_yr = st.columns(2)
            with col_dep:
                department = st.selectbox("Department", ["Computer Science", "Electrical Engineering", "Mechanical Engineering", "Civil Engineering", "Business Administration", "Chemistry", "Physics"])
            with col_yr:
                year = st.selectbox("Academic Year", ["1st Year", "2nd Year", "3rd Year", "4th Year"])
                
            col_phone, col_date = st.columns(2)
            with col_phone:
                phone = st.text_input("Phone Number", placeholder="+1 (555) 000-0000")
            with col_date:
                enrollment_date = st.date_input("Enrollment Date", value=datetime.date.today())
                
            submit_add = st.form_submit_button("Enroll Student")
            
            if submit_add:
                if not name.strip() or not email.strip() or not phone.strip():
                    st.error("Please fill in Name, Email, and Phone number.")
                elif not is_valid_email(email):
                    st.error("Please provide a valid email format.")
                # Check duplicate email in students json
                elif any(s.get("email").lower() == email.strip().lower() for s in students):
                    st.error("A student with this email address is already enrolled.")
                else:
                    new_student = {
                        "id": next_id,
                        "name": name.strip(),
                        "email": email.strip().lower(),
                        "department": department,
                        "year": year,
                        "phone": phone.strip(),
                        "enrollment_date": enrollment_date.strftime("%Y-%m-%d")
                    }
                    if add_student(new_student):
                        st.session_state.student_success_message = f"🎉 Success! Enrolled {name} with ID: {next_id}."
                        st.rerun()
                    else:
                        st.error("Error writing database. Please try again.")

# ----------------------------------------------------
# TAB 3: EDIT / DELETE STUDENT (ADMIN / FACULTY ONLY)
# ----------------------------------------------------
if is_privileged:
    with tabs[2]:
        st.markdown("### Update / Delete Student Records")
        
        if not students:
            st.info("No students enrolled yet.")
        else:
            selected_edit_id = st.selectbox("Select Student to Modify/Delete:", [f"{s.get('id')} - {s.get('name')}" for s in students])
            
            # Extract ID
            target_id = selected_edit_id.split(" - ")[0]
            student_to_edit = next((s for s in students if s.get("id") == target_id), None)
            
            if student_to_edit:
                st.markdown(f"**Modifying Student ID: {student_to_edit.get('id')}**")
                
                with st.form("edit_student_form"):
                    edit_name = st.text_input("Full Name", value=student_to_edit.get("name"))
                    edit_email = st.text_input("Email Address", value=student_to_edit.get("email"))
                    
                    col_edep, col_eyr = st.columns(2)
                    with col_edep:
                        # Find index
                        depts_list = ["Computer Science", "Electrical Engineering", "Mechanical Engineering", "Civil Engineering", "Business Administration", "Chemistry", "Physics"]
                        dept_idx = depts_list.index(student_to_edit.get("department")) if student_to_edit.get("department") in depts_list else 0
                        edit_dept = st.selectbox("Department", depts_list, index=dept_idx)
                    with col_eyr:
                        yrs_list = ["1st Year", "2nd Year", "3rd Year", "4th Year"]
                        yr_idx = yrs_list.index(student_to_edit.get("year")) if student_to_edit.get("year") in yrs_list else 0
                        edit_year = st.selectbox("Academic Year", yrs_list, index=yr_idx)
                        
                    edit_phone = st.text_input("Phone Number", value=student_to_edit.get("phone"))
                    
                    submit_edit = st.form_submit_button("Update Student Record")
                    
                    if submit_edit:
                        if not edit_name.strip() or not edit_email.strip() or not edit_phone.strip():
                            st.error("Please fill in Name, Email, and Phone number.")
                        elif not is_valid_email(edit_email):
                            st.error("Please provide a valid email format.")
                        # Check duplicate email excluding current student
                        elif any(s.get("email").lower() == edit_email.strip().lower() and s.get("id") != target_id for s in students):
                            st.error("A student with this email address is already enrolled.")
                        else:
                            updated_data = {
                                "name": edit_name.strip(),
                                "email": edit_email.strip().lower(),
                                "department": edit_dept,
                                "year": edit_year,
                                "phone": edit_phone.strip()
                            }
                            if update_student(target_id, updated_data):
                                st.session_state.student_success_message = "✅ Student details updated successfully."
                                st.rerun()
                            else:
                                st.error("Database update error. Please try again.")
                                
                # Danger Zone: Deletion
                st.markdown("---")
                st.markdown("#### ⚠️ Danger Zone")
                confirm_delete = st.checkbox(f"I confirm that I want to delete student: **{student_to_edit.get('name')}** permanently.")
                delete_btn = st.button("🔴 Permanently Delete Student")
                
                if delete_btn:
                    if confirm_delete:
                        if delete_student(target_id):
                            st.session_state.student_success_message = f"🗑️ Student {student_to_edit.get('name')} deleted permanently."
                            st.rerun()
                        else:
                            st.error("Delete operation failed.")
                    else:
                        st.error("Please check the confirmation box to delete.")
