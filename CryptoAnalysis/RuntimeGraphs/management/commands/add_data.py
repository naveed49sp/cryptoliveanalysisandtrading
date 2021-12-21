import sys
sys.path.append("...")

import yfinance as yf
from django.core.management.base import BaseCommand
from RuntimeGraphs.models import BTCDataset, ETHDataset, BNBDataset, SOLDataset


class Command(BaseCommand):
    help = "A command to add data from dataframe to the database"

    def handle(self, *args, **options):
        BTCDataset.objects.all().delete()
        ETHDataset.objects.all().delete()
        BNBDataset.objects.all().delete()
        SOLDataset.objects.all().delete()

        print("Previous Data Deleted--")

        dfbtc = yf.download(tickers='BTC-USD', period='2y', interval='1h',parse_dates=True)
        dfeth = yf.download(tickers='ETH-USD', period='2y', interval='1h',parse_dates=True)
        dfbnb = yf.download(tickers='BNB-USD', period='2y', interval='1h',parse_dates=True)
        dfsol = yf.download(tickers='SOL-USD', period='2y', interval='1h',parse_dates=True)
        dfbtc.drop('Adj Close', axis=1, inplace=True)
        dfeth.drop('Adj Close', axis=1, inplace=True)
        dfbnb.drop('Adj Close', axis=1, inplace=True)
        dfsol.drop('Adj Close', axis=1, inplace=True)
        # print(dfeth.columns)

        for agency in dfbtc.itertuples():
            fortune = BTCDataset(Date=getattr(agency, 'Index'), Open=getattr(agency, 'Open'),
                                    Close=getattr(agency, 'Close'), Volume=getattr(agency, 'Volume'),
                                    High=getattr(agency, 'High'), Low=getattr(agency, 'Low'))
            fortune.save()

        for agency in dfeth.itertuples():
            fortune = ETHDataset(Date=getattr(agency, 'Index'), Open=getattr(agency, 'Open'),
                                    Close=getattr(agency, 'Close'), Volume=getattr(agency, 'Volume'),
                                    High=getattr(agency, 'High'), Low=getattr(agency, 'Low'))
            fortune.save()

        for agency in dfbnb.itertuples():
            fortune = BNBDataset(Date=getattr(agency, 'Index'), Open=getattr(agency, 'Open'),
                                    Close=getattr(agency, 'Close'), Volume=getattr(agency, 'Volume'),
                                    High=getattr(agency, 'High'), Low=getattr(agency, 'Low'))
            fortune.save()
        for agency in dfsol.itertuples():
            fortune = SOLDataset(Date=getattr(agency, 'Index'), Open=getattr(agency, 'Open'),
                                    Close=getattr(agency, 'Close'), Volume=getattr(agency, 'Volume'),
                                    High=getattr(agency, 'High'), Low=getattr(agency, 'Low'))
            fortune.save()
        print("Command to save data executed successfully..")
