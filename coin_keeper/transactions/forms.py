from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
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

        