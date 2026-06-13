import streamlit as st
from services.data_service import fetch_ref_status

def check_ref_status_page():
    st.title("🔍 Check Ref Status")
    
    with st.container(border=True):
        search_ref = st.text_input(
            "Reference No.",
            key="search_ref_input_page",
            placeholder="Enter Reference No."
        )
        
        if st.button("Search", type="primary", use_container_width=True, key="search_ref_btn_page"):
            if not search_ref.strip():
                st.warning("Please enter a reference number")
            else:
                with st.spinner("Fetching data..."):
                    data = fetch_ref_status(search_ref.strip())
                    if not data:
                        st.error("Reference not found")
                    else:
                        st.session_state["ref_status_data"] = data
        
        # Display results if available
        if "ref_status_data" in st.session_state and st.session_state["ref_status_data"]:
            data = st.session_state["ref_status_data"]
            
            # Helper for case-insensitive and flexible key lookup
            def get_v(d, keys, default="N/A"):
                if not isinstance(d, dict): return default
                # Create a lowercased dictionary for case-insensitive matching
                d_lower = {k.lower(): v for k, v in d.items()}
                for k in keys:
                    if k.lower() in d_lower:
                        val = d_lower[k.lower()]
                        return val if val is not None else default
                return default

            with st.container(border=True):
                # 1. Application Summary Section
                inner_data = get_v(data, ['data'], {})
                office_val = get_v(inner_data, ['OFFICE', 'officename', 'office_name', 'office'])
                created_by_val = get_v(inner_data, ['CREATEDBY', 'created_by', 'username'])
                process_val = get_v(inner_data, ['PROCESSNAME_NP', 'processname', 'process'])
                subprocess_val = get_v(inner_data, ['SUBPROCESS_NP', 'subprocessname', 'subprocess'])
                created_at_val = get_v(inner_data, ['CREATEDAT', 'created_at', 'createddate', 'date'])
                app_status_val = get_v(inner_data, ['APPLICATIONSTATUS', 'status'])
                status_code = {
                    "1" : "SD  मा पेश गरिएको ।",
                    "6" : "चेकरबाट मेकरमा 'फिर्ता' आएको छ ।",
                    "8" : "'चेकरको' मा पठाइएको छ ।",
                    "30" : "LRIMS मा 'ट्रान्सफर्ड' भैसक्यो ।",
                    "31" : "भु-सेवा / मेकरको 'ड्राफ्टमा' छ ।",
                    "32" : "बैँकले 'रुजु' गराउन SD मा पठाएको छ ।",
                    "33" : "SD ले बैँको 'एप्रुभरको' मा पठाएको छ ।"
                }
                status_message = status_code.get(str(app_status_val), "स्थिति उपलब्ध छैन ।")
                lrims_refno = get_v(inner_data, ['DOLMA_REFERENCENO'])
                
                dolma_status = get_v(data, ['dolma_status'], {})
                uploaded_by = "-"
                uploaded_date = "-"

                if isinstance(dolma_status, dict):
                    tameli_detail = dolma_status.get("tameli", [])

                    if isinstance(tameli_detail, list) and tameli_detail:
                        first_record = tameli_detail[0]

                        if isinstance(first_record, dict):
                            uploaded_by = first_record.get("sequenceno", "-")
                            uploaded_date = first_record.get("uploadeddate", "-")
                
                # 1. Main Details Header
                st.markdown(f"#### 🏢 {office_val} <span style='font-size:14px; color:gray;'>(पेश गरिने कार्यालय)</span>", unsafe_allow_html=True)
                
                # Fetch all statuses first
                dolma_status = get_v(data, ['dolma_status', 'dolmastatus'], {})
                reg_no = get_v(dolma_status, ['REGISTRATIONNO', 'registration_no'], get_v(data, ['REGISTRATIONNO', 'registration_no']))
                lrims_status = get_v(dolma_status, ['APPLICATIONSTATUS', 'status'])

                # Grid Layout 1
                c1, c2, c3, c4 = st.columns(4)
                c1.markdown(f"**👤 जारी गर्ने व्यक्ति:**<br><small>{created_by_val}</small>", unsafe_allow_html=True)
                c2.markdown(f"**📅 मिति:**<br><small>{created_at_val}</small>", unsafe_allow_html=True)
                c3.markdown(f"**📋 प्रक्रिया:**<br><small>{process_val}</small>", unsafe_allow_html=True)
                c4.markdown(f"**📎 उप-प्रकार:**<br><small>{subprocess_val}</small>", unsafe_allow_html=True)

                st.write("")
                
                # Grid Layout 2
                c1, c2, c3, c4 = st.columns(4)
                c1.markdown(f"**🔖 LRIMS Ref:**<br><small>{lrims_refno}</small>", unsafe_allow_html=True)
                c2.markdown(f"**📌 स्थिति:**<br><span style='color:#1f77b4; font-weight:bold; font-size:14px;'>{status_message}</span>", unsafe_allow_html=True)
                c3.markdown(f"**🏦 LRIMS Status:**<br><small>{lrims_status}</small>", unsafe_allow_html=True)
                c4.markdown(f"**🔢 Reg No:**<br><small>{reg_no}</small>", unsafe_allow_html=True)

                st.write("")

                # Upload Info
                c1, c2 = st.columns(2)
                c1.markdown(f"<small>**📅 तामेली अपलोड मितिः** {uploaded_date}</small>", unsafe_allow_html=True)
                c2.markdown(f"<small>**👤 अपलोड गर्नेः** {uploaded_by}</small>", unsafe_allow_html=True)
                
                st.write("")
                
                # 3. Timeline / Status History Section
                history = get_v(data, ['dataStatusDetail', 'datastatusdetail'], [])
                if history and isinstance(history, list):
                    with st.expander(f"📜 पछिल्ला स्थितिहरुको विवरण ({len(history)} Updates)", expanded=False):
                        for idx, item in enumerate(history):
                            status_code = get_v(item, ["APPLICATIONSTATUS", "applicationstatuscode", "status"])
                            desc = get_v(item, ["DESCRIPTION", "description"])
                            uname = get_v(item, ["USERNAME", "username"])
                            
                            raw_date = get_v(item, ["CREATEDDATE", "createdat", "date"])
                            cdate = raw_date
                            if isinstance(raw_date, str) and "T" in raw_date:
                                try:
                                    import datetime
                                    dt = datetime.datetime.strptime(raw_date.split(".")[0], "%Y-%m-%dT%H:%M:%S")
                                    dt += datetime.timedelta(hours=5, minutes=45) # Convert UTC to NPT
                                    cdate = dt.strftime("%Y-%m-%d %H:%M:%S")
                                except:
                                    pass
                            
                            st.markdown(f"<small><b>{cdate}</b> | {status_code} | {desc} (by {uname})</small>", unsafe_allow_html=True)
                            if idx < len(history) - 1:
                                st.markdown("<hr style='margin: 0.5em 0; border: 0; border-top: 1px solid #ddd;'>", unsafe_allow_html=True)
                            
            with st.expander("🔍 Debug: View Raw Response Data"):
                st.json(data)
