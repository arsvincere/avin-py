#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations
from typing import Optional

from avin import *

__all__ = ("Scan","ScanList",)


class Scan:  # {{{
    class Status(enum.Enum):  # {{{
        UNDEFINE = 0
        NEW = 1
        EDITED = 2
        PROCESS = 3
        COMPLETE = 4

        @classmethod  # fromStr
        def fromStr(cls, string):
            statuses = {
                "NEW": Scan.Status.NEW,
                "EDITED": Scan.Status.EDITED,
                "PROCESS": Scan.Status.PROCESS,
                "COMPLETE": Scan.Status.COMPLETE,
            }
            return statuses[string]

    # }}}

    def __init__(self, name: str):  # {{{
        self.__name = name
        self.__filter: Optional[Filter] = None
        self.__asset: Optional[Asset] = None
        self.__begin = date(2018, 1, 1)
        self.__end = date(2023, 1, 1)
        self.__description = ""
        self.__deal_list = DealList(f"{self}-deal_list")
        self.__scan_list = None
        self.__status = Scan.Status.NEW

        # signals
        self.progress = Signal(int)

    # }}}
    def __str__(self):  # {{{
        return f"Scan={self.__name}"

    # }}}

    @property  # name  # {{{
    def name(self):
        return self.__name

    @name.setter
    def name(self, name: str):
        self.__name = name
        self.__deal_list.name = f"{self}-deal_list"

    # }}}
    @property  # filter  # {{{
    def filter(self):
        return self.__filter

    @filter.setter
    def filter(self, filter: Filter):
        self.__filter = Filter

    # }}}
    @property  # asset  # {{{
    def asset(self):
        return self.__asset

    @asset.setter
    def asset(self, asset: Asset):
        self.__asset = asset

    # }}}
    @property  # begin  # {{{
    def begin(self) -> date:
        return self.__begin

    @begin.setter
    def begin(self, begin: date):
        assert isinstance(begin, date)
        self.__begin = begin

    # }}}
    @property  # end  # {{{
    def end(self) -> date:
        return self.__end

    @end.setter
    def end(self, end: date):
        assert isinstance(end, date)
        self.__end = end

    # }}}
    @property  # description  # {{{
    def description(self):
        return self.__description

    @description.setter
    def description(self, description):
        self.__description = description

    # }}}
    @property  # deal_list  # {{{
    def deal_list(self):
        return self.__deal_list

    @deal_list.setter
    def deal_list(self, deal_list: DealList):
        self.__deal_list = deal_list

        if deal_list is not None:
            deal_list.name = f"{self}-deal_list"

    # }}}
    @property  # scan_list  # {{{
    def scan_list(self):
        return self.__scan_list

    @scan_list.setter
    def scan_list(self, scan_list: ScanList):
        self.__scan_list = scan_list

    # }}}
    @property  # status  # {{{
    def status(self):
        return self.__status

    @status.setter
    def status(self, new_status):
        self.__status = new_status

    # }}}

    @classmethod  # save  # {{{
    async def save(cls, scan: Scan) -> None:


    # }}}
    @classmethod  # load  # {{{
    async def load(cls, name: str) -> Scan | None:


    # }}}
    @classmethod  # delete  # {{{
    async def delete(cls, scan) -> None:


    # }}}
# }}}
class ScanList:  # {{{
    def __init__(self, name: str, scans: Optional[list[Scan]] = None):  # {{{

        self.__name = name
        self.__scans = scans if scans else list()

        for scan in self.__scans:
            scan.scan_list = self

    # }}}
    def __str__(self):  # {{{
        return f"ScanList={self.__name}"

    # }}}
    def __iter__(self) -> Iterator:  # {{{
        return iter(self.__scans)

    # }}}
    def __contains__(self, scan: Scan) -> bool:  # {{{
        return any(i == scan for i in self.__scans)

    # }}}
    def __len__(self):  # {{{
        return len(self.__scans)

    # }}}

    @property  # name  # {{{
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str):
        assert isinstance(name, str)
        self.__name = name

    # }}}
    @property  # scans  # {{{
    def scans(self) -> list[Scan]:
        return self.__scans

    @scans.setter
    def scans(self, scans: list[Scan]):
        assert isinstance(scans, list)
        for i in scans:
            assert isinstance(i, Scan)

        self.__scans = scans

    # }}}

    def add(self, scan: Scan) -> None:  # {{{
        assert isinstance(scan, Scan)

        if scan not in self:
            scan.scan_list = self
            self.__scans.append(scan)
            return

        logger.warning(f"{scan} already in list '{self.name}'")

    # }}}
    def remove(self, scan: Scan) -> None:  # {{{
        try:
            self.__scans.remove(scan)
            scan.scan_list = None
        except ValueError:
            logger.warning(f"'{scan}' not in list '{self.name}'")

    # }}}
    def clear(self) -> None:  # {{{
        for scan in self.__scans:
            scan.scan_list = None

        self.__scans.clear()

    # }}}

    @classmethod  # save  # {{{
    async def save(cls, scan_list: ScanList) -> None:
        logger.info(f":: Saving ScanList {name}")
        assert isinstance(scan_list, ScanList)

        for scan in scan_list:
            await Scan.save(scan)

    # }}}
    @classmethod  # load  # {{{
    async def load(cls, name: str) -> ScanList | None:
        logger.info(f":: Loading ScanList {name}")


    # }}}
    @classmethod  # delete  # {{{
    async def delete(cls, scan_list: ScanList) -> None:
        logger.info(f":: Deleting ScanList {name}")
        assert isinstance(scan_list, ScanList)


    # }}}
# }}}


if __name__ == "__main__":
    ...
