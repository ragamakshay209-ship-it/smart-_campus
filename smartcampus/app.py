import streamlit as st
import os
import config
from utils.database import init_db
from utils.helpers import load_custom_css

# 1. Initialize databases on app startup
init_db()

# 2. Configure Streamlit Page
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 3. Initialize Session States
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "registration_success" not in st.session_state:
    st.session_state.registration_success = False

# 4. Inject styles and theme
load_custom_css()

# 5. Render Sidebar Logo & Header
if os.path.exists("assets/logo.png"):
    st.sidebar.image("assets/logo.png", use_container_width=True)
st.sidebar.markdown(
    f"<h3 style='text-align: center; color: #2563EB; margin-top: 0;'>{config.APP_NAME}</h3>", 
    unsafe_allow_html=True
)

# Show logged in user badge
if st.session_state.logged_in and st.session_state.user:
    role_emoji = "🛡️" if st.session_state.user.get("role") == "Admin" else "👨‍🏫" if st.session_state.user.get("role") == "Faculty" else "🎓"
    
    avatar_html = ""
    if st.session_state.user.get("profile_picture"):
        avatar_src = f"data:image/png;base64,{st.session_state.user.get('profile_picture')}"
        avatar_html = f'<div style="text-align: center; margin-bottom: 8px;"><img src="{avatar_src}" style="border-radius: 50%; width: 60px; height: 60px; border: 2px solid #2563EB; object-fit: cover;"></div>'
    else:
        avatar_html = f'<div style="text-align: center; margin-bottom: 8px; font-size: 2rem; background: #2563EB15; border-radius: 50%; width: 60px; height: 60px; display: inline-flex; align-items: center; justify-content: center; border: 2px solid #2563EB; color: #2563EB; margin: 0 auto;">{role_emoji}</div>'

    st.sidebar.markdown(
        f"""
        <div style="
            background-color: #2563EB15;
            padding: 16px 12px;
            border-radius: 12px;
            margin-bottom: 20px;
            border: 1px solid #2563EB30;
            text-align: center;
        ">
            {avatar_html}
            <div style="font-weight: 600; color: #1E293B; margin-top: 5px;">{st.session_state.user.get('name')}</div>
            <div style="font-size: 0.8rem; color: #64748B; text-transform: uppercase; font-weight: 700; margin-top: 2px; letter-spacing: 0.5px;">{st.session_state.user.get('role')}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# 6. Define multi-page application routing structure
if st.session_state.logged_in:
    # Pages accessible after login
    dashboard_page = st.Page("pages/Dashboard.py", title="Dashboard", icon="📊", default=True)
    students_page = st.Page("pages/Students.py", title="Students", icon="👥")
    faculty_page = st.Page("pages/Faculty.py", title="Faculty", icon="👨‍🏫")
    attendance_page = st.Page("pages/Attendance.py", title="Attendance", icon="📅")
    library_page = st.Page("pages/Library.py", title="Library", icon="📚")
    events_page = st.Page("pages/Events.py", title="Events", icon="🎉")
    reports_page = st.Page("pages/Reports.py", title="Reports", icon="📋")
    profile_page = st.Page("pages/Profile.py", title="Profile", icon="👤")
    settings_page = st.Page("pages/Settings.py", title="Settings", icon="⚙️")
    logout_page = st.Page("pages/Logout.py", title="Logout", icon="🚪")
    
    pages = [
        dashboard_page,
        students_page,
        faculty_page,
        attendance_page,
        library_page,
        events_page,
        reports_page,
        profile_page,
        settings_page,
        logout_page
    ]
else:
    # Public Pages (Authentication flow)
    login_page = st.Page("pages/Login.py", title="Login", icon="🔑", default=True)
    register_page = st.Page("pages/Register.py", title="Register", icon="📝")
    
    pages = [login_page, register_page]

# Run the page navigation
pg = st.navigation(pages)
pg.run()
