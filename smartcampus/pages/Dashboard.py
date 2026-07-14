import streamlit as st
import datetime
import pandas as pd
import plotly.express as px
from utils.database import get_all_students, get_all_faculty, get_all_attendance, get_all_books, get_all_events
from utils.helpers import load_custom_css, render_metric_card, render_card
from utils.api import get_campus_weather, get_campus_insights

# Load styling
load_custom_css()

# Welcome Header & Weather Widget
col_header, col_weather = st.columns([3, 1])

with col_header:
    user_name = st.session_state.user.get("name", "User") if st.session_state.user else "User"
    st.markdown(f"<h1 style='margin-bottom: 5px;'>🏫 Campus Dashboard</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #64748B; font-size: 1.1rem; margin-top: 0;'>Welcome back, <b>{user_name}</b>! Here is the latest campus overview.</p>", unsafe_allow_html=True)

with col_weather:
    weather = get_campus_weather()
    st.markdown(
        f"""
        <div style="
            background-color: #E0F2FE;
            border: 1px solid #BAE6FD;
            padding: 12px 18px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        ">
            <div>
                <span style="font-size: 0.8rem; color: #0369A1; font-weight: 600; text-transform: uppercase;">Campus Weather</span>
                <h4 style="margin: 2px 0 0 0; color: #0369A1; font-size: 1.1rem; font-weight: 700;">{weather['temp']} - {weather['condition']}</h4>
            </div>
            <div style="font-size: 2rem;">{weather['emoji']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# Fetch database data
students = get_all_students()
faculty = get_all_faculty()
attendance = get_all_attendance()
books = get_all_books()
events = get_all_events()

# Calculate metric values
total_students = len(students)
total_faculty = len(faculty)

# Attendance percentage
if attendance:
    present = len([a for a in attendance if a.get("status") == "Present"])
    attendance_pct = (present / len(attendance)) * 100
else:
    attendance_pct = 92.5  # default if empty
    
# Unique departments * 2 to represent "Courses"
depts = set([s.get("department") for s in students] + [f.get("department") for f in faculty])
total_courses = max(len(depts) * 3, 6)

# Library books
total_books = sum(int(b.get("quantity", 0)) for b in books)

# Upcoming events count
today_str = datetime.date.today().strftime("%Y-%m-%d")
upcoming_events = [e for e in events if e.get("date") >= today_str]
total_upcoming_events = len(upcoming_events)

# Render Metric Cards (2 rows of 3 cards)
m_col1, m_col2, m_col3 = st.columns(3)
with m_col1:
    render_metric_card("Total Students", f"{total_students}", "🎓", "#2563EB")
with m_col2:
    render_metric_card("Total Faculty", f"{total_faculty}", "💼", "#14B8A6")
with m_col3:
    render_metric_card("Attendance Rate", f"{attendance_pct:.1f}%", "📊", "#F59E0B")

m_col4, m_col5, m_col6 = st.columns(3)
with m_col4:
    render_metric_card("Active Courses", f"{total_courses}", "📚", "#8B5CF6")
with m_col5:
    render_metric_card("Total Library Books", f"{total_books}", "📖", "#EC4899")
with m_col6:
    render_metric_card("Upcoming Events", f"{total_upcoming_events}", "📅", "#10B981")

# Layout: Main Content (Charts) vs Sidebar (Activity, Quick Actions, AI Recommendations)
left_layout, right_layout = st.columns([2, 1])

with left_layout:
    st.markdown("### 📈 Campus Analytics")
    tab_demographics, tab_trends = st.tabs(["Demographics & Departments", "Attendance & Faculty Split"])
    
    with tab_demographics:
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Student stats by Year
            if students:
                df_std = pd.DataFrame(students)
                year_counts = df_std["year"].value_counts().reset_index()
                year_counts.columns = ["Year", "Students"]
                fig_year = px.bar(
                    year_counts, 
                    x="Year", 
                    y="Students", 
                    title="Student Enrollment by Year",
                    color_discrete_sequence=["#2563EB"],
                    labels={"Students": "Count"}
                )
                fig_year.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_year, use_container_width=True)
            else:
                st.info("No student data available to display statistics.")
                
        with chart_col2:
            # Department Analytics
            if students:
                df_std = pd.DataFrame(students)
                dept_counts = df_std["department"].value_counts().reset_index()
                dept_counts.columns = ["Department", "Students"]
                fig_dept = px.bar(
                    dept_counts,
                    y="Department",
                    x="Students",
                    orientation="h",
                    title="Students by Department",
                    color_discrete_sequence=["#14B8A6"]
                )
                fig_dept.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_dept, use_container_width=True)
            else:
                st.info("No department data available.")

    with tab_trends:
        chart_col3, chart_col4 = st.columns(2)
        
        with chart_col3:
            # Attendance trends
            if attendance:
                df_att = pd.DataFrame(attendance)
                # Compute daily attendance percentage
                df_att["is_present"] = df_att["status"] == "Present"
                daily_pct = df_att.groupby("date")["is_present"].mean().reset_index()
                daily_pct["percentage"] = daily_pct["is_present"] * 100
                daily_pct = daily_pct.sort_values("date")
                
                fig_trend = px.line(
                    daily_pct,
                    x="date",
                    y="percentage",
                    title="Daily Attendance Trend (%)",
                    markers=True,
                    color_discrete_sequence=["#F59E0B"],
                    labels={"percentage": "Attendance %", "date": "Date"}
                )
                fig_trend.update_layout(yaxis_range=[0, 105], paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.info("No attendance data available.")
                
        with chart_col4:
            # Faculty distribution
            if faculty:
                df_fac = pd.DataFrame(faculty)
                fac_dept = df_fac["department"].value_counts().reset_index()
                fac_dept.columns = ["Department", "Faculty Count"]
                fig_fac = px.pie(
                    fac_dept,
                    values="Faculty Count",
                    names="Department",
                    hole=0.4,
                    title="Faculty Distribution by Department",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_fac.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_fac, use_container_width=True)
            else:
                st.info("No faculty data available.")

    # Upcoming events list card
    events_html = ""
    if upcoming_events:
        # Sort by date
        sorted_events = sorted(upcoming_events, key=lambda x: x.get("date"))[:3]
        for e in sorted_events:
            date_obj = datetime.datetime.strptime(e.get("date"), "%Y-%m-%d")
            formatted_date = date_obj.strftime("%b %d, %Y")
            events_html += f"""
            <div style="border-bottom: 1px solid #E2E8F0; padding: 10px 0;">
                <span style="font-size: 0.8rem; font-weight: 600; color: #2563EB; background: #2563EB15; padding: 3px 8px; border-radius: 4px;">{formatted_date}</span>
                <span style="font-size: 0.8rem; font-weight: 500; color: #64748B; margin-left: 10px;">📍 {e.get('location')}</span>
                <h5 style="margin: 6px 0 2px 0; color: #1E293B; font-weight: 600;">{e.get('title')}</h5>
                <p style="margin: 0; font-size: 0.85rem; color: #64748B;">{e.get('description')}</p>
            </div>
            """
    else:
        events_html = "<p style='color: #64748B; font-style: italic;'>No upcoming events scheduled.</p>"
        
    render_card("📅 Upcoming Campus Events", events_html)

with right_layout:
    # AI Admin Insights
    st.markdown("### 💡 System Insights")
    insights = get_campus_insights(total_students, total_faculty, attendance_pct)
    st.markdown(
        f"""
        <div style="
            background-color: #FAF5FF;
            border: 1px solid #F3E8FF;
            padding: 20px;
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            margin-bottom: 24px;
        ">
            <h4 style="color: #7E22CE; margin-top: 0; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">✨ AI Administrator Insights</h4>
            <div style="color: #581C87; font-size: 0.95rem; line-height: 1.6;">
                {insights}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Quick Actions Card
    st.markdown("### ⚡ Quick Actions")
    with st.container(border=True):
        st.markdown("<p style='font-size: 0.85rem; color: #64748B; margin-bottom: 15px;'>Common shortcuts for administrators and faculty members:</p>", unsafe_allow_html=True)
        
        btn_std = st.button("➕ Add New Student")
        btn_att = st.button("📝 Log Attendance")
        btn_lib = st.button("📖 Issue Library Book")
        btn_ev = st.button("🎉 Create Campus Event")
        
        if btn_std:
            st.switch_page("pages/Students.py")
        if btn_att:
            st.switch_page("pages/Attendance.py")
        if btn_lib:
            st.switch_page("pages/Library.py")
        if btn_ev:
            st.switch_page("pages/Events.py")

    # Campus Announcements
    announcements_html = """
    <div style="border-bottom: 1px solid #E2E8F0; padding-bottom: 8px; margin-bottom: 8px;">
        <span style="font-size: 0.75rem; font-weight: 600; color: #EF4444; background: #FEF2F2; padding: 2px 6px; border-radius: 4px;">Urgents</span>
        <h5 style="margin: 4px 0 2px 0; font-size: 0.9rem; font-weight: 600; color: #1E293B;">End-Semester Exam Schedule</h5>
        <p style="margin: 0; font-size: 0.8rem; color: #64748B;">Detailed schedules for theoretical and lab evaluations have been updated in Reports.</p>
    </div>
    <div>
        <span style="font-size: 0.75rem; font-weight: 600; color: #3B82F6; background: #EFF6FF; padding: 2px 6px; border-radius: 4px;">General</span>
        <h5 style="margin: 4px 0 2px 0; font-size: 0.9rem; font-weight: 600; color: #1E293B;">Annual Hackathon 2026</h5>
        <p style="margin: 0; font-size: 0.8rem; color: #64748B;">Registration opens for local and national teams next Monday. Tech Club auditorium.</p>
    </div>
    """
    render_card("📢 Campus Announcements", announcements_html)
