"""Tham do khoi 'Interview result' tren form Application (khong tao gi). Ghi output/probe_*.txt.
Chay: python -m pytest tests/test_interview_result.py -k probe
Doi tai khoan: IR_ACCOUNT=ten.tai.khoan   Doi ho so: APP_ID=...
"""
import os

from core import config
from core.probe import dump_page

APP_URL = config.BASE_URL + "/web#id={id}&action=739&model=hr.applicant&view_type=form&menu_id=569"


def test_probe_interview_result_block(login_as):
    app_id = int(os.getenv("APP_ID") or (config.OUTPUT_DIR / "last_application.txt").read_text().strip())
    user = os.getenv("IR_ACCOUNT") or config.INTERVIEWER_USER
    p = login_as(user)
    p.goto(APP_URL.format(id=app_id), wait_until="domcontentloaded", timeout=config.TIMEOUT_MS * 3)
    p.locator(".o_form_view").first.wait_for(timeout=config.TIMEOUT_MS * 3)
    p.wait_for_timeout(4000)
    blk = p.locator(".o_form_view [name='answer_ids']:visible, .o_form_view [name='multi_answer_ids']:visible")
    info = ["Tai khoan: " + user, f"So khoi answer hien: {blk.count()}"]
    info.append("Group 'Interview result' hien: " + str(p.locator(".o_form_view [name='interview_result']:visible").count()))
    for i in range(blk.count()):
        b = blk.nth(i)
        info.append(f"-- khoi {i}: name={b.get_attribute('name')}")
        info.append("   text: " + " | ".join(b.inner_text().splitlines())[:600])
        info.append("   nut/link: " + str(b.evaluate("e => [...e.querySelectorAll('button, a')].map(x => (x.getAttribute('name') || '') + ':' + (x.innerText||'').trim() + ':' + (x.className||'').slice(0,40))")))
    (config.OUTPUT_DIR / "probe_interview_result_block.txt").write_text("\n".join(info), encoding="utf-8")
    dump_page(p, "interview_result_form")
    print("\n" + "\n".join(info))


def test_probe_rr_create_result(login_as):
    """Tham do man RR: danh sach ung vien (new_rr_applicants_ids) co nut 'Create Result' khong. Khong bam gi."""
    rr_id = int(os.getenv("RR_ID") or 1799)
    user = os.getenv("IR_ACCOUNT") or config.DL_USER
    p = login_as(user)
    p.goto(f"{config.BASE_URL}/web#id={rr_id}&model=vti.resource.request&view_type=form", wait_until="domcontentloaded",
           timeout=config.TIMEOUT_MS * 3)
    p.locator(".o_form_view").first.wait_for(timeout=config.TIMEOUT_MS * 4)
    p.wait_for_timeout(5000)
    dump_page(p, "rr_form_create_result")
    box = p.locator(".o_form_view [name='new_rr_applicants_ids']:visible, .o_form_view [name='rr_applicants_ids']:visible")
    info = ["Tai khoan: " + user, f"So danh sach ung vien hien: {box.count()}"]
    for i in range(box.count()):
        b = box.nth(i)
        info.append(f"-- {b.get_attribute('name')}: " + " | ".join(b.inner_text().splitlines())[:500])
        info.append("   nut/link: " + str(b.evaluate("e => [...e.querySelectorAll('button, a')].map(x => (x.getAttribute('name') || '') + ':' + (x.innerText||'').trim())")))
    (config.OUTPUT_DIR / "probe_rr_create_result_block.txt").write_text("\n".join(info), encoding="utf-8")
    print("\n" + "\n".join(info))


def test_probe_rr_applicant_list(login_as):
    """Tham do man RR: danh sach ung vien (new_rr_applicants_ids) + cac nut tren dong. Khong bam gi."""
    rr_id = int(os.getenv("RR_ID") or 1799)
    user = os.getenv("IR_ACCOUNT") or config.DL_USER
    p = login_as(user)
    p.goto(config.BASE_URL + f"/web#id={rr_id}&model=vti.resource.request&view_type=form", wait_until="domcontentloaded",
           timeout=config.TIMEOUT_MS * 3)
    p.locator(".o_form_view").first.wait_for(timeout=config.TIMEOUT_MS * 3)
    p.wait_for_timeout(5000)
    info = ["Tai khoan: " + user, "URL: " + p.url]
    for name in ("new_rr_applicants_ids", "rr_applicants_ids"):
        blk = p.locator(f".o_form_view [name='{name}']:visible")
        info.append(f"-- {name}: hien={blk.count()}")
        if blk.count():
            b = blk.first
            info.append("   text: " + " | ".join(b.inner_text().splitlines())[:700])
            info.append("   nut/link: " + str(b.evaluate("e => [...e.querySelectorAll('button, a')].map(x => (x.getAttribute('name') || '') + ':' + (x.innerText||'').trim() + ':' + (x.className||'').slice(0,50))")))
    info.append("Cac so lieu bam duoc: " + str(p.locator(".o_form_view [name='waiting_for_result_quantity'], .o_form_view [name='interviewing_quantity'], .o_form_view [name='interviewed_quantity']").all_inner_texts()))
    (config.OUTPUT_DIR / "probe_rr_applicant_list.txt").write_text("\n".join(info), encoding="utf-8")
    dump_page(p, "rr_form")
    print("\n" + "\n".join(info))


def test_probe_create_result_click(login_as):
    """Tham do buoc 2: bam 'Create Result' tren dong ung vien cua RR -> ghi lai man ke tiep. KHONG luu gi them."""
    rr_id = int(os.getenv("RR_ID") or 1799)
    user = os.getenv("IR_ACCOUNT") or config.DL_USER
    p = login_as(user)
    p.goto(config.BASE_URL + f"/web#id={rr_id}&model=vti.resource.request&view_type=form", wait_until="domcontentloaded",
           timeout=config.TIMEOUT_MS * 3)
    p.locator(".o_form_view").first.wait_for(timeout=config.TIMEOUT_MS * 3)
    p.wait_for_timeout(4000)
    p.locator(".o_form_view [name='new_rr_applicants_ids'] button[name='view_interview_result']:visible").first.click()
    p.wait_for_timeout(8000)
    dump_page(p, "rr_after_create_result")


def test_dl_create_interview_result(login_as):
    """DL mo RR -> dong ung vien -> Create Result -> dien form -> Save (state Draft). Khong bam Pass/Fail.
    Chay: python -m pytest tests/test_interview_result.py -k dl_create"""
    from core.odoo_api import OdooApi
    from pages.application_page import ApplicationPage

    rr_id = int(os.getenv("RR_ID") or 1799)
    app_id = int(os.getenv("APP_ID") or (config.OUTPUT_DIR / "last_application.txt").read_text().strip())
    user = os.getenv("IR_ACCOUNT") or config.DL_USER
    api = OdooApi(user)
    before = api.call("vti.interview.answer", "search_read", [["applicant_id", "=", app_id]], fields=["state"])
    p = login_as(user)
    p.goto(config.BASE_URL + f"/web#id={rr_id}&model=vti.resource.request&view_type=form", wait_until="domcontentloaded",
           timeout=config.TIMEOUT_MS * 3)
    p.locator(".o_form_view").first.wait_for(timeout=config.TIMEOUT_MS * 3)
    p.wait_for_timeout(4000)
    p.locator(".o_form_view [name='new_rr_applicants_ids'] button[name='view_interview_result']:visible").first.click()
    p.locator(".o_form_view [name='vti_survey_id']:visible").first.wait_for(timeout=config.TIMEOUT_MS * 4)
    form = ApplicationPage(p)
    form._settle()

    def val(n):
        return form._value_of(n)

    report = [f"Tai khoan: {user}  RR: {rr_id}  Ho so: {app_id}", f"Truoc: {before}",
              f"Tu dien san: applicant_id='{val('applicant_id')}' resource_request_id='{val('resource_request_id')}'"]
    if not val("applicant_id"):
        form.set_field("applicant_id", "Nguyễn Văn Kiểm")
    if not val("resource_request_id"):
        form.set_field("resource_request_id", "RR01413")
    form.set_field("interview_type", "Face to Face")
    form.set_field("vti_survey_id", "VTI - KẾT QUẢ PHỎNG VẤN")
    form._settle()
    dump_page(p, "interview_result_before_save")
    new_id = form.save()
    p.wait_for_timeout(3000)
    dump_page(p, "interview_result_after_save")
    after = api.call("vti.interview.answer", "search_read", [["applicant_id", "=", app_id]], fields=["state", "vti_survey_id", "user_id"])
    report += [f"Id ban ghi moi (tu URL): {new_id}", f"Sau: {after}"]
    (config.OUTPUT_DIR / f"interview_result_{app_id}.txt").write_text("\n".join(report), encoding="utf-8")
    print("\n" + "\n".join(report))
