from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import TransactionForm
from .models import Category, Transaction
from django.views.generic import ListView

def create_transaction(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            category_name = cd.get('category_name', '').strip()
            type = cd['type']

            with transaction.atomic():
                if not category_name:
                    category, created = Category.objects.get_or_create(
                        name='Other Income' if type == Category.CategoryType.INCOME else 'Other Expense',
                        type=type,
                        user=None
                    )
                else:
                    category, created = Category.objects.get_or_create(
                        name=category_name,
                        type=type,
                        user=request.user
                    )
                Transaction.objects.create(
                    user=request.user,
                    amount=cd['amount'],
                    description=cd['description'],
                    category=category,
                )
            
            messages.success(request, _('Transaction created successfully!'))
            return redirect(reverse_lazy('transactions_list'))
    else:
        form = TransactionForm()
        return render(request, 'transactions/create.html', {'form': form})
    
        
class TransactionsListView(LoginRequiredMixin, ListView):
    model = Transaction
    paginate_by = 10
    context_object_name = 'transactions'
    template_name = 'transactions/list.html'

    def get_queryset(self):
        return super().get_queryset()\
                      .filter(user=self.request.user)\
                      .select_related('category')\
                      .order_by('-date')