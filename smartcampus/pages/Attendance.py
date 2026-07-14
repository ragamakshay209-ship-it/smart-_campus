import streamlit as st
import datetime
import pandas as pd
import plotly.express as px
from utils.database import get_all_students, get_all_attendance, add_attendance_records, update_attendance_record
from utils.helpers import load_custom_css, render_card, render_metric_card

# Load styling
load_custom_css()

st.markdown("<h1>📅 Attendance Tracker</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748B;'>Manage student attendance records, log daily presence, and compile statistics.</p>", unsafe_allow_html=True)

# User Role Authorization
user_role = st.session_state.user.get("role") if st.session_state.user else "Student"
user_email = st.session_state.user.get("email") if st.session_state.user else ""
is_privileged = user_role in ["Admin", "Faculty"]

# Fetch data
all_students = get_all_students()
attendance_logs = get_all_attendance()

# Helper to find student by email
logged_student = next((s for s in all_students if s.get("email").lower() == user_email.lower()), None)

# Setup tabs based on user role
if is_privileged:
    tab_names = ["📊 Attendance Analytics", "📝 Mark Attendance", "✏️ Edit Attendance Records"]
else:
    tab_names = ["👤 My Attendance Record"]

tabs = st.tabs(tab_names)

# ----------------------------------------------------
# PRIVILEGED TABS
# ----------------------------------------------------
if is_privileged:
    # TAB 1: ANALYTICS
    with tabs[0]:
        st.markdown("### Campus Attendance Insights")
        
        if not attendance_logs:
            st.info("No attendance records have been registered in the system.")
        else:
            # Metrics Row
            total_logs = len(attendance_logs)
            present_count = len([a for a in attendance_logs if a.get("status") == "Present"])
            absent_count = len([a for a in attendance_logs if a.get("status") == "Absent"])
            late_count = len([a for a in attendance_logs if a.get("status") == "Late"])
            
            rate = (present_count / total_logs) * 100 if total_logs > 0 else 0
            
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            with col_m1:
                render_metric_card("Presence Rate", f"{rate:.1f}%", "📊", "#F59E0B")
            with col_m2:
                render_metric_card("Total Logs", f"{total_logs}", "📝", "#2563EB")
            with col_m3:
                render_metric_card("Presents", f"{present_count}", "✅", "#10B981")
            with col_m4:
                render_metric_card("Absents / Lates", f"{absent_count} / {late_count}", "❌", "#EF4444")
                
            # Filter & Detail Viewer
            st.markdown("---")
            df_att = pd.DataFrame(attendance_logs)
            
            col_fdate, col_fstudent = st.columns(2)
            with col_fdate:
                dates = ["All Dates"] + list(sorted(list(set(a.get("date") for a in attendance_logs)), reverse=True))
                selected_date = st.selectbox("Search by Date", dates)
            with col_fstudent:
                students_options = ["All Students"] + list(sorted(list(set(f"{a.get('student_id')} - {a.get('student_name')}" for a in attendance_logs))))
                selected_student = st.selectbox("Search by Student", students_options)
                
            # Filter logic
            filtered_df = df_att.copy()
            if selected_date != "All Dates":
                filtered_df = filtered_df[filtered_df["date"] == selected_date]
            if selected_student != "All Students":
                sid = selected_student.split(" - ")[0]
                filtered_df = filtered_df[filtered_df["student_id"] == sid]
                
            # Display Table
            st.markdown("#### Log History")
            df_display = filtered_df[["date", "student_id", "student_name", "status", "marked_by"]].copy()
            df_display.columns = ["Date", "Student ID", "Student Name", "Attendance Status", "Logged By"]
            st.dataframe(df_display, hide_index=True, use_container_width=True)
            
            # Attendance Charts
            st.markdown("---")
            st.markdown("#### Visual Analytics")
            chart_col1, chart_col2 = st.columns(2)
            with chart_col1:
                # Status breakdown
                status_counts = filtered_df["status"].value_counts().reset_index()
                status_counts.columns = ["Status", "Count"]
                fig_status = px.pie(
                    status_counts, 
                    values="Count", 
                    names="Status", 
                    title="Attendance Status Breakdown",
                    color_discrete_map={"Present": "#10B981", "Absent": "#EF4444", "Late": "#F59E0B"}
                )
                st.plotly_chart(fig_status, use_container_width=True)
            with chart_col2:
                # Daily presence rate
                filtered_df["is_present"] = filtered_df["status"] == "Present"
                daily_stats = filtered_df.groupby("date")["is_present"].mean().reset_index()
                daily_stats["percentage"] = daily_stats["is_present"] * 100
                daily_stats = daily_stats.sort_values("date")
                fig_daily = px.bar(
                    daily_stats,
                    x="date",
                    y="percentage",
                    title="Daily Attendance Trend (%)",
                    color_discrete_sequence=["#2563EB"],
                    labels={"percentage": "Attendance Rate %"}
                )
                fig_daily.update_layout(yaxis_range=[0, 105])
                st.plotly_chart(fig_daily, use_container_width=True)

    # TAB 2: MARK ATTENDANCE
    with tabs[1]:
        st.markdown("### Record Daily Attendance")
        
        # 1. Filter class to mark
        col_mark_dept, col_mark_yr = st.columns(2)
        with col_mark_dept:
            depts_avail = list(sorted(list(set(s.get("department") for s in all_students)))) if all_students else ["Computer Science"]
            mark_dept = st.selectbox("Select Department to Mark", depts_avail)
        with col_mark_yr:
            mark_yr = st.selectbox("Select Academic Year to Mark", ["1st Year", "2nd Year", "3rd Year", "4th Year"])
            
        mark_date = st.date_input("Date of Attendance", value=datetime.date.today())
        
        # Filter matching students
        class_students = [s for s in all_students if s.get("department") == mark_dept and s.get("year") == mark_yr]
        
        if not class_students:
            st.warning(f"No students found registered under {mark_dept} - {mark_yr}.")
        else:
            st.markdown(f"**Marking attendance for {len(class_students)} students on {mark_date}**")
            
            # Check if attendance already marked for this class today to alert the user
            already_marked_today = [a for a in attendance_logs if a.get("date") == mark_date.strftime("%Y-%m-%d") and a.get("student_id") in [s.get("id") for s in class_students]]
            if already_marked_today:
                st.warning("⚠️ Attendance has already been logged for some of these students today. Submitting again will create extra duplicate entries. To update, use the 'Edit Attendance' tab.")
                
            # Create marking form
            with st.form("mark_attendance_form"):
                attendance_states = {}
                
                # Render header
                col_h_id, col_h_name, col_h_status = st.columns([1, 2, 2])
                with col_h_id:
                    st.markdown("**Student ID**")
                with col_h_name:
                    st.markdown("**Student Name**")
                with col_h_status:
                    st.markdown("**Attendance Status**")
                st.markdown("---")
                
                # Render students
                for student in class_students:
                    s_id = student.get("id")
                    s_name = student.get("name")
                    
                    c_id, c_name, c_status = st.columns([1, 2, 2])
                    with c_id:
                        st.write(s_id)
                    with c_name:
                        st.write(s_name)
                    with c_status:
                        attendance_states[s_id] = st.radio(
                            f"Status for {s_id}",
                            ["Present", "Absent", "Late"],
                            index=0,
                            horizontal=True,
                            label_visibility="collapsed"
                        )
                
                submit_marks = st.form_submit_button("Submit Attendance Roll")
                
                if submit_marks:
                    # Calculate next ATT index ID
                    if attendance_logs:
                        ids = [int(a.get("id")[3:]) for a in attendance_logs if a.get("id").startswith("ATT") and a.get("id")[3:].isdigit()]
                        next_idx = max(ids) + 1 if ids else 1
                    else:
                        next_idx = 1
                        
                    new_records = []
                    for s_id, status in attendance_states.items():
                        student_obj = next(s for s in class_students if s.get("id") == s_id)
                        new_records.append({
                            "id": f"ATT{next_idx:03d}",
                            "student_id": s_id,
                            "student_name": student_obj.get("name"),
                            "date": mark_date.strftime("%Y-%m-%d"),
                            "status": status,
                            "marked_by": st.session_state.user.get("email")
                        })
                        next_idx += 1
                        
                    if add_attendance_records(new_records):
                        st.success(f"Success! Attendance roll for {mark_dept} ({mark_yr}) logged successfully.")
                        st.rerun()
                    else:
                        st.error("Failed to save records.")

    # TAB 3: EDIT ATTENDANCE
    with tabs[2]:
        st.markdown("### Modify Existing Attendance Log")
        
        if not attendance_logs:
            st.info("No records to edit.")
        else:
            dates_avail = list(sorted(list(set(a.get("date") for a in attendance_logs)), reverse=True))
            edit_date = st.selectbox("Select Log Date to Modify:", dates_avail)
            
            # Filter logs for selected date
            date_logs = [a for a in attendance_logs if a.get("date") == edit_date]
            
            if not date_logs:
                st.warning("No records found for this date.")
            else:
                st.markdown(f"**Modifying {len(date_logs)} records logged on {edit_date}**")
                
                selected_edit_record = st.selectbox(
                    "Select Student Log to Edit:",
                    [f"{r.get('id')} | {r.get('student_id')} - {r.get('student_name')} ({r.get('status')})" for r in date_logs]
                )
                
                record_id = selected_edit_record.split(" | ")[0]
                target_record = next(r for r in date_logs if r.get("id") == record_id)
                
                if target_record:
                    with st.form("edit_single_attendance_form"):
                        st.write(f"Student: **{target_record.get('student_name')} ({target_record.get('student_id')})**")
                        
                        status_list = ["Present", "Absent", "Late"]
                        status_idx = status_list.index(target_record.get("status")) if target_record.get("status") in status_list else 0
                        new_status = st.radio("Modify Status:", status_list, index=status_idx, horizontal=True)
                        
                        submit_single_edit = st.form_submit_button("Update Log Entry")
                        if submit_single_edit:
                            if update_attendance_record(record_id, {"status": new_status, "marked_by": st.session_state.user.get("email")}):
                                st.success("Attendance entry updated successfully.")
                                st.rerun()
                            else:
                                st.error("Failed to update record.")

# ----------------------------------------------------
# STUDENT TABS
# ----------------------------------------------------
else:
    # TAB 1: MY ATTENDANCE RECORD
    with tabs[0]:
        st.markdown("### Personal Attendance Report")
        
        if not logged_student:
            st.error("Error: Could not locate a student profile associated with your login credentials. Please contact the administrator.")
        else:
            student_id = logged_student.get("id")
            student_name = logged_student.get("name")
            
            # Filter student records
            my_records = [a for a in attendance_logs if a.get("student_id") == student_id]
            
            if not my_records:
                st.info("No attendance check-ins have been logged for you yet.")
            else:
                total_my = len(my_records)
                presents = len([a for a in my_records if a.get("status") == "Present"])
                lates = len([a for a in my_records if a.get("status") == "Late"])
                absents = len([a for a in my_records if a.get("status") == "Absent"])
                
                presence_rate = ((presents + lates*0.5) / total_my) * 100 if total_my > 0 else 0
                
                col_p1, col_p2, col_p3 = st.columns(3)
                with col_p1:
                    render_metric_card("My Presence Rate", f"{presence_rate:.1f}%", "📊", "#2563EB")
                with col_p2:
                    render_metric_card("Total Sessions", f"{total_my}", "📝", "#14B8A6")
                with col_p3:
                    render_metric_card("Absents / Lates", f"{absents} / {lates}", "⚠️", "#EF4444")
                    
                st.markdown("#### Detail Attendance Log")
                df_my = pd.DataFrame(my_records)
                df_my_display = df_my[["date", "status", "marked_by"]].copy()
                df_my_display.columns = ["Session Date", "Attendance Status", "Logged By"]
                df_my_display = df_my_display.sort_values("Session Date", ascending=False)
                
                st.dataframe(df_my_display, hide_index=True, use_container_width=True)
                
                # Donut of stats
                st.markdown("---")
                fig_my = px.pie(
                    df_my,
                    names="status",
                    hole=0.5,
                    title="My Attendance Status Breakdown",
                    color_discrete_map={"Present": "#10B981", "Absent": "#EF4444", "Late": "#F59E0B"}
                )
                st.plotly_chart(fig_my, use_container_width=True)
