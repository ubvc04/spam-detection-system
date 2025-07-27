from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('predict/url/', views.predict_url, name='predict_url'),
    path('predict/sms/', views.predict_sms, name='predict_sms'),
    path('predict/email/', views.predict_email, name='predict_email'),
    path('clear-history/', views.clear_history, name='clear_history'),
    path('delete-prediction/<uuid:prediction_id>/', views.delete_prediction, name='delete_prediction'),
    path('delete-selected-history/', views.delete_selected_history, name='delete_selected_history'),
] 