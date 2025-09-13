#!/usr/bin/env python3
# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from avin import *


def test_path():
    p = Cmd.path("/home", "user", "file_name.txt")

    assert str(p) == "/home/user/file_name.txt"


def test_is_exist():
    p = Cmd.path("/home")

    assert Cmd.is_exist(p)


def test_is_file():
    p = Cmd.path("/etc/fstab")

    assert Cmd.is_file(p)


def test_is_dir():
    p = Cmd.path("/usr/bin")

    assert Cmd.is_dir(p)


def test_make_dirs():
    p = Cmd.path("/home", "alex", "AVIN", "__tmp_dir__")

    Cmd.make_dirs(p)
    assert Cmd.is_exist(p)

    Cmd.delete_dir(p)


def test_name():
    p = Cmd.path("/home", "alex", "AVIN", "README.md")

    name = Cmd.name(p)
    assert name == "README"

    name_with_extension = Cmd.name(p, extension=True)
    assert name_with_extension == "README.md"


def test_dir_name():
    p = Cmd.path("/home", "alex", "AVIN", "README.md")

    name = Cmd.dir_name(p)
    assert name == "AVIN"


def test_dir_path():
    p = Cmd.path("/home", "alex", "AVIN", "README.md")

    dir_path = Cmd.dir_path(p)
    assert str(dir_path) == "/home/alex/AVIN"


def test_content():
    pass
