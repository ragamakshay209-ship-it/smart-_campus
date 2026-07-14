import streamlit as st
import base64
from io import BytesIO
from PIL import Image
from utils.auth import update_user_profile
from utils.helpers import load_custom_css, render_card

# Load styling
load_custom_css()

st.markdown("<h1>👤 My Profile</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748B;'>Manage your profile information, password, and avatar picture.</p>", unsafe_allow_html=True)

# Fetch session user
user = st.session_state.user

if not user:
    st.error("Authentication session error. Please log in again.")
else:
    col_profile, col_form = st.columns([1, 2])
    
    # Left Column: Profile Card & Avatar Preview
    with col_profile:
        st.markdown("### Profile Summary")
        
        avatar_html = ""
        if user.get("profile_picture"):
            avatar_src = f"data:image/png;base64,{user.get('profile_picture')}"
            avatar_html = f"""
            <div style="text-align: center; margin-bottom: 20px;">
                <img src="{avatar_src}" style="border-radius: 50%; width: 150px; height: 150px; border: 4px solid #2563EB; object-fit: cover; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);">
            </div>
            """
        else:
            role_emoji = "🛡️" if user.get("role") == "Admin" else "👨‍🏫" if user.get("role") == "Faculty" else "🎓"
            avatar_html = f"""
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="
                    font-size: 5rem; 
                    background: #2563EB15; 
                    border-radius: 50%; 
                    width: 150px; 
                    height: 150px; 
                    display: inline-flex; 
                    align-items: center; 
                    justify-content: center; 
                    border: 4px solid #2563EB;
                    color: #2563EB;
                    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
                    margin: 0 auto;
                ">
                    {role_emoji}
                </div>
            </div>
            """
        st.markdown(avatar_html, unsafe_allow_html=True)
        
        card_content = f"""
        <div style="text-align: center; font-size: 0.95rem;">
            <h4 style="margin: 0 0 4px 0; font-size: 1.25rem;">{user.get('name')}</h4>
            <span style="background: #2563EB15; color:#2563EB; font-weight:600; font-size: 0.8rem; padding: 3px 10px; border-radius: 12px; text-transform: uppercase;">{user.get('role')}</span>
            <p style="color: #64748B; margin-top: 15px; margin-bottom: 0;">✉️ {user.get('email')}</p>
        </div>
        """
        render_card("User Badge", card_content)
        
    # Right Column: Update forms
    with col_form:
        st.markdown("### Edit Profile Details")
        
        with st.form("update_profile_form"):
            new_name = st.text_input("Full Name", value=user.get("name"))
            
            st.markdown("<p style='font-size:0.85rem; color:#64748B; margin-bottom:0;'>Change Password (leave blank to keep current):</p>", unsafe_allow_html=True)
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                new_pw = st.text_input("New Password", type="password", placeholder="••••••••")
            with col_p2:
                new_pw_confirm = st.text_input("Confirm New Password", type="password", placeholder="••••••••")
                
            # Profile picture upload
            uploaded_file = st.file_uploader("Upload Avatar / Profile Picture", type=["png", "jpg", "jpeg"])
            
            submit_update = st.form_submit_button("Save Changes")
            
            if submit_update:
                profile_pic_b64 = None
                if uploaded_file is not None:
                    try:
                        # Compress image to save database space (JSON limits)
                        img = Image.open(uploaded_file)
                        img = img.resize((150, 150))
                        buffered = BytesIO()
                        # Convert all uploads to PNG
                        img.save(buffered, format="PNG")
                        profile_pic_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
                    except Exception as e:
                        st.error(f"Image processing error: {e}")
                
                # Validation checks
                if not new_name.strip():
                    st.error("Full Name cannot be empty.")
                elif new_pw and len(new_pw.strip()) < 6:
                    st.error("New password must be at least 6 characters.")
                elif new_pw != new_pw_confirm:
                    st.error("New passwords do not match.")
                else:
                    # If no new photo uploaded, carry over existing profile picture
                    photo = profile_pic_b64 if profile_pic_b64 else user.get("profile_picture")
                    
                    success, msg, updated_user = update_user_profile(
                        user.get("email"), 
                        new_name, 
                        password=new_pw, 
                        profile_picture_base64=photo
                    )
                    
                    if success:
                        st.session_state.user = updated_user
                        st.success("Success! Profile settings saved.")
                        st.rerun()
                    else:
                        st.error(msg)
