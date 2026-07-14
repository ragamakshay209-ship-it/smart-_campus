import os
import streamlit as st
from email_validator import validate_email, EmailNotValidError

def is_valid_email(email: str) -> bool:
    """Validates if an email address is format-compliant."""
    try:
        # Check email structure; do not require SMTP deliverability checks
        validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False

def load_custom_css():
    """Reads custom stylesheet assets/style.css and injects it into streamlit."""
    css_path = "assets/style.css"
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
            
    # Inject Theme dynamic overrides based on session state
    theme = st.session_state.get("theme", "light")
    if theme == "dark":
        st.markdown(
            """
            <style>
                /* Dark Mode custom overrides */
                .stApp {
                    background-color: #0F172A !important;
                    color: #F8FAFC !important;
                }
                .main-card {
                    background-color: #1E293B !important;
                    color: #F8FAFC !important;
                    border: 1px solid #334155 !important;
                }
                div[data-testid="stMetricValue"] {
                    color: #F8FAFC !important;
                }
                div[data-testid="stMarkdownContainer"] p {
                    color: #E2E8F0 !important;
                }
                h1, h2, h3, h4, h5, h6 {
                    color: #FFFFFF !important;
                }
                /* Style inputs inside forms */
                input, select, textarea {
                    background-color: #1E293B !important;
                    color: #F8FAFC !important;
                    border: 1px solid #475569 !important;
                }
            </style>
            """,
            unsafe_allow_html=True
        )

def render_metric_card(title, value, emoji, color="#2563EB"):
    """Renders a custom HTML metric card with glassmorphism hover effects."""
    theme = st.session_state.get("theme", "light")
    
    # Theme specific coloring
    bg_color = "#FFFFFF" if theme == "light" else "#1E293B"
    text_color = "#1E293B" if theme == "light" else "#FFFFFF"
    sub_color = "#64748B" if theme == "light" else "#94A3B8"
    border_color = "rgba(0, 0, 0, 0.05)" if theme == "light" else "rgba(255, 255, 255, 0.05)"
    
    card_html = f"""
<div style="
    background-color: {bg_color};
    padding: 24px;
    border-radius: 16px;
    box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.05);
    border: 1px solid {border_color};
    border-left: 6px solid {color};
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
" class="metric-card">
    <div>
        <p style="color: {sub_color}; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; margin: 0 0 6px 0; letter-spacing: 0.5px;">{title}</p>
        <h3 style="color: {text_color}; font-size: 2rem; font-weight: 700; margin: 0; line-height: 1;">{value}</h3>
    </div>
    <div style="font-size: 2.5rem; background-color: {color}15; padding: 12px; border-radius: 12px; display: flex; align-items: center; justify-content: center;">
        {emoji}
    </div>
</div>
"""
    # Strip leading whitespace on all lines to prevent markdown code block detection
    clean_html = "\n".join([line.strip() for line in card_html.split("\n")])
    st.markdown(clean_html, unsafe_allow_html=True)

def render_card(title, content_html, color=None):
    """Renders a generic stylized content card."""
    theme = st.session_state.get("theme", "light")
    bg_color = "#FFFFFF" if theme == "light" else "#1E293B"
    text_color = "#1E293B" if theme == "light" else "#FFFFFF"
    border_color = "rgba(0, 0, 0, 0.05)" if theme == "light" else "rgba(255, 255, 255, 0.05)"
    border_top = f"border-top: 4px solid {color};" if color else ""
    
    # Strip any leading spaces from the inner content
    clean_content = "\n".join([line.strip() for line in content_html.split("\n")])
    
    card_html = f"""
<div style="
    background-color: {bg_color};
    padding: 24px;
    border-radius: 16px;
    box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.05);
    border: 1px solid {border_color};
    {border_top}
    margin-bottom: 20px;
">
    <h4 style="color: {text_color}; margin: 0 0 16px 0; font-size: 1.15rem; font-weight: 600; display: flex; align-items: center; gap: 8px;">{title}</h4>
    <div style="color: {text_color};">
        {clean_content}
    </div>
</div>
"""
    clean_card = "\n".join([line.strip() for line in card_html.split("\n")])
    st.markdown(clean_card, unsafe_allow_html=True)
