import streamlit as st

# Reset login session state variables
st.session_state.logged_in = False
st.session_state.user = None

# Success feedback & direct navigation trigger back to Login page
st.success("You have been successfully logged out.")
st.switch_page("pages/Login.py")
