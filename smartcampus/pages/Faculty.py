import streamlit as st
import datetime
import pandas as pd
from utils.database import get_all_faculty, add_faculty, update_faculty, delete_faculty
from utils.helpers import load_custom_css, is_valid_email, render_card

# Load styles
load_custom_css()

st.markdown("<h1>👨‍🏫 Faculty Directory</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748B;'>Search, add, update, and manage campus faculty staff.</p>", unsafe_allow_html=True)

# User Role Authorization
user_role = st.session_state.user.get("role") if st.session_state.user else "Student"
is_admin = user_role == "Admin"

# Prepare tabs
if is_admin:
    tab_list = ["🔍 Faculty Directory", "➕ Add Faculty Member", "✏️ Edit / Delete Faculty"]
else:
    tab_list = ["🔍 Faculty Directory"]

tabs = st.tabs(tab_list)
faculty_list = get_all_faculty()

# ----------------------------------------------------
# TAB 1: FACULTY DIRECTORY
# ----------------------------------------------------
with tabs[0]:
    st.markdown("### Campus Faculty Roster")
    
    if not faculty_list:
        st.info("No faculty records found in the database.")
    else:
        # Search controls
        col_search, col_dept = st.columns([2, 1])
        with col_search:
            search_query = st.text_input("Search Faculty", placeholder="Type Name, Email, ID or Designation...")
        with col_dept:
            depts = ["All Departments"] + list(sorted(list(set(f.get("department") for f in faculty_list))))
            selected_dept = st.selectbox("Department Filter", depts)
            
        filtered_faculty = faculty_list
        if search_query.strip():
            q = search_query.lower().strip()
            filtered_faculty = [
                f for f in filtered_faculty
                if q in f.get("name").lower() or q in f.get("email").lower() or q in f.get("id").lower() or q in f.get("designation").lower()
            ]
            
        if selected_dept != "All Departments":
            filtered_faculty = [f for f in filtered_faculty if f.get("department") == selected_dept]
            
        if not filtered_faculty:
            st.warning("No faculty matches your criteria.")
        else:
            df = pd.DataFrame(filtered_faculty)
            df_display = df[["id", "name", "email", "department", "designation", "phone", "joining_date"]].copy()
            df_display.columns = ["Faculty ID", "Full Name", "Email", "Department", "Designation", "Phone", "Joining Date"]
            st.dataframe(df_display, hide_index=True, use_container_width=True)
            
            # Faculty bio selector
            st.markdown("#### 👤 Faculty details")
            selected_id = st.selectbox("Select Faculty Member:", [f.get("id") for f in filtered_faculty])
            fac = next((f for f in filtered_faculty if f.get("id") == selected_id), None)
            if fac:
                col_avatar, col_bio = st.columns([1, 3])
                with col_avatar:
                    st.markdown(
                        f"""
                        <div style="
                            background-color: #F1F5F9;
                            border-radius: 50%;
                            width: 120px;
                            height: 120px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 3rem;
                            color: #0F172A;
                            border: 3px solid #14B8A6;
                        ">
                            👨‍🏫
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with col_bio:
                    details_html = f"""
                    <table style="width: 100%; font-size: 0.95rem;">
                        <tr><td style="font-weight: 600; width: 30%; color: #64748B;">Faculty ID:</td><td style="color:#1E293B; font-weight:700;">{fac.get('id')}</td></tr>
                        <tr><td style="font-weight: 600; color: #64748B;">Full Name:</td><td style="color:#1E293B;">{fac.get('name')}</td></tr>
                        <tr><td style="font-weight: 600; color: #64748B;">Email Address:</td><td style="color:#1E293B;">{fac.get('email')}</td></tr>
                        <tr><td style="font-weight: 600; color: #64748B;">Department:</td><td style="color:#1E293B;">{fac.get('department')}</td></tr>
                        <tr><td style="font-weight: 600; color: #64748B;">Designation:</td><td style="color:#14B8A6; font-weight:600;">{fac.get('designation')}</td></tr>
                        <tr><td style="font-weight: 600; color: #64748B;">Phone:</td><td style="color:#1E293B;">{fac.get('phone')}</td></tr>
                        <tr><td style="font-weight: 600; color: #64748B;">Joining Date:</td><td style="color:#1E293B;">{fac.get('joining_date')}</td></tr>
                    </table>
                    """
                    render_card(f"{fac.get('name')}'s Academic Profile", details_html)

# ----------------------------------------------------
# TAB 2: ADD FACULTY (ADMIN ONLY)
# ----------------------------------------------------
if is_admin:
    with tabs[1]:
        st.markdown("### Register New Faculty Staff Member")
        
        # Calculate Next ID
        if faculty_list:
            ids = [int(f.get("id")[1:]) for f in faculty_list if f.get("id").startswith("F") and f.get("id")[1:].isdigit()]
            next_id = f"F{max(ids) + 1}" if ids else "F1001"
        else:
            next_id = "F1001"
            
        with st.form("add_faculty_form"):
            col_fid, col_fname = st.columns([1, 3])
            with col_fid:
                st.text_input("Generated ID", value=next_id, disabled=True)
            with col_fname:
                name = st.text_input("Full Name", placeholder="Dr. John Smith")
                
            email = st.text_input("Email Address", placeholder="smith@campus.edu")
            
            col_fdep, col_fdes = st.columns(2)
            with col_fdep:
                department = st.selectbox("Department", ["Computer Science", "Electrical Engineering", "Mechanical Engineering", "Civil Engineering", "Business Administration", "Chemistry", "Physics"])
            with col_fdes:
                designation = st.selectbox("Designation", ["Professor", "Associate Professor", "Assistant Professor", "Lecturer", "Instructor"])
                
            col_fphone, col_fdate = st.columns(2)
            with col_fphone:
                phone = st.text_input("Phone Number", placeholder="+1 (555) 000-0000")
            with col_fdate:
                joining_date = st.date_input("Joining Date", value=datetime.date.today())
                
            submit_add = st.form_submit_button("Register Faculty Member")
            
            if submit_add:
                if not name.strip() or not email.strip() or not phone.strip():
                    st.error("Please fill in Name, Email, and Phone number.")
                elif not is_valid_email(email):
                    st.error("Please provide a valid email format.")
                elif any(f.get("email").lower() == email.strip().lower() for f in faculty_list):
                    st.error("A faculty member with this email is already registered.")
                else:
                    new_fac = {
                        "id": next_id,
                        "name": name.strip(),
                        "email": email.strip().lower(),
                        "department": department,
                        "designation": designation,
                        "phone": phone.strip(),
                        "joining_date": joining_date.strftime("%Y-%m-%d")
                    }
                    if add_faculty(new_fac):
                        st.success(f"Successfully registered {name} with ID: {next_id}.")
                        st.rerun()
                    else:
                        st.error("Error writing database. Please try again.")

# ----------------------------------------------------
# TAB 3: EDIT / DELETE FACULTY (ADMIN ONLY)
# ----------------------------------------------------
if is_admin:
    with tabs[2]:
        st.markdown("### Update / Retire Faculty Records")
        
        if not faculty_list:
            st.info("No faculty registered.")
        else:
            selected_edit_id = st.selectbox("Select Faculty Member to Modify/Delete:", [f"{f.get('id')} - {f.get('name')}" for f in faculty_list])
            target_id = selected_edit_id.split(" - ")[0]
            fac_to_edit = next((f for f in faculty_list if f.get("id") == target_id), None)
            
            if fac_to_edit:
                st.markdown(f"**Modifying Faculty ID: {fac_to_edit.get('id')}**")
                
                with st.form("edit_faculty_form"):
                    edit_name = st.text_input("Full Name", value=fac_to_edit.get("name"))
                    edit_email = st.text_input("Email Address", value=fac_to_edit.get("email"))
                    
                    col_fedep, col_fedes = st.columns(2)
                    with col_fedep:
                        depts_list = ["Computer Science", "Electrical Engineering", "Mechanical Engineering", "Civil Engineering", "Business Administration", "Chemistry", "Physics"]
                        dept_idx = depts_list.index(fac_to_edit.get("department")) if fac_to_edit.get("department") in depts_list else 0
                        edit_dept = st.selectbox("Department", depts_list, index=dept_idx)
                    with col_fedes:
                        des_list = ["Professor", "Associate Professor", "Assistant Professor", "Lecturer", "Instructor"]
                        des_idx = des_list.index(fac_to_edit.get("designation")) if fac_to_edit.get("designation") in des_list else 0
                        edit_designation = st.selectbox("Designation", des_list, index=des_idx)
                        
                    edit_phone = st.text_input("Phone Number", value=fac_to_edit.get("phone"))
                    
                    submit_edit = st.form_submit_button("Update Faculty Record")
                    
                    if submit_edit:
                        if not edit_name.strip() or not edit_email.strip() or not edit_phone.strip():
                            st.error("Please fill in Name, Email, and Phone number.")
                        elif not is_valid_email(edit_email):
                            st.error("Please provide a valid email format.")
                        elif any(f.get("email").lower() == edit_email.strip().lower() and f.get("id") != target_id for f in faculty_list):
                            st.error("A faculty member with this email is already registered.")
                        else:
                            updated_data = {
                                "name": edit_name.strip(),
                                "email": edit_email.strip().lower(),
                                "department": edit_dept,
                                "designation": edit_designation,
                                "phone": edit_phone.strip()
                            }
                            if update_faculty(target_id, updated_data):
                                st.success("Faculty member details updated successfully.")
                                st.rerun()
                            else:
                                st.error("Database update error. Please try again.")
                                
                st.markdown("---")
                st.markdown("#### ⚠️ Danger Zone")
                confirm_delete = st.checkbox(f"I confirm that I want to delete faculty member: **{fac_to_edit.get('name')}** permanently.")
                delete_btn = st.button("🔴 Permanently Delete Faculty Record")
                
                if delete_btn:
                    if confirm_delete:
                        if delete_faculty(target_id):
                            st.success(f"Faculty record {fac_to_edit.get('name')} deleted.")
                            st.rerun()
                        else:
                            st.error("Delete operation failed.")
                    else:
                        st.error("Please check the confirmation box to delete.")
