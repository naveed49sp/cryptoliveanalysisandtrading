from django.shortcuts import render
from .utils import get_plot
from .models import CryptoDataset
import yfinance as yf
import plotly.graph_objs as go

# Create your views here.


def index(request):
    charts = []
    data = yf.download(tickers='BTC-USD', period='2y', interval='1h')
    data.drop('Adj Close', axis=1, inplace=True)
    charts.append(get_plot(data.index, data.Open))
    charts.append(get_plot(data.index, data.Close))
    # declare figure
    return render(request, 'index.html', {'chart': charts})


def about(request):
    return render(request, 'about.html', {})
