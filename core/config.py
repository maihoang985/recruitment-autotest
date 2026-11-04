"""Doc cau hinh tu file .env o thu muc goc project."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

BASE_URL = os.getenv("BASE_URL", "https://vms-ta.stg.vti.com.vn").rstrip("/")
DEFAULT_PASSWORD = os.getenv("DEFAULT_PASSWORD", "")
TA_USER = os.getenv("TA_USER", "")              # Rec User
DL_USER = os.getenv("DL_USER", "")
BOD_USER = os.getenv("BOD_USER", "")
REVIEWER_USER = os.getenv("REVIEWER_USER", "")
INTERVIEWER_USER = os.getenv("INTERVIEWER_USER", "")
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
TIMEOUT_MS = int(os.getenv("TIMEOUT_SECONDS", "20")) * 1000

DATA_DIR = ROOT / "data"
CV_SAMPLES_DIR = DATA_DIR / "cv_samples"
OUTPUT_DIR = ROOT / "output"
AUTH_DIR = ROOT / ".auth"
