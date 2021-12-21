from django.db import models


# Create your models here.
class BTCDataset(models.Model):
    Date = models.DateTimeField(primary_key=True)
    Open = models.FloatField()
    Low = models.FloatField()
    Close = models.FloatField()
    High = models.FloatField()
    Volume = models.FloatField()

    def __str__(self):
        return self.Date


class ETHDataset(models.Model):
    Date = models.DateTimeField(primary_key=True)
    Open = models.FloatField()
    Low = models.FloatField()
    Close = models.FloatField()
    High = models.FloatField()
    Volume = models.FloatField()

    def __str__(self):
        return self.Date

class BNBDataset(models.Model):
    Date = models.DateTimeField(primary_key=True)
    Open = models.FloatField()
    Low = models.FloatField()
    Close = models.FloatField()
    High = models.FloatField()
    Volume = models.FloatField()

    def __str__(self):
        return self.Date


class SOLDataset(models.Model):
    Date = models.DateTimeField(primary_key=True)
    Open = models.FloatField()
    Low = models.FloatField()
    Close = models.FloatField()
    High = models.FloatField()
    Volume = models.FloatField()

    def __str__(self):
        return self.Date

class Wallet(models.Model):
    username = models.CharField(default='user1', max_length=255)
    wallet = models.FloatField()
    btc = models.FloatField(default=1.0)
    eth = models.FloatField(default=1.0)
    # ad=models.FloatField(default=1.0)
 
    def __float__(self):
        return self.username


class Purchase(models.Model):
    date = models.DateTimeField()
    currency_name = models.CharField(max_length=255)
    currency_purchase = models.FloatField()
    is_sold = models.BooleanField()
    net_gain = models.FloatField()

    def __str__(self):
        return self.currency_name
    
    
# class Employee(models.Model):  
#     eid = models.CharField(max_length=20)  
#     ename = models.CharField(max_length=100)  
#     eemail = models.EmailField()  
#     econtact = models.CharField(max_length=15)  
#     class Meta:  
#         db_table = "employee" 
