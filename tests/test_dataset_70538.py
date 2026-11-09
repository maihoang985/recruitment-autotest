"""Tao bang data da chot cho task cha #70538 (test #73087): moi dong mot ho so, dung o dung buoc de nguoi dung check tay.

Data: data/application/dataset_70538.json. RR: output/last_rr.txt (RR dang Open).
Chay lai an toan: dong nao da xong thi bo qua, dong loi thi lam tiep tu buoc do (output/dataset_70538_state.json).
Ket qua cho nguoi dung: python scripts/report_dataset_70538.py -> output/dataset_70538.md

Chay tat ca:  .\\.venv\\Scripts\\python.exe -m pytest tests/test_dataset_70538.py -q --tb=short
Chay 1 dong:  .\\.venv\\Scripts\\python.exe -m pytest tests/test_dataset_70538.py -q --tb=short -k D13
"""
import json
from contextlib import contextmanager
from datetime import datetime, timedelta

import pytest

from core import config, mask_check
from core.cv_maker import make_cv
from core.login import login
from core.odoo_api import OdooApi
from pages.application_page import ApplicationPage, app_data

DATA = json.loads((config.DATA_DIR / "application" / "dataset_70538.json").read_text(encoding="utf-8"))
ROWS = {r["id"]: r for r in DATA["rows"]}
ACCOUNTS = DATA["accounts"]
STATE_FILE = config.OUTPUT_DIR / "dataset_70538_state.json"
EXTRA_DIR = config.OUTPUT_DIR / "dataset_70538"
LINE_URL = config.BASE_URL + "/web#id={id}&action=758&model=hr.applicant.lines&view_type=form&menu_id=585"
VJP_HIDDEN_FIELDS = ("business_domain_id", "recruitment_type", "working_type", "market_id")
NEEDS_LINE = ("draft_line", "submitted", "accepted_meeting", "submit_now")


def _load() -> dict:
    return json.loads(STATE_FILE.read_text(encoding="utf-8")) if STATE_FILE.exists() else {}


def _save_row(rid: str, cur: dict):
    state = _load()
    state[rid] = cur
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")


def _candidate(row: dict) -> dict:
    slug = row["slug"]
    return {
        "source_id": row["source_id"], "prefix_name": row["prefix_name"], "last_name": row["last_name"],
        "first_name": row["first_name"], "date_of_birth": row.get("date_of_birth", "1996"), "expect_salary_fix": "18000000",
        "lien_he": {k: v.replace("{slug}", slug) for k, v in DATA["lien_he"].items()},
        "cv": {**DATA["cv_chung"], **DATA["noi_dung"][row.get("noi_dung", "A")], "portfolio": f"https://{slug}.dev"},
        "working_history": {"reason_detail": "Muốn tìm môi trường phát triển tốt hơn"},
    }


def _make_extra(row: dict, cand: dict):
    """File de nguoi dung tu upload tay: CV moi (D10) hoac file thay CV Masked (D11)."""
    kind = row.get("extra")
    if not kind:
        return None
    cv_data = app_data(candidate=cand)["cv"]  # lan sinh moi: SDT, email, link khac lan upload dau
    if kind == "replace_masked":
        cv_data = {**cv_data, "contacts": {"email": "Đã che thủ công"},
                   "address_lines": [{"label": "Địa chỉ", "value": "Đã che thủ công"}]}
    return str(make_cv(kind, EXTRA_DIR, cv_data, stem=f"{row['id']}_{row['slug']}")["path"])


@contextmanager
def _session(browser, user: str):
    ctx = browser.new_context()
    page = ctx.new_page()
    page.set_default_timeout(config.TIMEOUT_MS)
    try:
        login(page, user)
        yield page
    finally:
        ctx.close()


def _accept(page, line_id: int) -> list[str]:
    """Accept CV o form CV Review: hop xac nhan -> popup Accept CV. Cho moi hop dong han roi moi xet hop ke tiep."""
    page.goto(LINE_URL.format(id=line_id), wait_until="domcontentloaded", timeout=config.TIMEOUT_MS * 3)
    btn = page.locator("button[name=accept_cv_form]:visible").first
    btn.wait_for(timeout=config.TIMEOUT_MS * 3)
    btn.click()
    log, dlg = [], page.locator(".modal-dialog:visible")
    for _ in range(4):
        try:
            dlg.first.wait_for(timeout=6000)
        except Exception:
            break
        log.append(" | ".join(dlg.first.inner_text().splitlines()))
        final = dlg.first.locator("button[name=accept_cv]")
        (final.first if final.count() else dlg.first.locator(".modal-footer button.btn-primary").first).click()
        try:
            dlg.first.wait_for(state="hidden", timeout=config.TIMEOUT_MS * 3)
        except Exception:
            pass
    page.wait_for_timeout(3000)
    return log


def _mask_state(api: OdooApi, app_id: int) -> str:
    return str(api.read_one("hr.applicant", app_id, ["cv_mask_state"])["cv_mask_state"])


def _line(api: OdooApi, app_id: int) -> dict | None:
    lines = api.read_one("hr.applicant", app_id, ["applicant_line_ids"])["applicant_line_ids"]
    return api.call("hr.applicant.lines", "read", lines[:1], fields=["id", "state"])[0] if lines else None


@pytest.mark.parametrize("rid", list(ROWS))
def test_create_dataset_row(browser, rid):
    row = ROWS[rid]
    stop = row["stop"]
    user = ACCOUNTS[row["account"]]
    api = OdooApi(user)
    cur = _load().get(rid, {})
    if cur.get("done"):
        pytest.skip(f"{rid} da xong: ho so {cur['app_id']}")

    with _session(browser, user) as page:
        app = ApplicationPage(page)
        cand = _candidate(row)
        d = app_data(candidate=cand)
        d.update(row.get("form", {}))  # o rieng cua dong nay (vd Partner HRI khong co Business Domain "Khac")
        if not cur.get("app_id"):
            if row["source_id"] == "VJP":
                for k in VJP_HIDDEN_FIELDS:
                    d.pop(k, None)
            cv = make_cv(row["kind"], config.OUTPUT_DIR / "cv", d["cv"], stem=f"{rid}_{row['slug']}")
            app.open_create()
            app.fill_form(d)
            app.upload_cv(cv["files"])
            app_id = app.save()
            mask_check.save_spec(app_id, cv)
            cur.update(app_id=app_id, user=user, name=f"{d['last_name']} {d['first_name']}", files=[f.name for f in cv["files"]])
            extra = _make_extra(row, cand)
            if extra:
                cur["extra_file"] = extra
            _save_row(rid, cur)
            print(f"\n[{rid}] ho so {app_id} {cur['name']}")
        else:
            app_id = cur["app_id"]
            app.open_existing(app_id)

        if stop in NEEDS_LINE:
            rr = (config.OUTPUT_DIR / "last_rr.txt").read_text(encoding="utf-8").strip()
            cur["rr"] = rr
            if not api.call("applicant.working.history", "search_count", [["applicant_id", "=", app_id]]):
                app.add_working_history(d["working_history"])
                app.open_existing(app_id)
            if not _line(api, app_id):
                app.edit()
                app.add_review_line(rr)
                app.save()
                _save_row(rid, cur)

        if stop == "submit_now":
            before = _mask_state(api, app_id)
            changed = False
            if before != "pending":  # job che nhanh hon test -> doi file CV de ban che quay ve chua xong
                cv2 = make_cv("pdf_text", config.OUTPUT_DIR / "cv", d["cv"], stem=f"{rid}_{row['slug']}_lan2")
                app.open_existing(app_id)
                app.edit()
                app.remove_cv()
                app.upload_cv(cv2["files"])
                app.save()
                mask_check.save_spec(app_id, cv2)
                changed = True
                before = _mask_state(api, app_id)
            message = app.submit_cv_on_line()
            page.wait_for_timeout(5000)
            ln = _line(api, app_id)
            report = [f"Ho so {app_id}", f"Da doi file CV de ban che ve chua xong: {changed}",
                      f"Trang thai ban che TRUOC khi bam Submit: {before}", f"Thong bao khi Submit: {message or '(khong co)'}",
                      f"Trang thai ban che SAU Submit: {_mask_state(api, app_id)}", f"Dong Review CV sau Submit: {ln}"]
            (config.OUTPUT_DIR / f"submit_now_{app_id}.txt").write_text("\n".join(report), encoding="utf-8")
            print("\n".join(report))

        if stop in ("submitted", "accepted_meeting") and _line(api, app_id)["state"] == "draft":
            app.open_existing(app_id)
            message = app.submit_cv_on_line()
            page.wait_for_timeout(3000)
            state = _line(api, app_id)["state"]
            assert state != "draft", f"Submit CV khong thanh cong, dong van Draft. Thong bao: {message}"

    if stop == "accepted_meeting":
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

    cur["done"] = True
    _save_row(rid, cur)
