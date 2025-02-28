#!/usr/bin/env python3
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com

import os
import sys
import json
import pickle
import shutil
import bisect
import zipfile
import logging
import subprocess
from collections import deque
from datetime import datetime, timedelta, timezone
sys.path.append("/home/alex/AVIN/")
from avin.const import UTC, LOGGER_FORMAT

logging.basicConfig(format = LOGGER_FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def codeCounter(dir_path):
    count_file = 0
    count_str = 0
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                text = Cmd.load(file_path)
                n = len(text)
                count_str += n
                count_file += 1
    return count_file, count_str

def now():
    return datetime.utcnow().replace(tzinfo=UTC)

def binarySearch(vector, x, key=None):
    left = 0
    right = len(vector) - 1
    while left <= right:
        mid = (left + right) // 2
        mid_val = vector[mid] if key is None else key(vector[mid])
        if x == mid_val:
            return mid
        if x < mid_val:
            right = mid - 1
        else:
            left = mid + 1
    return None

def findLeft(vector, x, key=None):
    """ Возвращает индекс элемента меньше или равного 'x'
    Если 'x', меньше самого левого элемента в векторе, возвращает None
    """
    i = bisect.bisect_right(vector, x, key=key)
    if i:
        return i-1
    return None

def findRight(vector, x, key=None):
    """ Возвращает индекс элемента больше или равного 'x'
    Если 'x', больше самого правого элемента в векторе, возвращает None
    """
    i = bisect.bisect_left(vector, x, key=key)
    if i != len(vector):
        return i
    return None


class Cmd():
    @staticmethod  #join
    def join(*path):
        logger.debug(f"Cmd.join({path})")
        path = os.path.join(*path)
        return path

    @staticmethod  #getFileName
    def getFileName(file_path, extension=False):
        """ -- Doc
        Отделяет имя файла из пути к файлу
        /home/file_name.txt -> file_name.txt  # extension=True
        /home/file_name.txt -> file_name  # extension=False
        """
        logger.debug(f"Cmd.getFileName({file_path}, extension={extension}")
        file_name = os.path.basename(file_path)  # == somename.xxx
        if extension:
            return file_name
        else:
            name = os.path.splitext(file_name)[0]  # == somename
            return name

    @staticmethod  #isExist
    def isExist(path):
        logger.debug(f"Cmd.isExist({path})")
        return os.path.exists(path)

    @staticmethod  #isFile
    def isFile(path):
        logger.debug(f"Cmd.isFile({path})")
        return os.path.isfile(path)

    @staticmethod  #isDir
    def isDir(path):
        logger.debug(f"Cmd.isFile({path})")
        return os.path.isdir(path)

    @staticmethod  #getFiles
    def getFiles(dir_path, full_path=False):
        logger.debug(f"Cmd.getFiles({dir_path}, full_path={full_path})")
        list_files = list()
        names = os.listdir(dir_path)
        for name in names:
            path = Cmd.join(dir_path, name)
            if os.path.isfile(path):
                if full_path:
                    list_files.append(path)
                else:
                    list_files.append(name)
        return list_files

    @staticmethod  #getDirs
    def getDirs(dir_path, full_path=False):
        """ -- Doc
        Возвращает список папок в каталоге 'dir_path' без обхода подпапок
        """
        logger.debug(f"Cmd.getDirs({dir_path}, full_path={full_path})")
        list_dirs = list()
        names = os.listdir(dir_path)
        for name in names:
            path = Cmd.join(dir_path, name)
            if os.path.isdir(path):
                if full_path:
                    list_dirs.append(path)
                else:
                    list_dirs.append(name)
        return list_dirs

    @staticmethod  #createDirs
    def createDirs(path):
        """ Создает все необходимые папки для этого пути """
        try:
            os.makedirs(path)
            logger.debug(f"Create dirs: {path}")
        except FileExistsError as err:
            pass  # Если папка уже существует просто выходим

    @staticmethod  #deleteDir
    def deleteDir(path):
        shutil.rmtree(path)
        logger.debug(f"Delete dir: {path}")

    @staticmethod  #extractArchive
    def extractArchive(archive_path, dest_dir):
        with zipfile.ZipFile(archive_path, "r") as file:
            file.extractall(dest_dir)
        logger.debug(f"Extracted archive: '{archive_path}'")

    @staticmethod  #findFile
    def findFile(file_name, dir_path):
        logger.debug(f"Cmd.findFile({file_name}, {dir_path})")
        for root, dirs, files in os.walk(dir_path):
            if file_name in files:
                return os.path.join(root, file_name)
            else:
                raise FileNotFoundError(f"Файл '{file_name}' не найден "
                                         "в директории '{dir_path}'")

    @staticmethod  #findDir
    def findDir(dir_name, root_dir):
        logger.debug(f"Cmd.findDir({dir_name}, {root_dir})")
        for root, dirs, files in os.walk(root_dir):
            if dir_name in dirs:
                return os.path.join(root, dir_name)
        raise FileNotFoundError(f"Папка '{dir_name}' не найдена "
                                 "в директории '{root_dir}'")

    @staticmethod  #select
    def select(files, extension):
        """ Возвращает список файлов c расширением 'extension' """
        selected = list()
        for file in files:
            if file.endswith(extension):
                selected.append(file)
        return selected

    @staticmethod  #rename
    def rename(old_path, new_path):
        """ Переименовывает old_path в new_path"""
        os.replace(old_path, new_path)

    @staticmethod  #replace
    def replace(src, dest):
        """ Перемещает src в dest """
        os.replace(src, dest)

    @staticmethod  #delete
    def delete(file_path):
        """ Удаляет файла по указанному пути """
        os.remove(file_path)
        logger.debug(f"Delete: {file_path}")

    @staticmethod  #open
    def open(program, file_path):
        logger.debug(f"Cmd.open({program}, {file_path})")
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
        command = [program, file_path]
        # new_window_command = "x-terminal-emulator -e".split()
        new_window_command = "xfce4-terminal -x".split()
        # new_window_command = "xterm -e".split()
        subprocess.call(new_window_command + command)

    @staticmethod  #save
    def save(text: list[str], file_path: str) -> bool:
        with open(file_path, "w", encoding="utf-8") as file:
            for line in text:
                file.write(line)
        logger.debug(f"Save file: {file_path}")
        return True

    @staticmethod  #load
    def load(file_path, by_line=True):
        text = list()
        with open(file_path, "r", encoding="utf-8") as file:
            if by_line:
                for line in file:
                    text.append(line)
            else:
                text = file.read()
        logger.debug(f"Load file: {file_path}")
        return text

    @staticmethod  #append
    def append(text, file_path):
        raise ItemError("Функция не написана")

    @staticmethod  #getTail
    def getTail(file_path, n):
        """ идиотский способ на самом деле.
        по сути он же читает весь файл построчно и добавляет его в
        очередь, у которой максимальная длина n... таким образом
        дойдя до конца файла в очереди останется n последних строк
        - тогда уж проще прочитать весь файл и взять N последний строк
        """
        with open(file_path, "r", encoding="utf-8") as file:
            text = list(deque(file, n))
        return text

    @staticmethod  #saveJSON
    def saveJSON(obj, file_path):
        text = json.dumps(obj, indent=4, ensure_ascii=False)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(text)
        logger.debug(f"Save json: {file_path}")

    @staticmethod  #loadJSON
    def loadJSON(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            obj = json.load(file)
        logger.debug(f"Load json: {file_path}")
        return obj

    @staticmethod  #saveBin
    def saveBin(self, file_path, silent=False, compress=False):
        if file_path == "auto":
            file_name = self.__autoFileName()
            dir_path = self.__autoDirPath()
            file_path = os.path.join(dir_path, file_name)
        fh = None
        try:
            if compress:
                fh = gzip.open(file_path, "wb")
            else:
                fh = open(file_path, "wb")
            pickle.dump([self.ID, self.timeframe, self.bars],
                        fh, pickle.HIGHEST_PROTOCOL)
            if not silent:
                print("SAVED:", file_path)
            return True
        except (EnvironmentError, pickle.PicklingError) as err:
            print("{0}: Ошибка сохранения: {1}".format(
                  os.path.basename(sys.argv[0]), err))
            return False
        finally:
            if fh is not None:
                fh.close()

    @staticmethod  #loadBin
    def loadBin(file_path, silent=False):
        GZIP_MAGIC = b"\x1F\x8B"  # метка .gzip файлов
        fh = None
        try:
            fh = open(file_path, "rb")
            magic = fh.read(len(GZIP_MAGIC))
            if magic == GZIP_MAGIC:
                fh.close()
                fh = gzip.open(file_path, "rb")
            else:
                fh.seek(0)
            ID, timeframe, bars = pickle.load(fh)
            if not silent:
                print("LOADED:", file_path)
            return Data.Data(ID, timeframe, bars)
        except (EnvironmentError, pickle.UnpicklingError) as err:
            print("{0}: Ошибка загрузки: {1}".format(
                  os.path.basename(sys.argv[0]), err))
            return False
        finally:
            if fh is not None:
                fh.close()



class Fuzzy(object):
    def __init__(self, value=0.0):
        self.__value = value

    def __invert__(self):  # operator ~ (логическое 'не')
        return Fuzzy(0.0 - self.__value)

    def __and__(self, other):  ## operator & (логическое 'и')
        return Fuzzy(min(self.__value, other.__value))

    def __iand__(self, other):  ## operator &= (логическое 'и')
        self.__value = Fuzzy(min(self.__value, other.__value))
        return self

    def __or__(self, other):  ## operator | (логическое 'или')
        return Fuzzy(max(self.__value, other.__value))

    def __ior__(self, other):  ## operator |= (логическое 'или')
        self.__value = Fuzzy(max(self.__value, other.__value))
        return self

    def __add__(self, other):  # operator +
        return Fuzzy(self.__value + other.__value)

    def __iadd__(self, other):  # operator +=
        self.__value = self.__value + other.__value
        return self

    def __sub__(self, other):  # operator -
        return Fuzzy(self.__value - other.__value)

    def __isub__(self, other):  # operator -=
        self.__value = self.__value - other.__value
        return self

    def __eq__(self, other):  # operator ==
        if not isinstance(other, Fuzzy):
            raise TypeError("operator == between <Fuzzy>"
                            " and {0}".format(type(other)))
            return self.__value == other.__value

    def __lt__(self, other):  # operator <
        if not isinstance(other, Fuzzy):
            raise TypeError("operator < between <Fuzzy>"
                            " and {0}".format(type(other)))
        return self.__value < other.__value

    def __le__(self, other):  # operator <=
        if not isinstance(other, Fuzzy):
            raise TypeError("operator <= between <Fuzzy>"
                            " and {0}".format(type(other)))
        return self.__value <= other.__value

    def __repr__(self):
        return ("{0}({1})".format(self.__class__.__name__,
                                  self.__value))

    def __str__(self):
        return str(self.__value)

    def __bool__(self):
        return self.__value > 0.0

    def __int__(self):
        return round(self.__value)

    def __float__(self):
        return self.__value

    def __hash__(self):
        return hash(id(self))

    def __format__(self, format_spec):
        return self.__value.__format__(format_spec)

    def disjunction(*fuzzies):
        """ Returns the logical or of all the Fuzzy """
        return Fuzzy(max([float(x) for x in fuzzies]))

    def conjunction(*fuzzies):
        """ Returns the logical and of all the Fuzzy """
        return Fuzzy(min([float(x) for x in fuzzies]))


class FuzzyBool(object):
    def __init__(self, value=0.0):
        """ UnitTest
        >>> f = Fuzzy()
        >>> g = Fuzzy(.5)
        >>> h = Fuzzy(3.75)
        >>> f, g, h
        (Fuzzy(0.0), Fuzzy(0.5), Fuzzy(0.0))
        """
        self.__value = value if 0.0 <= value <= 1.0 else 0.0

    def __invert__(self):  # operator ~ (логическое 'не')
        """ Returns the logical not of this Fuzzy
        >>> f = Fuzzy(0.125)
        >>> ~f
        Fuzzy(0.875)
        >>> ~Fuzzy()
        Fuzzy(1.0)
        >>> ~Fuzzy(1)
        Fuzzy(0.0)
        """
        return Fuzzy(1.0 - self.__value)

    def __and__(self, other):  ## operator & (логическое 'и')
        """ Returns the logical and of this Fuzzy and the other one
        >>> Fuzzy(0.5) & Fuzzy(0.6)
        Fuzzy(0.5)
        """
        return Fuzzy(min(self.__value, other.__value))

    def __iand__(self, other):  ## operator &= (логическое 'и')
        """Applies logical and to this Fuzzy with the other one
        >>> f = Fuzzy(0.5)
        >>> f &= Fuzzy(0.6)
        >>> f
        Fuzzy(0.5)
        """
        self.__value = Fuzzy(min(self.__value, other.__value))
        return self

    def __or__(self, other):  ## operator | (логическое 'и')
        """Returns the logical or of this Fuzzy and the other one
        >>> Fuzzy(0.5) | Fuzzy(0.75)
        Fuzzy(0.75)
        """
        return Fuzzy(max(self.__value, other.__value))

    def __ior__(self, other):  ## operator |= (логическое 'и')
        """Applies logical or to this Fuzzy with the other one
        >>> f = Fuzzy(0.5)
        >>> f |= Fuzzy(0.75)
        >>> f
        Fuzzy(0.75)
        """
        self.__value = Fuzzy(max(self.__value, other.__value))
        return self

    def __add__(self, other):  # operator +
        """ UnitTest
        >>> a = Fuzzy(0.2)
        >>> b = Fuzzy(0.3)
        >>> a + b
        Fuzzy(0.5)
        """
        s = self.__value + other.__value
        if 0.0 <= s <= 1.0:
            return Fuzzy(round(s, 2))
        elif s < 0:
            return Fuzzy(0.0)
        elif s > 1.0:
            return Fuzzy(1.0)

    def __iadd__(self, other):  # operator +=
        """ UnitTest
        >>> a = Fuzzy(0.8)
        >>> b = Fuzzy(0.7)
        >>> a += b
        >>> print(a)
        1.0
        """
        s = self.__value + other.__value
        if 0.0 <= s <= 1.0:
            self.__value = Fuzzy(round(s, 2))
        elif s < 0:
            self.__value = Fuzzy(0.0)
        elif s > 1.0:
            self.__value = Fuzzy(1.0)
        return self

    def __sub__(self, other):  # operator -
        """ UnitTest
        >>> a = Fuzzy(0.8)
        >>> b = Fuzzy(0.7)
        >>> a - b
        Fuzzy(0.1)
        >>> print(a)
        0.8
        """
        s = self.__value - other.__value
        if 0.0 <= s <= 1.0:
            return Fuzzy(round(s, 2))
        elif s < 0:
            return Fuzzy(0.0)
        elif s > 1.0:
            return Fuzzy(1.0)

    def __isub__(self, other):  # operator -=
        """ UnitTest
        >>> a = Fuzzy(0.8)
        >>> b = Fuzzy(0.9)
        >>> a -= b
        >>> print(a)
        0.0
        """
        s = self.__value - other.__value
        if 0.0 <= s <= 1.0:
            self.__value = Fuzzy(round(s, 2))
        elif s < 0:
            self.__value = Fuzzy(0.0)
        elif s > 1.0:
            self.__value = Fuzzy(1.0)
        return self

    def __eq__(self, other):  # operator ==
        if not isinstance(other, Fuzzy):
            raise TypeError("operator == between <Fuzzy>"
                            " and {0}".format(type(other)))
            return self.__value == other.__value

    def __lt__(self, other):  # operator <
        if not isinstance(other, Fuzzy):
            raise TypeError("operator < between <Fuzzy>"
                            " and {0}".format(type(other)))
        return self.__value < other.__value

    def __le__(self, other):  # operator <=
        if not isinstance(other, Fuzzy):
            raise TypeError("operator <= between <Fuzzy>"
                            " and {0}".format(type(other)))
        return float(self.__value) <= float(other.__value)

    def __repr__(self):
        """
        >>> f = Fuzzy(0.5)
        >>> repr(f)
        'Fuzzy(0.5)'
        """
        return ("{0}({1})".format(self.__class__.__name__,
                                  self.__value))

    def __str__(self):
        """
        >>> f = Fuzzy(0.5)
        >>> str(f)
        '0.5'
        """
        return str(self.__value)

    def __bool__(self):
        """
        >>> f = Fuzzy(.3)
        >>> g = Fuzzy(.51)
        >>> bool(f), bool(g)
        (False, True)
        """
        return self.__value > 0.5

    def __int__(self):
        return round(self.__value)

    def __float__(self):
        return self.__value

    def __hash__(self):
        return hash(id(self))

    def __format__(self, format_spec):
        """
        >>> f = Fuzzy(.875)
        >>> "{0:.0%}".format(f)
        '88%'
        >>> "{0:.1%}".format(f)
        '87.5%'
        """
        return self.__value.__format__(format_spec)

    def disjunction(*fuzzies):
        """Returns the logical or of all the Fuzzy
        >>> disjunction(Fuzzy(0.5), Fuzzy(0.75), 0.2, 0.1)
        Fuzzy(0.75)
        """
        return Fuzzy(max([float(x) for x in fuzzies]))

    def conjunction(*fuzzies):
        """Returns the logical and of all the Fuzzy
        >>> conjunction(Fuzzy(0.5), Fuzzy(0.6), 0.2, 0.125)
        Fuzzy(0.125)
        >>> print(conjunction(Fuzzy(1.0), Fuzzy(1.0)))
        1.0
        """
        return Fuzzy(min([float(x) for x in fuzzies]))


class SortedList(object):
    def __init__(self, seq=None, key=None):
        """ UnitTest
        >>> f = FuzzyBool()
        >>> g = FuzzyBool(.5)
        >>> h = FuzzyBool(3.75)
        >>> f, g, h
        (FuzzyBool(0.0), FuzzyBool(0.5), FuzzyBool(0.0))
        super().__init__()
        """
        self.__key = key or _identity
        assert hasattr(self.__key, "__call__")
        if seq is None:
            self.__list = []
        elif isinstance(seq, SortedList) and seq.key == self.__key:
            self.__list = seq.__list[:]
        else:
            self.__list = sorted(list(seq), key=self.__key)

    @property  #key
    def key(self):
        return self.__key()

    def add(self, value):
        index = self.__bisect_left(value)
        if index == len(self.__list):
            self.__list.append(value)
        else:
            self.__list.insert(index, value)

    def remove(self, value):
        index = self.__bisect_left(value)
        if index < len(self.__list) and self.__list[index] == value:
            del self.__list[index]
        else:
            raise ValueError("{0}.remove({1}): {1} not in list"\
                             .format(self.__class__.__name__, value))

    def removeEvery(self, value):
        count = 0
        index = self.__bisect_left(value)
        while (index < len(self.__list) and self.__list[index] == value):
            del self.__list[index]
            count += 1
        return count

    def count(self, value):
        count = 0
        index = self.__bisect_left(value)
        while (index < len(self.__list) and self.__list[index] == value):
            index += 1
            count += 1
        return count

    def index(self, value):
        index = self.__bisect_left(value)
        if index < len(self.__list) and self.__list[index] == value:
            return index
        raise ValueError("{0}.index({1}): {1} not in list"\
                .format(self.__class__.__name__, value))

    def clear(self):
        self.__list = []

    def pop(self, index=-1):
        return self.__list.pop(index)

    def copy(self):
        return SortedList(self, self.__key)

    def __bisect_left(self, value):
        key = self.__key(value)
        left, right = 0, len(self.__list)
        while left < right:
            middle = (left + right) // 2
            if self.__key(self.__list[middle]) < key:
                left = middle + 1
            else:
                right = middle
        return left

    def __delitem__(self, index):
        del self.__list[index]

    def __getitem__(self, index):  # operator [ ]
        return self.__list[index]

    def __setitem__(self, index, value):  # operator L[x] =
        raise TypeError("Use add() to insert a value")

    def __iter__(self):
        return iter(self.__list)

    def __reversed__(self):
        return reversed(self.__list)

    def __contains__(self, value):  # operator 'in'
        index = self.__bisect_left(value)
        return (index < len(self.__list) and self.__liset[index] == value)

    def __len__(self):
        return len(self.__list)

    def __str__(self):
        return str(self.__list)



if __name__ == "__main__":
    ...

