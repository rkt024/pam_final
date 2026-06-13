import streamlit as st
from services.data_service import do_transfer, do_return

def dashboard_page():
    st.title("🏛️ DOLMA Dashboard")
    st.markdown("Welcome to the DOLMA Portal Dashboard. Use the Quick Response tool below for fast actions.")
    st.write("") # small spacing

    # Compact centered quick response section
    left, center, right = st.columns([1, 2, 1])

    with center:
        st.markdown("### ⚡ Quick Response")
        with st.container(border=True):
            # Use columns to group related inputs horizontally
            inp_col1, inp_col2 = st.columns(2)
            
            with inp_col1:
                t_id = st.text_input(
                    "Reference No.",
                    max_chars=7,
                    placeholder="Enter 7 digits",
                    key="dash_ref"
                )
                
            with inp_col2:
                t_type = st.selectbox(
                    "Type",
                    ["Rokka", "Fukuwa", "Others"], index=2,
                    key="dash_type"
                )

            remarks = st.text_area(
                "Remarks",
                value="भू सेवाबाट माग भए बमोजिम फिर्ता ।",
                height=68,
                key="dash_remarks"
            )

            is_valid = t_id.isdigit() and len(t_id) == 7

            if t_id and not is_valid:
                st.warning("⚠️ Enter exactly 7 digits")

            btn_col1, btn_col2 = st.columns(2)

            # TRANSFER
            if btn_col1.button(
                "🔄 Transfer",
                use_container_width=True,
                type="primary"
            ):
                if not is_valid:
                    st.warning("Enter valid 7-digit ID")
                else:
                    do_transfer(t_id, t_type)
                    st.rerun()

            # RETURN
            if btn_col2.button(
                "↩️ Return",
                use_container_width=True
            ):
                if not is_valid:
                    st.warning("Enter valid 7-digit ID")
                elif not remarks.strip():
                    st.warning("Remarks cannot be empty")
                else:
                    do_return(t_id, remarks)
                    st.rerun()
