from datetime import datetime
import yfinance as yf
from django.core.management.base import BaseCommand
from ...models import CryptoDataset, Wallet, Purchase
import time


class Command(BaseCommand):
    help = "A command to add data from dataframe to the database"

    def handle(self, *args, **options):
        while 1:
            data = yf.download(tickers='BTC-USD', period='2y', interval='1h')
            data.drop('Adj Close', axis=1, inplace=True)
            d1 = data.iloc[-1]
            fortune = CryptoDataset(date=data.index[-1], open=d1['Open'],
                                    close=d1['Close'], volume=d1['Volume'],
                                    high=d1['High'], low=d1['Low'])
            pa = (((data.Close.iloc[-2] - data.Close.iloc[-1]) / data.Close.iloc[-1]) * 100).round(2)
            fortune.save()
            wal = Wallet.objects.get(id=2)
            btc = wal.btc
            cash = wal.wallet
            if pa >= 2:
                if pa >= 5:
                    if (btc - (100 / data.Close.iloc[-1])) >= 0:
                        amount = (100 / data.Close.iloc[-1])
                        btc -= amount
                        cash += 100
                        wal = wal(wallet=cash, btc=btc)
                        pur = Purchase(date=datetime.now(), currency_name="USD", currency_value=100, is_sold=False,
                                       net_gain=amount)
                        pur.save()
                        wal.save()
            elif pa <= -5:
                if cash >= 100:
                    cash -= 100
                    amount = (1 / data.Close.iloc[-1]) * 100
                    btc += amount
                    pur = Purchase(date=datetime.now(), currency_name="BTC", currency_value=btc, is_sold=False,
                                   net_gain=amount)
                    wal = wal(wallet=cash, btc=btc)
                    pur.save()
                    wal.save()
            time.sleep(3600)
