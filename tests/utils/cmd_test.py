# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from pathlib import Path

from avin import *


def test_path():
    root = Path.home()
    a = Path("aaa")
    b = Path("bbb")
    c = Path("ccc")

    res = Cmd.path(root, a, b, c)

    assert res == Path("/home/alex/aaa/bbb/ccc")


def test_make_dirs():
    root = Path.home()
    a = Path("test_cmd_make_dir")
    res = Cmd.path(root, a)

    res.mkdir(parents=True, exist_ok=True)
    assert res.is_dir()

    res.rmdir()


def test_name():
    p = Path("/home/alex/avin/requirements.txt")

    file_name_with_extension = Cmd.name(p, extension=True)
    assert file_name_with_extension == "requirements.txt"

    file_name = Cmd.name(p)
    assert file_name == "requirements"


def test_dir_name():
    p = Path("/home/alex/avin/requirements.txt")

    dir_name = Cmd.dir_name(p)

    assert dir_name == "avin"


def test_dir_path():
    p = Path("/home/alex/avin/requirements.txt")

    dir_path = Cmd.dir_path(p)

    assert dir_path == Path("/home/alex/avin")


def test_is_exist():
    p = Path("/home/alex/avin/requirements.txt")
    assert Cmd.is_exist(p)

    p = Path("/home/alex/avin")
    assert Cmd.is_exist(p)


def test_is_file():
    p = Path("/home/alex/avin/requirements.txt")
    assert Cmd.is_file(p)

    p = Path("/home/alex/avin")
    assert not Cmd.is_file(p)


def test_is_dir():
    p = Path("/home/alex/avin")
    assert Cmd.is_dir(p)

    p = Path("/home/alex/avin/requirements.txt")
    assert not Cmd.is_dir(p)
