from kucoin.client import Client
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.http import request
from RuntimeGraphs.models import Wallet
from datetime import datetime
from django.shortcuts import render, redirect
from .forms import PriceSearchForm
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
from FaceRecognition.live_face_rec import RealTimeRecognition
from django.http.response import StreamingHttpResponse
from .utils import *
import requests
import json
import atexit
import time
import plotly
import plotly.graph_objs as go
from .models import Myuser
plt_sal.style.use('fivethirtyeight')




    


def bitcoin(request):
    return render(request, 'bitcoin.html', {})


def ada(request):
    return render(request, 'ada.html', {})


def realtimechart(request):
    return render(request, 'realtimechart.html', {})


def show(request):
    wallets = Wallet.objects.all()
    return render(request, "main.html", {'wallet': wallets})

def signup2(request):
    if request.method == "POST":
        if request.POST['password1'] == request.POST['password2']:
            uname = request.POST['username']
            passwd = request.POST['password1']
            count = Myuser.objects.filter(username=uname).count()
            if count > 0:
                return render(request, 'register.html', {'error': 'Username is already taken!'})
            else:
                user = Myuser(username = uname, password = passwd, cash = 0, coins=0.0)
                user.save()
                return redirect('login')
        else:
            return render(request, 'register.html', {'error': 'Password does not match!'})
    else:
        return render(request, 'register.html')

def main(request,id):
    if request.session.has_key('is_logged'):
        try:
            user = Myuser.objects.get(id=id)
        except:
            return redirect('login')
        return render(request, 'main.html', context={'us':user})
    else:
        return redirect('login')

def login(request):
    if request.method == 'POST':
        uname = request.POST['username']
        passwd = request.POST['password']
        user = Myuser.objects.filter(username = uname, password=passwd)
        if user.count()>0:
            request.session['is_logged'] = True
            temp = 'main/'+str(user.first().id)
            return redirect(temp)
            # return render(request, 'main.html', context={'us': user.first()})
        else:
            return render(request, 'login.html', {'error': 'Username or password is incorrect!'})
    else:
        return render(request, 'login.html')

def update(request,id):
    if request.session.has_key('is_logged'):
        user = Myuser.objects.filter(id = id)
        if request.method == 'POST':
            uname = request.POST['name']
            csh = request.POST['cash']
            coin = request.POST['coin']
            user.update(username=uname, cash=csh, coins=coin )
            temp = '/main/'+str(user.first().id)
            return redirect(temp)
        else:
            return render(request, 'update_wallet.html', context={'us': user.first()})
    else:
        return redirect('login')

def logout(request):
    del request.session['is_logged']
    return redirect('/')


def chart(request):
    bitcoin_price = None
    wrong_input = None
    range_error = None

    # assign the functions imported from services.py to variables to allow for easier use
    initiateDateGet = getDateService() # it is a class and we are creating an object of it
    date_from, date_to = initiateDateGet.getCurrentDateView()  # get the dates for present day and present day - 10 days

    initiateDefaultDataGet = getDefaultData() # it is a class and we are creating an object of it
    search_form = initiateDefaultDataGet.makeDefaultApiView(date_from, date_to) # use the 10days period obtained from the function above to set the default form values
    
    initiateUserDateGet = getUserInputDateRange()
    initiateRangeErrorGet = outOfRange()

    

    

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

# Naveed Code Start's from here Please don't edit in this section

def facerecognition(request):
    return render(request, "cam.html")

def video_feed(request):
    
    StreamingHttpResponse(
        RealTimeRecognition().open_camer(request),
        content_type="multipart/x-mixed-replace; boundary=frame",
    )


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

    if request.method == 'POST':
        form_data = request.POST.dict()
        t1 = form_data.get('coins', '')
        t2 = form_data.get('comparewith', '')
        p = '2y'
        i = '1h'  
        df1 = configdf(t1,p,i)
        df2 = configdf(t2,p,i)
        start=str(request.POST.get('start',''))
        end=str(request.POST.get('end',''))
        print(start, end, type(start), type(end))
        test1 = df1.loc[start:end] 
        test2 = df2.loc[start:end] 
        print(test1.shape) 
        
        
        graphs = []

        graphs.append(
            go.Scatter(x=test1.index, y=test1['Close'], mode = 'lines', name = t1)
        )

        graphs.append(
            go.Scatter(x=test2.index, y=test2['Close'], mode = 'lines', name = t2)
        )

        # layout for the figure
        layout = {
        'title': 'Comparison',
        'xaxis_title': 'Date',
        'yaxis_title': 'Close Price',
        'height': 600,
        'width': 800,
        }

        plot_div=plot({'data': graphs, 'layout': layout}, output_type='div')
    
        return render(request, 'comparison.html', {'plotdiv': plot_div, 'iplots':inplots, 'coin1': t1, 'coin2': t2})
    else:
        return render(request, 'comparison.html', {'iplots':inplots})

def trade(request):
    if request.method == 'POST':
        form_data = request.POST.dict()
        t = form_data.get('coins', '')
        p = '1y'
        i = '1h'  
        df = yf.download(tickers=t, period=p, interval=i, parse_dates=True)
        start=str(request.POST.get('start',''))
        test = df.loc[start:]
        buy, sell, amount, coin = buy_sell(test, coin=1, amount=10000)
        wallet = {'amount': amount, 'coin': coin, 'date': start, 'ticker' : t}
        graphs = []
        print('Buy', len(buy), len(sell), len(test.index))
        graphs.append(
            go.Scatter(x=test.index, y=test['Close'], mode = 'lines', name='Close Price')
        )
        graphs.append(
            go.Scatter(x=test.index, y=buy, mode = 'markers', marker_symbol = 'square', name='Buy' )
        )
        graphs.append(
            go.Scatter(x=test.index, y=sell, mode = 'markers', marker_symbol = 'x', name='Sell' )
        )

        layout ={
        'title': 'Trading',
        'xaxis_title': 'Date',
        'yaxis_title': 'Close Price',
        'height': 600,
        'width': 800,
        }

        plot_div = plot({'data': graphs, 'layout': layout}, output_type='div')
        return render(request, 'trade_strategy.html', {'plotdiv': plot_div, 'wallet': wallet})
    else:
        return render(request, 'trade_strategy.html')
        