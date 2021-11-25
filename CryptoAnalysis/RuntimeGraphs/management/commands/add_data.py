import yfinance as yf
from django.core.management.base import BaseCommand
from ...models import CryptoDataset
import time


class Command(BaseCommand):
    help = "A command to add data from dataframe to the database"

    def handle(self, *args, **options):
        data = yf.download(tickers='BTC-USD', period='2y', interval='1h')
        data.drop('Adj Close', axis=1, inplace=True)
        print(data.columns)

        for agency in data.itertuples():
            fortune = CryptoDataset(date=getattr(agency, 'Index'), open=getattr(agency, 'Open'),
                                    close=getattr(agency, 'Close'), volume=getattr(agency, 'Volume'),
                                    high=getattr(agency, 'High'), low=getattr(agency, 'Low'))
            fortune.save()
        while 1:
            data = yf.download(tickers='BTC-USD', period='2y', interval='1h')
            data.drop('Adj Close', axis=1, inplace=True)
            d1 = data.iloc[-1]
            fortune = CryptoDataset(date=data.index[-1], open=d1['Open'],
                                    close=d1['Close'], volume=d1['Volume'],
                                    high=d1['High'], low=d1['Low'])
            fortune.save()
            time.sleep(3600)
        # print(data.columns)
