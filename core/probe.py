"""Ghi lai man hinh hien tai ra file TEXT (re hon anh rat nhieu khi gui cho Claude doc).

Dung khi script gap cho la: popup chua biet, thong bao loi, khong thay nut.
    from core.probe import dump_page
    dump_page(page, "sau_khi_save")
-> output/probe_<ten>.txt (+ output/probe_<ten>.png de nguoi xem neu can)
"""
from playwright.sync_api import Page

from core import config

_JS = r"""
() => {
  const vis = el => !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length)
                    && getComputedStyle(el).visibility !== 'hidden';
  const txt = el => (el.innerText || el.value || '').replace(/\s+/g, ' ').trim().slice(0, 300);
  const out = {};

  // Popup / hop xac nhan dang mo (Odoo 12: .modal)
  out.dialogs = [...document.querySelectorAll('.modal.show, .modal.in, .modal[style*="display: block"]')]
    .filter(vis).map(m => ({
      title: txt(m.querySelector('.modal-title') || m),
      body: txt(m.querySelector('.modal-body') || m),
      buttons: [...m.querySelectorAll('.modal-footer button, .modal-footer a.btn')].filter(vis).map(txt),
    }));

  // Thong bao loi / canh bao / notification
  out.messages = [...document.querySelectorAll(
      '.o_notification, .alert-danger, .alert-warning, .o_dialog_warning, .o_form_invalid, .o_field_invalid')]
    .filter(vis).map(e => (e.classList.contains('o_field_invalid')
        ? 'O loi: ' + (e.getAttribute('name') || e.closest('[name]')?.getAttribute('name') || '?')
        : txt(e)));

  // Trang thai (statusbar), breadcrumb
  out.breadcrumb = txt(document.querySelector('.breadcrumb') || document.body).slice(0, 200);
  out.status = txt(document.querySelector('.o_statusbar_status .btn-primary, .o_statusbar_status .o_arrow_button.btn-primary') || document.createElement('i'));

  // Nut dang hien (header form, footer popup, nut trong bang con)
  const root = document.querySelector('.modal.show, .modal.in') || document;
  out.buttons = [...root.querySelectorAll('button, a.btn, .o_statusbar_buttons a')].filter(vis)
    .map(b => {
      const t = txt(b), n = b.getAttribute('name');
      return n ? `${t || '(icon)'}  [name="${n}"]` : t;
    }).filter(Boolean);
  out.buttons = [...new Set(out.buttons)];

  // O tren form: name + nhan + gia tri + bat buoc
  out.fields = [...root.querySelectorAll('.o_field_widget[name]')].filter(vis).map(f => {
    const name = f.getAttribute('name');
    const id = f.id || f.querySelector('input,select,textarea')?.id;
    const lbl = id ? document.querySelector(`label[for="${id}"]`) : null;
    const flags = [f.classList.contains('o_required_modifier') ? 'BAT BUOC' : '',
                   f.classList.contains('o_readonly_modifier') ? 'chi doc' : ''].filter(Boolean).join(',');
    return `${name} | ${lbl ? txt(lbl) : ''} | ${txt(f).slice(0, 80)}${flags ? ' | ' + flags : ''}`;
  });
  return out;
}
"""


def dump_page(page: Page, name: str) -> str:
    config.OUTPUT_DIR.mkdir(exist_ok=True)
    base = config.OUTPUT_DIR / f"probe_{name}"
    try:
        info = page.evaluate(_JS)
    except Exception as e:  # trang dang load / bi dong
        info = {"error": str(e)}
    lines = [f"URL: {page.url}"]
    for key in ("error", "breadcrumb", "status"):
        if info.get(key):
            lines.append(f"{key}: {info[key]}")
    for d in info.get("dialogs", []):
        lines += ["", "== POPUP ==", f"Tieu de: {d['title']}", f"Noi dung: {d['body']}",
                  f"Nut: {' | '.join(d['buttons'])}"]
    if info.get("messages"):
        lines += ["", "== THONG BAO / LOI =="] + info["messages"]
    lines += ["", "== NUT DANG HIEN =="] + info.get("buttons", [])
    lines += ["", "== O DANG HIEN (name | nhan | gia tri | co) =="] + info.get("fields", [])
    text = "\n".join(lines)
    base.with_suffix(".txt").write_text(text, encoding="utf-8")
    try:
        page.screenshot(path=str(base.with_suffix(".png")))
    except Exception:
        pass
    return text
