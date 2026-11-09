"""Task #73336/#73337: tao ho so tren RR rieng de kiem chung lo hong sua luong OL.

Data: data/application/offer_73336.json. Trang thai: output/offer_73336_state.json.
Chay lai an toan: buoc nao xong thi bo qua, buoc loi thi lam tiep tu do.

Chay: .\\.venv\\Scripts\\python.exe -m pytest tests/test_offer_73336.py -q --tb=short -k A
"""
import json
import os
import re
from datetime import datetime, timedelta

import pytest

from core import config
from core.cv_maker import make_cv
from core.odoo_api import OdooApi
from core.probe import dump_page
from pages.application_page import ApplicationPage, app_data
from test_dataset_70538 import _accept, _candidate, _line, _session

DATA = json.loads((config.DATA_DIR / "application" / "offer_73336.json").read_text(encoding="utf-8"))
ROWS = {r["id"]: r for r in DATA["rows"]}
ACCOUNTS = DATA["accounts"]
STATE_FILE = config.OUTPUT_DIR / "offer_73336_state.json"


def _load() -> dict:
    return json.loads(STATE_FILE.read_text(encoding="utf-8")) if STATE_FILE.exists() else {}


def _save_row(rid: str, cur: dict):
    state = _load()
    state[rid] = cur
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")


def _open_until(page, url: str, target, probe_name: str, attempts: int = 3):
    """Mo url va cho dung phan tu can dung. Sau dang nhap Odoo co luc de trang mac dinh len url vua mo -> mo lai."""
    for attempt in range(attempts):
        page.goto(url, wait_until="domcontentloaded", timeout=config.TIMEOUT_MS * 3)
        try:
            target.wait_for(timeout=config.TIMEOUT_MS * 2)
            return
        except Exception:
            if attempt == attempts - 1:
                dump_page(page, probe_name)
                raise
            page.reload(wait_until="domcontentloaded", timeout=config.TIMEOUT_MS * 3)
            page.wait_for_timeout(3000)


@pytest.mark.parametrize("rid", list(ROWS))
def test_application_to_meeting(browser, rid):
    """TA tao ho so -> Working History -> dong Review CV -> Submit CV -> DL Accept -> Add a Meeting."""
    row = ROWS[rid]
    user = ACCOUNTS[row["account"]]
    api = OdooApi(user)
    cur = _load().get(rid, {})

    with _session(browser, user) as page:
        app = ApplicationPage(page)
        d = app_data(candidate=_candidate(row))
        if not cur.get("app_id"):
            cv = make_cv(row["kind"], config.OUTPUT_DIR / "cv", d["cv"], stem=f"offer73336_{rid}_{row['slug']}")
            app.open_create()
            app.fill_form(d)
            app.upload_cv(cv["files"])
            cur.update(app_id=app.save(), user=user, rr=DATA["rr"], name=f"{d['last_name']} {d['first_name']}")
            _save_row(rid, cur)
            print(f"\n[{rid}] ho so {cur['app_id']} {cur['name']}")
        else:
            app.open_existing(cur["app_id"])
        app_id = cur["app_id"]

        if not api.call("applicant.working.history", "search_count", [["applicant_id", "=", app_id]]):
            app.add_working_history(d["working_history"])
            app.open_existing(app_id)
        if not _line(api, app_id):
            app.edit()
            app.add_review_line(DATA["rr"])
            app.save()
        if _line(api, app_id)["state"] == "draft":
            app.open_existing(app_id)
            message = app.submit_cv_on_line()
            page.wait_for_timeout(3000)
            state = _line(api, app_id)["state"]
            assert state != "draft", f"Submit CV khong thanh cong, dong van Draft. Thong bao: {message}"

    ln = _line(api, app_id)
    if ln["state"] == "submit":
        with _session(browser, ACCOUNTS["DL_ACCEPT"]) as page:
            cur["accept_log"] = _accept(page, ln["id"])
        _save_row(rid, cur)
        state = _line(api, app_id)["state"]
        assert state == "accept", f"Accept CV khong thanh cong, dong dang {state}. Hop thoai: {cur['accept_log']}"

    if not api.read_one("hr.applicant", app_id, ["meet_ids"])["meet_ids"]:
        people = OdooApi(ACCOUNTS["INTERVIEWER"])
        name = people.call("res.users", "read", [people.uid], fields=["name"])[0]["name"]
        day = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0) - timedelta(days=1)
        fmt = "%d/%m/%Y %H:%M:%S"
        with _session(browser, user) as page:
            app = ApplicationPage(page)
            app.open_existing(app_id)
            err = app.add_meeting(day.strftime(fmt), (day + timedelta(hours=1)).strftime(fmt), keep_attendee=name)
            page.wait_for_timeout(3000)
        assert api.read_one("hr.applicant", app_id, ["meet_ids"])["meet_ids"], f"Khong tao duoc Meeting: {err}"

    cur["meeting_done"] = True
    _save_row(rid, cur)
    print(f"\n[{rid}] ho so {app_id}: da co Meeting, dong Review CV = {_line(api, app_id)['state']}")


@pytest.mark.parametrize("rid", list(ROWS))
def test_create_interview_result(browser, rid):
    """DL mo RR -> dong ung vien -> Create Result -> dien form -> Save (Draft). Ghi man hinh de biet buoc sau."""
    cur = _load()[rid]
    app_id = cur["app_id"]
    user = ACCOUNTS["INTERVIEWER"]
    api = OdooApi(user)
    fields = ["state", "stage_interview", "interview_result", "offer_status", "line_ids", "vti_survey_id"]
    found = api.call("vti.interview.answer", "search_read", [["applicant_id", "=", app_id]], fields=fields)
    if found:
        print(f"\n[{rid}] da co ket qua phong van: {found}")
        return
    rr_id = api.call("vti.resource.request", "search", [["code", "=", DATA["rr"]]])[0]
    with _session(browser, user) as page:
        btn = page.locator(".o_form_view [name='new_rr_applicants_ids'] button[name='view_interview_result']:visible").first
        _open_until(page, f"{config.BASE_URL}/web#id={rr_id}&model=vti.resource.request&view_type=form", btn,
                    "offer73336_rr_no_button")
        dump_page(page, "offer73336_rr_before_result")
        btn.click()
        page.locator(".o_form_view [name='vti_survey_id']:visible").first.wait_for(timeout=config.TIMEOUT_MS * 4)
        form = ApplicationPage(page)
        form._settle()
        if not form._value_of("applicant_id"):
            form.set_field("applicant_id", cur["name"])
        if not form._value_of("resource_request_id"):
            form.set_field("resource_request_id", DATA["rr"])
        form.set_field("interview_type", "Face to Face")
        form.set_field("vti_survey_id", "VTI - KẾT QUẢ PHỎNG VẤN")
        form._settle()
        dump_page(page, "offer73336_result_before_save")
        cur["answer_id"] = form.save()
        _save_row(rid, cur)
        page.wait_for_timeout(3000)
        dump_page(page, "offer73336_result_after_save")
    print(f"\n[{rid}] ket qua: {api.call('vti.interview.answer', 'search_read', [['applicant_id', '=', app_id]], fields=fields)}")


def _open_result_form(page, api, answer_id: int):
    """Vao form ket qua tu dong ung vien tren RR (mo thang URL thi Odoo dung form khac)."""
    rr_id = api.call("vti.resource.request", "search", [["code", "=", DATA["rr"]]])[0]
    row_btn = page.locator(".o_form_view button[name='view_interview_result']:visible").first
    _open_until(page, f"{config.BASE_URL}/web#id={rr_id}&model=vti.resource.request&view_type=form", row_btn,
                "offer73336_rr_no_button")
    row_btn.click()
    page.locator(".o_form_view [name='applicant_id']:visible").first.wait_for(timeout=config.TIMEOUT_MS * 2)
    page.wait_for_timeout(3000)
    assert f"id={answer_id}" in page.url, f"Form dang mo khong phai ket qua {answer_id}: {page.url}"


def _fill_score_line(page, modal, item: dict):
    """Dien 1 cau cua phieu: tim nhan roi lay o tra loi dang hien ngay sau nhan do."""
    # Moi cau co du cac o answer_* nhung chi 1 o hien, nen ghep theo thu tu: nhan thu i <-> o dang hien thu i
    labels = [t.strip() for t in modal.locator("[name='label_html']:visible").all_inner_texts()]
    index = next(i for i, t in enumerate(labels) if t.startswith(item["label"]))
    field = modal.locator("[name^='answer_']:visible").nth(index)
    name = field.get_attribute("name")
    value = item.get("value")
    if "days" in item:
        value = (datetime.now() + timedelta(days=item["days"])).strftime("%d/%m/%Y")
    if name == "answer_select":
        inp = field.locator("input").first
        inp.click()
        options = page.locator("ul.ui-autocomplete:visible li a")
        options.first.wait_for(timeout=15000)
        (options.filter(has_text=value).first if value else options.first).click()
        page.wait_for_timeout(500)
    elif name == "answer_date":
        inp = field if field.evaluate("e => e.tagName.toLowerCase()") == "input" else field.locator("input").first
        inp.click()
        inp.fill(value)
        inp.press("Enter")
    else:
        field.fill(value)
    return name, value


def _fill_offer_popup(page, form, modal, offer: dict):
    """Popup Nhap Offer: chon cac o radio theo dung chu tren nhan, roi nhap muc luong va tien te."""
    for name in ("object_type", "offer_options"):
        modal.locator(f"[name='{name}'] label").filter(has_text=re.compile(rf"^\s*{re.escape(offer[name])}\s*$")).first.click()
        page.wait_for_timeout(800)
    form.set_field("salary_rate", offer["salary_rate"])  # o nay la <select>, khong phai radio
    for name in ("offer_min", "offer_max"):
        modal.locator(f"input[name='{name}']:visible").first.fill(str(offer[name]))
    form.set_field("currency_id", offer["currency"])
    modal.locator("[name='note_offer']:visible").first.fill(offer["note"])
    page.wait_for_timeout(1000)


@pytest.mark.parametrize("rid", list(ROWS))
def test_fill_score_popup(browser, rid):
    """Mo phieu danh gia vong 1 (link Edit), dien cac cau bat buoc, bam Save trong popup."""
    cur = _load()[rid]
    answer_id, user = cur["answer_id"], ACCOUNTS["INTERVIEWER"]
    api = OdooApi(user)
    score = DATA["phieu_danh_gia"]
    with _session(browser, user) as page:
        _open_result_form(page, api, answer_id)
        page.locator(".o_form_view [name='multi_interview_answer']").get_by_text("Edit", exact=True).first.click()
        modal = page.locator(".modal-dialog:visible").first
        modal.locator("[name='label_html']").first.wait_for(timeout=config.TIMEOUT_MS * 2)
        form = ApplicationPage(page)
        form._scope = ".modal-dialog"
        form.set_field("interview_type", score["interview_type"])
        if not modal.locator("[name='interviewer_ids'] .badge").filter(has_text=score["interviewer"]).count():
            form.set_field("interviewer_ids", score["interviewer"])  # da chon roi thi khong con trong danh sach
        filled = [_fill_score_line(page, modal, item) for item in score["cau"]]
        dump_page(page, "offer73336_score_before_save")
        score_btn = os.getenv("SCORE_BTN")  # nut bam thay cho Save trong popup phieu, vd action_final_result
        if not score_btn:
            modal.locator("button[name='get_view_interview']").click()
            page.wait_for_timeout(6000)
            dump_page(page, "offer73336_score_after_save")
        else:
            modal.locator(f"button[name='{score_btn}']").click()
            page.wait_for_timeout(10000)
            boxes = page.locator(".modal-dialog:visible")
            print(f"\n[POPUP SAU {score_btn}] {[' | '.join(boxes.nth(i).inner_text().splitlines())[:400] for i in range(boxes.count())]}")
            dump_page(page, f"offer73336_after_{score_btn}")
            print("[SAU NUT]", api.read_one("vti.interview.answer", answer_id,
                                            ["state", "interview_result", "stage_interview", "permission_send_dl", "permission_submit"]))
            print("[UNG VIEN]", api.read_one("hr.applicant", cur["app_id"], ["stage_id"]))
            if os.getenv("OFFER_CONFIRM"):
                _fill_offer_popup(page, form, boxes.first, DATA["offer"])
                dump_page(page, "offer73336_offer_before_confirm")
                boxes.first.locator("button[name='confirm_submit_interview']").click()
                confirm = boxes.filter(has_text="Submit interview result").last
                confirm.wait_for(timeout=config.TIMEOUT_MS * 2)
                confirm.locator(".modal-footer button.btn-primary").first.click()  # chi bam 1 lan
                confirm.wait_for(state="hidden", timeout=config.TIMEOUT_MS * 3)
                page.wait_for_timeout(10000)
                print(f"[POPUP SAU CONFIRM] {[' | '.join(boxes.nth(i).inner_text().splitlines())[:300] for i in range(boxes.count())]}")
                dump_page(page, "offer73336_after_offer_confirm")
                print("[SAU CONFIRM]", api.read_one("vti.interview.answer", answer_id,
                                                    ["state", "interview_result", "stage_interview", "offer_min", "offer_max",
                                                     "permission_send_dl", "permission_send_sm", "is_noti_dl"]))
                print("[UNG VIEN]", api.read_one("hr.applicant", cur["app_id"], ["stage_id"]))
    print(f"\n[{rid}] da dien: {filled}")
    print(f"[SAU] dong phieu: {len(api.read_one('vti.interview.answer', answer_id, ['line_ids'])['line_ids'])}")


def test_click_answer_button(browser):
    """Bam 1 nut tren form Ket qua phong van. Hop Confirmation thi xac nhan 1 lan; popup nhap lieu thi dung, ghi lai.
    Bien moi truong: BTN (bat buoc), ACT_USER (mac dinh Interviewer), RID (mac dinh A)."""
    rid = os.getenv("RID", "A")
    btn_name = os.environ["BTN"]
    user = os.getenv("ACT_USER") or ACCOUNTS["INTERVIEWER"]
    cur = _load()[rid]
    fields = ["state", "stage_interview", "interview_result", "offer_status", "is_noti_dl", "permission_submit",
              "permission_send_dl", "permission_send_sm"]
    api = OdooApi(user)
    answer_id = cur["answer_id"]
    print(f"\n[TRUOC] {api.read_one('vti.interview.answer', answer_id, fields)}")
    log = []
    with _session(browser, user) as page:
        # Phai vao tu dong ung vien tren RR: mo thang URL thi Odoo dung form 1680, khong co nut Pass/Fail cua luong RR
        rr_id = api.call("vti.resource.request", "search", [["code", "=", DATA["rr"]]])[0]
        # Co ket qua roi thi RR doi tu bang new_rr_applicants_ids sang rr_applicants_ids -> tim nut o bang nao cung duoc
        row_btn = page.locator(".o_form_view button[name='view_interview_result']:visible").first
        _open_until(page, f"{config.BASE_URL}/web#id={rr_id}&model=vti.resource.request&view_type=form", row_btn,
                    "offer73336_rr_no_button")
        row_btn.click()
        if os.getenv("DRY"):  # chi mo form va ghi lai cac nut, khong bam gi
            page.locator(".o_form_view [name='applicant_id']:visible").first.wait_for(timeout=config.TIMEOUT_MS * 2)
            page.wait_for_timeout(4000)
            dump_page(page, "offer73336_form_dry")
            return
        btn = page.locator(f".o_form_view button[name='{btn_name}']:visible").first
        try:
            btn.wait_for(timeout=config.TIMEOUT_MS * 2)
        except Exception:
            dump_page(page, f"offer73336_no_{btn_name}")
            raise
        page.wait_for_timeout(2000)
        if f"id={answer_id}" not in page.url:
            dump_page(page, f"offer73336_wrong_record_{btn_name}")
            raise AssertionError(f"Form dang mo khong phai ket qua {answer_id}: {page.url}")
        btn.click()
        dlg = page.locator(".modal-dialog:visible")
        for _ in range(4):
            try:
                dlg.first.wait_for(timeout=8000)
            except Exception:
                break
            text = " | ".join(dlg.first.inner_text().splitlines())
            log.append(text)
            if not text.startswith("Confirmation"):
                break
            dlg.first.locator(".modal-footer button.btn-primary").first.click()
            dlg.first.wait_for(state="hidden", timeout=config.TIMEOUT_MS * 3)
        page.wait_for_timeout(4000)
        dump_page(page, f"offer73336_after_{btn_name}")
    print(f"[HOP THOAI] {log}")
    print(f"[SAU] {api.read_one('vti.interview.answer', answer_id, fields)}")
    print(f"[UNG VIEN] {api.read_one('hr.applicant', cur['app_id'], ['stage_id'])}")
