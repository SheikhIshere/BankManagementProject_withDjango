from django.db import models
from accounts.models import UserBankAccout
from .constants import TRANSACTION_TYPE

class Transaction(models.Model):
    account = models.ForeignKey(UserBankAccout, related_name='transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    balance_after_transaction = models.DecimalField(decimal_places=2, max_digits=12)
    transaction_type = models.PositiveSmallIntegerField(choices=TRANSACTION_TYPE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    loan_approve = models.BooleanField(default=False)  # Fixed typo from 'load_approve' to 'loan_approve'

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.get_transaction_type_display()} of ${self.amount} for {self.account}"