"""Sua Reviewer/Interviewer cua RR dang Draft cho dung data roi Submit, khong tao RR moi.
Dang nhap bang DL cua RR (STG khong cho nguoi khac Submit thay).

Chay: $env:RR_CODE="RR01415"; $env:RR_DATA="rr_70538.json"; $env:RR_DL="dang.nguyenhuu"
      .\\.venv\\Scripts\\python.exe -m pytest tests/test_rr_set_people.py -q --tb=short
Thanh cong -> ghi ma RR vao output/last_rr.txt de buoc Approve dung tiep.
"""
import os

from core import config
from pages.resource_request_page import ResourceRequestPage, rr_data


def test_set_people_and_submit(login_as):
    code = os.environ["RR_CODE"]
    d = rr_data(os.environ["RR_DATA"])
    page = login_as(os.environ["RR_DL"])
    rr = ResourceRequestPage(page)
    rr.open_rr(code)
    status = rr.status().lower()
    assert status in ("draft", "to approve"), f"{code} dang o trang thai {rr.status()}"
    page.locator(".o_form_button_edit:visible").click()
    page.locator(".o_form_view.o_form_editable").wait_for()
    for label, key in (("Reviewer", "reviewer"), ("Interviewer", "interviewer")):
        rr._ensure_tag(label, d[key])
    rr.save()
    if status == "draft":
        rr.submit()
    (config.OUTPUT_DIR / "last_rr.txt").write_text(code, encoding="utf-8")
    print(f"\n[RR] {code} -> {rr.status()}")
