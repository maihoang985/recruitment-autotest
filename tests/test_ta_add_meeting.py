"""TA bam Add a Meeting tren Application -> ghi lai popup (cac o, bat buoc, dropdown) ra output/probe_ta_meeting_popup.txt.
Giai doan tham do: KHONG tao meeting, chi mo popup roi dong lai.
Chay: .\.venv\Scripts\python.exe -m pytest tests/test_ta_add_meeting.py
"""
import os

from core import config
from core.probe import dump_page

APP_URL = config.BASE_URL + "/web#id={id}&action=739&model=hr.applicant&view_type=form&menu_id=569"


def test_probe_add_meeting_popup(login_as):
    app_id = int(os.getenv("APP_ID") or (config.OUTPUT_DIR / "last_application.txt").read_text().strip())
    p = login_as(config.TA_USER)
    p.goto(APP_URL.format(id=app_id), wait_until="domcontentloaded", timeout=config.TIMEOUT_MS * 3)
    p.locator(".o_form_view").first.wait_for(timeout=config.TIMEOUT_MS * 3)
    p.wait_for_timeout(3000)
    p.locator(".o_form_view button[name='add_meeting_room']:visible").first.click()
    dlg = p.locator(".modal-dialog:visible")
    dlg.first.wait_for(timeout=config.TIMEOUT_MS * 3)
    p.wait_for_timeout(3000)
    dump_page(p, "ta_meeting_popup")
    dlg.first.locator(".modal-header button.close").first.click()


def test_add_meeting_step2_confirm(login_as):
    """Buoc 2 tham do: bam Confirm o popup 'Create a meeting' -> ghi lai man hinh ke tiep (chua luu them gi)."""
    app_id = int(os.getenv("APP_ID") or (config.OUTPUT_DIR / "last_application.txt").read_text().strip())
    p = login_as(config.TA_USER)
    p.goto(APP_URL.format(id=app_id), wait_until="domcontentloaded", timeout=config.TIMEOUT_MS * 3)
    p.locator(".o_form_view").first.wait_for(timeout=config.TIMEOUT_MS * 3)
    p.wait_for_timeout(3000)
    p.locator(".o_form_view button[name='add_meeting_room']:visible").first.click()
    dlg = p.locator(".modal-dialog:visible")
    dlg.first.wait_for(timeout=config.TIMEOUT_MS * 3)
    dlg.first.locator("button[name='add_meeting']").first.click()
    p.wait_for_timeout(8000)
    dump_page(p, "ta_meeting_after_confirm")


def test_ta_add_meeting_in_past(login_as):
    """Phuong an A: chi giu Interviewer cua RR lam nguoi tham du, khong gui thu moi, gio hop o QUA KHU
    (hom qua 10:00-11:00) de sau do co the tao Interview Result."""
    from datetime import datetime, timedelta

    from core.odoo_api import OdooApi
    from pages.application_page import ApplicationPage

    app_id = int(os.getenv("APP_ID") or (config.OUTPUT_DIR / "last_application.txt").read_text().strip())
    api = OdooApi(config.TA_USER)
    before = api.read_one("hr.applicant", app_id, ["meet_ids"])["meet_ids"]
    day = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0) - timedelta(days=1)
    fmt = "%d/%m/%Y %H:%M:%S"
    p = login_as(config.TA_USER)
    app = ApplicationPage(p)
    app.open_existing(app_id)
    err = app.add_meeting(day.strftime(fmt), (day + timedelta(hours=1)).strftime(fmt), keep_attendee="Đặng Văn Trường")
    p.wait_for_timeout(3000)
    dump_page(p, "ta_meeting_after_save")
    after = api.read_one("hr.applicant", app_id, ["meet_ids"])["meet_ids"]
    report = [f"Ho so {app_id}", f"Meeting truoc: {before}", f"Meeting sau: {after}", f"Loi khi Save: {err or '(khong)'}"]
    for m in api.call("recruitment.interview.meeting", "read", after, fields=["display_name"]) if after else []:
        report.append(f"  {m}")
    (config.OUTPUT_DIR / f"add_meeting_{app_id}.txt").write_text("\n".join(report), encoding="utf-8")
    print("\n" + "\n".join(report))
