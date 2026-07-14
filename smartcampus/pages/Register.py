import streamlit as st
from utils.auth import register_user
from utils.helpers import load_custom_css, is_valid_email

# Load custom styles
load_custom_css()

st.markdown("<br><br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1.5, 1])

with col2:
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 20px;">
            <h2 style="margin: 0; color: #2563EB; font-weight: 700;">Create Account</h2>
            <p style="color: #64748B; margin-top: 5px;">Register for the Smart Campus portal</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    with st.form("register_form"):
        full_name = st.text_input("Full Name", placeholder="John Doe")
        email = st.text_input("Email Address", placeholder="john@campus.edu")
        
        col_pw1, col_pw2 = st.columns(2)
        with col_pw1:
            password = st.text_input("Password", type="password", placeholder="••••••••")
        with col_pw2:
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="••••••••")
            
        role = st.selectbox("Role / Account Type", ["Student", "Faculty", "Admin"])
        
        submit_btn = st.form_submit_button("Register Account")
        
        if submit_btn:
            # 1. Input Validation
            if not full_name.strip() or not email.strip() or not password or not confirm_password:
                st.error("All fields are required. Please fill in all text inputs.")
            elif not is_valid_email(email):
                st.error("Please enter a valid email address (e.g. user@domain.com).")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters long.")
            elif password != confirm_password:
                st.error("Passwords do not match. Please re-type your passwords.")
            else:
                # 2. Call Auth logic
                success, msg = register_user(full_name, email, password, role)
                if success:
                    st.session_state.registration_success = True
                    # Switch programmatically to Login page
                    st.switch_page("pages/Login.py")
                else:
                    st.error(msg)
                    
    # Navigation Help
    st.markdown(
        """
        <div style="text-align: center; margin-top: 16px; font-size: 0.85rem;">
            <span style="color: #64748B;">Already registered? Select <b>Login</b> in the sidebar.</span>
        </div>
        """,
        unsafe_allow_html=True
    )
