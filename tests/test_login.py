"""Smoke test: dang nhap duoc STG bang tai khoan TA_USER trong .env."""


def test_login_ta_user(login_as):
    page = login_as()
    assert "/web" in page.url
