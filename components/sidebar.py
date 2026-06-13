import streamlit as st
from config import PAGES

def toggle_theme():
    if st.session_state.theme == "light":
        st._config.set_option("theme.base", "dark")
        st.session_state.theme = "dark"
    else:
        st._config.set_option("theme.base", "light")
        st.session_state.theme = "light"

def sidebar():
    if "theme" not in st.session_state:
        st.session_state.theme = "light"

    st.sidebar.title("🏛️ DOLMA Portal")
    st.sidebar.caption(f"👤 {st.session_state.get('username', '')}")
    st.sidebar.divider()
    
    selected = st.sidebar.radio("📂 Workspaces", PAGES, key="nav_radio", index=PAGES.index(st.session_state["selected_page"]))
    st.session_state["selected_page"] = selected
    
    # Reset state on page switch
    if selected != st.session_state.get("_last_page_rendered"):
        st.session_state["_last_page_rendered"] = selected
        st.session_state["table_data"] = None
        st.session_state["page_num"] = 1
        st.session_state["expanded_row"] = None
        
    st.sidebar.divider()
    
    # Theme toggler
    theme_icon = "🌙 Switch to Dark Mode" if st.session_state.theme == "light" else "☀️ Switch to Light Mode"
    st.sidebar.button(theme_icon, on_click=toggle_theme, use_container_width=True)

    if st.sidebar.button("🧹 Clear Cache", key="btn_cache", use_container_width=True): 
        st.cache_data.clear()
        st.sidebar.success("Cache cleared")
        
    if st.sidebar.button("🚪 Logout", key="btn_logout", use_container_width=True): 
        st.session_state.clear()
        st.rerun()
