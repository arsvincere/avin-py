class _BarsDataFile:  # {{{
    def __init__(  # {{{
        self,
        ID: InstrumentId,
        data_type: DataType,
        bars: list[_Bar],
        source: Source,
    ):
        assert bars[0].dt.year == bars[-1].dt.year
        self.__ID = ID
        self.__data_type = data_type
        self.__bars = bars
        self.__source = source

    # }}}
    @property  # ID# {{{
    def ID(self):
        return self.__ID

    # }}}
    @property  # data_type# {{{
    def data_type(self):
        return self.__data_type

    # }}}
    @property  # bars# {{{
    def bars(self):
        return self.__bars

    # }}}
    @property  # source# {{{
    def source(self):
        return self.__source

    # }}}
    @property  # first_dt# {{{
    def first_dt(self):
        dt = self.bars[0].dt
        return dt

    # }}}
    @property  # last_dt# {{{
    def last_dt(self):
        dt = self.bars[-1].dt
        return dt

    # }}}
    @property  # year# {{{
    def year(self):
        y = self.bars[-1].dt.year
        return y

    # }}}
    @property  # dir_path# {{{
    def dir_path(self):
        dir_path = Cmd.path(self.__ID.dir_path, str(self.data_type.value))
        Cmd.makeDirs(dir_path)
        return dir_path

    # }}}
    def add(self, new_bars: list[_Bar]):  # {{{
        assert new_bars[-1].dt.year == self.year
        self.__bars += new_bars

    # }}}
    @classmethod  # save# {{{
    def save(cls, data):
        logger.debug(f"{cls.__name__}.save({data.ID.ticker})")
        cls.__saveID(data)
        cls.__saveDataType(data)
        cls.__saveBars(data)
        cls.__saveSource(data)

    # }}}
    @classmethod  # load# {{{
    def load(cls, ID: InstrumentId, data_type: DataType, year: int) -> _BarsDataFile:
        bars = cls.__loadBars(ID, data_type, year)
        source = cls.__loadSource(ID, data_type)
        data = _BarsDataFile(ID, data_type, bars, source)
        return data

    # }}}
    @classmethod  # __saveID# {{{
    def __saveID(cls, data: _BarsDataFile):
        path = Cmd.path(data.dir_path, "id")
        InstrumentId.save(data.ID, path)

    # }}}
    @classmethod  # __saveDataType# {{{
    def __saveDataType(cls, data):
        path = Cmd.path(data.dir_path, "data_type")
        Cmd.write(data.data_type.value, path)

    # }}}
    @classmethod  # __saveBars# {{{
    def __saveBars(cls, data):
        text = list()
        for bar in data.__bars:
            line = _Bar.toCSV(bar) + "\n"
            text.append(line)
        year = data.bars[0].dt.year
        file_path = Cmd.path(data.dir_path, f"{year}.csv")
        Cmd.saveText(text, file_path)

    # }}}
    @classmethod  # __saveSource# {{{
    def __saveSource(cls, data: _BarsDataFile):
        file_path = Cmd.path(data.dir_path, "source")
        Source.save(data.source, file_path)

    # }}}
    @classmethod  # __loadID# {{{
    def __loadID(cls, path, parent=None):
        ID = InstrumentId.load(path)
        return ID

    # }}}
    @classmethod  # __loadDataType# {{{
    def __loadDataType(cls, path, parent=None):
        data_type = DataType.load(path)
        return data_type

    # }}}
    @classmethod  # __loadBars# {{{
    def __loadBars(
        cls, ID: InstrumentId, data_type: DataType, year: int
    ) -> _BarsDataFile:
        file_path = Cmd.path(ID.dir_path, data_type.value, f"{year}.csv")
        if not Cmd.isExist(file_path):
            logger.error(f"No csv data: {ID.ticker}-{data_type.value} {year}")
            return list()
        text = Cmd.loadText(file_path)
        bars = list()
        for line in text:
            bar = _Bar.fromCSV(line)
            bars.append(bar)
        return bars

    # }}}
    @classmethod  # __loadDataType# {{{
    def __loadSource(cls, ID, data_type):
        path = Cmd.path(ID.dir_path, data_type.value, "source")
        source = Source.load(path)
        return source

    # }}}


# }}}
class _BarsDataFileIterator:  # {{{
    def __init__(self, ID: InstrumentId, data_type):  # {{{
        self.ID = ID
        self.data_type = data_type
        self.years = _Manager.availibleYears(ID, data_type)
        self.index = 0

    # }}}
    def __next__(self):  # {{{
        if self.index < len(self.years):
            year = self.years[self.index]
            data = _BarsDataFile.load(self.ID, self.data_type, year)
            self.index += 1
            return data
        else:
            raise StopIteration

    # }}}
    def __iter__(self):  # {{{
        # При передаче объекта функции iter возвращает самого себя
        # тем самым в точности реализуя протокол итератора
        return self

    # }}}


# }}}
