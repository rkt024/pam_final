import streamlit as st
import requests
from config import PAGES

def init_session_state():
    """Initializes default session state variables."""
    defaults = {
        "logged_in": False,
        "token": None,
        "user_id": None,
        "role_id": None,
        "office_id": None,
        "username": None,
        "password": None,
        "selected_page": PAGES[0],
        "table_data": None,
        "page_num": 1,
        "search_query": "",
        "expanded_row": None,
        "flash_message": None,
        "flash_type": None,
        "return_mode_ref": None,
        "http_session": requests.Session(),
        "_clear_flash_next": False,
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def show_flash():
    """Displays flash messages stored in session state."""
    msg = st.session_state.get("flash_message")
    msg_type = st.session_state.get("flash_type", "info")

    if msg:
        if msg_type == "success":
            st.success(msg)
        elif msg_type == "error":
            st.error(msg)
        elif msg_type == "warning":
            st.warning(msg)
        else:
            st.info(msg)

        # Keep message visible for one full render cycle
        if st.session_state.get("_clear_flash_next"):
            st.session_state["flash_message"] = None
            st.session_state["flash_type"] = None
            st.session_state["_clear_flash_next"] = False
        else:
            st.session_state["_clear_flash_next"] = True
