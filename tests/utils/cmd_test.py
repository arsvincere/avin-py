# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import gzip
import zipfile
from pathlib import Path

import polars as pl

from avin.utils.cmd import Cmd


def test_make_dirs(tmp_path: Path):
    path = tmp_path / "a" / "b" / "c"

    Cmd.make_dirs(path)

    assert path.is_dir()


def test_make_dirs_for_file(tmp_path: Path):
    file_path = tmp_path / "a" / "b" / "file.txt"

    Cmd.make_dirs_for_file(file_path)

    assert file_path.parent.is_dir()


def test_name(tmp_path: Path):
    file_path = tmp_path / "test.txt"

    assert Cmd.name(file_path) == "test"
    assert Cmd.name(file_path, extension=True) == "test.txt"


def test_exists_file_dir(tmp_path: Path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("hello")

    assert Cmd.exists(file_path)
    assert Cmd.is_file(file_path)

    assert Cmd.exists(tmp_path)
    assert Cmd.is_dir(tmp_path)


def test_content(tmp_path: Path):
    (tmp_path / "a.txt").write_text("1")
    (tmp_path / "b.txt").write_text("2")
    (tmp_path / "dir").mkdir()

    content = Cmd.content(tmp_path)

    assert "a.txt" in content
    assert "b.txt" in content
    assert "dir" in content


def test_get_files(tmp_path: Path):
    (tmp_path / "a.txt").write_text("1")
    (tmp_path / "b.txt").write_text("2")
    (tmp_path / "dir").mkdir()

    files = Cmd.get_files(tmp_path)

    assert sorted(files) == ["a.txt", "b.txt"]


def test_get_files_recursive(tmp_path: Path):
    (tmp_path / "root.txt").write_text("1")

    sub = tmp_path / "sub"
    sub.mkdir()

    (sub / "inner.txt").write_text("2")

    files = Cmd.get_files(
        tmp_path,
        include_sub_dir=True,
    )

    assert "root.txt" in files
    assert "inner.txt" in files


def test_get_dirs(tmp_path: Path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()

    dirs = Cmd.get_dirs(tmp_path)

    assert sorted(dirs) == ["a", "b"]


def test_find_file(tmp_path: Path):
    file_path = tmp_path / "abc.txt"
    file_path.write_text("hello")

    found = Cmd.find_file("abc.txt", tmp_path)

    assert found == [file_path]


def test_find_dir(tmp_path: Path):
    dir_path = tmp_path / "test_dir"
    dir_path.mkdir()

    found = Cmd.find_dir("test_dir", tmp_path)

    assert found == [dir_path]


def test_rename(tmp_path: Path):
    src = tmp_path / "old.txt"
    dst = tmp_path / "new.txt"

    src.write_text("hello")

    Cmd.rename(src, dst)

    assert not src.exists()
    assert dst.exists()


def test_replace(tmp_path: Path):
    src = tmp_path / "src.txt"
    dst = tmp_path / "dir" / "dst.txt"

    src.write_text("hello")

    Cmd.replace(src, dst)

    assert not src.exists()
    assert dst.read_text() == "hello"


def test_copy(tmp_path: Path):
    src = tmp_path / "src.txt"
    dst = tmp_path / "dst.txt"

    src.write_text("hello")

    Cmd.copy(src, dst)

    assert dst.read_text() == "hello"


def test_delete(tmp_path: Path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("hello")

    Cmd.delete(file_path)

    assert not file_path.exists()


def test_write_read(tmp_path: Path):
    file_path = tmp_path / "file.txt"

    Cmd.write("hello world", file_path)

    assert Cmd.read(file_path) == "hello world"


def test_write_read_text(tmp_path: Path):
    file_path = tmp_path / "file.txt"

    text = ["a\n", "b\n", "c\n"]

    Cmd.write_text(text, file_path)

    assert Cmd.read_text(file_path) == text


def test_append(tmp_path: Path):
    file_path = tmp_path / "file.txt"

    Cmd.write("a\n", file_path)

    Cmd.append(
        [
            "b\n",
            "c\n",
        ],
        file_path,
    )

    assert Cmd.read_text(file_path) == [
        "a\n",
        "b\n",
        "c\n",
    ]


def test_get_tail(tmp_path: Path):
    file_path = tmp_path / "file.txt"

    text = [
        "1\n",
        "2\n",
        "3\n",
        "4\n",
        "5\n",
    ]

    Cmd.write_text(text, file_path)

    assert Cmd.get_tail(file_path, 2) == [
        "4\n",
        "5\n",
    ]


def test_json(tmp_path: Path):
    file_path = tmp_path / "data.json"

    obj = {
        "a": 1,
        "b": "hello",
    }

    Cmd.write_json(obj, file_path)

    loaded = Cmd.read_json(file_path)

    assert loaded == obj


def test_json_string():
    obj = {
        "a": 1,
        "b": "hello",
    }

    string = Cmd.to_json_str(obj)

    loaded = Cmd.from_json_str(string)

    assert loaded == obj


def test_toml(tmp_path: Path):
    file_path = tmp_path / "data.toml"

    obj = {
        "server": {
            "host": "localhost",
            "port": 8080,
        }
    }

    Cmd.write_toml(obj, file_path)

    loaded = Cmd.read_toml(file_path)

    assert loaded == obj


def test_parquet(tmp_path: Path):
    file_path = tmp_path / "test.parquet"

    df = pl.DataFrame(
        {
            "a": [1, 2, 3],
            "b": ["x", "y", "z"],
        }
    )

    Cmd.write_pqt(df, file_path)

    loaded = Cmd.read_pqt(file_path)

    assert loaded.equals(df)


def test_extract_gz(tmp_path: Path):
    src = tmp_path / "source.txt"
    gz = tmp_path / "source.txt.gz"
    dst = tmp_path / "result.txt"

    src.write_text("hello")

    with open(src, "rb") as fin, gzip.open(gz, "wb") as fout:
        fout.write(fin.read())

    Cmd.extract_gz(gz, dst)

    assert dst.read_text() == "hello"


def test_extract_zip(tmp_path: Path):
    src = tmp_path / "file.txt"
    archive = tmp_path / "archive.zip"
    dest = tmp_path / "extract"

    src.write_text("hello")

    with zipfile.ZipFile(archive, "w") as z:
        z.write(src, arcname="file.txt")

    Cmd.extract_zip(archive, dest)

    assert (dest / "file.txt").read_text() == "hello"


def test_size(tmp_path: Path):
    file_path = tmp_path / "file.txt"

    file_path.write_text("hello")

    assert Cmd.size(file_path) == 5


def test_dir_name(tmp_path: Path):
    file_path = tmp_path / "mydir" / "file.txt"

    file_path.parent.mkdir()

    file_path.write_text("hello")

    assert Cmd.dir_name(file_path) == "mydir"


def test_dir_path(tmp_path: Path):
    file_path = tmp_path / "mydir" / "file.txt"

    file_path.parent.mkdir()

    file_path.write_text("hello")

    assert Cmd.dir_path(file_path) == file_path.parent
