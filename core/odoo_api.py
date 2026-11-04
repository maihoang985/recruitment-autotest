"""Goi Odoo XML-RPC bang tai khoan test (chi dung de DOC/kiem tra ket qua, tao data qua giao dien).
    api = OdooApi(config.TA_USER)
    api.call("hr.applicant", "read", [32625], fields=["cv_mask_state"])
"""
import base64
import xmlrpc.client

from core import config

DB = "vms_rec_stg"


class OdooApi:
    def __init__(self, username: str, password: str | None = None):
        self.password = password or config.DEFAULT_PASSWORD
        common = xmlrpc.client.ServerProxy(f"{config.BASE_URL}/xmlrpc/2/common")
        self.uid = common.authenticate(DB, username, self.password, {})
        if not self.uid:
            raise AssertionError(f"Dang nhap API that bai: {username}")
        self.username = username
        self._obj = xmlrpc.client.ServerProxy(f"{config.BASE_URL}/xmlrpc/2/object", allow_none=True)

    def call(self, model: str, method: str, *args, **kw):
        return self._obj.execute_kw(DB, self.uid, self.password, model, method, list(args), kw)

    def read_one(self, model: str, rec_id: int, fields: list[str]) -> dict:
        return self.call(model, "read", [rec_id], fields=fields)[0]

    def download(self, attachment_id: int) -> tuple[str, bytes]:
        a = self.read_one("ir.attachment", attachment_id, ["name", "datas"])
        return a["name"], base64.b64decode(a["datas"] or b"")

    def chatter(self, model: str, rec_id: int) -> list[str]:
        msgs = self.call("mail.message", "search_read", [["model", "=", model], ["res_id", "=", rec_id]],
                         fields=["body"], order="id")
        return [m["body"] or "" for m in msgs]
