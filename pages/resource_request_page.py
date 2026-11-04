"""Man hinh Resource Request (vti.resource.request) - Odoo 12.

Locator theo nhan (label[for] -> input), khong dung id dong.
"""
import json
import re
from datetime import date, timedelta

from playwright.sync_api import Page, expect

from core import config

LIST_URL = f"{config.BASE_URL}/web?#action=756&model=vti.resource.request&view_type=list&menu_id=565"
DATE_FMT = "%d/%m/%Y"  # dinh dang ngay tren STG (Creation Date hien 04/11/2026)

DROPDOWN_ITEM = "ul.ui-autocomplete:visible li.ui-menu-item a"


def rr_data(file: str = "rr_default.json", **override) -> dict:
    """Doc data RR tu data/rr/<file>. Co the ghi de tung truong: rr_data(approver="x")."""
    d = json.loads((config.DATA_DIR / "rr" / file).read_text(encoding="utf-8"))
    d.update(override)
    today = date.today()
    d["deadline"] = (today + timedelta(days=d.pop("deadline_days"))).strftime(DATE_FMT)
    d["onboard"] = (today + timedelta(days=d.pop("onboard_days"))).strftime(DATE_FMT)
    return d


class ResourceRequestPage:
    def __init__(self, page: Page):
        self.page = page

    # ---------- helpers ----------
    def _field(self, label: str):
        """Tra ve input/select gan voi label (Odoo: label[for]=id)."""
        lbl = self.page.locator("label.o_form_label").filter(
            has_text=re.compile(rf"^\s*{re.escape(label)}\s*$")).first
        input_id = lbl.get_attribute("for")
        return self.page.locator(f"[id='{input_id}']")

    def _pick(self, label: str, value: str):
        """Many2one / many2many: go chu, chon dong dau tien khop trong dropdown."""
        self._dismiss_dropdown()
        field = self._field(label)
        field.click()
        field.fill(value)
        items = self.page.locator(DROPDOWN_ITEM).filter(has_text=value)
        try:
            items.first.wait_for(timeout=5000)
        except Exception:
            # khong co ket qua khop -> lay lua chon dau tien (tru Search More / Create)
            field.fill("")
            items = self.page.locator(DROPDOWN_ITEM).filter(
                has_not_text=re.compile("Search More|Create"))
            items.first.wait_for()
        items.first.click()
        self._close_dropdown()

    def _dismiss_dropdown(self):
        """Dropdown cua o truoc con mo -> click vao cho trong de no tat (giong thao tac tay)."""
        menu = self.page.locator("ul.ui-autocomplete:visible")
        if menu.count():
            self.page.locator(".oe_title").first.click()
            menu.first.wait_for(state="hidden", timeout=5000)

    def _close_dropdown(self):
        menu = self.page.locator("ul.ui-autocomplete:visible")
        try:
            menu.first.wait_for(state="hidden", timeout=2000)
        except Exception:
            self.page.keyboard.press("Escape")
            menu.first.wait_for(state="hidden", timeout=5000)

    def _ensure_tag(self, label: str, user: str):
        """Many2many tags: chi chon them khi o chua co user do."""
        cell = self.page.locator("td", has=self.page.locator(
            "label.o_form_label", has_text=label)).locator("xpath=following-sibling::td[1]")
        if user.lower() not in cell.inner_text().lower() and not cell.locator(".badge, .o_tag").count():
            self._pick(label, user)

    def _fill(self, label: str, value: str):
        self._field(label).fill(value)

    def _select(self, label: str, text: str):
        self._field(label).select_option(label=re.compile(re.escape(text), re.I)) \
            if False else self._field(label).select_option(
                label=self._match_option(label, text))

    def _match_option(self, label: str, text: str) -> str:
        options = self._field(label).locator("option").all_inner_texts()
        for o in options:
            if text.lower() in o.lower():
                return o
        raise AssertionError(f"Khong co lua chon '{text}' o '{label}'. Co: {options}")

    def _fill_date(self, label: str, value: str):
        f = self.page.get_by_role("textbox", name=label)
        f.click()
        f.fill(value)
        f.press("Enter")
        expect(f).to_have_value(value)

    # ---------- flow ----------
    def goto_list(self):
        # Vao thang man RR, chi cho menu Recruitment (bo qua Helpdesk). Odoo co luc ghi de -> thu lai
        menu = self.page.get_by_role("button", name="Resource Requests")
        for attempt in range(3):
            self.page.goto(LIST_URL, wait_until="domcontentloaded")
            try:
                menu.wait_for(timeout=config.TIMEOUT_MS * 2)
                break
            except Exception:
                if attempt == 2:
                    raise

    def open_create(self):
        self.goto_list()
        save = self.page.get_by_role("button", name=re.compile("Save"))
        create = self.page.get_by_role("button", name=re.compile("Create"))
        create.or_(save).first.wait_for()
        if not save.is_visible():  # form chua mo san thi moi bam Create
            create.click()
        expect(self.page.get_by_role("button", name=re.compile("Save"))).to_be_visible(timeout=20000)

    def fill_form(self, d: dict):
        p = self.page
        # Department Leader mac dinh KHONG phai DL -> chon lai; Department tu doi theo
        self._pick("Department Leader", d["department_leader"])
        p.wait_for_timeout(1000)
        self._fill("Project", d["project"])
        self._pick("Job Location", d["job_location"])
        for lb, key in (("SM", "sm"), ("Reviewer", "reviewer"), ("Interviewer", "interviewer")):
            self._ensure_tag(lb, d[key])
        self._pick("Approver", d["approver"])
        self._fill("Expect Qty", d["expect_qty"])
        self._fill_date("Deadline Date", d["deadline"])
        self._pick("Job Position", d["job_position"])
        self._pick("Level", d["level"])
        self._pick("Main skill", d["main_skill"])
        self._select("Priority", d["priority"])
        self._fill("Salary Upto", d["salary"])
        cur = p.get_by_role("textbox", name=re.compile(r"C\s*u\s*r\s*r\s*e\s*n\s*c\s*y"))
        cur.click()
        cur.fill("")
        cur.fill("VND")
        p.locator(DROPDOWN_ITEM).filter(has_text="VND").first.click()
        self._close_dropdown()
        self._pick("Job Type", d["job_type"])
        self._pick("Interview type", d["interview_type"])
        self._select("Experience", d["experience"])
        self._pick("Languages", d["language"])
        self._fill_date("Expect Onboard Date", d["onboard"])
        # Company Follow co the da co san VTI Corporation -> chi chon neu chua co
        row = p.locator("td", has=p.locator("label.o_form_label", has_text="Company Follow")).locator("xpath=following-sibling::td[1]")
        if d["company_follow"] not in row.inner_text():
            self._pick("Company Follow", d["company_follow"])

        p.get_by_role("textbox", name=re.compile(r"^- Mô tả chi tiết")).fill(d["jd_vn"])
        p.get_by_role("textbox", name=re.compile(r"^- Detailed description")).fill(d["jd_en"])
        p.get_by_role("textbox", name=re.compile(r"^- Số năm kinh nghiệm")).fill(d["exp_vn"])
        p.get_by_role("textbox", name=re.compile(r"^- Minimum years")).fill(d["exp_en"])
        p.get_by_role("textbox", name=re.compile(r"^- Quy mô dự án")).fill(d["project_description"])
        p.locator("xpath=//*[normalize-space(text())='Note']/following::textarea[1]").fill(d["note"])

    def save(self):
        self.page.get_by_role("button", name=re.compile("Save")).click()
        expect(self.page.get_by_role("button", name=re.compile("Edit"))).to_be_visible()

    def submit(self):
        p = self.page
        p.get_by_role("button", name="Submit", exact=True).click()
        status = p.locator(".o_statusbar_status .o_arrow_button.btn-primary")
        for _ in range(20):
            dlg = p.locator(".modal-dialog:visible")
            if dlg.count():
                print("[DIALOG]", dlg.first.inner_text().replace(chr(10), " | "))
                ok = dlg.first.locator("button.btn-primary").first
                if "invalid" in dlg.first.inner_text().lower() or not ok.count():
                    raise AssertionError("Submit bi chan: " + dlg.first.inner_text())
                ok.click()
            if "approve" in status.inner_text().lower():
                return
            p.wait_for_timeout(1000)
        raise AssertionError("Sau Submit trang thai van la: " + status.inner_text())

    def code(self) -> str:
        return self.page.locator(".oe_title h1 [name='name'], .oe_title h1 span").first.inner_text().strip()

    def open_rr(self, code: str):
        """Tim RR theo Code trong list va mo form."""
        self.goto_list()
        p = self.page
        p.locator("tr.o_data_row").first.wait_for()
        while p.locator(".o_searchview_facet .o_facet_remove").count():  # bo loc mac dinh (Processing)
            p.locator(".o_searchview_facet .o_facet_remove").first.click()
            p.wait_for_timeout(1000)
        box = p.locator(".o_searchview_input")
        box.click()
        box.fill(code)
        box.press("Enter")
        p.wait_for_timeout(2000)
        row = p.locator("tr.o_data_row").filter(has_text=code).first
        row.wait_for()
        row.click()
        expect(p.locator(".oe_title h1")).to_have_text(code, timeout=20000)

    def status(self) -> str:
        return self.page.locator(".o_statusbar_status .o_arrow_button.btn-primary").inner_text().strip()

    def approve(self):
        p = self.page
        before = self.status()
        p.get_by_role("button", name="Approve", exact=True).first.click()
        dlg = p.locator(".modal-dialog:visible").first
        dlg.wait_for()
        print("[DIALOG]", dlg.inner_text().replace(chr(10), " | "))
        dlg.locator("button.btn-primary").first.click()  # Confirm: chi bam 1 lan
        dlg.wait_for(state="hidden")
        for _ in range(20):
            err = p.locator(".modal-dialog:visible")
            if err.count() and "Error" in err.first.inner_text():
                raise AssertionError("Approve bi loi: " + err.first.inner_text())
            if self.status() != before:
                return
            p.wait_for_timeout(1000)
        raise AssertionError("Sau Approve trang thai van la: " + self.status())
