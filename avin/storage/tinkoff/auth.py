# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

import t_tech.invest as ti

from avin.errors.exceptions import InvalidTokenError
from avin.system.conf import cfg
from avin.utils.cmd import Cmd

TOKEN_PATH = cfg.tinkoff_token_path


class TinkoffAuth:
    __token: str | None = None

    @classmethod
    def token(cls) -> str:
        # если токен уже прочитали и проверили то он тут, возвращаем
        if cls.__token is not None:
            return cls.__token

        token = _read_token()

        try:
            _validate_token(token)
        except ti.exceptions.UnauthenticatedError as err:
            raise InvalidTokenError("Invalid Tinkoff token") from err

        cls.__token = token

        return cls.__token


def _read_token() -> str:
    # NOTE:
    # Этот текст ошибки и что с ним делать пусть пока тут полежит,
    # он понадобится где то на более высоком уровне, а от сюда
    # тупо кидаем исключение с коротким пояснением.
    # Error:
    # "Tinkoff not exist token file, operations with market data "
    # "and orders unavailible. Make a token and put it in a "
    # f"'{TOKEN_PATH}'. Read more about token: "
    # "https://developer.tinkoff.ru/docs/intro/"
    # "manuals/self-service-auth"

    if not Cmd.exists(TOKEN_PATH):
        raise FileNotFoundError(f"Tinkoff token not found at {TOKEN_PATH}")

    token = Cmd.read(TOKEN_PATH).strip()
    if not token:
        raise FileNotFoundError("Tinkoff token file is empty")

    return token


def _validate_token(token: str) -> None:
    with ti.Client(token) as client:
        response = client.users.get_accounts()
        if not response:
            raise RuntimeError("Empty response from Tinkoff auth check")


if __name__ == "__main__":
    ...
