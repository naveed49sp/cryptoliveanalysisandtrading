from django.db import models


# Create your models here.
class CryptoDataset(models.Model):
    date = models.DateTimeField(primary_key=True)
    open = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    high = models.FloatField()
    volume = models.FloatField()

    def __str__(self):
        return self.date


class Wallet(models.Model):
    username = models.CharField(default='user1', max_length=255)
    wallet = models.FloatField()
    btc = models.FloatField(default=1.0)

    def __float__(self):
        return self.wallet


class Purchase(models.Model):
    date = models.DateTimeField()
    currency_name = models.CharField(max_length=255)
    currency_purchase = models.FloatField()
    is_sold = models.BooleanField()
    net_gain = models.FloatField()

    def __str__(self):
        return self.currency_name
