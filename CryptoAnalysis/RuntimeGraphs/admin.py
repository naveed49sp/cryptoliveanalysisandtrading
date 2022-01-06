from django.contrib import admin
from .models import Myuser

class MyuserAdmin(admin.ModelAdmin):
    list_display = ('username', "cash", 'coins')
    search_fields = ('username', 'coins')


admin.site.register(Myuser, MyuserAdmin)



