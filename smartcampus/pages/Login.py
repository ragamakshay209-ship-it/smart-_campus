import streamlit as st
from utils.auth import authenticate_user
from utils.helpers import load_custom_css

# Load custom styles
load_custom_css()

# Layout centering
st.markdown("<br><br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1.5, 1])

with col2:
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 20px;">
            <h2 style="margin: 0; color: #2563EB; font-weight: 700;">Sign In</h2>
            <p style="color: #64748B; margin-top: 5px;">Access the Smart Campus portal</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Show successful registration redirect message
    if st.session_state.get("registration_success"):
        st.success("🎉 Account created successfully! Please sign in below.")
        st.session_state.registration_success = False
        
    with st.form("login_form"):
        email = st.text_input("Email Address", placeholder="yourname@campus.edu")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        
        # Align Remember me and Forgot password placeholder
        remember_me = st.checkbox("Remember Me")
        
        submit_btn = st.form_submit_button("Sign In")
        
        if submit_btn:
            if not email.strip() or not password.strip():
                st.error("Please enter both email and password.")
            else:
                success, msg, user_data = authenticate_user(email, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.user = user_data
                    st.success("Success! Redirecting...")
                    st.rerun()
                else:
                    st.error(msg)
                    
    # Placeholders/Help
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-top: 16px; padding: 0 4px;">
            <a href="#" style="color: #2563EB; text-decoration: none;" onclick="alert('Password reset link has been simulated. Please contact Admin.')">Forgot Password?</a>
            <span style="color: #64748B;">New user? Select <b>Register</b> in the sidebar.</span>
        </div>
        """,
        unsafe_allow_html=True
    )
