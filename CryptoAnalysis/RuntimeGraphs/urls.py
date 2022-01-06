from django.urls import path
from . import views

urlpatterns = [
    # path('', views, name='index'),
    
    path('', views.indexmain, name='index'),
    path('compare', views.compare, name='compare'),
    path('trade', views.trade, name='trade'),
    path("main/<int:id>", views.main, name= "main"),
    path('update/<int:id>', views.update, name='update'),
    path('signup', views.signup2, name="signup"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name= "logout"),
    path("facerecognition", views.facerecognition, name="facerecognition"),
    path("video_feed", views.video_feed, name="video_feed"),
    
    path("ethereum", views.ethereum, name= "ethereum"),
    path("ada", views.ada, name= "ada"),
    path("bitcoinlive", views.chart, name="chart"),
    path("bitcoinrealtime", views.bitcoinrealtime, name="bitcoinrealtime"),
    path('ind', views.ind, name='ind'),
    path('wallet', views.wallet, name='wallet'),
    
    
    
    
]
