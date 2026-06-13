import streamlit as st
import math
from config import PROCESS_IDS, ROWS_PER_PAGE
from services.data_service import fetch_registration_data_cached, fetch_detail_cached, do_transfer, do_return, do_verify
from services.tracking_db_service import get_checked_refs, mark_as_checked, unmark_as_checked

@st.dialog("↩️ Return Reference")
def return_dialog(ref):
    remarks = st.text_area("Remarks", value="भू सेवाबाट माग भए बमोजिम फिर्ता ।")
    c_c, c_x = st.columns(2)
    if c_c.button("✅ Confirm Return", type="primary", use_container_width=True):
        do_return(ref, remarks)
        st.rerun()
    if c_x.button("❌ Cancel", use_container_width=True):
        st.rerun()

def render_table(page_name):
    pid = PROCESS_IDS[page_name]
    is_rokka = (page_name == "Rokka/Fukuwa")
    
    # Current user for tracking isolation
    current_user = st.session_state.get("username", "Unknown")
    
    # Lazy Load Data
    if st.session_state["table_data"] is None or st.session_state.get("_last_pid") != pid:
        with st.spinner(f"Loading {page_name}..."):
            df = fetch_registration_data_cached(
                st.session_state["token"],
                st.session_state["user_id"],
                st.session_state["role_id"],
                st.session_state["office_id"],
                pid
            )
            st.session_state["table_data"] = df
            st.session_state["_last_pid"] = pid
            st.session_state["page_num"] = 1
            st.session_state["search_query"] = ""
            st.session_state["expanded_row"] = None

    df = st.session_state["table_data"]
    if df.empty:
        st.info("No records found.")
        return

    # Check refs state - USER SPECIFIC
    checked_refs = get_checked_refs(current_user) if is_rokka else set()

    # Sort and Filter Options
    col_search, col_sort = st.columns([2, 1])
    with col_search:
        search = st.text_input("🔍 Search", value=st.session_state["search_query"], key="search_input")
    
    sort_option = "All"
    if is_rokka:
        with col_sort:
            sort_option = st.selectbox("Sort by Status", ["All", "Verified Only", "Not Verified Only"], key="sort_status")

    if search:
        mask = df.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
        df = df[mask]
    st.session_state["search_query"] = search
    
    if is_rokka:
        if sort_option == "Verified Only":
            df = df[df["reference_no"].astype(str).isin(checked_refs)]
        elif sort_option == "Not Verified Only":
            df = df[~df["reference_no"].astype(str).isin(checked_refs)]
    
    total = len(df)
    total_pages = max(1, math.ceil(total / ROWS_PER_PAGE))
    st.session_state["page_num"] = max(1, min(st.session_state["page_num"], total_pages))
    
    # Pagination
    c1, _, _, c2 = st.columns([1, 2, 2, 1])
    if c1.button("⬅ Prev", disabled=st.session_state["page_num"]==1, key="btn_prev"):
        st.session_state["page_num"] -= 1; st.session_state["expanded_row"] = None; st.rerun()
    c2.text(f"Page {st.session_state['page_num']}/{total_pages} ({total} records)")
    if c2.button("Next ➡", disabled=st.session_state["page_num"]==total_pages, key="btn_next"):
        st.session_state["page_num"] += 1; st.session_state["expanded_row"] = None; st.rerun()
       
    st.download_button("📥 Export CSV", df.to_csv(index=False).encode("utf-8-sig"), f"{page_name}.csv", "text/csv", key="btn_csv")
    st.divider()

    # Table Header
    if is_rokka:
        col_defs = st.columns([1.2, 1.2, 1.2, 1.2, 1.5, 0.8])
        headers = ["Ref No", "User", "Date", "Process", "Agency", "Action"]
    else:
        col_defs = st.columns([1.2, 1.2, 1.2, 1.2, 0.8, 0.8])
        headers = ["Ref No", "User", "Date", "Process", "Action", ""]
       
    for i, h in enumerate(headers):
        col_defs[i].markdown(f"**{h}**")
    st.divider()

    # Table Rows
    start = (st.session_state["page_num"] - 1) * ROWS_PER_PAGE
    page_df = df.iloc[start:start+ROWS_PER_PAGE]
    
    for _, row in page_df.iterrows():
        ref = str(row["reference_no"])
        
        if is_rokka:
            cols = st.columns([1.2, 1.2, 1.2, 1.2, 1.5, 0.8])
        else:
            cols = st.columns([1.2, 1.2, 1.2, 1.2, 0.8, 0.8])
        
        if is_rokka and ref in checked_refs:
            # Verified green color
            cols[0].markdown(f"<span style='color: #28a745; font-weight: bold;'>✅ {ref}</span>", unsafe_allow_html=True)
        else:
            cols[0].write(ref)
           
        cols[1].write(row["username"])
        cols[2].write(row["date"])
        cols[3].write(row["process"])
        
        if is_rokka:
            cols[4].write(row.get("agency", "-") or "-")

        expanded = st.session_state.get("expanded_row") == ref
        
        if is_rokka:
            # Only the View button on the main row for Rokka to save space
            if cols[5].button("👁️ View" if not expanded else "Hide", key=f"view_{ref}", type="primary" if not expanded else "secondary", use_container_width=True):
                st.session_state["expanded_row"] = None if expanded else ref
                st.rerun()
        else:
            # For non-rokka, show Transfer and Return directly
            if cols[4].button("🔄 Transfer", key=f"tr_{ref}", use_container_width=True):
                do_transfer(ref, row["process"])
                st.rerun()
               
            if cols[5].button("↩️ Return", key=f"ret_{ref}", use_container_width=True):
                return_dialog(ref)

        # Expanded Detail (Rokka/Fukuwa Only)
        if expanded and is_rokka:
            with st.container(border=True):
                # ---------------- ACTION BAR INSIDE EXPANDED VIEW ----------------
                is_fukuwa = "fukuwa" in str(row.get("process", "")).lower()
                
                act_cols = st.columns(4)
                if is_fukuwa:
                    if act_cols[0].button("↪️ Forward", key=f"verify_{ref}", use_container_width=True):
                        do_verify(ref)
                        st.rerun()
                
                if act_cols[1].button("🔄 Transfer", key=f"ex_tr_{ref}", use_container_width=True):
                    do_transfer(ref, row["process"])
                    st.rerun()
                   
                if act_cols[2].button("↩️ Return", key=f"ex_ret_{ref}", use_container_width=True):
                    return_dialog(ref)
                   
                is_verified = ref in checked_refs
                if not is_verified:
                    if act_cols[3].button("✅ Mark Verified", key=f"mark_ver_{ref}", type="primary", use_container_width=True):
                        mark_as_checked(ref, current_user)
                        st.rerun()
                else:
                    if act_cols[3].button("❌ Unmark Verified", key=f"unmark_ver_{ref}", type="secondary", use_container_width=True):
                        unmark_as_checked(ref, current_user)
                        st.rerun()
                
                st.divider()
                
                # ---------------- REFERENCE DETAILS ----------------
                detail = fetch_detail_cached(ref, st.session_state["token"])
                if detail:
                    process = detail.get("PROCESSREGISTRATION", {})
                    prop = detail.get("PROPERTYDETAIL", [])

                    munc = "-"
                    if isinstance(prop, list) and len(prop) > 0: 
                        munc = prop[0].get("MUNCNAME_NP", "-")
                    agency_detail = "-"
                    
                    process_name = process.get("processname", " ").lower()

                    if "rokka" in process_name:
                        rokka_info = detail.get("ROKKAINFORMATION", [])
                        if isinstance(rokka_info, list) and len(rokka_info) > 0:
                            agency_detail = rokka_info[0].get("AGENCYNAME_NP", "-")
                    else:
                        fukuwa = detail.get("data", {}).get("fukuwaDetails", [])
                        if isinstance(fukuwa, list) and len(fukuwa) > 0:
                            agency_detail = fukuwa[0].get("tblrokkaagency", {}).get("agencyname_np", "-")

                    st.markdown("##### 📄 Reference Details")
                   
                    c1, c2, c3, c4 = st.columns(4)
                    c1.markdown(f"**Municipality**  \n<small>{munc}</small>", unsafe_allow_html=True)
                    c2.markdown(f"**Agency**  \n<small>{agency_detail}</small>", unsafe_allow_html=True)
                    c3.markdown(f"**Process**  \n<small>{process.get('processname', '-')}</small>", unsafe_allow_html=True)
                    c4.markdown(f"**Date**  \n<small>{process.get('dateofapplication', '-')}</small>", unsafe_allow_html=True)
                else:
                    st.error("❌ Failed to load detail data")
            st.write("") # slight spacing after expanded block