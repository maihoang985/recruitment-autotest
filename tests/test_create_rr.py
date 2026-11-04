"""Buoc 1: DL tao RR -> Save (Draft) -> Submit (To approve). In ra Code RR, ghi vao output/last_rr.txt.
Doi file data: RR_DATA=rr_pure_roles.json (mac dinh rr_default.json, nam trong data/rr/)."""
import os

from core import config
from pages.resource_request_page import ResourceRequestPage, rr_data


def test_dl_create_and_submit_rr(login_as):
    page = login_as(config.DL_USER)
    rr = ResourceRequestPage(page)
    rr.open_create()
    rr.fill_form(rr_data(os.getenv("RR_DATA") or "rr_default.json"))
    rr.save()
    rr.submit()
    code = rr.code()
    (config.OUTPUT_DIR / "last_rr.txt").write_text(code, encoding="utf-8")
    print(f"\n[RR] Code = {code}")
