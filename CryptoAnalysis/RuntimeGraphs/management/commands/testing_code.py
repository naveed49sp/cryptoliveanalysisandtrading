import yfinance as yf
from django.core.management.base import BaseCommand
from ...models import CryptoDataset, Purchase, Wallet


class Command(BaseCommand):
    help = "A command to add data from dataframe to the database"

    def handle(self, *args, **options):
        c = CryptoDataset.objects.all()
        data = [value for value in c]
        print(data)