from django.urls import path

from . import views

app_name = "SingleGame"
urlpatterns = [
    path('', views.index, name='index'),
    path('startExperiment', views.startExperiment, name='startExperiment'),
    path('continueDisclaimer', views.continueDisclaimer, name='continueDisclaimer'),
    path('changeLanguage/<slug:language>/', views.changeLanguage, name='changeLanguage'),
    path('selectAdversaries', views.selectAdversaries, name='selectAdversaries'),
    path('startNewExperiment', views.startNewExperiment, name='startNewExperiment'),
    path('doAction', views.doAction, name='doAction'),
    path('startGame', views.startGame, name='startGame'),
    path('gameFinished', views.finishGame, name='gameFinished'),
    path('webGL', views.webGL, name='webGL'),
    path('rules', views.showRules, name='showRules'),
    path('rank', views.getPerformanceScoreRank, name='rank'),
    path('ruleBook', views.getRuleBook, name='ruleBook'),
    path('createDb', views.createDB, name='createDb')
]