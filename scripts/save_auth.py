"""Dang nhap ngam bang core.login va luu phien vao .auth/<username>.json.
Dung cho codegen.ps1 de mo codegen da dang nhap san.
    python scripts/save_auth.py truong.dangvan
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from playwright.sync_api import sync_playwright  # noqa: E402

from core import config  # noqa: E402
from core.login import login  # noqa: E402


def save_auth(username: str) -> Path:
    config.AUTH_DIR.mkdir(exist_ok=True)
    out = config.AUTH_DIR / f"{username}.json"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="chromium")
        context = browser.new_context()
        login(context.new_page(), username)
        context.storage_state(path=str(out))
        browser.close()
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Cach dung: save_auth.py <username>")
    print(f"[AUTH] Da luu: {save_auth(sys.argv[1])}")
