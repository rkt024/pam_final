import os
import urllib3
from dotenv import load_dotenv

# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------
load_dotenv()
VERIFY_SSL = False
if not VERIFY_SSL:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TRACKING_DB_PATH = os.getenv("TRACKING_DB_PATH", "tracking.db")


BASE_URL = "https://public.dolma.gov.np"
BASE_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0",
    "Origin": BASE_URL,
    "Referer": f"{BASE_URL}/dolma/",
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
