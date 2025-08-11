from django.urls import path
from . import views
from .forms import TransactionForm

urlpatterns = [
    path('create/', views.create_transaction, name='transaction_create'),
]
