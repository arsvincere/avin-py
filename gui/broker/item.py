#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

from avin.utils import Cmd


class IToken(QtWidgets.QTreeWidgetItem):  # {{{
    def __init__(self, name, token, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        self.__name = name
        self.__type = Tree.Type.TOKEN
        self.__token = token
        self.__config()

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        )
        self.setText(Tree.Column.Broker, self.__name)

    # }}}
    @property  # name# {{{
    def name(self):
        return self.__name

    # }}}
    @property  # type# {{{
    def type(self):
        return self.__type

    # }}}
    @property  # token# {{{
    def token(self):
        return self.__token


# }}}
# }}}
class ISandbox(Sandbox, QtWidgets.QTreeWidgetItem):  # {{{
    def __init__(self, path: str, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        Sandbox.__init__(self)
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        self.__path = path
        self.__name = Cmd.name(self.__path)
        self.__type = Tree.Type.BROKER
        self.__config()
        self.__createChilds()

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        )
        self.setText(Tree.Column.Broker, self.__name.title())

    # }}}
    def __createChilds(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createChilds()")
        dir_path = self.__path
        files = Cmd.getFiles(dir_path, full_path=True)
        files = Cmd.select(files, ".txt")
        for file in files:
            name = Cmd.name(file, extension=False)
            token = Cmd.read(file).strip()
            itoken = IToken(name, token, self)

    # }}}
    @property  # name# {{{
    def name(self):
        return self.__name

    # }}}
    @property  # type# {{{
    def type(self):
        return self.__type

    # }}}
    @property  # path# {{{
    def path(self):
        return self.__path


# }}}
# }}}
class ITinkoff(Tinkoff, QtWidgets.QTreeWidgetItem):  # {{{
    def __init__(self, path: str, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        Tinkoff.__init__(self)
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        self.__path = path
        self.__name = Cmd.name(self.__path)
        self.__type = Tree.Type.BROKER
        self.__config()
        self.__createChilds()

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        )
        self.setText(Tree.Column.Broker, self.__name.title())

    # }}}
    def __createChilds(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createChilds()")
        dir_path = self.__path
        files = Cmd.getFiles(dir_path, full_path=True)
        files = Cmd.select(files, ".txt")
        for file in files:
            name = Cmd.name(file, extension=False)
            token = Cmd.read(file).strip()
            itoken = IToken(name, token, self)

    # }}}
    @property  # name# {{{
    def name(self):
        return self.__name

    # }}}
    @property  # type# {{{
    def type(self):
        return self.__type

    # }}}
    @property  # path# {{{
    def path(self):
        return self.__path


# }}}
# }}}


if __name__ == "__main__":
    ...
