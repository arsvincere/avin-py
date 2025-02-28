#!/usr/bin/env  python3
# ============================================================================
# URL:          http://alexavin.blog
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPL
# ============================================================================

import re
from avin.utils import Cmd

# ----------------------------------------------------------------------------

SRC_DIR = "avin"
DESIGN_DIR = "dev/design"
MD_DIR = "/home/alex/ya/diary/note"

def main():
    code_files = Cmd.getFiles(SRC_DIR, full_path=True, include_sub_dir=True)
    code_files = Cmd.select(code_files, extension=".py")
    code_files = filter(lambda x: not Cmd.name(x) == "__init__", code_files)
    for file_path in code_files:
        process(file_path)

    # export to obsidian
    formated_files = Cmd.getFiles(DESIGN_DIR, full_path=True, include_sub_dir=True)
    for file_path in formated_files:
        splitByClass(file_path)

def process(file_path):# {{{
    code = Cmd.loadText(file_path)
    code = removeMarkers(code)
    code = removeComment(code)
    code = removeDocStr(code)
    code = removeImport(code)
    code = removeLoggerAndSysPath(code)
    code = removeException(code)
    code = removeEmptyLine(code)
    code = replaceArgsInOneLine(code)

    # reload
    # костыль с переносами строк после replaceArgsInOneLine
    # проще перезагрузить чем исправлять
    new_file_path = file_path.replace(SRC_DIR, DESIGN_DIR) + "i"
    Cmd.saveText(code, new_file_path)
    code = Cmd.loadText(new_file_path)

    code = removeCode(code)
    code = formatDecorators(code)
    code = clearArgs(code)
    # code = removePrivateMembers(code)
    Cmd.saveText(code, new_file_path)
# }}}
def removeMarkers(code):# {{{{{{
    i = 0
    while i < len(code):
        line = code[i]
        line = line.replace("# {{{", "")
        line = line.replace("# }}}", "")
        code[i] = line
        i += 1
    return code
# }}}}}}
def removeComment(code):# {{{
    i = 0
    while i < len(code):
        line = code[i]
        if re.match(" *#.+\n", line):
            code.pop(i)
        else:
            i += 1

    i = 0
    while i < len(code):
        line = code[i]
        if "  # operator" in line:
            line = line[0:line.find("  # operator")] + "\n"
            code[i] = line
        i += 1
    return code
# }}}
def removeDocStr(code):# {{{
    # remove single string docs
    i = 0
    while i < len(code):
        line = code[i]
        if re.match(' *""".+"""', line):
            code.pop(i)
        else:
            i += 1

    # remove multiple string docs
    i = 0
    while i < len(code):
        line = code[i]
        if line.strip().startswith('"""'):
            code.pop(i)
            while not code[i].strip().endswith('"""'):
                code.pop(i)
            code.pop(i)
        else:
            i += 1
    return code
# }}}
def removeImport(code):# {{{
    # remove import
    i = 0
    while i < len(code):
        line = code[i]
        if line.startswith("import "):
            code.pop(i)
        else:
            i += 1

    # remove from
    i = 0
    while i < len(code):
        line = code[i]
        if re.match("from .*[^(] \\(", line):  # типо 'from modul import ('
            code.pop(i)
            while not re.match(".*[^)]\\)\n", code[i]):
                code.pop(i)
            code.pop(i)  # )  конец импорта в скобках
        elif line.startswith("from "): # однострочный 'from a import b'
            code.pop(i)
        else:
            i += 1
    return code
# }}}
def removeLoggerAndSysPath(code):# {{{
    i = 0
    while i < len(code):
        line = code[i]
        if line.startswith("logger"):
            code.pop(i)
        elif line.startswith("sys.path.append("):
            code.pop(i)
        else:
            i += 1
    return code
# }}}
def removeException(code):# {{{
    i = 0
    while i < len(code):
        line = code[i]
        if re.match("class .+(Exception).+", line):
            code.pop(i)
        else:
            i += 1
    return code
# }}}
def removeEmptyLine(code):# {{{
    i = 0
    while i < len(code):
        line = code[i].strip()
        if len(line) == 0:
            code.pop(i)
        else:
            i += 1
    return code
# }}}
def replaceArgsInOneLine(code): # {{{
    i = 0
    while i < len(code):
        line = code[i]
        if line.startswith("    def") and line.endswith("(\n"):
            line = line.replace("\n", "")
            while not code[i + 1].endswith(":\n"):
                line += code[i + 1].lstrip().replace("\n", "") + " "
                code.pop(i + 1)
            line += code[i + 1].lstrip()
            code.pop(i + 1)
            code[i] = line
        else:
            i += 1
    return code
# }}}
def removeCode(code):# {{{
    i = 0
    while i < len(code):
        line = code[i]
        first_word, *_ = line.strip(' ":=').split()
        if first_word.isupper() and len(first_word) > 3:
            i += 1
            continue
        elif line.startswith("class"):
            i += 1
            continue
        elif line.startswith("    class"):
            i += 1
            continue
        elif "@abc.abstractmethod " in line:
            i += 1
            continue
        elif "@staticmethod " in line:
            i += 1
            continue
        elif "@classmethod " in line:
            i += 1
            continue
        elif "@property " in line:
            i += 1
            continue
        elif "def " in line:
            i += 1
            continue
        else:
            code.pop(i)
    return code
# }}}
def formatDecorators(code):# {{{
    i = 0
    while i < len(code):
        line = code[i]
        if line.startswith("    @abc.abstractmethod"):
            code[i] = "    @abc.abstractmethod "
            code[i] += code.pop(i + 1).strip() + "\n"  # def line
            i += 1
        elif line.startswith("    @staticmethod"):
            code[i] = "    @staticmethod "
            code[i] += code.pop(i + 1).strip() + "\n"  # def line
            i += 1
        elif line.startswith("    @classmethod"):
            code[i] = "    @classmethod "
            code[i] += code.pop(i + 1).strip() + "\n"  # def line
            i += 1
        elif line.startswith("    @property"):
            code[i] = "    @property "
            code[i] += code.pop(i + 1).strip() + "\n"  # def line
            i += 1
        elif line.startswith("        @staticmethod"):
            code[i] = "        @staticmethod "
            code[i] += code.pop(i + 1).strip() + "\n"  # def line
            i += 1
        elif line.startswith("        @classmethod"):
            code[i] = "        @classmethod "
            code[i] += code.pop(i + 1).strip() + "\n"  # def line
            i += 1
        elif line.startswith("        @property"):
            code[i] = "        @property "
            code[i] += code.pop(i + 1).strip() + "\n"  # def line
            i += 1
        else:
            i += 1
    return code
# }}}
def clearArgs(code):# {{{
    i = 0
    while i < len(code):
        line = code[i]
        if "def" in line:
            line = re.sub("cls, ", "", line)
            line = re.sub("cls", "", line)
            line = re.sub("self, ", "", line)
            line = re.sub("self", "", line)
            line = re.sub(": [^,)]+", "", line)
            line = re.sub("=[^,)]+", "", line)
            code[i] = line
        i += 1
    return code
# }}}
def removePrivateMembers(code):# {{{
    i = 0
    while i < len(code):
        line = code[i]
        if re.match(".*def .*[^_]__.*", line):  # magic methon, оставляем
            i += 1
            continue
        if re.match(".*def __.+", line):  # def __*  удаляем
            code.pop(i)
        else:
            i += 1
    return code
# }}}
def splitByClass(file_path):# {{{
    # print(file_path)
    code = Cmd.loadText(file_path)
    dir_path = Cmd.dirPath(file_path)
    file_name = Cmd.name(file_path)
    sub_dir = Cmd.path(MD_DIR, dir_path, file_name).replace("/dev", "")
    Cmd.makeDirs(sub_dir)
    print(dir_path, file_name, sub_dir)
    i = 0
    while i < len(code):
        line = code[i]
        if line.startswith("class"):
            _, class_name, *_ = line.split()
            class_name = class_name[0:class_name.find("(")] + ".md"
            one_class = list()
            one_class.append("```python\n")
            one_class.append(code[i])
            i += 1
            while i < len(code) and not code[i].startswith("class"):
                one_class.append(code[i])
                i += 1
            one_class.append("\n```")
            path = Cmd.path(sub_dir, class_name)
            Cmd.saveText(one_class, path)
        else:
            i += 1
# }}}



if __name__ == "__main__":
    main()

# async def main():
#     g = General()
#     g.initialize()
#     await g.start()
#
#
# if __name__ == "__main__":
#     asyncio.run(main())


