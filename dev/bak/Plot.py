
sys.path.append("/home/alex/.local/lib/python3.9/site-packages")
import plotly.graph_objects as go

class Plot():
    def __init__(self):
        self.font = dict(
                family = "Arial",
                size = 14,
                color = "#000000"
                )
        self.shift = None
        self.signal = None
        self.trade = None
        self.data = None
        self.sig_dt = None
        self.opn_dt = None
        self.cls_dt = None
        self.open_price = None
        self.close_price = None
        self.fig = None
        self.title = None
        self.shapes = list()
        self.annotations = list()

    def show(self, chart):
        dt = chart.head.dt
        ID = chart.ID
        timeframe = chart.timeframe
        begin = dt - ONE_MONTH * 2
        end = dt + ONE_MONTH * 2
        self.chart = Chart(ID, timeframe, begin, end)
        self.__generatePlotData()
        head_shape = dict(
            x0 = dt.date(),
            x1 = dt.date(),
            y0 = chart.head.high * 1.02,
            y1 = chart.head.high * 1.03,
            xref='x', yref='y',
            editable=True,
            line_width=20
            )
        self.shapes.append(head_shape)
        self.__createFig()
        self.__updateFig()
        self.fig.show()
        self.clear()
        input("SHOW PLOT. Press 'Enter' to continue...")

    def showSignal(self, signal):
        self.signal = trade
        self.__readSignalInfo(signal)
        self.__loadChart()
        self.__generatePlotData()
        self.__generateTitleText()
        self.__createShapes()
        self.__createAnnotations()
        self.__createFig()
        self.__updateFig()
        self.fig.show()
        self.clear()
        input("SHOW PLOT. Press 'Enter' to continue...")
        # Добавляем справа
        # riskmanager_info = trade["risk manager"]
        # s = "Risk manager:<br>"
        # for key, value in riskmanager_info.items():
        #     s += f"  - {key}: {value}<br>"
        # portfolio_info = trade["portfolio manager"]
        # s = " <br>Portfolio:<br>"
        # for key, value in portfolio_info.items():
        #     s += f"  - {key}: {value}<br>"
        # result_info = trade["summary"]
        # s = " <br>Summary:<br>"
        # for key, value in result_info.items():
        #     s += f"  - {key}: {value}<br>"
        # month = datetime.timedelta(days=30)
        # fig.add_annotation(x=dt + month, y="paper",
        #             text=s,
        #             showarrow=False,
        #             font=dict(
        #                 family="Arial",
        #                 size=14,
        #                 color="#000000"
        #                 ),
        #             align="left"
        #             )

    def showTrade(self, trade):
        self.trade = trade
        self.__readTradeInfo(trade)
        self.__loadChart(trade)
        self.__generatePlotData()
        self.__generateTitleText()
        self.__createShapes()
        self.__createAnnotations()
        self.__createFig()
        self.__updateFig()
        self.fig.show()
        self.clear()
        input("SHOW PLOT. Press 'Enter' to continue...")
        # Добавляем справа
        # riskmanager_info = trade["risk manager"]
        # s = "Risk manager:<br>"
        # for key, value in riskmanager_info.items():
        #     s += f"  - {key}: {value}<br>"
        # portfolio_info = trade["portfolio manager"]
        # s = " <br>Portfolio:<br>"
        # for key, value in portfolio_info.items():
        #     s += f"  - {key}: {value}<br>"
        # result_info = trade["summary"]
        # s = " <br>Summary:<br>"
        # for key, value in result_info.items():
        #     s += f"  - {key}: {value}<br>"
        # month = datetime.timedelta(days=30)
        # fig.add_annotation(x=dt + month, y="paper",
        #             text=s,
        #             showarrow=False,
        #             font=dict(
        #                 family="Arial",
        #                 size=14,
        #                 color="#000000"
        #                 ),
        #             align="left"
        #             )

    def clear(self):
        self.font = dict(
                family = "Arial",
                size = 14,
                color = "#000000"
                )
        self.shift = timedelta(days=3)
        self.signal = None
        self.trade = None
        self.data = None
        self.sig_dt = None
        self.opn_dt = None
        self.cls_dt = None
        self.open_price = None
        self.close_price = None
        self.fig = None
        self.title = None
        self.shapes = list()
        self.annotations = list()

    def __readSignalInfo(self, signal):
        self.sig_dt = datetime.fromisoformat(
            signal["strategy"]["signal datetime"]
            )
        self.open_price = float(signal["strategy"]["open price"])
        self.close_price = float(signal["strategy"]["close price"])

    def __readTradeInfo(self, trade):
        self.sig_dt = datetime.fromisoformat(
            trade["strategy"]["signal datetime"]
            )
        self.opn_dt = datetime.fromisoformat(
            trade["position"]["open datetime"]
            )
        self.cls_dt = datetime.fromisoformat(
            trade["position"]["close datetime"]
            )
        self.open_price = float(trade["position"]["open price"])
        self.close_price = float(trade["position"]["close price"])
        timeframe = TimeFrame((trade["strategy"]["timeframe"]))
        self.shift = timeframe.period * 3

    def __loadChart(self, info):
        ticker = info["strategy"]["ticker"]
        ID = Id("share", "ticker", ticker)
        timeframe = info["strategy"]["timeframe"]
        delta = TimeFrame(timeframe) * 30
        begin = self.sig_dt - delta
        end = self.cls_dt + delta
        self.title = s

    def __createFig(self):
        # Добавление текста к всплывающем на барах поп-ап окну
        bars = self.data
        hovertext = []
        # for i in range(len(bars)):
        #     hovertext.append('Volume: '+str(bars["vol"][i]))
        self.fig = go.Figure(
            data = [go.Ohlc(
                x = bars["dt"],
                open = bars["open"],
                high = bars["high"],
                low = bars["low"],
                close = bars["close"],
                text = hovertext)]
            )

    def __updateFig(self):
        self.fig.update(layout_xaxis_rangeslider_visible=False)
        self.fig.update_layout(
            title = dict(
                text = self.title,
                font = self.font
                ),
            margin = dict(l=0, r=0, t=23, b=0),
            shapes = self.shapes,
            annotations = self.annotations,
        )

    def __createShapes(self):
        self.shapes = list()
        self.__createTradeShape()
        self.__createOpenShape()
        self.__createCloseShape()

    def __createTradeShape(self):
        trade_shape = dict(
            x0 = self.sig_dt,
            x1 = self.sig_dt,
            y0 = self.open_price * 1.001,
            y1 = self.open_price * 1.004,
            xref='x', yref='y',
            editable=True,
            line_width=3
            )
        self.shapes.append(trade_shape)

    def __createOpenShape(self):
        open_shape = dict(
            x0 = self.opn_dt,
            x1 = self.cls_dt + self.shift,
            y0 = self.open_price,
            y1 = self.open_price,
            xref = 'x', yref='y',
            editable = True,
            line_width = 1
            )
        self.shapes.append(open_shape)

    def __createCloseShape(self):
        info = self.trade["strategy"]
        if info["stop loss"] == "None":
            close_shape = dict(
                x0 = self.opn_dt,
                x1 = self.cls_dt + self.shift,
                y0 = self.close_price,
                y1 = self.close_price,
                xref = 'x', yref = 'y',
                editable = True,
                line_width = 2
                )
            self.shapes.append(close_shape)
        if info["stop loss"] != "None":
            self.__createStopLossShape()
        if info["take profit"] != "None":
            self.__createTakeProfitShape()

    def __createStopLossShape(self):
        stop_loss_shape = dict(
            x0 = self.opn_dt,
            x1 = self.cls_dt + self.shift,
            y0 = self.trade["strategy"]["stop loss price"],
            y1 = self.trade["strategy"]["stop loss price"],
            xref = 'x', yref = 'y',
            editable = True,
            line_width = 2
            )
        self.shapes.append(stop_loss_shape)

    def __createTakeProfitShape(self):
        take_profit_shape = dict(
            x0 = self.opn_dt,
            x1 = self.cls_dt + self.shift,
            y0 = self.trade["strategy"]["take profit price"],
            y1 = self.trade["strategy"]["take profit price"],
            xref = 'x', yref = 'y',
            editable = True,
            line_width = 2
            )
        self.shapes.append(take_profit_shape)

    def __createAnnotations(self):
        self.annotations = list()
        self.__createTradeAnnotation()
        self.__createOpenAnnotation()
        self.__createCloseAnnotation()

    def __createTradeAnnotation(self):
        trade = self.trade
        s = f"Signal datetime: {self.sig_dt}<br>"
        result = trade["position"].get("result", None)
        hold = trade["position"].get("holding days", None)
        percent = trade["position"].get("percent", None)
        percent_per_day = trade["position"].get("percent per day", None)
        s += f"Hold: {hold}, {percent_per_day}%<br>"
        s += f"Resul: {result}, {percent}%<br>"
        trade_annotation = dict(
            x = self.sig_dt,
            y = self.open_price * 1.01,
            xref = 'x', yref = 'y',
            showarrow = False,
            font = self.font,
            text=s)
        self.annotations.append(trade_annotation)

    def __createOpenAnnotation(self):
        open_str = f"Open: {self.open_price:.3f}"
        open_annotation = dict(
            x = self.cls_dt + self.shift,
            y = self.open_price,
            xref = 'x', yref = 'y',
            showarrow = False,
            xanchor = "left",
            bgcolor = "rgb(200,200,200)",
            text = open_str)
        self.annotations.append(open_annotation)

    def __createCloseAnnotation(self):
        info = self.trade["strategy"]
        if info["stop loss"] == "None":
            close_str = f"Close: {self.open_price:.3f}"
            close_annotation = dict(
                x = self.cls_dt + self.shift,
                y = self.close_price,
                xref = 'x', yref = 'y',
                showarrow = False,
                xanchor = "left",
                bgcolor = "rgb(200,200,200)",
                text = close_str)
            self.annotations.append(close_annotation)
        if info["stop loss"] != "None":
            self.__createStopLossAnnotation()
        if info["take profit"] != "None":
            self.__createTakeProfitAnnotation()

    def __createStopLossAnnotation(self):
        info = self.trade["strategy"]
        stop_loss_price = float(info["stop loss price"])
        stop_loss_str = f"Stop loss: {stop_loss_price:.3f}"
        stop_loss_annotation = dict(
            x = self.cls_dt + self.shift,
            y = stop_loss_price,
            xref = 'x', yref = 'y',
            showarrow = False,
            xanchor = "left",
            bgcolor = "rgb(203,124,130)",
            text = stop_loss_str)
        self.annotations.append(stop_loss_annotation)

    def __createTakeProfitAnnotation(self):
        info = self.trade["strategy"]
        take_profit_price = float(info["take profit price"])
        take_profit_str = f"Take profit: {take_profit_price:.3f}"
        take_profit_annotation = dict(
            x = self.cls_dt + self.shift,
            y = take_profit_price,
            xref = 'x', yref = 'y',
            showarrow = False,
            xanchor = "left",
            bgcolor = "rgb(174,195,172)",
            text = take_profit_str
        )
        self.annotations.append(take_profit_annotation)

