r"""Them Working History cho cac ho so DA TAO o batch (khong tao ho so moi).
Mac dinh: moi ho so ghi trong output/batch_masking.md chua co dong Working History nao.
Chay tat ca:   .\.venv\Scripts\python.exe -m pytest tests/test_add_working_history.py
Chay 1 ho so:  $env:APP_ID="32726"; $env:CODE="CV01"; .\.venv\Scripts\python.exe -m pytest tests/test_add_working_history.py
"""
import os
import re

import pytest

from core import config
from core.odoo_api import OdooApi
from pages.application_page import ApplicationPage, app_data

VJP_USER = "trung.phambao"  # nguoi cong ty VJP tao ho so VJP (xem test_masking_batch.py)


def _targets() -> list[tuple[str, int]]:
    if os.getenv("APP_ID"):
        return [(os.getenv("CODE", "CV01"), int(os.environ["APP_ID"]))]
    rows = []
    for line in (config.OUTPUT_DIR / "batch_masking.md").read_text(encoding="utf-8").splitlines():
        c = [x.strip() for x in line.split("|")]
        m = re.search(r"\(id (\d+)\)", c[5]) if len(c) > 6 and c[2].startswith("CV") else None
        if m:
            rows.append((c[2], int(m.group(1))))
    return list(dict.fromkeys(rows))


@pytest.mark.parametrize("code,app_id", _targets())
def test_add_working_history(login_as, code, app_id):
    user = VJP_USER if code == "CV08" else config.TA_USER
    if OdooApi(user).call("applicant.working.history", "search_count", [["applicant_id", "=", app_id]]):
        pytest.skip(f"Ho so {app_id} da co Working History")
    d = app_data(candidate=code)
    api = OdooApi(user)
    page = login_as(user)
    app = ApplicationPage(page)
    for attempt in range(3):  # STG cham/treo giua chung -> lam lai, nhung chi khi ho so van chua co Working History
        try:
            app.open_existing(app_id)
            app.add_working_history(d["working_history"])
            break
        except Exception as e:
            if api.call("applicant.working.history", "search_count", [["applicant_id", "=", app_id]]):
                break  # da luu duoc roi (loi xay ra sau khi Save) -> khong them lan 2
            if attempt == 2:
                raise
            print(f"[{code}] lan {attempt + 1} loi ({type(e).__name__}): {chr(32).join(str(e).split())[:400]}")
            page.wait_for_timeout(10000)
            try:
                page.reload(wait_until="domcontentloaded")  # bo popup cu con ket lai
            except Exception:
                pass
    print(f"[{code}] ho so {app_id}: da them Working History, ly do = {d['working_history']['reason_detail']}")
