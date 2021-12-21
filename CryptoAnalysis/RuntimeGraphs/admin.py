from django.contrib import admin
from .models import BTCDataset, ETHDataset, BNBDataset, SOLDataset, Wallet, Purchase


class DatasetAdmin(admin.ModelAdmin):
    list_display = ('Date', 'Open', 'High', 'Low', 'Close', 'Volume')


admin.site.register(BTCDataset)


class WalletAdmin(admin.ModelAdmin):
    list_display = ('Id', 'wallet')


admin.site.register(Wallet)


class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('currency_name', 'currency_purchase', 'currency_purchase', 'is_sold', 'net_gain')


admin.site.register(Purchase)
admin.site.register(ETHDataset)
