# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

import json
import shutil
import subprocess
import tomllib
import zipfile
from collections import deque
from pathlib import Path

import polars as pl
import tomli_w


class Cmd:
    @staticmethod
    def path(*path_parts: (Path)) -> Path:
        """Склеивает все части в один путь"""

        path = Path.joinpath(*path_parts)
        return path

    @staticmethod
    def make_dirs(dir_path: Path) -> None:
        """Создает все необходимые папки для этого пути"""

        dir_path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def make_dirs_for_filepath(file_path: Path) -> None:
        # TODO: test it
        dir_path = file_path.parent
        Cmd.make_dirs(dir_path)

    @staticmethod
    def name(file_path: Path, extension: bool = False) -> str:
        """Отделяет имя файла из пути к файлу
        /home/file_name.txt -> file_name.txt  # extension=True
        /home/file_name.txt -> file_name  # extension=False
        """

        if extension:
            return file_path.name  # == name.xxx
        else:
            return file_path.stem  # == name

    @staticmethod
    def size(file_path: Path) -> int:
        # TODO: test it
        return file_path.stat().st_size

    @staticmethod
    def dir_name(file_path: Path) -> str:
        assert Cmd.is_file(file_path)

        return file_path.parent.name

    @staticmethod
    def dir_path(file_path: Path) -> Path:
        assert Cmd.is_file(file_path)

        return file_path.parent

    @staticmethod
    def is_exist(path: Path) -> bool:
        return path.is_file() or path.is_dir()

    @staticmethod
    def is_file(path: Path) -> bool:
        return path.is_file()

    @staticmethod
    def is_dir(path: Path) -> bool:
        return path.is_dir()

    @staticmethod
    def content(dir_path: Path, full_path=False) -> list[str]:
        contents = list()

        for i in dir_path.iterdir():
            if full_path:
                contents.append(str(i))
            else:
                contents.append(i.name)

        return contents

    @staticmethod
    def get_files(
        dir_path: Path, full_path=False, include_sub_dir=False
    ) -> list[str]:
        if include_sub_dir:
            return Cmd.__get_files_in_dir_include_subdir(dir_path, full_path)
        else:
            return Cmd.__get_files_in_dir(dir_path, full_path)

    @staticmethod
    def get_dirs(dir_path: Path, full_path=False) -> list[str]:
        """Возвращает список папок в 'dir_path' без обхода подпапок"""

        dirs = list()

        for i in dir_path.iterdir():
            if i.is_dir():
                if full_path:
                    dirs.append(str(i))
                else:
                    dirs.append(i.name)

        return dirs

    @staticmethod
    def find_file(file_name: str, dir_path: Path) -> list[Path]:
        """Searching file include subdirs, collect all founded.
        file_name may be a pattern, for example "*_test.py"
        """

        finded = list()

        for i in dir_path.rglob(file_name):
            if i.is_file():
                finded.append(i)

        return finded

    @staticmethod
    def find_dir(dir_name: str, root_dir: Path) -> list[Path]:
        """Searching dir (include subdirs), collect all founded.
        dir_name may be a pattern, for example "u*"
        """
        finded = list()

        for i in root_dir.rglob(dir_name):
            if i.is_dir():
                finded.append(i)

        return finded

    @staticmethod
    def rename(old_path: Path, new_path: Path) -> None:
        """Переименовывает old_path в new_path"""

        old_path.rename(new_path)

    @staticmethod
    def replace(src: Path, dest: Path, create_dirs=True) -> None:
        """Перемещает src в dest.

        В отличии от Cmd.rename флаг create_dirs позволяет
        создать при необходимости путь к директории.

        WARNING: Overriding if dest is exist!
        """

        if create_dirs:
            Cmd.make_dirs_for_filepath(dest)

        src.replace(dest)

    @staticmethod
    def copy(src_file: Path, dest_file: Path) -> None:
        """Копирует src в dest"""

        shutil.copy(src_file, dest_file)

    @staticmethod
    def copy_dir(src: Path, dest: Path) -> None:
        """Копирует src в dest"""

        shutil.copytree(src, dest)

    @staticmethod
    def delete(file_path: Path) -> None:
        """Удаляет файла по указанному пути"""

        file_path.unlink()

    @staticmethod
    def delete_dir(dir_path: Path) -> None:
        shutil.rmtree(dir_path)

    @staticmethod
    def extract(archive_path: Path, dest_dir: Path) -> None:
        with zipfile.ZipFile(archive_path, "r") as file:
            file.extractall(dest_dir)

    @staticmethod
    def read(file_path: Path) -> str:
        """Read file as one string"""

        with open(file_path, encoding="utf-8") as file:
            string = file.read()

        return string

    @staticmethod
    def write(string: str, file_path: Path, create_dirs=True) -> None:
        """Write string in file (overwrite)"""
        if create_dirs:
            Cmd.make_dirs_for_filepath(file_path)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(string)

    @staticmethod
    def append(text: list[str], file_path: Path) -> None:
        """Append text in file"""

        with open(file_path, "a", encoding="utf-8") as file:
            for line in text:
                file.write(line)

    @staticmethod
    def get_tail(file_path: Path, n: int) -> list[str]:
        # Читает весь файл построчно и добавляет его в
        # очередь, у которой максимальная длина n... таким образом
        # дойдя до конца файла в очереди останется n последних строк

        with open(file_path, encoding="utf-8") as file:
            text = list(deque(file, n))

        return text

    @staticmethod
    def read_text(file_path: Path) -> list[str]:
        """Read file by row, return list[str]"""

        text = list()
        with open(file_path, encoding="utf-8") as file:
            for line in file:
                text.append(line)

        return text

    @staticmethod
    def write_text(
        text: list[str], file_path: Path, create_dirs=True
    ) -> None:
        if create_dirs:
            Cmd.make_dirs_for_filepath(file_path)

        with open(file_path, "w", encoding="utf-8") as file:
            for line in text:
                file.write(line)

    @staticmethod
    def read_json(file_path: Path, decoder=None):
        with open(file_path, encoding="utf-8") as file:
            obj = json.load(
                fp=file,
                object_hook=decoder,
            )

        return obj

    @staticmethod
    def write_json(
        obj, file_path: Path, encoder=None, indent=4, create_dirs=True
    ) -> None:
        if create_dirs:
            Cmd.make_dirs_for_filepath(file_path)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(
                obj=obj,
                fp=file,
                indent=indent,
                default=encoder,
                ensure_ascii=False,
            )

    @staticmethod
    def from_json_str(string: str, decoder=None) -> object:
        obj = json.loads(
            string,
            object_hook=decoder,
        )

        return obj

    @staticmethod
    def to_json_str(obj, encoder=None, indent=0) -> str:
        string = json.dumps(
            obj=obj,
            indent=indent,
            default=encoder,
            ensure_ascii=False,
        )

        return string

    @staticmethod
    def read_toml(file_path: Path) -> object:
        with file_path.open(mode="rb") as f:
            data = tomllib.load(f)

        return data

    @staticmethod
    def write_toml(obj, file_path: Path) -> None:
        with file_path.open(mode="wb") as f:
            tomli_w.dump(obj, f)

    @staticmethod
    def read_pqt(path: Path) -> pl.DataFrame:
        df = pl.read_parquet(path)

        return df

    @staticmethod
    def write_pqt(
        df: pl.DataFrame, path: Path, create_dirs: bool = True
    ) -> None:
        if create_dirs:
            Cmd.make_dirs_for_filepath(path)

        df.write_parquet(path)

    @staticmethod
    def subprocess(command: list[str]) -> None:
        """
        import platform
        import subprocess
        # define a command that starts new terminal
        if platform.system() == "Windows":
            new_window_command = "cmd.exe /c start".split()
        else:
            new_window_command = "x-terminal-emulator -e".split()
        subprocess.check_call(new_window_command + command)
        """
        subprocess.call(command)

    @staticmethod
    def __get_files_in_dir(dir_path: Path, full_path: bool) -> list[str]:
        all_files = list()

        for i in dir_path.iterdir():
            if i.is_file():
                if full_path:
                    all_files.append(str(i))
                else:
                    all_files.append(i.name)

        return all_files

    @staticmethod
    def __get_files_in_dir_include_subdir(
        dir_path: Path, full_path: bool
    ) -> list[str]:
        all_files = list()

        for i in dir_path.rglob("*"):
            if i.is_file():
                if full_path:
                    all_files.append(str(i))
                else:
                    all_files.append(i.name)

        return all_files

    # @staticmethod
    # def write_bin(
    #     obj: object, path: str, compres=False, create_dirs=True
    # ) -> None:
    #     if create_dirs:
    #         Cmd.make_dirs_for_filepath(path)
    #
    #     fh = None
    #     try:
    #         fh = gzip.open(path, "wb") if compres else open(path, "wb")
    #         pickle.dump(obj, fh, pickle.HIGHEST_PROTOCOL)
    #
    #     except (OSError, pickle.PicklingError):
    #         exit(1)
    #
    #     finally:
    #         if fh is not None:
    #             fh.close()

    # @staticmethod
    # def read_bin(file_path) -> object:
    #     GZIP_MAGIC = b"\x1f\x8b"  # метка .gzip файлов
    #
    #     try:
    #         fh = open(file_path, "rb")
    #         magic = fh.read(len(GZIP_MAGIC))
    #         if magic == GZIP_MAGIC:
    #             fh.close()
    #             fh = gzip.open(file_path, "rb")
    #         else:
    #             fh.seek(0)
    #         obj = pickle.load(fh)
    #         return obj
    #
    #     except (OSError, pickle.UnpicklingError):
    #         exit(1)
    #
    #     finally:
    #         if fh is not None:
    #             fh.close()


if __name__ == "__main__":
    ...
