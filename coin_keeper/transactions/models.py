from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Category(models.Model):
    class CategoryType(models.TextChoices):
        INCOME = 'IN', _('Income')
        EXPENSE = 'EX', _('Expense')
    
    name = models.CharField(
        _('Name'),
        max_length=50,
    )
    type = models.CharField(
        _('Type'),
        max_length=2,
        choices=CategoryType.choices,
        default=CategoryType.EXPENSE
    )
    # If user is null, this is default category (for all users)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='categories',
        verbose_name=_('User'),
        null=True,
        blank=True,
    )
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        indexes = [
            models.Index(fields=['type']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['name', 'user', 'type'], name="unique_category_per_user_and_type")
        ]

    def __str__(self):
        return self.name


class Transaction(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name=_('User')
    )
    amount = models.DecimalField(
        _('Amount'),
        max_digits=10,
        decimal_places=2
    )
    description = models.CharField(
        _('Description'),
        max_length=255,
        blank=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name=_('Category'),
        null=True,
        blank=True
    )
    date = models.DateTimeField(
        _('Date'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')
        indexes = [
            models.Index(fields=['user', 'date']),
        ]

    def __str__(self):
        return f"{self.user}: {self.amount} ({self.date.date()})"