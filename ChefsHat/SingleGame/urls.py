from django.urls import path

from . import views

app_name = "SingleGame"
urlpatterns = [
    path('', views.index, name='index'),
    path('selectAdversaries', views.selectAdversaries, name='selectAdversaries'),
    path('startNewExperiment', views.startNewExperiment, name='startNewExperiment'),
    path('doAction', views.doAction, name='doAction'),
    path('startGame', views.startGame, name='startGame'),
    path('gameFinished', views.startGame, name='gameFinished')
]