from datetime import datetime
from django.shortcuts import render
from django.views.generic import TemplateView
from sklearn.linear_model import LinearRegression
from pylab import rcParams
from fbprophet import Prophet
import numpy as np
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt_sal
from .models import Wallet
import plotly.graph_objects as go
import mpld3

plt_sal.style.use('fivethirtyeight')
# from fbprophet import Prophet
from matplotlib import pyplot as plt23
import statsmodels.api as sm


def is_support(df, i):
    support = df['low'][i] < df['low'][i - 1] < df['low'][i - 2] and df['low'][i] < df['low'][i + 1] < df['low'][
        i + 2]
    return support


def is_resistance(df, i):
    resistance = df['high'][i] > df['high'][i - 1] > df['high'][i - 2] and df['high'][i] > df['high'][i + 1] > \
                 df['high'][i + 2]
    return resistance


def SMA(data, period=24, column='close'):
    return data[column].rolling(window=period).mean()


def strategy(df):
    buy = []
    sell = []
    flag = 0
    buy_price = 0

    for i in range(0, len(df)):
        if df['SMA24'][i] > df['close'][i] and flag == 0:
            buy.append(df['close'][i])
            sell.append(np.nan)
            buy_price = df['close'][i]
            flag = 1
        elif df['SMA24'][i] < df['close'][i] and flag == 1 and buy_price < df['close'][i]:
            sell.append(df['close'][i])
            buy.append(np.nan)
            buy_price = 0
            flag = 0
        else:
            sell.append(np.nan)
            buy.append(np.nan)
    return buy, sell


class Index(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        # initiate context
        context = super().get_context_data(**kwargs)
        chart = []
        # get variable from Wallet
        Wallet.objects.all()
        wal = Wallet.objects.get(id=2)
        context['wallet'] = wal.wallet

        # make connection to database and get runtimegraphs table into dataframe
        conn = sqlite3.connect("db.sqlite3")
        df = pd.read_sql_query("select * from RuntimeGraphs_cryptodataset;", conn)
        # 1 year comprehensive analysis
        dd = df.copy()
        btc_year = wal.btc
        cash_year = wal.wallet
        df_date = df.copy()
        df_sal = df.copy()
        times = pd.date_range(end=datetime.now(), freq="H", periods=8760)
        df_wl = df.copy()
        # df_wl = df_wl.sort_index()
        df_wl['Date'] = pd.to_datetime(df_wl['date']).dt.date
        df_wl['Time'] = pd.to_datetime(df_wl['date']).dt.time
        # df_wl = df_wl.sort_index()
        df_wl['Date'] = df_wl['Date'].astype(str)
        context['previous_btc_val'] = (df_wl[df_wl['Date'] == str(times[0].date())].iloc[0].close * btc_year).round(2)
        for dat in times:
            value = df_wl[df_wl['Date'] == str(dat.date())]
            for i in range(0, len(value) - 1):
                PA = ((value.close.iloc[i] - value.close.iloc[i + 1]) / value.close.iloc[i + 1]) * 100
                if PA >= 5:
                    if btc_year >= 0:
                        amount = (100 / value.close.iloc[i])
                        btc_year -= amount
                        cash_year += 100
                elif PA <= -5:
                    if cash_year >= 100:
                        cash_year -= 100
                        btc_year += (1 / value.close.iloc[i]) * 100
        context['now_btc_val'] = (df.close.iloc[-1] * btc_year).round(2)
        pa = (((df.close.iloc[-2] - df.close.iloc[-1]) / df.close.iloc[-1]) * 100).round(2)
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
        # variable to display on the webpage
        context['pa'] = pa
        context['signal'] = signal
        context['starting'] = times[0]
        context['ending'] = times[-1]
        context['btc_year'] = btc_year
        context['cash_year'] = cash_year
        context['cash_start'] = wal.wallet
        context['btc_start'] = wal.btc

        # plot monthly graph
        df['Date'] = pd.to_datetime(df['date']).dt.date
        df['Time'] = pd.to_datetime(df['date']).dt.time
        layout = go.Layout(title="1 Month Bitcoin Data", xaxis={'title': 'Date'}, yaxis={'title': 'Close'})
        fig = go.Figure(data=[go.Candlestick(x=df.date.iloc[-720:],
                                             open=df['open'],
                                             high=df['high'],
                                             low=df['low'],
                                             close=df['close'])], layout=layout)
        context['graph_message_1'] = ''
        context['graph_1'] = fig.to_html()
        # plot graph on hourly basis
        value = df.iloc[-24:]
        dfpl = value.copy()
        fig = go.Figure()
        fig.update_layout(title="24 Hours Bitcoin Data", xaxis_title='Date', yaxis_title='Close')
        fig.add_trace(go.Candlestick(x=dfpl['Time'],
                                     open=dfpl.open,
                                     high=dfpl.high,
                                     low=dfpl.low,
                                     close=dfpl.close))
        context['graph_message_2'] = ''
        context['graph_2'] = fig.to_html()
        # 2020 and 2021 difference
        df_date['date'] = pd.to_datetime(df_date['date'])
        df_date.set_index('date', drop=True, inplace=True)
        m2021 = df_date.loc['2021', 'close'].resample('M').mean().values
        m2020 = df_date.loc['2020', 'close'].resample('M').mean().values
        fig = plt.figure(figsize=(6.5, 2), dpi=180)
        plt.plot(m2021, label='2021')
        plt.plot(m2020, label='2020')
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        plt.xticks(np.arange(0, 12), labels=months, rotation=75)
        plt.legend(loc=0)
        plt.grid(True, alpha=0.1)
        html_str = mpld3.fig_to_html(fig)
        context['graph_3'] = html_str
        context['graph_message_3'] = '''
        The above graph shows the average of monthly price for 2020 and 2021. Follwoing are major insights from the graph

- There is a stron up trend from Oct-2020 to Apr-2021

- From Apr to July there is fall in prices

- For both of the years there is up-trend.

Let's dig into the details from Apr to July 2021'''

        aprtojul = df_date.loc['2021-4-1':'2021-7-31', 'close'].resample('W').mean()
        fig = plt.figure(figsize=(6, 2), dpi=200)
        plt.plot(aprtojul)
        plt.xticks(rotation=75)
        plt.grid(True, alpha=0.1)
        html_str = mpld3.fig_to_html(fig)
        context['graph_4'] = html_str
        context['graph_message_4'] = """
        Conclusions are:

- There is a small uptrend from third week of april to second week of May

- From 7th of May to 15th of June there is a strong down-trend
        """
        context["graph_message_5_upper"] = """
        Since its a Hourly time series and may follows a certain repetitive pattern every day, we can plot each day as a separate line in the same plot. This lets you compare the day wise patterns side-by-side. Seasonal Plot of a Time Series

"""
        df_date['year'] = [d.year for d in df_date.index]
        df_date['month'] = [d.strftime('%b') for d in df_date.index]
        fig = plt.figure(figsize=(4, 2), dpi=300)
        ax1 = plt.plot(df_date.loc[df_date.year == 2020, 'month'], df_date.loc[df_date.year == 2020, 'close'],
                       label='2020')
        ax2 = plt.plot(df_date.loc[df_date.year == 2021, 'month'], df_date.loc[df_date.year == 2021, 'close'],
                       label='2021')
        plt.grid(True, alpha=0.2)
        plt.legend()
        html_str = mpld3.fig_to_html(fig)
        context['graph_5'] = html_str
        context['graph_message_5'] = """
        Conclusions are:

- There is huge fluctuation in 2021 compare to 2020

- Oct, May and Feb are high fluctuated months
        """

        # X = np.array(df['open'].iloc[-720:-1]).reshape(-1, 1)
        # y = np.array(df['close'].iloc[-720:-1]).reshape(-1, 1)
        # lr = LinearRegression()
        # lr.fit(X, y)
        # prediction = lr.predict(X)
        # # Visualize our model
        # figure = plt.figure(figsize=(11, 4))
        # plt.scatter(X.flatten(), y.flatten(), color="red", label='Data')
        # plt.plot(X.flatten(), prediction.flatten(), color="green", label='Regression Line')
        # plt.title("Open Price vs  Close Price")
        # plt.xlabel("Open Price")
        # plt.ylabel("Close Price")
        # plt.legend(loc=0)
        # html_str = mpld3.fig_to_html(figure)
        # chart.append(html_str)
        # # chart.append(get_plot(X.flatten(), prediction.flatten(), True, X.flatten(), y.flatten()))
        #
        # value.set_index('Date', drop=True, inplace=True)
        # sr = []
        # for i in range(2, value.shape[0] - 2):
        #     if is_support(value, i):
        #         sr.append((i, value['low'][i]))
        #     elif is_resistance(value, i):
        #         sr.append((i, value['high'][i]))
        # s = 0
        # e = len(value)
        # dfpl = value[s:e]
        # fig = go.Figure(data=[go.Candlestick(x=dfpl['Time'],
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
        # plotlist1 = [x[0] for x in sr if x[1] == 1]
        # plotlist2 = [x[0] for x in sr if x[1] == 2]
        # plotlist1.sort()
        # plotlist2.sort()
        #
        # for i in range(1, len(plotlist1)):
        #     if (i >= len(plotlist1)):
        #         break
        #     elif abs(plotlist1[i] - plotlist1[i - 1]) <= 0.005:
        #         plotlist1.pop(i)
        #
        # for i in range(1, len(plotlist2)):
        #     if (i >= len(plotlist2)):
        #         break
        #     elif abs(plotlist2[i] - plotlist2[i - 1]) <= 0.005:
        #         plotlist2.pop(i)
        #
        # s = 0
        # e = 24
        # dfpl = value[s:e]
        # fig = go.Figure(data=[go.Candlestick(x=dfpl['Time'],
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
        # for i in range(2, value.shape[0] - 2):
        #     if is_support(value, i):
        #         ss.append((i, value['low'][i]))
        #     elif is_resistance(value, i):
        #         rr.append((i, value['high'][i]))
        # #
        # s = 0
        # e = len(value)
        # dfpl = value[s:e]
        #
        # fig = go.Figure(data=[go.Candlestick(x=dfpl.Time,
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

        #         rcParams['figure.figsize'] = 18, 8
        #         y = df_date.loc['2021':'2020', 'close'].resample('MS').mean()
        #         decomposition = sm.tsa.seasonal_decompose(y, model='additive')
        #         fig = decomposition.plot()
        #         html_str = mpld3.fig_to_html(fig)
        #         context['graph_6'] = html_str
        #         context['graph_message_6'] = """
        #         Conclusion:
        #
        # We can see that there is stron uptrend after 5th month of 2020
        #
        # There is seasonal uptrend from 1st to 5th month of each year, and down trend from 5th to 10th month
        #         """
        dd['date'] = pd.to_datetime(dd['date'])
        dd.drop_duplicates(subset='close', keep='first')
        dd.drop(['open', 'high', 'low', 'volume'], axis=1, inplace=True)
        dd['Date'] = dd['date'].dt.date
        dd.set_index('Date')
        dd.drop(['date'], axis=1, inplace=True)
        dd.columns = ['y', 'ds']
        m = Prophet(interval_width=0.95, daily_seasonality=True)
        model = m.fit(dd)
        future = m.make_future_dataframe(periods=100, freq='D')
        forecast = m.predict(future)
        fig = plt23.figure(figsize=(8, 8))
        m.plot(forecast)
        m.plot_components(forecast)
        html_str = mpld3.fig_to_html(fig)
        context['graph_7'] = html_str
        context['graph_message_7'] = ""

        df_sal['date'] = pd.to_datetime(df_sal['date'])
        df_sal.set_index('date', drop=True, inplace=True)
        df_sal = df_sal.tail(168)
        df_sal['SMA24'] = SMA(df_sal)
        # Get the buy and sell list
        strat = strategy(df_sal)
        df_sal['Buy'] = strat[0]
        df_sal['Sell'] = strat[1]

        # Visualize the close price and the buy and sell signals
        fig = plt_sal.figure(figsize=(10.5, 4))
        plt_sal.title('Bitcoin Close Price and MVA with Buy and Sell Signals')
        plt_sal.plot(df_sal['close'], alpha=0.5, label='Close Price Last 7 days')
        plt_sal.plot(df_sal['SMA24'], alpha=0.5, label='Simple Moving Avg')
        plt_sal.scatter(df_sal.index, df_sal['Buy'], color='green', label='Buy Signal', alpha=1)
        plt_sal.scatter(df_sal.index, df_sal['Sell'], color='red', label='Sell Signal', alpha=1)
        plt_sal.xlabel('Date')
        plt_sal.ylabel('Close Price in USD')
        plt_sal.legend(loc=3)
        html_str = mpld3.fig_to_html(fig)
        context['graph_6'] = html_str
        context['graph_message_6'] = """
The graph above shows the relationship between the date and the close price of Bitcoin in USD.

The blue line trend represents the closing price of Bitcoin over the last seven days, while the red line trend represents the moving averages over one day. 

There are also Buy and Sell Signals on this graph.

Buy = green :-

  Buy the Bitcoin when SMA of 1 day goes below the close price 

Sell = Red :-

  Sell When the 1 day SMA goes above the close price

Also, Never going to sell at a price lower than I bought.
                """

        return context


def about(request):
    return render(request, 'about.html', {})
