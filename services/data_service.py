import streamlit as st
import pandas as pd
from utils.api import api_call
from config import BASE_URL

@st.cache_data(ttl=300)
def fetch_registration_data_cached(token, user_id, role_id, office_id, pid):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "pid": pid,
        "statusid": 1,
        "userid": user_id,
        "roleid": role_id,
        "officeid": office_id
    }
    
    if pid == "8,15":
        payload.update({
            "dateFrom": "",
            "dateTo": "",
            "district": "",
            "kitta": "",
            "munVdc": "",
            "phoneno": "",
            "refNo": "",
            "type": "bank_submitted"
        })
        
    res = api_call(f"{BASE_URL}/pam/app/allregprocess", json=payload, headers=headers)
    if not res or res.status_code != 200:
        return pd.DataFrame()
        
    data = res.json().get("data", [])
    if not data:
        return pd.DataFrame()
        
    df = pd.DataFrame([{
        "reference_no": r.get("referenceno"),
        "username": r.get("username"),
        "date": r.get("dateofapplication"),
        "process": r.get("processname"),
        "agency": r.get("rokkaagency")
    } for r in data])
    
    df["reference_no"] = pd.to_numeric(df["reference_no"], errors="coerce").astype("Int64")
    return df.sort_values("reference_no", ascending=False).reset_index(drop=True)

@st.cache_data(ttl=600)
def fetch_detail_cached(ref, token):
    headers = {"Authorization": f"Bearer {token}"}
    res = api_call(f"{BASE_URL}/pam/app/rokka/application/detail/{ref}", headers=headers)
    if res and res.status_code == 200:
        return res.json().get("data")
    return None

def do_transfer(ref, process_name):
    pn = (process_name or "").lower()

    if "rokka" in pn:
        url = f"{BASE_URL}/pam/app/rokka/data/send/{ref}"
        method = "POST"
    elif "fukuwa" in pn:
        url = f"{BASE_URL}/pam/app/fukuwa/data/send/{ref}"
        method = "GET"
    else:
        url = f"{BASE_URL}/pam/app/all/data/send/{ref}"
        method = "POST"

    res = api_call(
        url,
        method=method,
        json={} if method == "POST" else None
    )

    if res and res.ok:
        d = res.json()
        if d.get("status"):
            ref_no = d.get("data", {}).get("referenceNo", "N/A")
            st.session_state["flash_message"] = f"✅ Transfer Successful | Ref No: {ref_no}"
            st.session_state["flash_type"] = "success"
        else:
            st.session_state["flash_message"] = f"❌ Failed: {d.get('message', 'Unknown Error')}"
            st.session_state["flash_type"] = "error"
    else:
        st.session_state["flash_message"] = f"❌ Transfer Error: {res.status_code if res else 'No Response'}"
        st.session_state["flash_type"] = "error"

def do_return(ref, remarks):
    url = f"{BASE_URL}/pam/app/submit/deed/application/{ref}/6"
    res = api_call(
        url,
        json={"remarks": remarks}
    )

    if res and res.ok:
        d = res.json()
        if d.get("status"):
            st.session_state["flash_message"] = f"✅ Returned Successfully | ID: {d.get('data')}"
            st.session_state["flash_type"] = "success"
        else:
            st.session_state["flash_message"] = f"❌ Failed: {d.get('message', 'Unknown Error')}"
            st.session_state["flash_type"] = "error"
    else:
        st.session_state["flash_message"] = f"❌ Return Error: {res.status_code if res else 'No Response'}"
        st.session_state["flash_type"] = "error"

def do_verify(ref):
    url = f"{BASE_URL}/pam/app/submit/deed/application/{ref}/33"
    res = api_call(url)

    if res and res.ok:
        d = res.json()
        if d.get("status"):
            st.session_state["flash_message"] = f"✅ Verified Successfully | ID: {d.get('data')}"
            st.session_state["flash_type"] = "success"
        else:
            st.session_state["flash_message"] = f"❌ Failed: {d.get('message', 'Unknown Error')}"
            st.session_state["flash_type"] = "error"
    else:
        st.session_state["flash_message"] = f"❌ Verify Error: {res.status_code if res else 'No Response'}"
        st.session_state["flash_type"] = "error"

def fetch_ref_status(ref_no):
    url = f"{BASE_URL}/pam/app/refrencedetails/{ref_no}"
    res = api_call(url, method="GET")
    if res and res.ok:
        data = res.json()
        if data.get("status"):
            return data
    return None
