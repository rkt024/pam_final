import os
import socket
import urllib3
from dotenv import load_dotenv

# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------
load_dotenv()
VERIFY_SSL = False
if not VERIFY_SSL:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Data directory - can be overridden via env var for Docker volumes
DATA_DIR = os.getenv("DATA_DIR", os.path.join(os.path.dirname(__file__), "data"))
os.makedirs(DATA_DIR, exist_ok=True)

TRACKING_DB_PATH = os.getenv("TRACKING_DB_PATH", os.path.join(DATA_DIR, "tracking.db"))


# DOLMA API Configuration
# Streamlit Cloud (AWS) DNS cannot resolve public.dolma.gov.np.
# We connect by IP and send the hostname via the Host header.
_DOLMA_HOSTNAME = "public.dolma.gov.np"
_DOLMA_IP = None


def _resolve_dolma_ip():
    """Resolve public.dolma.gov.np to IP, with hardcoded fallback.
    Uses a short timeout to avoid blocking on unreachable DNS (e.g. Streamlit Cloud)."""
    global _DOLMA_IP
    if _DOLMA_IP:
        return _DOLMA_IP
    # Set a short timeout for DNS resolution to avoid hanging
    socket.setdefaulttimeout(3)
    try:
        _DOLMA_IP = socket.gethostbyname(_DOLMA_HOSTNAME)
    except Exception:
        _DOLMA_IP = "202.45.146.50"  # fallback — update if server IP changes
    finally:
        socket.setdefaulttimeout(None)  # reset to default (no timeout)
    return _DOLMA_IP


DOLMA_IP = _resolve_dolma_ip()
BASE_URL = f"https://{DOLMA_IP}"
BASE_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0",
    "Origin": f"https://{_DOLMA_HOSTNAME}",
    "Referer": f"https://{_DOLMA_HOSTNAME}/dolma/",
    "Host": _DOLMA_HOSTNAME,
    "user-type": "3"
}

PAGES = [
    "Dashboard",
    "Check Ref Status",
    "Rokka/Fukuwa",
    "Likhat Parit",
    "Samsodan",
    "Halsabik",
    "Namsari",
    "Pratilipi",
    "Guthi Adhinastha",
    "Dakhil Kharej",
    "Apartment",
    "Jagga Darta"
]

PROCESS_IDS = {
    "Likhat Parit": "1", "Jagga Darta": "2", "Namsari": "3", "Dakhil Kharej": "4",
    "Samsodan": "5", "Halsabik": "7", "Rokka/Fukuwa": "8,15", "Apartment": "16",
    "Pratilipi": "21", "Guthi Adhinastha": "22"
}

ROWS_PER_PAGE = 7
