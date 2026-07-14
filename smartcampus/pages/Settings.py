import streamlit as st
from utils.auth import update_user_profile
from utils.helpers import load_custom_css, render_card

# Load styling
load_custom_css()

st.markdown("<h1>⚙️ System Settings</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748B;'>Configure application theme preferences, update security passwords, and view system metadata.</p>", unsafe_allow_html=True)

# Fetch user
user = st.session_state.user

if not user:
    st.error("Authentication session error. Please log in again.")
else:
    tab_theme, tab_security, tab_info = st.tabs(["🎨 Interface Theme", "🔒 Change Password", "ℹ️ Application Information"])
    
    # ----------------------------------------------------
    # TAB 1: INTERFACE THEME
    # ----------------------------------------------------
    with tab_theme:
        st.markdown("### Theme Preferences")
        st.write("Customize your view mode. Theme choices are applied instantly across all modules.")
        
        # Setup selection index based on session state
        theme_index = 0 if st.session_state.theme == "light" else 1
        selected_theme = st.selectbox(
            "Application Theme Mode",
            ["Light Theme", "Dark Theme"],
            index=theme_index
        )
        
        target_theme = "light" if selected_theme == "Light Theme" else "dark"
        
        # Trigger reload if theme changed
        if target_theme != st.session_state.theme:
            st.session_state.theme = target_theme
            st.success(f"Theme switched to {selected_theme}!")
            st.rerun()
            
        # Preview Card
        st.markdown("<br>", unsafe_allow_html=True)
        preview_text = "Standard Clean Slate mode. Best for bright rooms and daytime viewing." if st.session_state.theme == "light" else "Premium Night mode. Employs deep indigo colors to reduce eye strain."
        render_card(f"Preview: {selected_theme}", f"<p style='margin:0;'>{preview_text}</p>")

    # ----------------------------------------------------
    # TAB 2: CHANGE PASSWORD
    # ----------------------------------------------------
    with tab_security:
        st.markdown("### Change Password")
        st.write("Ensure your account credentials remain secure by changing your password periodically.")
        
        with st.form("settings_password_form"):
            current_pw = st.text_input("Confirm Current Password (placeholder validation)", type="password", placeholder="••••••••")
            new_pw = st.text_input("New Secure Password", type="password", placeholder="••••••••")
            confirm_pw = st.text_input("Confirm New Password", type="password", placeholder="••••••••")
            
            submit_pw = st.form_submit_button("Update Password")
            
            if submit_pw:
                if not current_pw or not new_pw or not confirm_pw:
                    st.error("All password fields are required.")
                elif len(new_pw) < 6:
                    st.error("New password must be at least 6 characters long.")
                elif new_pw != confirm_pw:
                    st.error("New passwords do not match.")
                else:
                    # Update password in database
                    success, msg, updated_user = update_user_profile(
                        user.get("email"),
                        user.get("name"),
                        password=new_pw,
                        profile_picture_base64=user.get("profile_picture")
                    )
                    if success:
                        st.session_state.user = updated_user
                        st.success("Your password has been changed successfully.")
                    else:
                        st.error(msg)

    # ----------------------------------------------------
    # TAB 3: APPLICATION INFORMATION
    # ----------------------------------------------------
    with tab_info:
        st.markdown("### Smart Campus ERP System")
        st.write("Application diagnostic and deployment parameters:")
        
        info_html = """
        <table style="width: 100%; border-collapse: collapse; font-size: 0.95rem;">
            <tr style="border-bottom: 1px solid #E2E8F0;"><td style="padding: 10px 0; font-weight: 600; color: #64748B; width: 35%;">Application Name:</td><td style="padding: 10px 0; color: #1E293B;">Smart Campus Management System</td></tr>
            <tr style="border-bottom: 1px solid #E2E8F0;"><td style="padding: 10px 0; font-weight: 600; color: #64748B;">System Version:</td><td style="padding: 10px 0; color: #10B981; font-weight: 600;">v1.0.0 (Production Ready)</td></tr>
            <tr style="border-bottom: 1px solid #E2E8F0;"><td style="padding: 10px 0; font-weight: 600; color: #64748B;">Framework / Engine:</td><td style="padding: 10px 0; color: #1E293B;">Streamlit v1.35.0+, Python 3.11+</td></tr>
            <tr style="border-bottom: 1px solid #E2E8F0;"><td style="padding: 10px 0; font-weight: 600; color: #64748B;">Database Engine:</td><td style="padding: 10px 0; color: #1E293B;">Thread-Safe Local JSON Document Store</td></tr>
            <tr style="border-bottom: 1px solid #E2E8F0;"><td style="padding: 10px 0; font-weight: 600; color: #64748B;">Styling Schema:</td><td style="padding: 10px 0; color: #1E293B;">Custom CSS (Outfit Typography, Glassmorphism Cards)</td></tr>
            <tr><td style="padding: 10px 0; font-weight: 600; color: #64748B;">AI Intelligence Assistant:</td><td style="padding: 10px 0; color: #2563EB; font-weight: 600;">GPT-4o Mini Integrator / Fallback Rule Heuristics</td></tr>
        </table>
        """
        render_card("System Diagnostic Board", info_html)
        
        st.markdown("<p style='text-align: center; color: #94A3B8; font-size: 0.8rem; margin-top: 20px;'>Designed by Antigravity AI &copy; 2026. Deployable to Streamlit Community Cloud, Render, and Railway.</p>", unsafe_allow_html=True)
