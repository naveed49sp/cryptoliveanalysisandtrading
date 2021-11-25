from django.shortcuts import render
from django.views.generic import TemplateView
import random
from matplotlib.animation import FuncAnimation
from itertools import count
from django.http import HttpResponse
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from .models import CryptoDataset, Purchase, Wallet
import plotly.graph_objects as go
import datetime


def support(df1, l, n1, n2):
    for i in range(l - n1 + 2, l + 1):

        if df1.low[i] > df1.low[i - 1]:
            print('working')
            return 0
    for i in range(l + 1, l + n2 + 1):
        if df1.low[i] < df1.low[i - 1]:
            return 0
    return 1


# support(df,46,3,2)

def resistance(df1, l, n1, n2):  # n1 n2 before and after candle l
    for i in range(l - n1 + 2, l + 1):
        if df1.high[i] < df1.high[i - 1]:
            return 0
    for i in range(l + 1, l + n2 + 1):
        if df1.high[i] > df1.high[i - 1]:
            return 0
    return 1


# resistance(df, 30, 3, 5)


class Index(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chart = []
        Wallet.objects.all()

        wal = Wallet.objects.get(id=2)
        context['wallet'] = wal.wallet
        conn = sqlite3.connect("db.sqlite3")
        df = pd.read_sql_query("select * from RuntimeGraphs_cryptodataset;", conn)
        # wallet analysis

        btc_year = wal.btc
        cash_year = wal.wallet

        Current_date = datetime.date.today().strftime('%Y-%m-%d')
        times = pd.date_range('2018-05-15', '2021-11-20')
        df_wl = df.copy()
        df_wl = df_wl.sort_index()
        df_wl['Date'] = pd.to_datetime(df_wl['date']).dt.date
        df_wl['Time'] = pd.to_datetime(df_wl['date']).dt.time
        df_wl = df_wl.sort_index()
        df_wl['Date'] = df_wl['Date'].astype(str)
        total_selling = 0
        total_buying = 0
        value = df_wl
        for dat in times:
            value = df_wl[df_wl['Date'] == str(dat.date())]
            for i in range(0, len(value) - 1):
                PA = ((value.close.iloc[i] - value.close.iloc[i + 1]) / value.close.iloc[i + 1]) * 100
                if PA >= 5:
                    if btc_year >= 0:
                        amount = (100 / value.close.iloc[i])
                        btc_year -= amount
                        cash_year += 100
                        total_selling += 1
                elif PA <= -5:
                    if cash_year >= 100:
                        cash_year -= 100
                        btc_year += (1 / value.close.iloc[i]) * 100
                        total_buying += 1

        pa = (((value.close.iloc[-2] - value.close.iloc[-1]) / value.close.iloc[-1]) * 100).round(2)
        signal = ''
        btc = wal.btc
        cash = wal.wallet
        while 1:
            if pa >= 2:
                if pa >= 5:
                    if btc >= 0:
                        signal += 'Sold btc'
                else:
                    signal += 'Sell coin now!'
            elif pa <= -5:
                if cash >= 100:
                    signal += 'Coin is purchased'
            else:
                signal += 'do nothing'
            break
        context['pa'] = pa
        context['signal'] = signal
        context['starting'] = df_wl['Date'].iloc[0]
        context['ending'] = df_wl['Date'].iloc[-1]
        context['btc_year'] = btc_year
        context['cash_year'] = cash_year

        context['cash_start'] = wal.wallet
        context['btc_start'] = wal.btc
        # plotting graphs
        df['Date'] = pd.to_datetime(df['date']).dt.date
        df['Time'] = pd.to_datetime(df['date']).dt.time
        df = df.sort_index()
        df['Date'] = df['Date'].astype(str)
        layout = go.Layout(title="1 Month Bitcoin Data", xaxis={'title': 'Date'}, yaxis={'title': 'Close'})
        fig = go.Figure(data=[go.Candlestick(x=df.date.iloc[-720:-1],
                                             open=df['open'],
                                             high=df['high'],
                                             low=df['low'],
                                             close=df['close'])], layout=layout)
        chart.append(fig.to_html())
        value = df[df['Date'].astype(str) == '2021-11-23']
        dfpl = value
        df.reset_index(drop=True, inplace=True)
        df.isna().sum()
        layout = go.Layout(title="24 Hours Bitcoin Data", xaxis={'title': 'Date'}, yaxis={'title': 'Close'})
        fig = go.Figure(data=[go.Candlestick(x=dfpl.date,
                                             open=dfpl['open'],
                                             high=dfpl['high'],
                                             low=dfpl['low'],
                                             close=dfpl['close'])], layout=layout)

        chart.append(fig.to_html())

        # from sklearn.linear_model import LinearRegression
        #
        # X = np.array(value['open'].iloc[-720:-1]).reshape(-1, 1)
        # y = np.array(value['close'].iloc[-720:-1]).reshape(-1, 1)
        # lr = LinearRegression()
        # lr.fit(X, y)
        # print("R-Squared: ", lr.score(X, y))
        # prediction = lr.predict(X)
        # # Visualize our model
        # plt.scatter(X.flatten(), y.flatten(), color="red")
        # plt.plot(X.flatten(), prediction.flatten(), color="green")
        # plt.title("Open vs  Close Price")
        # plt.xlabel("No of observations")
        # plt.ylabel("Close Price")
        # plt.show()

        # sr = []
        # n1 = 3
        # n2 = 2
        # for row in range(n1, len(value)):  # len(df)-n
        #     #     print(value.low[row], value.low[row-1])
        #     if support(value, row, n1, n2):
        #         sr.append((row, value.low[row], 1))
        #     if resistance(value, row, n1, n2):
        #         sr.append((row, value.high[row], 2))
        # s = 0
        # e = len(value)
        # dfpl = value[s:e]
        # fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
        #                                      open=dfpl['open'],
        #                                      high=dfpl['high'],
        #                                      low=dfpl['low'],
        #                                      close=dfpl['close'])])
        #
        # c = 0
        # while (1):
        #     if (c > len(sr) - 1):  # or sr[c][0]>e
        #         break
        #     fig.add_shape(type='line', x0=s, y0=sr[c][1],
        #                   x1=e,
        #                   y1=sr[c][1]
        #                   )  # x0=sr[c][0]-5 x1=sr[c][0]+5
        #     c += 1
        # chart.append(fig.to_html())
        #
        # plotlist1 = [x[1] for x in sr if x[2] == 1]
        # plotlist2 = [x[1] for x in sr if x[2] == 2]
        # plotlist1.sort()
        # plotlist2.sort()
        #
        # for i in range(1, len(plotlist1)):
        #     if (i >= len(plotlist1)):
        #         break
        #     if abs(plotlist1[i] - plotlist1[i - 1]) <= 0.005:
        #         plotlist1.pop(i)
        #
        # for i in range(1, len(plotlist2)):
        #     if (i >= len(plotlist2)):
        #         break
        #     if abs(plotlist2[i] - plotlist2[i - 1]) <= 0.005:
        #         plotlist2.pop(i)
        #
        # s = 0
        # e = 24
        # dfpl = value[s:e]
        #
        # fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
        #                                      open=dfpl['open'],
        #                                      high=dfpl['high'],
        #                                      low=dfpl['low'],
        #                                      close=dfpl['close'])])
        #
        # c = 0
        # while (1):
        #     if (c > len(plotlist1) - 1):  # or sr[c][0]>e
        #         break
        #     fig.add_shape(type='line', x0=s, y0=plotlist1[c],
        #                   x1=e,
        #                   y1=plotlist1[c],
        #                   line=dict(color="MediumPurple", width=3)
        #                   )
        #     c += 1
        #
        # c = 0
        # while (1):
        #     if (c > len(plotlist2) - 1):  # or sr[c][0]>e
        #         break
        #     fig.add_shape(type='line', x0=s, y0=plotlist2[c],
        #                   x1=e,
        #                   y1=plotlist2[c],
        #                   line=dict(color="RoyalBlue", width=1)
        #                   )
        #     c += 1
        #
        # chart.append(fig.to_html())
        #
        # ss = []
        # rr = []
        # n1 = 2
        # n2 = 2
        # for row in range(3, len(value)):  # len(df)-n2
        #     if support(value, row, n1, n2):
        #         ss.append((row, df.low[row]))
        #     if resistance(value, row, n1, n2):
        #         rr.append((row, df.high[row]))
        #
        # s = 0
        # e = len(value)
        # dfpl = value[s:e]
        #
        # fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
        #                                      open=dfpl['open'],
        #                                      high=dfpl['high'],
        #                                      low=dfpl['low'],
        #                                      close=dfpl['close'])])
        #
        # c = 0
        # while (1):
        #     if (c > len(ss) - 1):
        #         break
        #     fig.add_shape(type='line', x0=ss[c][0], y0=ss[c][1],
        #                   x1=e,
        #                   y1=ss[c][1],
        #                   line=dict(color="MediumPurple", width=3)
        #                   )
        #     c += 1
        #
        # c = 0
        # while (1):
        #     if (c > len(rr) - 1):
        #         break
        #     fig.add_shape(type='line', x0=rr[c][0], y0=rr[c][1],
        #                   x1=e,
        #                   y1=rr[c][1],
        #                   line=dict(color="RoyalBlue", width=1)
        #                   )
        #     c += 1
        #
        # chart.append(fig.to_html())

        context['graph'] = chart

        return context


def about(request):
    return render(request, 'about.html', {})
