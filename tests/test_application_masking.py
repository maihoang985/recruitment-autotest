"""Buoc 2-4 lo trinh Masking (#73087):
TA tao Application (Source VTI) qua giao dien -> upload CV PDF co chu -> Save
-> cho he thong che xong (BR6) -> tai CV Masked qua API -> kiem tra che dung/du (BR1-BR3, BR5).

Chay: .\\.venv\\Scripts\\python.exe -m pytest tests/test_application_masking.py
Ket qua: output/last_application.txt, output/mask_check_<id>.txt (+ ban che .pdf trong output/cv)
Ban che chua xong -> kiem tra lai sau, khong can tao lai: python scripts/check_mask.py <id>
"""
import os

from core import config, mask_check
from core.cv_maker import make_text_cv
from pages.application_page import ApplicationPage, app_data

MASK_WAIT_SECONDS = 240  # SRS: 1-2 phut


def test_ta_create_application_and_mask_cv(login_as):
    d = app_data()
    cv_file = config.OUTPUT_DIR / "cv" / f"CV_{d['first_name']}_{d['email'].split('@')[0]}.pdf"
    cv = make_text_cv(cv_file, d["cv"])

    # 1. Giao dien: tao Application + upload CV + Save
    page = login_as(config.TA_USER)
    app = ApplicationPage(page)
    app.open_create()
    app.fill_form(d)
    app.upload_cv(cv_file)
    app_id = app.save()
    (config.OUTPUT_DIR / "last_application.txt").write_text(str(app_id), encoding="utf-8")
    mask_check.save_spec(app_id, cv)
    print(f"\n[APP] id = {app_id}  {page.url}")

    # 2. API: cho ban che roi kiem tra. MASK_WAIT=0 -> chi tao data, kiem tra sau bang scripts/check_mask.py
    if os.getenv("MASK_WAIT") == "0":
        return
    problems = mask_check.run(app_id, MASK_WAIT_SECONDS)
    assert not problems, "\n".join(problems)
