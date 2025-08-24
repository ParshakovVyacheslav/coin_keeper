from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django import forms
from .models import Transaction, Category

class TransactionForm(forms.ModelForm):
    type = forms.ChoiceField(
        choices=Category.CategoryType.choices,
        label=_('Transaction Type'),
        initial=Category.CategoryType.EXPENSE,
        widget=forms.Select()
    )
    category = forms.CharField(
        max_length=50,
        label=_('Category'),
        required=False,
        widget=forms.TextInput()
    )

    class Meta:
        model = Transaction
        fields = ['amount', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['amount'].validators.append(MinValueValidator)
        self.fields['amount'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Amount'),
            'min': '0.01',
            'step': '0.01',
            'required': 'True'
        })
        self.fields['type'].widget.attrs.update({
            'class': 'form-control'
        })
        self.fields['category'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Enter category name')
        })
        self.fields['description'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Description')
        })


class AnalyticsForm(forms.Form):
    type = forms.ChoiceField(
        choices=Category.CategoryType.choices,
        label=_('Transaction Type'),
        initial=Category.CategoryType.EXPENSE,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    date_from = forms.DateField(
        label=_('From'),
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    date_to = forms.DateField(
        label=_('To'),
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    page = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput()
    )
    category = forms.CharField(
        required=False, 
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.now().date()
        one_month_ago = today - timezone.timedelta(days=30)

        if not self.is_bound:
            self.fields['date_from'].initial = one_month_ago
            self.fields['date_to'].initial = today

    def clean(self):
        cd = self.cleaned_data
        if cd.get('date_from', '') > cd.get('date_to', ''):
            raise forms.ValidationError('\'To\' date can\'t be less than \'From\'')
        return cd