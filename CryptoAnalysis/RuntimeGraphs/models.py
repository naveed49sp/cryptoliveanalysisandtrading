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
