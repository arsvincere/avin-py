import pytest
import t_tech.invest as ti

from avin.data.tinkoff.auth import TinkoffAuth
from avin.utils.exceptions import InvalidToken

# =========================
# Fake Tinkoff client layer
# =========================


class FakeUsers:
    def __init__(self, raise_error=False, empty=False):
        self.raise_error = raise_error
        self.empty = empty

    def get_accounts(self):
        if self.raise_error:
            raise ti.exceptions.UnauthenticatedError(
                code=401, details="unauthorized", metadata={}
            )
        if self.empty:
            return None
        return True


class FakeClient:
    def __init__(self, raise_error=False, empty=False):
        self.users = FakeUsers(raise_error=raise_error, empty=empty)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


# =========================
# Tests
# =========================


def test_token_success(monkeypatch):
    monkeypatch.setattr("avin.data.tinkoff.auth.Cmd.exists", lambda _: True)
    monkeypatch.setattr(
        "avin.data.tinkoff.auth.Cmd.read", lambda _: "valid-token"
    )

    monkeypatch.setattr(
        "avin.data.tinkoff.auth.ti.Client",
        lambda _: FakeClient(),
    )

    TinkoffAuth._TinkoffAuth__token = None

    token = TinkoffAuth.token()

    assert token == "valid-token"


def test_token_file_not_found(monkeypatch):
    monkeypatch.setattr("avin.data.tinkoff.auth.Cmd.exists", lambda _: False)

    TinkoffAuth._TinkoffAuth__token = None

    with pytest.raises(FileNotFoundError):
        TinkoffAuth.token()


def test_token_file_empty(monkeypatch):
    monkeypatch.setattr("avin.data.tinkoff.auth.Cmd.exists", lambda _: True)
    monkeypatch.setattr("avin.data.tinkoff.auth.Cmd.read", lambda _: "   ")

    TinkoffAuth._TinkoffAuth__token = None

    with pytest.raises(FileNotFoundError):
        TinkoffAuth.token()


def test_invalid_token(monkeypatch):
    monkeypatch.setattr("avin.data.tinkoff.auth.Cmd.exists", lambda _: True)
    monkeypatch.setattr(
        "avin.data.tinkoff.auth.Cmd.read", lambda _: "bad-token"
    )

    monkeypatch.setattr(
        "avin.data.tinkoff.auth.ti.Client",
        lambda _: FakeClient(raise_error=True),
    )

    TinkoffAuth._TinkoffAuth__token = None

    with pytest.raises(InvalidToken):
        TinkoffAuth.token()


def test_empty_response_from_api(monkeypatch):
    """
    client.users.get_accounts() -> None
    должно вызвать RuntimeError в _validate_token
    """
    monkeypatch.setattr("avin.data.tinkoff.auth.Cmd.exists", lambda _: True)
    monkeypatch.setattr(
        "avin.data.tinkoff.auth.Cmd.read", lambda _: "valid-token"
    )

    monkeypatch.setattr(
        "avin.data.tinkoff.auth.ti.Client",
        lambda _: FakeClient(empty=True),
    )

    TinkoffAuth._TinkoffAuth__token = None

    with pytest.raises(RuntimeError):
        TinkoffAuth.token()


def test_token_cached(monkeypatch):
    monkeypatch.setattr("avin.data.tinkoff.auth.Cmd.exists", lambda _: True)
    monkeypatch.setattr(
        "avin.data.tinkoff.auth.Cmd.read", lambda _: "cached-token"
    )

    monkeypatch.setattr(
        "avin.data.tinkoff.auth.ti.Client",
        lambda _: FakeClient(),
    )

    TinkoffAuth._TinkoffAuth__token = None

    t1 = TinkoffAuth.token()
    t2 = TinkoffAuth.token()

    assert t1 == t2 == "cached-token"
