from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import TransactionForm
from .models import Category, Transaction
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils.http import url_has_allowed_host_and_scheme

def create_transaction(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            category_name = cd.get('category', '').strip()
            type = cd['type']

            with transaction.atomic():
                if not category_name:
                    category, created = Category.objects.get_or_create(
                        name='Other Income' if type == Category.CategoryType.INCOME else 'Other Expenses',
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
    

@require_POST
@login_required
def delete_transaction(request, id):
    try:
        transaction = Transaction.objects.filter(user=request.user).get(id=id)
        transaction.delete()
        messages.success(request, _('Transaction deleted successfully'))
    except Transaction.DoesNotExist:
        messages.error(request, _('Transaction not found'))

    referer = request.META.get('HTTP_REFERER', '/')
    if url_has_allowed_host_and_scheme(referer, allowed_hosts={request.get_host()}):
        return redirect(referer)
    return redirect(reverse_lazy('transactions_list'))