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
    p = Cmd.path("/home", "alex", "avin", "__tmp_dir__")

    Cmd.make_dirs(p)
    assert Cmd.is_exist(p)

    Cmd.delete_dir(p)


def test_name():
    p = Cmd.path("/home", "alex", "avin", "README.md")

    name = Cmd.name(p)
    assert name == "README"

    name_with_extension = Cmd.name(p, extension=True)
    assert name_with_extension == "README.md"


def test_dir_name():
    p = Cmd.path("/home", "alex", "avin", "README.md")

    name = Cmd.dir_name(p)
    assert name == "avin"


def test_dir_path():
    p = Cmd.path("/home", "alex", "avin", "README.md")

    dir_path = Cmd.dir_path(p)
    assert str(dir_path) == "/home/alex/avin"


def test_content():
    p = Cmd.path("/boot")
    names = Cmd.content(p)
    assert len(names) == 6


def test_get_files():
    p = Cmd.path("/boot")
    file_names = Cmd.get_files(p)
    assert len(file_names) == 4


def test_get_dirs():
    p = Cmd.path("/boot")
    file_names = Cmd.get_dirs(p)
    assert len(file_names) == 2


def test_find_file():
    p = Cmd.path("/boot")
    file_path = Cmd.find_file("vmlinuz-linux-zen", p)
    assert str(file_path) == "/boot/vmlinuz-linux-zen"


def test_find_dir():
    p = Cmd.path("/boot")
    dir_path = Cmd.find_dir("grub", p)
    assert str(dir_path) == "/boot/grub"


def test_rename_replace():
    old_path = Cmd.path("/home", "alex", "download")
    new_path = Cmd.path("/home", "alex", "__download__")

    Cmd.rename(old_path, new_path)

    Cmd.replace(new_path, old_path)


def test_copy_delete():
    src_path = Cmd.path("/home/alex/utils/vial/udev")
    dst_path = Cmd.path("/home/alex/utils/vial/udev_copy")

    Cmd.copy(src_path, dst_path)
    Cmd.delete(dst_path)


def test_copy_dir_delete_dir():
    src_path = Cmd.path("/home/alex/utils/vial")
    dst_path = Cmd.path("/home/alex/utils/vial_copy")

    Cmd.copy_dir(src_path, dst_path)
    Cmd.delete_dir(dst_path)


def test_extract():
    # TODO:
    pass


def test_read_write():
    # TODO:
    pass


def test_append():
    # TODO:
    pass


def test_get_tail():
    # TODO:
    pass


def test_rw_text():
    # TODO:
    pass


def test_rw_json():
    # TODO:
    pass


def test_from_to_json_str():
    # TODO:
    pass


def test_rw_toml():
    # TODO:
    pass


def test_rw_pqt():
    # TODO:
    pass


def test_subprocess():
    # TODO:
    pass
