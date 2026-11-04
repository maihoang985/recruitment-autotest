"""Man hinh Applications (hr.applicant, form view 4899) - Odoo 12.

Locator theo thuoc tinh name cua o (lay tu scripts/inspect_model.py), khong dung id dong:
    char/integer : input[name=X]      selection : select[name=X]
    many2one/tags: div[name=X] input  date      : div[name=X] input
    file (many2many_binary): div[name=X] input[type=file]
"""
import json
import random
import re
import time
import uuid
from datetime import date, timedelta

from playwright.sync_api import Page, expect

from core import config

FORM_URL = f"{config.BASE_URL}/web#action=739&model=hr.applicant&view_type=form&menu_id=569"
DATE_FMT = "%d/%m/%Y"
DROPDOWN_ITEM = "ul.ui-autocomplete:visible li.ui-menu-item a"
SKIP_KEYS = {"cv", "expect_ob_days", "working_history"}

# Popup hien ra khi dien form (API khong bao truoc, phat hien khi chay). Chu trong popup -> nut se bam.
KNOWN_POPUPS = {
    # Chon Current Company -> hoi them vao Working History. Test Masking khong can -> Cancel.
    "add this company to the Working History": "Cancel",
}


def _expand(value: str, tag: str) -> str:
    """{tag} -> 4 ky tu ngau nhien, {n3}/{n4} -> 3/4 chu so ngau nhien (moi vi tri mot so khac)."""
    value = value.replace("{tag}", tag)
    return re.sub(r"\{n(\d)\}", lambda m: "".join(random.choice("0123456789") for _ in range(int(m.group(1)))), value)


def app_data(file: str = "app_default.json", candidate: str | None = None, **override) -> dict:
    """Doc data/application/<file>, sinh SDT/email/link moi (khong trung ung vien cu).
    candidate="CV01": lay ung vien do trong data/application/candidates.json (ten, lien he, noi dung CV)."""
    d = json.loads((config.DATA_DIR / "application" / file).read_text(encoding="utf-8"))
    d = {k: v for k, v in d.items() if not k.startswith("_")}
    if candidate:
        cand = json.loads((config.DATA_DIR / "application" / "candidates.json").read_text(encoding="utf-8"))[candidate]
        for k in ("source_id", "prefix_name", "last_name", "first_name", "date_of_birth", "expect_salary_fix"):
            d[k] = cand[k]
        d["cv"] = {**d["cv"], **cand["cv"]}
        d["working_history"] = {**d["working_history"], **cand.get("working_history", {})}
    d.update(override)
    tag = uuid.uuid4().hex[:4]
    d["expect_ob_date"] = (date.today() + timedelta(days=d["expect_ob_days"])).strftime(DATE_FMT)
    full_name = f"{d['last_name']} {d['first_name']}"
    if candidate:
        contacts = {k: _expand(v, tag) for k, v in cand["lien_he"].items()}
        d["email"] = contacts["email"]
        mobile = re.sub(r"\D", "", contacts["phone"])  # o Mobile = SDT trong CV, dang 0xxxxxxxxx
        d["partner_mobile"] = "0" + mobile[2:] if contacts["phone"].startswith("+84") else mobile
        d["cv"] = {**d["cv"], "full_name": full_name, "dob": d["date_of_birth"], "contacts": contacts,
                   "phone": contacts["phone"], "email": d["email"]}
        return d
    s = f"{int(time.time()) % 10_000_000:07d}"  # 7 chu so cuoi SDT
    d["email"] = f"auto.mask.{tag}@gmail.com"
    d["partner_mobile"] = f"098{s}"
    d["cv"] = {
        **d["cv"],
        "full_name": full_name,
        "dob": d["date_of_birth"],
        "phone": f"098 {s[:4]} {s[4:]}",   # cung so voi o Mobile, co dau cach
        "phone_intl": f"+84 97 {s}",
        "email": d["email"],
        "github": f"https://github.com/automask{tag}",
        "linkedin": f"https://www.linkedin.com/in/automask{tag}",
    }
    return d


class ApplicationPage:
    def __init__(self, page: Page):
        self.page = page
        self._scope = ".o_form_view"  # doi thanh popup khi dien o trong hop thoai (trung ten o voi form chinh)

    # ---------- helpers ----------
    def _el(self, name: str):
        return self.page.locator(f"{self._scope} [name='{name}']:visible").first

    def _close_dropdown(self):
        """Dong danh sach goi y va CHO den khi no thuc su yen (STG cham: ket qua tim kiem cu co the tra ve muon
        va mo lai danh sach -> o ke tiep bi che / bam nham vao danh sach do)."""
        menu = self.page.locator("ul.ui-autocomplete:visible")
        for _ in range(4):
            try:
                menu.first.wait_for(state="hidden", timeout=2000)
            except Exception:
                self.page.keyboard.press("Escape")
                menu.first.wait_for(state="hidden", timeout=5000)
            self.page.wait_for_timeout(800)  # co ket qua tre khong? neu danh sach mo lai -> dong tiep
            if not menu.count():
                return

    def _pick(self, inp, value: str):
        """many2one / many2many tags: go chu -> chon dong trung khop (uu tien khop dung ca chu)."""
        try:  # STG co o tu dien san (vd chon Current Company -> tu dien Business Domain): da dung gia tri thi bo qua
            if inp.input_value().strip().lower() == value.strip().lower():
                return
        except Exception:
            pass
        tags = inp.locator("xpath=ancestor::*[contains(@class,'o_field_many2manytags')][1]//span[contains(@class,'badge')]")
        if tags.filter(has_text=re.compile(rf"^\s*{re.escape(value)}\s*$", re.I)).count():
            return  # o nhieu gia tri da co tag nay roi -> khong chon them (tranh tag trung)
        items = self.page.locator(DROPDOWN_ITEM)
        exact = items.filter(has_text=re.compile(rf"^\s*{re.escape(value)}\s*$", re.I))
        contains = items.filter(has_text=value)
        for attempt in range(3):  # STG cham / onchange o truoc chua xong -> go lai
            inp.click()
            if inp.input_value():  # o dang rong thi khong xoa: moi lan fill la mot lan tim kiem, ket qua cu ve muon se de len
                inp.fill("")
            inp.fill(value)
            try:
                exact.or_(contains).first.wait_for(timeout=10000)
                break
            except Exception:
                if attempt == 2:
                    raise
        (exact if exact.count() else contains).first.click()
        self._close_dropdown()

    def _handle_popup(self, wait: int = 1500):
        """Popup hien ra sau khi chon gia tri (onchange). Da biet -> bam nut tuong ung; la -> dung lai."""
        if self._scope != ".o_form_view":  # dang dien o trong popup cua minh -> khong phai popup la
            return
        dlg = self.page.locator(".modal-dialog:visible")
        try:
            dlg.first.wait_for(timeout=wait)
        except Exception:
            return
        text = dlg.first.inner_text()
        for key, button in KNOWN_POPUPS.items():
            if key in text:
                print(f"[POPUP] '{key}' -> {button}")
                dlg.first.locator(".modal-footer button", has_text=button).first.click()
                dlg.first.wait_for(state="hidden")
                return
        raise AssertionError("Popup chua biet: " + " | ".join(text.split("\n")))

    def set_field(self, name: str, value: str):
        self._handle_popup(wait=300)  # popup tu o truoc co the hien MUON (STG cham) va che o nay
        el = self._el(name)
        el.wait_for()
        tag = el.evaluate("e => e.tagName.toLowerCase()")
        cls = el.get_attribute("class") or ""
        if tag == "select":
            opts = el.locator("option").all_inner_texts()
            label = next((o for o in opts if o.strip().lower() == value.lower()), None) \
                or next((o for o in opts if value.lower() in o.lower()), None)
            if label is None:
                raise AssertionError(f"O '{name}' khong co lua chon '{value}'. Co: {opts}")
            el.select_option(label=label)
        elif tag in ("input", "textarea"):
            el.fill(str(value))
        elif "o_datepicker" in cls:
            inp = el.locator("input").first
            inp.click()
            inp.fill(value)
            inp.press("Enter")
        elif "o_field_many2one" in cls or "o_field_many2manytags" in cls:
            self._pick(el.locator("input").first, value)
        else:
            raise AssertionError(f"Chua ho tro loai o '{name}' (class={cls})")
        self._handle_popup()

    # ---------- flow ----------
    def open_create(self):
        for attempt in range(3):  # STG cham / trang trang -> thu lai
            try:
                self.page.goto(FORM_URL, wait_until="domcontentloaded", timeout=config.TIMEOUT_MS * 3)
                self.page.locator(".o_form_view.o_form_editable").wait_for(timeout=config.TIMEOUT_MS * 2)
                return
            except Exception:
                if attempt == 2:
                    raise

    def _settle(self):
        """STG cham: onchange tra ve muon se ghi de len o da dien -> cho mang yen roi moi di tiep."""
        try:
            self.page.wait_for_load_state("networkidle", timeout=30000)
        except Exception:
            pass
        self.page.wait_for_timeout(2000)
        self._handle_popup(wait=1500)

    def _value_of(self, name: str) -> str:
        """O char/select: chinh phan tu la input/select. O many2one/date: input nam ben trong div."""
        try:
            el = self._el(name)
            if el.evaluate("e => ['input', 'select', 'textarea'].includes(e.tagName.toLowerCase())", timeout=3000):
                return el.input_value(timeout=3000).strip()
            return el.locator("input, select").first.input_value(timeout=3000).strip()
        except Exception:
            return ""

    def fill_form(self, d: dict):
        todo = {k: v for k, v in d.items() if k not in SKIP_KEYS and v not in (None, "")}
        for name, value in todo.items():
            self.set_field(name, value)
        # Kiem tra lai: o nao bi onchange tre ghi de thanh trong -> dien lai (toi da 3 lan)
        simple = [k for k in todo if k not in ("language_ids",)]
        for _ in range(3):
            self._settle()
            empty = [k for k in simple if not self._value_of(k)]
            if not empty:
                return
            print(f"[FORM] o bi trong sau onchange, dien lai: {empty}")
            for k in empty:
                self.set_field(k, todo[k])
        self._settle()

    def upload_cv(self, paths):
        """paths: 1 file hoac list file (nhieu file CV cung luc)."""
        paths = [paths] if not isinstance(paths, (list, tuple)) else list(paths)
        box = self._el("cv_attachment_ids")
        box.locator("input[type='file']").set_input_files([str(p) for p in paths])
        for p in paths:
            expect(box).to_contain_text(p.name, timeout=60000)
        # Ten file hien ngay khi dang upload -> cho het icon dang tai + cho nut xoa (chi hien khi da gan xong)
        expect(box.locator(".o_attachment_uploading, .fa-spin")).to_have_count(0, timeout=120000)
        try:
            expect(box.locator(".oe_attachment .oe_delete")).to_have_count(len(paths), timeout=15000)
        except AssertionError:
            (config.OUTPUT_DIR / "dbg_attachment_box.html").write_text(box.inner_html(), encoding="utf-8")
            raise
        self.page.wait_for_timeout(1500)

    def remove_cv(self):
        """Xoa het file trong o CV Attachment (de upload lai). Can dang o che do Edit."""
        box = self._el("cv_attachment_ids")
        dels = box.locator(".oe_attachment .oe_delete, .o_delete, .fa-times")
        while dels.count():
            dels.first.click()
            self.page.wait_for_timeout(500)

    def open_existing(self, app_id: int):
        url = f"{config.BASE_URL}/web#id={app_id}&action=739&model=hr.applicant&view_type=form&menu_id=569"
        for attempt in range(3):  # STG cham / mang doi (ERR_NETWORK_CHANGED) -> thu lai
            try:
                self.page.goto(url, wait_until="domcontentloaded", timeout=config.TIMEOUT_MS * 3)
                self.page.locator(".o_form_view").wait_for(timeout=config.TIMEOUT_MS * 2)
                return
            except Exception:
                if attempt == 2:
                    raise
                self.page.wait_for_timeout(5000)

    def edit(self):
        self.page.locator(".o_form_button_edit:visible").click()
        self.page.locator(".o_form_view.o_form_editable").wait_for()

    # ---------- Review CV (BR7, BR8) ----------
    def add_review_line(self, rr_code: str):
        """Tab Review CV: Add a line -> chon RR. Chua Save form."""
        box = self.page.locator(".o_form_view [name='applicant_line_ids']:visible").first
        box.locator("a:has-text('Add a line')").first.click()
        row = box.locator("tr.o_selected_row").first
        row.wait_for()
        cell = row.locator("td[data-name='resource_request_id'] input, [name='resource_request_id'] input").first
        self._pick(cell, rr_code)
        return box

    def submit_cv_on_line(self) -> str:
        """Bam Submit CV tren dong Review CV dau tien -> xac nhan hop thoai.
        Tra ve noi dung thong bao/loi he thong hien ra (rong = khong co popup loi)."""
        p = self.page
        btn = p.locator(".o_form_view [name='applicant_line_ids'] button[name='submit_cv']:visible").first
        btn.wait_for(timeout=config.TIMEOUT_MS)
        btn.click()
        out = []
        for _ in range(3):  # hop xac nhan -> (co the) hop loi E_002
            dlg = p.locator(".modal-dialog:visible")
            try:
                dlg.first.wait_for(timeout=4000)
            except Exception:
                break
            text = " | ".join(dlg.first.inner_text().splitlines())
            out.append(text)
            ok = dlg.first.locator(".modal-footer button.btn-primary, .modal-footer button:has-text('Ok'), .modal-footer button:has-text('OK')").first
            ok.click()
            try:  # cho hop thoai dong han roi moi xet hop thoai ke tiep (tranh bam Confirm 2-3 lan khi STG cham)
                dlg.first.wait_for(state="hidden", timeout=config.TIMEOUT_MS * 3)
            except Exception:
                pass
            p.wait_for_timeout(1500)
        return " || ".join(out)

    def save(self) -> int:
        p = self.page
        p.locator(".o_form_button_save:visible").click()
        edit = p.locator(".o_form_button_edit:visible")
        problem = p.locator(".modal-dialog:visible, .o_notification:visible")
        edit.or_(problem).first.wait_for(timeout=config.TIMEOUT_MS * 2)
        if not edit.count():
            raise AssertionError("Save bi chan: " + problem.first.inner_text())
        m = re.search(r"[#&]id=(\d+)", p.url)
        if not m:
            raise AssertionError(f"Khong lay duoc id tu URL: {p.url}")
        return int(m.group(1))

    # ---------- Working History (Submit CV bat buoc phai co) ----------
    def add_working_history(self, d: dict):
        """Bam Add Working History (can ho so da Save) -> dien popup -> Save popup.
        d: current_company_id, company_size, package, business_domain_id, personal_healthcare, project_scale,
           role_project_ta_ids, reason_resignation_job_id, reason_detail."""
        p = self.page
        p.locator(".o_form_view button[name='action_open_add_working_history']:visible").first.click()
        dlg = p.locator(".modal-dialog:visible")
        dlg.first.wait_for(timeout=config.TIMEOUT_MS * 2)
        self._scope = ".modal-dialog:visible .o_form_view"
        try:
            for name, value in d.items():
                self.set_field(name, value)
            self._settle()
            # STG tu dien san 2 tag "Others" (2 ban ghi trung ten) khi mo popup -> giu 1 tag, xoa tag trung ten
            tags = p.locator(".modal-dialog:visible [name='role_project_ta_ids'] .badge")
            texts = [t.strip() for t in tags.all_inner_texts()]
            for i in range(len(texts) - 1, 0, -1):
                if texts[i] in texts[:i]:
                    tags.nth(i).locator(".o_delete").click()
                    p.wait_for_timeout(500)
            # Nut Save nam trong than form cua popup (khong phai .modal-footer)
            dlg.first.locator("button.o_form_button_save:visible, button:has-text('Save'):visible").first.click()
            # Save xong popup VAN MO (chuyen sang che do xem) -> cho luu xong, roi bam nut X goc phai de dong
            saved = dlg.first.locator("button.o_form_button_edit:visible")
            error = p.locator(".modal-dialog:visible .o_notification, .o_notification:visible")
            saved.or_(error).first.wait_for(timeout=config.TIMEOUT_MS * 3)
            if not saved.count():
                raise AssertionError("Save Working History bi chan: " + error.first.inner_text())
            dlg.first.locator(".modal-header button.close").first.click()
            dlg.first.wait_for(state="hidden", timeout=config.TIMEOUT_MS * 3)
        finally:
            self._scope = ".o_form_view"

    # ---------- Add a Meeting (TA) ----------
    def add_meeting(self, start: str, end: str, keep_attendee: str, invite_email: bool = False) -> str:
        """Add a Meeting -> Confirm popup 1 -> form 'Create a meeting': giu lai 1 nguoi tham du, bo tich Invite email
        va Google Meet, dien gio (dinh dang dd/mm/yyyy HH:MM:SS) -> Save. Tra ve thong bao loi (rong = OK)."""
        p = self.page
        p.locator(".o_form_view button[name='add_meeting_room']:visible").first.click()
        dlg = p.locator(".modal-dialog:visible")
        dlg.first.wait_for(timeout=config.TIMEOUT_MS * 3)
        dlg.first.locator("button[name='add_meeting']").first.click()
        form = ".modal-dialog:visible .o_form_view"
        p.locator(f"{form} [name='start_datetime']:visible").first.wait_for(timeout=config.TIMEOUT_MS * 4)
        self._scope = form
        try:
            # Attendees: xoa het tag, chi giu tag co ten keep_attendee
            tags = p.locator(f"{form} [name='partner_ids'] .badge")
            for _ in range(20):
                other = tags.filter(has_not_text=keep_attendee)
                if not other.count():
                    break
                other.first.locator(".o_delete").click()
                p.wait_for_timeout(500)
            for name, want in (("invite_by_email", invite_email), ("create_meet_link", False)):
                box = p.locator(f"{form} [name='{name}'] input[type='checkbox']").first
                if box.count() and box.is_checked() != want:
                    box.click()
            self.set_field("start_datetime", start)
            self.set_field("stop_datetime", end)
            self._settle()
            dlg = p.locator(".modal-dialog:visible")
            dlg.first.locator("button.o_form_button_save:visible, button:has-text('Save'):visible").first.click()
            # Save xong popup VAN MO o che do xem (co nut Edit) -> bam X dong. Neu loi, popup loi hien ra.
            saved = dlg.first.locator("button.o_form_button_edit:visible")
            problem = p.locator(".modal-dialog:visible").nth(1).or_(p.locator(".o_notification:visible"))
            saved.or_(problem).first.wait_for(timeout=config.TIMEOUT_MS * 3)
            if not saved.count():
                return " | ".join(problem.first.inner_text().splitlines())
            dlg.first.locator(".modal-header button.close").first.click()
            dlg.first.wait_for(state="hidden", timeout=config.TIMEOUT_MS * 3)
            return ""
        finally:
            self._scope = ".o_form_view"
