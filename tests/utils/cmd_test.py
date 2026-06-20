# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from pathlib import Path

import polars as pl

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


def test_content():
    p = Path("/home/alex/avin/")

    content = Cmd.content(p, full_path=False)
    assert len(content) > 10


def test_get_files():
    p = Path("/home/alex/avin/")

    files = Cmd.get_files(p, full_path=False, include_sub_dir=False)
    assert len(files) > 5


def test_get_dirs():
    p = Path("/home/alex/avin/")

    dirs = Cmd.get_dirs(p, full_path=False)
    assert len(dirs) > 5


def test_find_file():
    p = Path("/home/alex/avin/")
    pattern = "pyproject.toml"

    result = Cmd.find_file(pattern, p)
    assert len(result) == 1


def test_rename():
    o = Path("/home/alex/avin/usr")
    n = Path("/home/alex/avin/usss")
    Cmd.rename(o, n)
    assert n.exists()

    # cancel rename
    Cmd.rename(n, o)


def test_replace():
    src = Path("/home/alex/avin/usr")
    dest = Path("/home/alex/avin/usss")
    Cmd.replace(src, dest)
    assert dest.exists()

    # cancel replace
    Cmd.replace(dest, src)


def test_copy_delete_file():
    src = Path("/home/alex/avin/requirements.txt")
    dest = Path("/home/alex/avin/requirements.txt.2")

    Cmd.copy(src, dest)

    assert Cmd.is_exist(dest)

    # delete
    Cmd.delete(dest)


def test_copy_delete_dir():
    src = Path("/home/alex/avin/tests")
    dest = Path("/home/alex/avin/tests2")

    Cmd.copy_dir(src, dest)

    assert Cmd.is_exist(dest)

    # delete
    Cmd.delete_dir(dest)


def test_read():
    p = Path("/home/alex/avin/requirements.txt")

    text = Cmd.read(p)
    assert len(text) > 0


def test_write():
    p = Path("/home/alex/avin/requirements.txt")
    text = Cmd.read(p)

    p2 = Path("/home/alex/avin/requirements.txt2")
    Cmd.write(text, p2)

    Cmd.delete(p2)


def test_read_text():
    p = Path("/home/alex/avin/requirements.txt")

    text = Cmd.read_text(p)
    assert len(text) > 0


def test_write_text():
    p = Path("/home/alex/avin/requirements.txt")

    text = Cmd.read_text(p)
    assert len(text) > 0

    p2 = Path("/home/alex/avin/requirements.txt2")
    Cmd.write_text(text, p2)

    Cmd.delete(p2)


def test_read_write_json():
    obj = {
        "name": "alex",
        "age": 18,
        "trader": True,
    }

    p = Path("/home/alex/avin/test.json")
    Cmd.write_json(obj, p)

    readed_obj = Cmd.read_json(p)
    assert obj == readed_obj

    Cmd.delete(p)


def test_from_to_json():
    obj = {
        "name": "alex",
        "age": 18,
        "trader": True,
    }

    s = Cmd.to_json_str(obj)
    from_s = Cmd.from_json_str(s)

    assert obj == from_s


def test_toml():
    obj = {
        "name": "alex",
        "age": 18,
        "trader": True,
    }
    p = Path("/home/alex/avin/test.toml")
    Cmd.write_toml(obj, p)

    readed = Cmd.read_toml(p)
    assert obj == readed

    Cmd.delete(p)


def test_pqt():
    data = {
        "employee_id": [101, 102, 103, 104],
        "name": ["Alice", "Bob", "Charlie", "David"],
        "department": ["HR", "IT", "IT", "Sales"],
        "salary": [60000, 85000, 90000, 55000],
    }
    df = pl.DataFrame(data)

    p = Path("/home/alex/avin/test.pqt")
    Cmd.write_pqt(df, p)

    readed = Cmd.read_pqt(p)
    assert df.equals(readed)

    Cmd.delete(p)
