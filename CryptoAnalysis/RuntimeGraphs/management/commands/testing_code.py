import datetime
import sqlite3
import pandas as pd
import yfinance as yf
from django.core.management.base import BaseCommand
from ...models import CryptoDataset, Purchase, Wallet


class Command(BaseCommand):
    help = "A command to add data from dataframe to the database"

    def handle(self, *args, **options):
        conn = sqlite3.connect("db.sqlite3")
        df = pd.read_sql_query("select * from RuntimeGraphs_cryptodataset;", conn)
        # wallet analysis
        wallet = Wallet.objects.get(id=2)
        btc = wallet.btc
        wallet = wallet.wallet

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
        for dat in times:
            value = df_wl[df_wl['Date'] == str(dat.date())]
            for i in range(0, len(value)-1):
                PA = ((value.close.iloc[i] - value.close.iloc[i + 1]) / value.close.iloc[i + 1]) * 100
                if PA >= 5:
                    if btc >= 0:
                        amount = (100 / value.close.iloc[i]).round(7)
                        btc -= amount
                        wallet += 100
                        total_selling += 1
                elif PA < -5:
                    if wallet >= 100:
                        wallet -= 100
                        btc += (1 / value.close.iloc[i]).round(7) * 100
                        total_buying += 1
        print(wallet, btc)
