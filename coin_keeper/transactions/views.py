from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import TransactionForm, AnalyticsForm
from .models import Category, Transaction
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils.http import url_has_allowed_host_and_scheme
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils import timezone
from django.db.models import Sum

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


def analytics(request):
    # Transactions sort
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    today = timezone.now().date()
    form = AnalyticsForm(request.GET)

    if form.is_valid():
        cd = form.cleaned_data
        type = cd.get('type', Category.CategoryType.EXPENSE)
        date_from = cd.get('date_from')
        date_to = cd.get('date_to')
        page = cd.get('page')
        category = cd.get('category','')
        if date_from and date_to:
            transactions = transactions.filter(date__gte=date_from, date__lte=date_to)
    else:
        type = Category.CategoryType.EXPENSE
        page = request.GET.get('page')
        category = request.GET.get('category', '')
    if category:
        transactions = transactions.filter(category__name=category)
    transactions = transactions.filter(category__type=type)

    # Analytics
    sum = transactions.aggregate(sum=Sum('amount'))['sum']
    if not category:
        categories_sum = transactions.values_list('category__name')\
                                     .annotate(total_sum=Sum('amount'))\
                                     .values_list('category__name', 'total_sum')

    # Pagination
    paginator = Paginator(transactions, 5)
    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        transactions = paginator.page(1)
    except EmptyPage:
        transactions = paginator.page(paginator.num_pages)

    # Context
    context = {
        'form': form,
        'page_obj': transactions,
        'sum': sum
    }
    if category:
        context['category'] = category
    else:
        context['categories_sum'] = categories_sum

    return render(request, 'transactions/analytics.html', context)