import streamlit as st
from utils.api import login_api

def login_page():
    # Simple UI Styling
    st.markdown("""
        <style>
        /* Keep sidebar hidden during login */
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
        header { visibility: hidden; }
        </style>
    """, unsafe_allow_html=True)

    # Vertical centering spacer
    for _ in range(3):
        st.write("")

    _, col, _ = st.columns([1, 1.2, 1])
    
    with col:
        st.markdown("<h1 style='text-align: center;'>🏛️ DOLMA</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Department of Land Management and Archive</p>", unsafe_allow_html=True)
        
        st.write("") # Spacer

        with st.container(border=True):
            st.markdown("### 🔐 Secure Login")
            with st.form("login_form"):
                username = st.text_input("Username", key="login_user", placeholder="Enter your username")
                password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")
                
                st.write("") # Spacer
                submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")
                if submitted:
                    if not username or not password:
                        st.warning("⚠️ Please enter both username and password")
                    else:
                        with st.spinner("Authenticating..."):
                            if login_api(username, password):
                                st.success("✅ Login successful")
                                st.rerun()
