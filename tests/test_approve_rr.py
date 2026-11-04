"""Buoc 2: BOD Approve RR (code lay tu output/last_rr.txt, sinh ra o buoc 1)."""
from core import config
from pages.resource_request_page import ResourceRequestPage


def test_bod_approve_rr(login_as):
    code = (config.OUTPUT_DIR / "last_rr.txt").read_text(encoding="utf-8").strip()
    page = login_as(config.BOD_USER)
    rr = ResourceRequestPage(page)
    rr.open_rr(code)
    assert rr.status().lower() == "to approve", f"{code} dang o trang thai {rr.status()}"
    rr.approve()
    print(f"[RR] {code} -> {rr.status()}")
