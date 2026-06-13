import streamlit as st

st.set_page_config(page_title="DOLMA Office Portal", page_icon="🏛️", layout="wide")

from utils.state import init_session_state, show_flash
from components.sidebar import sidebar
from components.table import render_table
from pages.login import login_page
from pages.dashboard import dashboard_page
from pages.check_ref_status import check_ref_status_page
from services.tracking_db_service import init_tracking_db

# Initialize state early to check login status
init_session_state()

# Global Styles and Conditional Sidebar Hiding
if not st.session_state.get("logged_in", False):
    hide_sidebar_style = """
        <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="collapsedControl"] { display: none; }
        </style>
    """
    st.markdown(hide_sidebar_style, unsafe_allow_html=True)

st.markdown("""
<style>
/* Hide top multipage navigation */
[data-testid="stSidebarNav"] {
    display: none;
}

/* Optional: remove extra top spacing */
[data-testid="stSidebarContent"] {
    padding-top: 1rem;
}

/* Custom UI Tweaks */
/* Smooth button transitions */
button {
    transition: all 0.2s ease-in-out !important;
}

/* Improve container styling */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 8px !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
}

/* Tweak text inputs to look slightly better */
[data-testid="stTextInput"] input {
    border-radius: 6px !important;
}
</style>
""", unsafe_allow_html=True)

def main():
    # State is already initialized above
    init_tracking_db()

    if not st.session_state["logged_in"]:
        login_page()
        return

    sidebar()
    show_flash()

    selected = st.session_state["selected_page"]

    if selected == "Dashboard":
        dashboard_page()
    elif selected == "Check Ref Status":
        check_ref_status_page()
    else:
        render_table(selected)

if __name__ == "__main__":
    main()