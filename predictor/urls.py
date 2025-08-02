from django.urls import path
from .views import home,symptom_check

urlpatterns = [
    path('', home, name='home'),
    path('symp/', symptom_check, name='symptom_check'),
]