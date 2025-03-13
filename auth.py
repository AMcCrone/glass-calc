# auth.py
import streamlit as st
from config import PASSWORD

def check_password():
    """Check the password input against the secret password."""
    if st.session_state.get("password_input") == PASSWORD:
        st.session_state["authenticated"] = True
    else:
        st.error("Incorrect password.")

def ensure_authenticated():
    """Display password prompt and halt if not authenticated."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        st.text_input("Enter Password:", type="password", key="password_input", on_change=check_password)
        st.stop()
