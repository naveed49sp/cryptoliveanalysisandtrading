from django.shortcuts import render
from django.views.generic import TemplateView
from .utils import get_plot, get_plot_candle
import random
from matplotlib.animation import FuncAnimation
from itertools import count
from django.http import HttpResponse
import pandas as pd
import sqlite3
# import matplotlib.pyplot as plt
from .models import CryptoDataset
import plotly.graph_objects as go


class Index(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        x = [-2, 0, 4, 6, 7]
        y = [q ** 2 - q + 3 for q in x]
        trace1 = go.Scatter(x=x, y=y, marker={'color': 'red', 'symbol': 104, 'size': "10"},
                            mode="lines", name='1st Trace')
        layout = go.Layout(title="Meine Daten", xaxis={'title': 'x1'}, yaxis={'title': 'x2'})
        figure = go.Figure(data=['trace1'], layout=layout)
        context['graph'] = figure.to_html()
        return context


# def index(request):
#     charts = []
#     # data = yf.download(tickers='BTC-USD', period='2y', interval='1h')
#     # data.drop('Adj Close', axis=1, inplace=True)
#     conn = sqlite3.connect("db.sqlite3")
#     df = pd.read_sql_query("select * from RuntimeGraphs_cryptodataset;", conn)
#
#     # huzaifa plotting
#     # df['Date'] = pd.to_datetime(df['date']).dt.date
#     # df['Time'] = pd.to_datetime(df['date']).dt.time
#     # df = df.sort_index()
#     # df['Date'] = df['Date'].astype(str)
#     #
#     # value = df[df['Date'].astype(str) == '2021-11-20']
#     #
#     #
#     # def support(df1, l, n1, n2):
#     #     for i in range(l - n1 + 2, l + 1):
#     #
#     #         if df1.low[i] > df1.low[i - 1]:
#     #             print('working')
#     #             return 0
#     #     for i in range(l + 1, l + n2 + 1):
#     #         if (df1.low[i] < df1.low[i - 1]):
#     #             return 0
#     #     return 1
#     #
#     # # support(df,46,3,2)
#     #
#     # def resistance(df1, l, n1, n2):  # n1 n2 before and after candle l
#     #     for i in range(l - n1 + 2, l + 1):
#     #         if (df1.high[i] < df1.high[i - 1]):
#     #             return 0
#     #     for i in range(l + 1, l + n2 + 1):
#     #         if (df1.high[i] > df1.high[i - 1]):
#     #             return 0
#     #     return 1
#     #
#     # dfpl = value
#     # from datetime import datetime
#     #
#     # fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
#     #                                      open=dfpl['open'],
#     #                                      high=dfpl['high'],
#     #                                      low=dfpl['low'],
#     #                                      close=dfpl['close'])])
#     # charts.append(fig.show)
#     #
#     # sr = []
#     # n1 = 3
#     # n2 = 2
#     #
#     # for row in range(n1, len(value)):  # len(df)-n
#     #     #     print(value.low[row], value.low[row-1])
#     #     if support(value, row, n1, n2):
#     #         sr.append((row, value.low[row], 1))
#     #     if resistance(value, row, n1, n2):
#     #         sr.append((row, value.high[row], 2))
#     # print(sr)
#     #
#     # s = 0
#     # e = len(value)
#     # dfpl = value[s:e]
#     # # import plotly.graph_objects as go
#     # from datetime import datetime
#     # import matplotlib.pyplot as plt
#     #
#     # fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
#     #                                      open=dfpl['open'],
#     #                                      high=dfpl['high'],
#     #                                      low=dfpl['low'],
#     #                                      close=dfpl['close'])])
#     #
#     # c = 0
#     # while (1):
#     #     if (c > len(sr) - 1):  # or sr[c][0]>e
#     #         break
#     #     fig.add_shape(type='line', x0=s, y0=sr[c][1],
#     #                   x1=e,
#     #                   y1=sr[c][1]
#     #                   )  # x0=sr[c][0]-5 x1=sr[c][0]+5
#     #     c += 1
#     # charts.append(fig.show())
#     # #
#     # plotlist1 = [x[1] for x in sr if x[2] == 1]
#     # plotlist2 = [x[1] for x in sr if x[2] == 2]
#     # plotlist1.sort()
#     # plotlist2.sort()
#     #
#     # for i in range(1, len(plotlist1)):
#     #     if (i >= len(plotlist1)):
#     #         break
#     #     if abs(plotlist1[i] - plotlist1[i - 1]) <= 0.005:
#     #         plotlist1.pop(i)
#     #
#     # for i in range(1, len(plotlist2)):
#     #     if (i >= len(plotlist2)):
#     #         break
#     #     if abs(plotlist2[i] - plotlist2[i - 1]) <= 0.005:
#     #         plotlist2.pop(i)
#     # plotlist2
#     # # plt.hist(plotlist, bins=10, alpha=0.5)
#     #
#     # s = 0
#     # e = 24
#     # dfpl = value[s:e]
#     # import plotly.graph_objects as go
#     # from datetime import datetime
#     # import matplotlib.pyplot as plt
#     #
#     # fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
#     #                                      open=dfpl['open'],
#     #                                      high=dfpl['high'],
#     #                                      low=dfpl['low'],
#     #                                      close=dfpl['close'])])
#     #
#     # c = 0
#     # while (1):
#     #     if (c > len(plotlist1) - 1):  # or sr[c][0]>e
#     #         break
#     #     fig.add_shape(type='line', x0=s, y0=plotlist1[c],
#     #                   x1=e,
#     #                   y1=plotlist1[c],
#     #                   line=dict(color="MediumPurple", width=3)
#     #                   )
#     #     c += 1
#     #
#     # c = 0
#     # while (1):
#     #     if (c > len(plotlist2) - 1):  # or sr[c][0]>e
#     #         break
#     #     fig.add_shape(type='line', x0=s, y0=plotlist2[c],
#     #                   x1=e,
#     #                   y1=plotlist2[c],
#     #                   line=dict(color="RoyalBlue", width=1)
#     #                   )
#     #     c += 1
#     #
#     # fig.show()
#     #
#     # ss = []
#     # rr = []
#     # n1 = 2
#     # n2 = 2
#     # for row in range(3, len(value)):  # len(df)-n2
#     #     if support(value, row, n1, n2):
#     #         ss.append((row, df.low[row]))
#     #     if resistance(value, row, n1, n2):
#     #         rr.append((row, df.high[row]))
#     #
#     # s = 0
#     # e = len(value)
#     # dfpl = value[s:e]
#     # import plotly.graph_objects as go
#     # from datetime import datetime
#     # import matplotlib.pyplot as plt
#     #
#     # fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
#     #                                      open=dfpl['open'],
#     #                                      high=dfpl['high'],
#     #                                      low=dfpl['low'],
#     #                                      close=dfpl['close'])])
#     #
#     # c = 0
#     # while (1):
#     #     if (c > len(ss) - 1):
#     #         break
#     #     fig.add_shape(type='line', x0=ss[c][0], y0=ss[c][1],
#     #                   x1=e,
#     #                   y1=ss[c][1],
#     #                   line=dict(color="MediumPurple", width=3)
#     #                   )
#     #     c += 1
#     #
#     # c = 0
#     # while (1):
#     #     if (c > len(rr) - 1):
#     #         break
#     #     fig.add_shape(type='line', x0=rr[c][0], y0=rr[c][1],
#     #                   x1=e,
#     #                   y1=rr[c][1],
#     #                   line=dict(color="RoyalBlue", width=1)
#     #                   )
#     #     c += 1
#     #
#     # fig.show()
#     #
#     # # data.reset_index(drop=True, inplace=True)
#     # # data.set_index('date', drop=True, inplace=True)
#     # charts.append(get_plot(df.date, df.open))
#     # charts.append(get_plot(df.date, df.close))
#     # return HttpResponse(pie_url)
#     # g = Graph
#     # context = g.get_context_data()
#     # graph = {'graph': graph}
#     return render(request, 'index.html')


def about(request):
    return render(request, 'about.html', {})
