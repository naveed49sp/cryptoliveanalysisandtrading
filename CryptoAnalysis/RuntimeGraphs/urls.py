from django.urls import path
from . import views

urlpatterns = [
    # path('', views, name='index'),
    
    path('', views.indexmain, name='index'),
    path('compare', views.compare, name='compare'),
    path('signup', views.signup, name="signup"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name= "logout"),
    path("main", views.Main, name= "main"),
    path("ethereum", views.ethereum, name= "ethereum"),
    path("bitcoin", views.Index.as_view(), name="bitcoin"),
    path("eth", views.Eth.as_view(), name="eth"),
    path("ada", views.ada, name= "ada"),
    path("bitcoinlive", views.chart, name="chart"),
    path("bitcoinrealtime", views.bitcoinrealtime, name="bitcoinrealtime"),
    path('ind', views.ind, name='ind'),
    path('wallet', views.wallet, name='wallet'),
    
    
    
    
]
