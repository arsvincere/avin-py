#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================
""" Doc """

from __future__ import annotations

class Strategy():# {{{
    """ Message """# {{{
    signal = Message(Signal)
    # }}}
    def __init__(self, name, version, general=None):# {{{
        self.__name = name
        self.__version = version
        self.__general = general
        self.__loadConfig()
        self.__loadShortList()
        self.__loadLongList()
    # }}}
    def __str__(self):# {{{
        return self.name
    # }}}
    def __loadConfig(self):# {{{
        path = Cmd.join(self.dir_path, "config.cfg")
        self.__cfg = Cmd.loadJSON(path)
    # }}}
    def __loadLongList(self):# {{{
        path = Cmd.join(self.dir_path, "long.al")
        self.__long_list = AssetList.load(path, parent=self)
    # }}}
    def __loadShortList(self):# {{{
        path = Cmd.join(self.dir_path, "short.al")
        self.__short_list = AssetList.load(path, parent=self)
    # }}}
    @staticmethod  #load# {{{
    def load(name: str, version: str, general=None):
        module = name.lower()
        path = f"user.strategy.{name}.{version}"
        modul = importlib.import_module(path)
        strategy_class = modul.__getattribute__(f"UStrategy")
        s = strategy_class(general=general)
        return s
    # }}}
    @staticmethod  #versions# {{{
    def versions(strategy_name: str):
        path = Cmd.join(STRATEGY_DIR, strategy_name)
        files = Cmd.getFiles(path)
        files = Cmd.select(files, extension=".py")
        ver_list = list()
        for file in files:
            ver = file.replace(".py", "")
            ver_list.append(ver)
        return ver_list
    # }}}
    @property  #name# {{{
    def name(self):
        return self.__name
    # }}}
    @property  #version# {{{
    def version(self):
        return self.__version
    # }}}
    @property  #config# {{{
    def config(self):
        return self.__cfg
    # }}}
    @property  #timeframe_list# {{{
    def timeframe_list(self):
        return self.__cfg["timeframe_list"]
    # }}}
    @property  #long_list# {{{
    def long_list(self):
        return self.__long_list
    @long_list.setter
    def long_list(self, alist):
        alist.name = "long"
        self.__long_list = alist
    # }}}
    @property  #short_list# {{{
    def short_list(self):
        return self.__short_list
    @short_list.setter
    def short_list(self, alist):
        alist.name = "short"
        self.__short_list = alist
    # }}}
    @property  #path# {{{
    def path(self):
        path = Cmd.join(self.dir_path, f"{self.version}.py")
        return path
    # }}}
    @property  #dir_path# {{{
    def dir_path(self):
        path = Cmd.join(STRATEGY_DIR, self.name)
        Cmd.createDirs(path)
        return path
    # }}}
    @property  #general# {{{
    def general(self):
        return self.__general
    # }}}
    def start(self):# {{{
        self.last_tested_dt = datetime(1, 1, 1, 0, 0, tzinfo=UTC)
    # }}}
    def finish(self):# {{{
        ...
    # }}}
    ALL = list()# {{{
    __dirs = Cmd.getDirs(STRATEGY_DIR, full_path=False)
    for __name in __dirs:
        ALL.append(__name)
    # }}}
# }}}

if __name__ == "__main__":
    ...

