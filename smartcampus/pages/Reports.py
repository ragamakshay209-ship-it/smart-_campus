import streamlit as st
import pandas as pd
from utils.database import get_all_students, get_all_faculty, get_all_attendance, get_all_books, get_all_events
from utils.helpers import load_custom_css, render_card

# Load styles
load_custom_css()

st.markdown("<h1>📋 Reports Compiler</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748B;'>Select a data collection, preview administrative statistics, and export cleaned tables in CSV format.</p>", unsafe_allow_html=True)

# Prepare tabs
tabs = st.tabs([
    "👥 Students Report", 
    "📅 Attendance Report", 
    "👨‍🏫 Faculty Report", 
    "📚 Library Report", 
    "🎉 Events Report"
])

# ----------------------------------------------------
# TAB 1: STUDENTS REPORT
# ----------------------------------------------------
with tabs[0]:
    st.markdown("### Students Enrollment Report")
    students = get_all_students()
    
    if not students:
        st.info("No student records available.")
    else:
        df_students = pd.DataFrame(students)
        
        # Display Stats
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.metric("Total Enrolled Students", len(students))
        with col_s2:
            st.metric("Unique Departments", len(df_students["department"].unique()))
        with col_s3:
            st.metric("Latest Enrollment Date", df_students["enrollment_date"].max())
            
        # Display data
        df_disp = df_students[["id", "name", "email", "department", "year", "phone", "enrollment_date"]].copy()
        df_disp.columns = ["Student ID", "Full Name", "Email", "Department", "Academic Year", "Phone", "Enrollment Date"]
        st.dataframe(df_disp, hide_index=True, use_container_width=True)
        
        # CSV Export
        csv_data = df_disp.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Students Report as CSV",
            data=csv_data,
            file_name=f"students_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# ----------------------------------------------------
# TAB 2: ATTENDANCE REPORT
# ----------------------------------------------------
with tabs[1]:
    st.markdown("### Attendance Registry Report")
    attendance = get_all_attendance()
    
    if not attendance:
        st.info("No attendance records logged.")
    else:
        df_att = pd.DataFrame(attendance)
        
        total_sessions = len(df_att)
        presents = len(df_att[df_att["status"] == "Present"])
        absents = len(df_att[df_att["status"] == "Absent"])
        lates = len(df_att[df_att["status"] == "Late"])
        presence_rate = (presents / total_sessions) * 100 if total_sessions > 0 else 0
        
        # Display Stats
        col_a1, col_a2, col_a3, col_a4 = st.columns(4)
        with col_a1:
            st.metric("Total Logs Recorded", total_sessions)
        with col_a2:
            st.metric("Overall Presence Rate", f"{presence_rate:.1f}%")
        with col_a3:
            st.metric("Total Absences Logged", absents)
        with col_a4:
            st.metric("Late Logs", lates)
            
        # Display table
        df_disp = df_att[["date", "student_id", "student_name", "status", "marked_by"]].copy()
        df_disp.columns = ["Session Date", "Student ID", "Student Name", "Attendance Status", "Logged By"]
        st.dataframe(df_disp, hide_index=True, use_container_width=True)
        
        # CSV Export
        csv_data = df_disp.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Attendance Report as CSV",
            data=csv_data,
            file_name=f"attendance_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# ----------------------------------------------------
# TAB 3: FACULTY REPORT
# ----------------------------------------------------
with tabs[2]:
    st.markdown("### Faculty Registry Report")
    faculty = get_all_faculty()
    
    if not faculty:
        st.info("No faculty records available.")
    else:
        df_fac = pd.DataFrame(faculty)
        
        # Display Stats
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            st.metric("Total Active Faculty Members", len(faculty))
        with col_f2:
            st.metric("Departments Represented", len(df_fac["department"].unique()))
        with col_f3:
            st.metric("Senior Professors", len(df_fac[df_fac["designation"] == "Professor"]))
            
        # Display table
        df_disp = df_fac[["id", "name", "email", "department", "designation", "phone", "joining_date"]].copy()
        df_disp.columns = ["Faculty ID", "Full Name", "Email", "Department", "Designation", "Phone", "Joining Date"]
        st.dataframe(df_disp, hide_index=True, use_container_width=True)
        
        # CSV Export
        csv_data = df_disp.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Faculty Report as CSV",
            data=csv_data,
            file_name=f"faculty_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# ----------------------------------------------------
# TAB 4: LIBRARY REPORT
# ----------------------------------------------------
with tabs[3]:
    st.markdown("### Library Inventory & Active Loans Report")
    books = get_all_books()
    
    if not books:
        st.info("No library books registered.")
    else:
        df_books = pd.DataFrame(books)
        
        total_titles = len(df_books)
        total_copies = df_books["quantity"].sum()
        total_available = df_books["available"].sum()
        active_loans = total_copies - total_available
        
        # Display Stats
        col_l1, col_l2, col_l3, col_l4 = st.columns(4)
        with col_l1:
            st.metric("Total Catalog Titles", total_titles)
        with col_l2:
            st.metric("Total Stock Volume", total_copies)
        with col_l3:
            st.metric("Copies Available", total_available)
        with col_l4:
            st.metric("Active Borrow Loans", active_loans)
            
        # Display main catalog
        st.markdown("#### Library Catalog")
        df_disp_b = df_books[["id", "title", "author", "isbn", "quantity", "available"]].copy()
        df_disp_b.columns = ["Book ID", "Title", "Author", "ISBN", "Total Stock", "Available Stock"]
        st.dataframe(df_disp_b, hide_index=True, use_container_width=True)
        
        # CSV Export
        csv_data_b = df_disp_b.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Book Catalog as CSV",
            data=csv_data_b,
            file_name=f"library_catalog_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        # Compile active borrowings list
        borrow_records = []
        for b in books:
            for issue in b.get("issued_to", []):
                borrow_records.append({
                    "book_id": b.get("id"),
                    "book_title": b.get("title"),
                    "student_id": issue.get("student_id"),
                    "student_name": issue.get("student_name"),
                    "issue_date": issue.get("issue_date"),
                    "due_date": issue.get("due_date")
                })
                
        if borrow_records:
            st.markdown("#### Active Loan Register")
            df_loans = pd.DataFrame(borrow_records)
            df_loans.columns = ["Book ID", "Book Title", "Student ID", "Student Name", "Issue Date", "Due Date"]
            st.dataframe(df_loans, hide_index=True, use_container_width=True)
            
            csv_data_loans = df_loans.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Borrow Records as CSV",
                data=csv_data_loans,
                file_name=f"active_loans_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

# ----------------------------------------------------
# TAB 5: EVENTS REPORT
# ----------------------------------------------------
with tabs[4]:
    st.markdown("### Published Campus Events Report")
    events = get_all_events()
    
    if not events:
        st.info("No events registered on the campus roll.")
    else:
        df_ev = pd.DataFrame(events)
        
        # Display Stats
        col_e1, col_e2, col_e3 = st.columns(3)
        with col_e1:
            st.metric("Total Events Logged", len(events))
        with col_e2:
            st.metric("Category Split Types", len(df_ev["category"].unique()))
        with col_e3:
            latest_ev = df_ev.sort_values("date", ascending=False).iloc[0]
            st.metric("Latest Event Scheduled", latest_ev["title"])
            
        # Display data
        df_disp = df_ev[["id", "title", "category", "date", "time", "location", "description"]].copy()
        df_disp.columns = ["Event ID", "Title", "Category", "Scheduled Date", "Scheduled Time", "Venue", "Description"]
        st.dataframe(df_disp, hide_index=True, use_container_width=True)
        
        # CSV Export
        csv_data = df_disp.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Events Schedule as CSV",
            data=csv_data,
            file_name=f"events_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
