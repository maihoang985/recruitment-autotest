"""Doc cau truc form + gia tri dropdown + record mau cua 1 model Odoo qua XML-RPC (chi DOC, khong ghi).
    python scripts/inspect_model.py vti.resource.request truong.dangvan
    python scripts/inspect_model.py hr.applicant chau.phamminh 4899   # form view rieng cua menu
Ket qua: output/inspect_<model>.json (day du) + in tom tat ra man hinh.
"""
import json
import sys
import xml.etree.ElementTree as ET
import xmlrpc.client
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core import config  # noqa: E402

DB = "vms_rec_stg"
OPTION_LIMIT = 40
SAMPLE_RECORDS = 5


def main(model: str, username: str, view_id: int | None = None):
    common = xmlrpc.client.ServerProxy(f"{config.BASE_URL}/xmlrpc/2/common")
    uid = common.authenticate(DB, username, config.DEFAULT_PASSWORD, {})
    if not uid:
        sys.exit(f"Dang nhap API that bai: {username}")
    obj = xmlrpc.client.ServerProxy(f"{config.BASE_URL}/xmlrpc/2/object", allow_none=True)

    def call(m, method, *args, **kw):
        return obj.execute_kw(DB, uid, config.DEFAULT_PASSWORD, m, method, list(args), kw)

    # 1. Form view: thu tu truong, modifiers (required/invisible/readonly), domain tren view
    view = get_form_view(call, model, view_id)
    arch = ET.fromstring(view["arch"])
    form_fields, seen = [], set()
    for node in arch.iter("field"):
        name = node.get("name")
        # bo qua field con trong one2many (tree long ben trong)
        if name in seen or name not in view["fields"]:
            continue
        seen.add(name)
        mods = json.loads(node.get("modifiers") or "{}")
        form_fields.append({
            "name": name,
            "view_domain": node.get("domain"),
            "widget": node.get("widget"),
            "required": mods.get("required"),
            "invisible": mods.get("invisible"),
            "readonly": mods.get("readonly"),
        })

    # 1b. Nut tren form: nut nao hien o state nao, co hop xac nhan khong, co mo popup (wizard) khong
    buttons = read_buttons(call, arch)
    # nut trong bang con (one2many), vd dong Review CV -> nut Submit CV
    sub_buttons = {}
    for fname, f in view["fields"].items():
        for vtype, sub in (f.get("views") or {}).items():
            bs = read_buttons(call, ET.fromstring(sub["arch"]))
            if bs:
                sub_buttons[f"{fname} ({f.get('string')}, {f.get('relation')}) - {vtype}"] = bs

    # 2. Dinh nghia truong
    meta = call(model, "fields_get", [f["name"] for f in form_fields],
                attributes=["string", "type", "required", "relation", "selection", "readonly", "domain"])

    # 3. Gia tri dropdown
    for f in form_fields:
        m = meta.get(f["name"], {})
        f.update(label=m.get("string"), type=m.get("type"), relation=m.get("relation"),
                 field_required=m.get("required"))
        if m.get("type") == "selection":
            f["options"] = [v for _, v in m.get("selection", [])]
        elif m.get("type") in ("many2one", "many2many") and m.get("relation"):
            try:
                f["option_count"] = call(m["relation"], "search_count", [])
                f["options"] = [n for _, n in call(m["relation"], "name_search", "", limit=OPTION_LIMIT)]
            except xmlrpc.client.Fault as e:
                f["options_error"] = e.faultString.strip().splitlines()[-1][:200]

    # 4. Record mau: uu tien RR moi nhat
    names = [f["name"] for f in form_fields if f.get("type") not in ("one2many", "binary")]
    has_state = "state" in meta or "state" in call(model, "fields_get", ["state"], attributes=["type"])
    samples = call(model, "search_read", [], fields=names + (["state"] if has_state else []),
                   order="id desc", limit=SAMPLE_RECORDS)
    states = {}
    if has_state:
        for s in call(model, "read_group", [], ["state"], ["state"]):
            states[s["state"]] = s["state_count"]

    out = config.OUTPUT_DIR / f"inspect_{model}.json"
    config.OUTPUT_DIR.mkdir(exist_ok=True)
    out.write_text(json.dumps({"model": model, "buttons": buttons, "sub_buttons": sub_buttons, "fields": form_fields,
                               "samples": samples, "state_counts": states},
                              ensure_ascii=False, indent=1, default=str),
                   encoding="utf-8")
    print(f"Da luu: {out}  ({len(form_fields)} truong, {len(buttons)} nut, {len(samples)} record mau)")
    print("Nut tren form:")
    print_buttons(buttons)
    for table, bs in sub_buttons.items():
        print(f"Nut trong bang con {table}:")
        print_buttons(bs)


def get_form_view(call, model: str, view_id: int | None):
    """fields_view_get: model thuong la @api.model; vai model (hr.applicant) bi override thanh ham
    multi -> can truyen ids rong o dau."""
    kw = {"view_id": view_id or False, "view_type": "form"}
    try:
        return call(model, "fields_view_get", **kw)
    except xmlrpc.client.Fault as e:
        if "IndexError" not in e.faultString:
            raise
        return call(model, "fields_view_get", [], **kw)


def read_buttons(call, arch, depth: int = 0) -> list[dict]:
    """Liet ke <button> trong form view. Nut type=action -> doc them form cua popup (wizard)."""
    result = []
    for node in arch.iter("button"):
        mods = json.loads(node.get("modifiers") or "{}")
        b = {
            "string": node.get("string") or "".join(node.itertext()).strip() or None,
            "name": node.get("name"),
            "type": node.get("type"),
            "states": node.get("states"),
            "invisible": mods.get("invisible"),
            "confirm": node.get("confirm"),
            "groups": node.get("groups"),
            "special": node.get("special"),
            "in_header": False,
        }
        result.append(b)
        if b["type"] == "action" and depth == 0 and b["name"]:
            b["wizard"] = read_wizard(call, b["name"], depth)
    for node in arch.iter("header"):
        for btn in node.iter("button"):
            for b in result:
                if b["name"] == btn.get("name") and b["string"] == (btn.get("string") or b["string"]):
                    b["in_header"] = True
    return result


def read_wizard(call, action_ref: str, depth: int):
    """Nut type=action: name la id cua ir.actions.act_window -> model popup + cac o + nut cua popup."""
    try:
        act_id = int(action_ref)
        act = call("ir.actions.act_window", "read", [act_id], fields=["name", "res_model", "target", "view_id"])
        if not act:
            return {"error": "khong doc duoc action"}
        act = act[0]
        wiz = {"action": act["name"], "model": act["res_model"], "target": act["target"]}
        view = get_form_view(call, act["res_model"], act["view_id"][0] if act.get("view_id") else None)
        warch = ET.fromstring(view["arch"])
        wiz["fields"] = []
        for node in warch.iter("field"):
            n = node.get("name")
            if n in view["fields"] and n not in [f["name"] for f in wiz["fields"]]:
                mods = json.loads(node.get("modifiers") or "{}")
                wiz["fields"].append({"name": n, "label": view["fields"][n].get("string"),
                                      "type": view["fields"][n].get("type"),
                                      "required": mods.get("required"), "invisible": mods.get("invisible")})
        wiz["buttons"] = read_buttons(call, warch, depth + 1)
        return wiz
    except (ValueError, xmlrpc.client.Fault) as e:
        msg = e.faultString.strip().splitlines()[-1][:200] if isinstance(e, xmlrpc.client.Fault) else str(e)
        return {"error": msg}


def print_buttons(buttons: list[dict], indent: str = "  "):
    for b in buttons:
        if b.get("special") == "cancel" and not b.get("name"):
            show = "(dong popup)"
        else:
            inv = b.get("invisible")
            if b.get("states"):
                show = f"hien khi state = {b['states']}"
            elif inv is True:
                show = "luon an"
            elif inv:
                show = "an khi " + json.dumps(inv, ensure_ascii=False)
            else:
                show = "luon hien"
        if show == "luon an":
            continue
        line = f"{indent}[{b.get('string')}] {b.get('type') or ''}:{b.get('name')} | {show}"
        if b.get("confirm"):
            line += f" | HOP XAC NHAN: {b['confirm']}"
        print(line)
        wiz = b.get("wizard")
        if wiz:
            if wiz.get("error"):
                print(f"{indent}    -> popup: (loi doc: {wiz['error']})")
            else:
                req = [f["label"] for f in wiz["fields"] if f.get("required") is True]
                print(f"{indent}    -> POPUP '{wiz['action']}' ({wiz['model']}), o bat buoc: {req or 'khong'}")
                print_buttons(wiz["buttons"], indent + "      ")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("Cach dung: inspect_model.py <model> <username> [form_view_id]")
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else None)
