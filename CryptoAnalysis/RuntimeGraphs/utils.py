import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import yfinance as yf
import base64
from io import BytesIO



def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

def get_heatmap(rr, title="Correlation Heat Map", mask=None):
    plt.switch_backend('AGG')
    plt.figure(figsize=(10, 5))
    plt.title(title, fontsize=20)
    sns.heatmap(rr, annot=True, mask=mask)
    plt.xticks(rotation=45, fontsize=12)
    plt.yticks(fontsize=12)
    plt.tight_layout()
    graph = get_graph()
    return graph

def get_barplot(x,y, title="Bar Plot"):
    plt.switch_backend('AGG')
    plt.figure(figsize=(10,5))
    plt.title(title, fontsize=20)
    sns.barplot(x=x, y=y, palette='coolwarm')
    plt.xticks(rotation=45, fontsize=12)
    plt.yticks(fontsize=12)
    plt.tight_layout()
    graph = get_graph()
    return graph

def buy_sell(df, coin=1.0, amount=10000):
    df['pctchange'] = df['Close'].pct_change()*100 
    buy = []
    sell = []
    amount=amount
    coin = coin
    for r in df.itertuples():
        if r.pctchange <= -3.0 and amount>0:
            amount -= 100      # buy coin   
            coin += 100/r.Close
            buy.append(r.Close)
            sell.append(np.nan)
        elif r.pctchange >= 5.0 and coin>0: 
            amount += 100          #sell coin
            coin -= 100/r.Close
            sell.append(r.Close)
            buy.append(np.nan)
        else:
            sell.append(np.nan)
            buy.append(np.nan)
    return buy, sell, amount, coin


def configdf(t='BTC-USD', p='2y', i='1h'):
    df = yf.download(tickers= t, period = p, interval= i, parse_dates=True)
    df['Date'] = df.index.date.astype(str)
    df['Time'] = df.index.time.astype(str)
    df['Year'] = pd.DatetimeIndex(df.index.date).year
    df['Month'] = df.index.strftime('%b') #Name of month abbreviated
    df['Monthday'] = pd.DatetimeIndex(df.index.date).day
    df['Weekday'] = df.index.strftime('%a') #weekday abbreviated
    df['Hour'] = pd.DatetimeIndex(df.index).hour
    return df

def get_plot(x, y, title, xlabel, ylabel, scatter=None, x_sca=None, y_sca=None):
    plt.switch_backend('AGG')
    plt.figure(figsize=(10, 5))
    plt.title(title)
    plt.plot(x, y)
    plt.xticks(rotation=45)
    if scatter is not None:
        plt.scatter(x_sca, y_sca, color="red")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    graph = get_graph()
    return graph

