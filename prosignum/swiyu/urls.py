from django.urls import path
from . import views

app_name = 'swiyu'

urlpatterns = [
    path('login/', views.swiyu_login_page, name='login'),
    path('status/<uuid:verification_uuid>/', views.swiyu_check_status, name='check_status'),
]
