import streamlit as st
import requests as req_lib
from config import BASE_URL, BASE_HEADERS, VERIFY_SSL

def api_call(url, method="POST", **kwargs):
    """Makes a request. If 401/403, relogs in and retries ONCE."""
    session = st.session_state["http_session"]
    token = st.session_state.get("token")
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    kwargs["headers"] = headers
    kwargs.setdefault("timeout", 60)
    kwargs.setdefault("verify", VERIFY_SSL)
    
    try:
        res = session.request(method, url, **kwargs)
        if res.status_code in (401, 403):
            u, p = st.session_state.get("username"), st.session_state.get("password")
            if u and p:
                login_res = session.post(
                    f"{BASE_URL}/pam/api/auth/login",
                    headers=BASE_HEADERS,
                    json={"usernameOrEmail": u, "password": p, "remember": True},
                    timeout=60, verify=VERIFY_SSL
                )
                if login_res.ok and login_res.json().get("status"):
                    new_token = login_res.json()["data"]["accessToken"]
                    st.session_state["token"] = new_token
                    headers["Authorization"] = f"Bearer {new_token}"
                    kwargs["headers"] = headers
                    res = session.request(method, url, **kwargs)
        return res
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

def login_api(username, password):
    try:
        # Use a fresh session for login to avoid any session-level header issues
        with req_lib.Session() as fresh_session:
            fresh_session.headers.update(BASE_HEADERS)
            res = fresh_session.post(
                f"{BASE_URL}/pam/api/auth/login",
                json={"usernameOrEmail": username, "password": password, "remember": True},
                timeout=60,
                verify=VERIFY_SSL
            )
        
        if not res or res.status_code != 200:
            st.error(f"Server Error: {res.status_code if res else 'No Response'}")
            return False
        data = res.json()
        if not data.get("status"):
            st.error(f"Invalid username or password — {data.get('message', '')}")
            return False
            
        user = data["data"]["user"]
        roles = user.get("roles", [])
        role_id = roles[0].get("roleId") if roles else None
        if not role_id:
            st.error("No valid role assigned")
            return False
            
        st.session_state.update({
            "token": data["data"]["accessToken"],
            "user_id": user.get("userId"),
            "office_id": user.get("officeId"),
            "role_id": role_id,
            "username": username, "password": password, "logged_in": True
        })
        return True
    except req_lib.exceptions.ConnectTimeout:
        st.error("Connection timed out. The server may be slow or unreachable. Please try again.")
        return False
    except req_lib.exceptions.ReadTimeout:
        st.error("Server took too long to respond. Please try again.")
        return False
    except req_lib.exceptions.ConnectionError as e:
        st.error(f"Cannot connect to server: {e}")
        return False
    except Exception as e:
        st.error(f"Login Error: {e}")
        return False
