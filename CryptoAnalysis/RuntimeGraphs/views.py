from kucoin.client import Client
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.http import request
from .forms import NewUserForm
from .forms import PriceSearchForm
from RuntimeGraphs.models import Wallet
from datetime import datetime
from django.shortcuts import render, redirect
# from django import flash
# from django import requests
import yfinance as yf
import requests
from RuntimeGraphs.management.commands import get_data
import config
from django.views.generic import TemplateView
from sklearn.linear_model import LinearRegression
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from pylab import rcParams
import numpy as np
import pandas as pd
import seaborn as sns
import sqlite3
# import business logic from services.py layer
from .management.commands.services import getDateService, getDefaultData, getUserInputDateRange, outOfRange
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt_sal
from datetime import date, timedelta
from .models import Wallet
import plotly.graph_objects as go
import  plotly.figure_factory as ff
import plotly.express as px
from plotly.offline import plot
import mpld3
from matplotlib import pyplot as plt23
import statsmodels.api as sm
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from pusher import Pusher
import config
from django.http import Http404
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import pprint
import csv
from io import BytesIO
import base64

from .utils import *
import requests
import json
import atexit
import time
import plotly
import plotly.graph_objs as go
plt_sal.style.use('fivethirtyeight')


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


def SMA2(data, period=24, column='Close'):
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


def strategy2(df):
    buy = []
    sell = []
    flag = 0
    buy_price = 0

    for i in range(0, len(df)):
        if df['SMA24'][i] > df['Close'][i] and flag == 0:
            buy.append(df['Close'][i])
            sell.append(np.nan)
            buy_price = df['Close'][i]
            flag = 1
        elif df['SMA24'][i] < df['Close'][i] and flag == 1 and buy_price < df['Close'][i]:
            sell.append(df['Close'][i])
            buy.append(np.nan)
            buy_price = 0
            flag = 0
        else:
            sell.append(np.nan)
            buy.append(np.nan)
    return buy, sell


class Index(TemplateView):
    template_name = 'bitcoin.html'

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
        df = pd.read_sql_query(
            "select * from RuntimeGraphs_btcdataset;", conn)
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
        context['previous_btc_val'] = (df_wl[df_wl['Date'] == str(
            times[0].date())].iloc[0].close * btc_year).round(2)
        for dat in times:
            value = df_wl[df_wl['Date'] == str(dat.date())]
            for i in range(0, len(value) - 1):
                PA = (
                    (value.close.iloc[i] - value.close.iloc[i + 1]) / value.close.iloc[i + 1]) * 100
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
        pa = (((df.close.iloc[-2] - df.close.iloc[-1]) /
              df.close.iloc[-1]) * 100).round(2)
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
        layout = go.Layout(title="1 Month Bitcoin Data", xaxis={
                           'title': 'Date'}, yaxis={'title': 'Close'})
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
        fig.update_layout(title="24 Hours Bitcoin Data",
                          xaxis_title='Date', yaxis_title='Close')
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
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June',
                  'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
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

        aprtojul = df_date.loc['2021-4-1':'2021-7-31',
                               'close'].resample('W').mean()
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
        plt_sal.title('Bitcoin Close Price and MA with Buy and Sell Signals')
        plt_sal.plot(df_sal['close'], alpha=0.5,
                     label='Close Price Last 7 days')
        plt_sal.plot(df_sal['SMA24'], alpha=0.5, label='Simple Moving Avg')
        plt_sal.scatter(
            df_sal.index, df_sal['Buy'], color='green', label='Buy Signal', alpha=1)
        plt_sal.scatter(
            df_sal.index, df_sal['Sell'], color='red', label='Sell Signal', alpha=1)
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



def Main(request):
    return render(request, 'main.html', {})


def bitcoin(request):
    return render(request, 'bitcoin.html', {})


# def ethereum(request):
#     return render(request, 'ethereum.html', {})

def ada(request):
    return render(request, 'ada.html', {})


def realtimechart(request):
    return render(request, 'realtimechart.html', {})


def show(request):
    wallets = Wallet.objects.all()
    return render(request, "main.html", {'wallet': wallets})


def signup(request):
    if request.method == "POST":
        if request.POST['password1'] == request.POST['password2']:
            try:
                User.objects.get(username=request.POST['username'])
                return render(request, 'register.html', {'error': 'Username is already taken!'})
            except User.DoesNotExist:
                user = User.objects.create_user(
                    request.POST['username'], password=request.POST['password1'])
                auth.login(request, user)
                return redirect('login')
        else:
            return render(request, 'register.html', {'error': 'Password does not match!'})
    else:
        return render(request, 'register.html')


def login(request):
    if request.method == 'POST':
        user = auth.authenticate(
            username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            auth.login(request, user)
            return redirect('/main')
        else:
            return render(request, 'login.html', {'error': 'Username or password is incorrect!'})
    else:
        return render(request, 'login.html')


def logout(request):
    if request.method == 'POST':
        auth.logout(request)
    return redirect('/')


def chart(request):
    bitcoin_price = None
    wrong_input = None
    range_error = None

    # assign the functions imported from services.py to variables to allow for easier use
    initiateDateGet = getDateService()
    initiateDefaultDataGet = getDefaultData()
    initiateUserDateGet = getUserInputDateRange()
    initiateRangeErrorGet = outOfRange()

    # get the dates for present day and present day - 10 days
    date_from, date_to = initiateDateGet.getCurrentDateView()

    # use the 10days period obtained from the function above to set the default form values
    search_form = initiateDefaultDataGet.makeDefaultApiView(date_from, date_to)

    # use the 10days period obtained from the function above to get dafualt 10days data
    bitcoin_price = getBitcoinData(date_from, date_to)

    # if request method is 'post', validate the form and get date range supplied by user and use it for the api call
    from_date, to_date = getUserDateView(request)

    if from_date is not None and to_date is not None:  # check if data was supplied by the user

        date_today = date_to  # assign todays date to date_today variable

        date_from, date_to, date_out_of_range, search_form = initiateRangeErrorGet.ooR(
            from_date, to_date, range_error)  # check if the supplied date range is not greater than 3 months

        if date_out_of_range is not None:
            # if date range is more than 3 months, render this error in the html page
            range_error = date_out_of_range
            bitcoin_price = None
        else:
            # if there is data supplied my the user via the form, proceed to make the api call and retrieve the required data
            bitcoin_price, date_from, date_to, wrong_input = getUserInputData(
                from_date, to_date, date_today, wrong_input)
            # make the date range submitted in the form supplied by the user via the form the default input of the form
            search_form = initiateUserDateGet.userFormInputView(
                from_date, to_date, date_today)

    context = {
        'search_form': search_form,
        'price': bitcoin_price,
        'wrong_input': wrong_input,
        'date_from': date_from,
        'date_to': date_to,
        'range_error': range_error
    }

    return render(request, "bitcoinlive.html", context)

# function to confirm if valid date ranges have been supplied by the user.


def getUserDateView(request):
    date_from = None
    date_to = None
    # get post request from the front end
    search_form = PriceSearchForm(request.POST or None)
    if request.method == 'POST':
        if search_form.is_valid():  # Confirm if valid data was received from the form
            # extract input 1 from submitted data
            date_from = request.POST.get('date_from')
            # extract input 2 from submitted data
            date_to = request.POST.get('date_to')

        else:
            raise Http404("Sorry, this did not work. Invalid input")

    return date_from, date_to


def getUserInputData(date_from, date_to, date_today, wrong_input):
    from_date = None
    to_date = None
    requested_btc_price_range = None

    if date_to > date_from:  # confirm that input2 is greater than input 1
        if date_to > date_today:  # if the date to from input is greater than today's date; there wont be data for the extra days, so we change the 'date_to' input back to todays's date
            date_to = date_today
        api = 'https://api.coindesk.com/v1/bpi/historical/close.json?start=' + date_from + '&end=' + \
            date_to + \
            '&index=[USD]'  # use the 10days period obtained above to get dafualt 10days value
        try:
            # get api response data from coindesk based on date range supplied by user with a timeout of 10seconds
            response = requests.get(api, timeout=10)
            # raise error if HTTP request returned an unsuccessful status code.
            response.raise_for_status()
            prices = response.json()  # convert response to json format
            # filter prices based on "bpi" values only
            requested_btc_price_range = prices.get("bpi")
            from_date = date_from
            to_date = date_to
        except requests.exceptions.ConnectionError as errc:  # raise error if connection fails
            raise ConnectionError(errc)
        # raise error if the request gets timed out after 10 seconds without receiving a single byte
        except requests.exceptions.Timeout as errt:
            raise TimeoutError(errt)
        # raise a general error if the above named errors are not triggered
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)
    else:
        # print out an error message if the user chooses a date that is greater than input1's date
        wrong_input = 'Wrong date input selection: date from cant be greater than date to, please try again'

    return requested_btc_price_range, from_date, to_date, wrong_input,


def getBitcoinData(date_from, date_to):

    api = 'https://api.coindesk.com/v1/bpi/historical/close.json?start=' + \
        date_from + '&end=' + date_to + '&index=[USD]'
    try:
        # get api response data from coindesk based on date range supplied by user
        response = requests.get(api, timeout=10)
        # raise error if HTTP request returned an unsuccessful status code.
        response.raise_for_status()
        prices = response.json()  # convert response to json format
        # filter prices based on "bpi" values only
        default_btc_price_range = prices.get("bpi")
    except requests.exceptions.ConnectionError as errc:  # raise error if connection fails
        raise ConnectionError(errc)
    # raise error if the request gets timed out after 10 seconds without receiving a single byte
    except requests.exceptions.Timeout as errt:
        raise TimeoutError(errt)
    # raise a general error if the above named errors are not triggered
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    return default_btc_price_range


pusher = Pusher(
    app_id="1310064",
    key="d09e49e4cef4860923b7",
    secret="48f3b5a74991f80f7b19",
    cluster="us3",
    ssl=True
)
times = []
currencies = ["ETH"]
prices = {"ETH": []}


def ethereum(request):
    return render(request, 'ethereum.html', {})


def ETH_data():
    current_prices = {}
    for currency in currencies:
        current_prices[currency] = []

    times.append(time.strftime('%H:%M:%S'))

    api_url = "https://min-api.cryptocompare.com/data/pricemulti?fsyms={}&tsyms=USD".format(
        ",".join(currencies))
    response = json.loads(requests.get(api_url).content)

    for currency in currencies:
        price = response[currency]['USD']
        current_prices[currency] = price
        prices[currency].append(price)

    graph_data = [go.Scatter(
        x=times,
        y=prices.get(currency),
        name="{} Prices".format(currency)
    ) for currency in currencies]

    bar_chart_data = [go.Bar(
        x=currencies,
        y=list(current_prices.values())
    )]

    data = {
        'graph': json.dumps(list(graph_data), cls=plotly.utils.PlotlyJSONEncoder),
        'bar_chart': json.dumps(list(bar_chart_data), cls=plotly.utils.PlotlyJSONEncoder)
    }

    pusher.trigger("crypto", "data-updated", data)


scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    func=ETH_data,
    trigger=IntervalTrigger(seconds=10),
    id='prices_retrieval_job',
    name='Retrieve prices every 10 seconds',
    replace_existing=True)

# atexit.register(lambda: scheduler.shutdown())


def ind(request):
    return render(request, 'ind.html', {})


def bitcoinrealtime(request):
    return render(request, 'bitcoinrealtime.html', {})


api_key = "61b86b0eefeab100014e106b"
api_secret = "5b12ab03-98f8-4b6e-afd0-c618acc1c4e7"
api_passphrase = "helloworld"


def wallet(request):
    client = Client(api_key, api_secret, api_passphrase)
    currencies = client.get_currency('ETH')
    results = client.get_account('61b895307330e50001ca3d84')
    # print(results)
    accnts=client.get_accounts()
    # print(accnts)
    # context = {
    #     "mydata": results
    # }
    context ={
        'accnts': accnts
    }
    return render(request, 'wallet.html', context)
# def chart(low_time_frame_data=[], high_time_frame_data=[], selected_symbols="", selected_date_start="",
#           selected_date_end=""):
#     title = "Charts"
#     symbols = get_data.get_symbols()
#     low_time_frame_data = low_time_frame_data
#     high_time_frame_data = high_time_frame_data
#     selected_symbols = selected_symbols
#     selected_date_start = selected_date_start
#     selected_date_end = selected_date_end
#     return render("chart_form.html", title=title, symbols=symbols,
#                            low_time_frame_data=low_time_frame_data, high_time_frame_data=high_time_frame_data,
#                            selected_symbols=selected_symbols, selected_date_start=selected_date_start,
#                            selected_date_end=selected_date_end)


# def plot():
#     try:

#         low_time_frame_data = []
#         high_time_frame_data = []

#         # data returns a list with objects then is turn to json with js on frontend
#         if len(request.form["date_start"]) != 0 and len(request.form["date_end"]) != 0:
#             low_time_frame_data = get_data.get_low_time_frame_data(request.form["symbols"], request.form["date_start"],
#                                                                    request.form["date_end"])
#             high_time_frame_data = get_data.get_high_time_frame_data(request.form["symbols"],
#                                                                      request.form["date_start"],
#                                                                      request.form["date_end"])
#             messages("Form data submitted", "Success")
#         else:
#             messages("Please enter data in all fields", "Success")
#     except Exception as e:
#         # If message attribute is not found, then e is an object that is not json serializable
#         # so convert to string to read.
#         messages(e.message if hasattr(e, 'message') else str(e), "Error")

#     return chart(low_time_frame_data, high_time_frame_data, request.form["symbols"], request.form["date_start"],
#                  request.form["date_end"])


# def csv_report():
#     title = "CSV Reports"
#     return render("csv.html", title=title)


# def balance():
#     title = "My balances"
#     my_balances = get_data.get_balance()
#     return render("balance.html", title=title, my_balances=my_balances)


# def download_last_prices_data():
#     return get_data.get_last_prices()


# def download_1day_interval_report_for_btcusdt_data():
#     return get_data.get_1day_interval_report_for_btcusdt()


# pusher = Pusher(
#     app_id = "1314831",
#     key = "9679e7e81e540fc2574f",
#     secret = "02359172c078f068c8a2",
#     cluster = "us3",
#     ssl=True,
#  )
# times = []
# currencies = ["BTC"]
# prices = {"BTC": []}


# def bitcoinrealtime(request):
#    pusher = Pusher(
#    app_id = "1310064",
#    key = "d09e49e4cef4860923b7",
#    secret = "48f3b5a74991f80f7b19",
#    cluster = "us3",
#    ssl=True
# )
#     times = []
#     currencies = ["BTC"]
#     prices = {"BTC": []}
#     return render(request, 'bitcoinrealtime.html', {})


# def BTC_data():
#     current_prices = {}
#     for currency in currencies:
#         current_prices[currency] = []

#     times.append(time.strftime('%H:%M:%S'))

#     api_url = "https://min-api.cryptocompare.com/data/pricemulti?fsyms={}&tsyms=USD".format(",".join(currencies))
#     response = json.loads(requests.get(api_url).content)

#     for currency in currencies:
#         price = response[currency]['USD']
#         current_prices[currency] = price
#         prices[currency].append(price)

#     graph_data = [go.Scatter(
#         x=times,
#         y=prices.get(currency),
#         name="{} Prices".format(currency)
#         ) for currency in currencies]

#     bar_chart_data = [go.Bar(
#         x=currencies,
#         y=list(current_prices.values())
#         )]

#     data = {
#         'graph': json.dumps(list(graph_data), cls=plotly.utils.PlotlyJSONEncoder),
#         'bar_chart': json.dumps(list(bar_chart_data), cls=plotly.utils.PlotlyJSONEncoder)
#     }


#     pusher.trigger("crypto", "data-updated", data)


# scheduler = BackgroundScheduler()
# scheduler.start()
# scheduler.add_job(
#     func=BTC_data,
#     trigger=IntervalTrigger(seconds=10),
#     id='prices_retrieval_job',
#     name='Retrieve prices every 10 seconds',
#     replace_existing=True)

# atexit.register(lambda: scheduler.shutdown())
class Eth(TemplateView):
    template_name = 'eth2.html'

    def get_context_data(self, **kwargs):
        # initiate context
        context = super().get_context_data(**kwargs)
        chart = []
        # get variable from Wallet
        Wallet.objects.all()
        wal = Wallet.objects.get(id=2)
        context['wallet'] = wal.wallet

        # fetcg data
        df = yf.download(tickers='ETH-USD', period='2y',
                         interval='1h', parse_dates=True)

        # 1 year comprehensive analysis
        dd = df.copy()
        eth_year = wal.eth
        cash_year = wal.wallet
        df_date = df.copy()
        df_sal = df.copy()
        times = pd.date_range(end=datetime.now(), freq="H", periods=8760)
        df_wl = df.copy()
        # df_wl = df_wl.sort_index()
        df_wl['Date'] = df.index.date.astype(str)
        df_wl['Time'] = df.index.time.astype(str)
        # df_wl = df_wl.sort_index()
        # df_wl['Date'] = df_wl['Date'].astype(str)
        context['eth_btc_val'] = (df_wl[df_wl['Date'] == str(
            times[0].date())].iloc[0].Close * eth_year).round(2)
        for dat in times:
            value = df_wl[df_wl['Date'] == str(dat.date())]
            for i in range(0, len(value) - 1):
                PA = (
                    (value.Close.iloc[i] - value.Close.iloc[i + 1]) / value.Close.iloc[i + 1]) * 100
                if PA >= 5:
                    if eth_year >= 0:
                        amount = (100 / value.Close.iloc[i])
                        eth_year -= amount
                        cash_year += 100
                elif PA <= -5:
                    if cash_year >= 100:
                        cash_year -= 100
                        eth_year += (1 / value.Close.iloc[i]) * 100
        context['now_btc_val'] = (df.Close.iloc[-1] * eth_year).round(2)
        pa = (((df.Close.iloc[-2] - df.Close.iloc[-1]) /
              df.Close.iloc[-1]) * 100).round(2)
        signal = ''
        btc = wal.btc
        cash = wal.wallet
        while 1:
            if pa >= 2:
                if pa >= 5:
                    if btc >= 0:
                        signal += 'Sold Eth'
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
        context['btc_year'] = eth_year
        context['cash_year'] = cash_year
        context['cash_start'] = wal.wallet
        context['btc_start'] = wal.eth

        # plot monthly graph
        df['Date'] = df.index.date.astype(str)
        df['Time'] = df.index.time.astype(str)
        layout = go.Layout(title="1 Month Ethereum Data", xaxis={
                           'title': 'Date'}, yaxis={'title': 'Close'})
        fig = go.Figure(data=[go.Candlestick(x=df.Date.iloc[-720:],
                                             open=df['Open'],
                                             high=df['High'],
                                             low=df['Low'],
                                             close=df['Close'])], layout=layout)
        context['graph_message_1'] = ''
        context['graph_1'] = fig.to_html()
        # plot graph on hourly basis
        value = df.iloc[-24:]
        dfpl = value.copy()
        fig = go.Figure()
        fig.update_layout(title="24 Hours ETH Data",
                          xaxis_title='Date', yaxis_title='Close')
        fig.add_trace(go.Candlestick(x=dfpl['Time'],
                                     open=dfpl.Open,
                                     high=dfpl.High,
                                     low=dfpl.Low,
                                     close=dfpl.Close))
        context['graph_message_2'] = ''
        context['graph_2'] = fig.to_html()
        # 2020 and 2021 difference
        # df_date['date'] = pd.to_datetime(df_date['date'])
        df_date['date'] = pd.to_datetime(df.index.date.astype(str))
        df_date.set_index('date', drop=True, inplace=True)
        m2021 = df_date.loc['2021', 'Close'].resample('M').mean().values
        m2020 = df_date.loc['2020', 'Close'].resample('M').mean().values
        fig = plt.figure(figsize=(6.5, 2), dpi=180)
        plt.plot(m2021, label='2021')
        plt.plot(m2020, label='2020')
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June',
                  'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        plt.xticks(np.arange(0, 12), labels=months, rotation=75)
        plt.legend(loc=0)
        plt.grid(True, alpha=0.1)
        html_str = mpld3.fig_to_html(fig)
        context['graph_3'] = html_str
        context['graph_message_3'] = '''
        The above graph shows the average of monthly price for 2020 and 2021. Follwoing are major insights from the graph

- There is a strong up trend from Oct-2020 to Apr-2021

- From Apr to July there is fall in prices

- For both of the years there is up-trend.

Let's dig into the details from Apr to July 2021'''

        aprtojul = df_date.loc['2021-4-1':'2021-7-31',
                               'Close'].resample('W').mean()
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
        ax1 = plt.plot(df_date.loc[df_date.year == 2020, 'month'], df_date.loc[df_date.year == 2020, 'Close'],
                       label='2020')
        ax2 = plt.plot(df_date.loc[df_date.year == 2021, 'month'], df_date.loc[df_date.year == 2021, 'Close'],
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

        # df_sal['date'] = pd.to_datetime(df_sal['date'])
        df_sal['date'] = pd.to_datetime(df_sal.index.date.astype(str))
        df_sal.set_index('date', drop=True, inplace=True)
        df_sal = df_sal.tail(168)
        df_sal['SMA24'] = SMA2(df_sal)
        # Get the buy and sell list
        strat = strategy2(df_sal)
        df_sal['Buy'] = strat[0]
        df_sal['Sell'] = strat[1]

        # Visualize the close price and the buy and sell signals
        fig = plt_sal.figure(figsize=(10.5, 4))
        plt_sal.title('Bitcoin Close Price and MA with Buy and Sell Signals')
        plt_sal.plot(df_sal['Close'], alpha=0.5,
                     label='Close Price Last 7 days')
        plt_sal.plot(df_sal['SMA24'], alpha=0.5, label='Simple Moving Avg')
        plt_sal.scatter(
            df_sal.index, df_sal['Buy'], color='green', label='Buy Signal', alpha=1)
        plt_sal.scatter(
            df_sal.index, df_sal['Sell'], color='red', label='Sell Signal', alpha=1)
        plt_sal.xlabel('Date')
        plt_sal.ylabel('Close Price in USD')
        plt_sal.legend(loc=3)
        html_str = mpld3.fig_to_html(fig)
        context['graph_6'] = html_str
        context['graph_message_6'] = """
The graph above shows the relationship between the date and the close price of ETH in USD.

The blue line trend represents the closing price of ETH over the last seven days, while the red line trend represents the moving averages over one day. 

There are also Buy and Sell Signals on this graph.

Buy = green :-

  Buy ETH when SMA of 1 day goes below the close price 

Sell = Red :-

  Sell When the 1 day SMA goes above the close price

Also, Never going to sell at a price lower than I bought.
                """

        return context






# Naveed Code Start's from here Please don't edit in this section


def indexmain(request):
    if request.method == 'POST':
        form_data = request.POST.dict()
        t = form_data.get('coins', '')
        p = '2y'
        i = '1h'  
        df = configdf(t,p,i)
        start=str(request.POST.get('start',''))
        end=str(request.POST.get('end',''))
        print(start, end, type(start), type(end))
        test = df.loc[start:end] 
        print(test.shape) 
        
        
        graphs = []
        layouts = []

        graphs.append(
            go.Scatter(x=test.index, y=test['Close'], mode = 'lines')
        )

        layouts.append(
            {
        'title': 'Line Plot',
        'xaxis_title': 'Date',
        'yaxis_title': 'Close Price',
        'height': 600,
        'width': 800,
        }

        ) 

        hourly_mean = test[['Close', 'Hour']].groupby(['Hour']).mean()

        graphs.append(
            go.Bar(x=hourly_mean.index.astype(str), y=hourly_mean['Close'])
        )

        layouts.append(
            {
        'title': 'Mean Prices for each hour of the day',
        'xaxis_title': 'Hours',
        'yaxis_title': 'Mean Price',
        'height': 600,
        'width': 800,
        }
        ) 

        weekday_mean = test[['Close', 'Weekday']].groupby(['Weekday']).mean()
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        weekday_mean = weekday_mean.reindex(days)

        graphs.append(
            go.Bar(x=weekday_mean.index, y=weekday_mean['Close'])
        )

        layouts.append(
            {
        'title': 'Mean Prices for each day of the Week',
        'xaxis_title': 'Day of Week',
        'yaxis_title': 'Mean Price',
        'height': 600,
        'width': 800,
        }
        )

        monthday_mean = test[['Close', 'Monthday']].groupby(['Monthday']).mean()

        graphs.append(
            go.Bar(x=monthday_mean.index.astype(str), y=monthday_mean['Close'])
        )

        layouts.append(
            {
        'title': 'Mean Prices for each day of the Month',
        'xaxis_title': 'Day of Month',
        'yaxis_title': 'Mean Price',
        'height': 600,
        'width': 800,
        }
        )

        monthly_mean = test[['Close', 'Month']].groupby(['Month']).mean()
        reorder = ['Jan', 'Feb', 'Mar','Apr', 'May', 'Jun','Jul','Aug','Sep','Oct', 'Nov','Dec']
        monthly_mean = monthly_mean.reindex(reorder)

        graphs.append(
            go.Bar(x=monthly_mean.index, y=monthly_mean['Close'])
        )

        layouts.append(
            {
        'title': 'Mean Prices for each Month of the Year',
        'xaxis_title': 'Months',
        'yaxis_title': 'Mean Price',
        'height': 600,
        'width': 800,
        }
        )

        yearly_mean = test[['Close', 'Year']].groupby(['Year']).mean()

        graphs.append(
            go.Bar(x=yearly_mean.index.astype(str), y=yearly_mean['Close'])
        )

        layouts.append(
            {
        'title': 'Mean Prices for each Year',
        'xaxis_title': 'Years',
        'yaxis_title': 'Mean Price',
        'height': 600,
        'width': 800,
        }
        )

        data_7days = test.iloc[-168:]

        graphs.append(
            go.Candlestick(x=data_7days.index, open=data_7days['Open'],
            high=data_7days['High'], low=data_7days['Low'],
            close=data_7days['Close']     
            )
        )

        layouts.append(
            {
        'title': 'Candlestick for recent 7-Days Data',
        'xaxis_title': 'Dates',
        'yaxis_title': 'Price',
        'height': 600,
        'width': 800,
        }
        )

        data_24hrs = test.iloc[-24:]

        graphs.append(
            go.Candlestick(x=data_24hrs.index, open=data_24hrs['Open'],
            high=data_24hrs['High'], low=data_24hrs['Low'],
            close=data_24hrs['Close']     
            )
        )

        layouts.append(
            {
        'title': 'Candlestick for recent 24-Hours Data',
        'xaxis_title': 'Hours',
        'yaxis_title': 'Price',
        'height': 600,
        'width': 800,
        }
        )


        plot_div=[]
        for g,l in zip(graphs,layouts):
            plot_div.append(plot({'data': g, 'layout': l}, output_type='div'))
        return render(request, 'index.html',{'plotdivs': plot_div, 'coin': t})
    else:
        return render(request, 'index.html', {})


def compare(request):
    inplots = []
    # make connection to database and get runtimegraphs table into dataframe
    conn = sqlite3.connect("db.sqlite3")
    # fetching data from database
    df_btc = pd.read_sql_query("select * from RuntimeGraphs_btcdataset;", conn, 
            parse_dates=True, index_col='Date')
    df_eth = pd.read_sql_query("select * from RuntimeGraphs_ethdataset;", conn, 
            parse_dates=True, index_col='Date')
    df_bnb = pd.read_sql_query("select * from RuntimeGraphs_bnbdataset;", conn, 
            parse_dates=True, index_col='Date')
    df_sol = pd.read_sql_query("select * from RuntimeGraphs_soldataset;", conn, 
            parse_dates=True, index_col='Date')
    
    # getting Close column and its percentage change
    btc = df_btc.Close.pct_change()
    eth = df_eth.Close.pct_change()
    bnb = df_bnb.Close.pct_change()
    sol = df_sol.Close.pct_change()
    # making a dataframe from multiple series
    dfclose = pd.DataFrame({'BTC': btc, 'ETH': eth, 'BNB': bnb, 'SOL': sol})
    corr_all = dfclose.corr()
    mask = np.triu(np.ones_like(corr_all, dtype=np.bool))
    heatmap_all = get_heatmap(corr_all, title="Percentage Change Correlation between Coins", mask=mask)
    inplots.append(heatmap_all)
    # corelation between BTC and other coins
    ethr = btc.corr(eth)
    bnbr = btc.corr(bnb)
    solr = btc.corr(sol)
    corr_with_btc = pd.Series(data=[ethr, bnbr, solr], index=['ETH', 'BNB', 'SOL'])
    df_corr_with_btc = corr_with_btc.to_frame(name='BTC')
    heatmap_btc = get_heatmap(df_corr_with_btc, title="Correlation of Other Coins With BTC")
    inplots.append(heatmap_btc)
    # bar plot
    corr_with_btc.sort_values(ascending=False, inplace= True)
    bars = get_barplot(x=corr_with_btc.index, y=corr_with_btc.values, 
        title='Correlation Between BTC and Other Coins')
    inplots.append(bars)
    return render(request, 'comparison.html', {'iplots':inplots})


        