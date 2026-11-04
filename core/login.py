"""Dang nhap Odoo (VMS TA). Locator lay theo project vms-ta-auto."""
from playwright.sync_api import Page, expect

from core import config


def login(page: Page, username: str, password: str | None = None) -> Page:
    password = password or config.DEFAULT_PASSWORD
    if not username or not password:
        raise ValueError("Thieu username/password. Kiem tra file .env (TA_USER, DEFAULT_PASSWORD).")

    for attempt in range(5):  # STG cham / trang login tu dieu huong them 1 lan -> thu lai
        try:
            page.goto(f"{config.BASE_URL}/web/login", wait_until="commit", timeout=config.TIMEOUT_MS * 3)
        except Exception:
            page.wait_for_timeout(3000)  # goto bi ngat boi lan dieu huong thu 2: ke, chi can thay o dang nhap
        try:
            page.locator("#login").wait_for(timeout=config.TIMEOUT_MS * 2)
            break
        except Exception:
            if attempt == 4:
                raise
    page.locator("#login").fill(username)
    page.locator("#password").fill(password)
    page.locator(".oe_login_buttons button[type='submit']").click()

    error = page.locator(".oe_login_form .alert-danger")
    page.wait_for_function(
        "() => !location.pathname.startsWith('/web/login') "
        "|| document.querySelector('.oe_login_form .alert-danger')",
        timeout=config.TIMEOUT_MS * 4,
    )
    if error.count() > 0:
        raise AssertionError(f"Dang nhap that bai [{username}]: {error.inner_text().strip()}")

    # Khong cho navbar o day: sau login Odoo mo Helpdesk, khong lien quan. Trang can dung tu cho menu cua no.
    print(f"[LOGIN] OK: {username}")
    return page
