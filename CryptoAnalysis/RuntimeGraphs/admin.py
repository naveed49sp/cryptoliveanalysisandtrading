from django.contrib import admin
from .models import CryptoDataset


class DatasetAdmin(admin.ModelAdmin):
    list_display = ('date', 'open', 'high', 'low', 'close', 'volume')


admin.site.register(CryptoDataset)
