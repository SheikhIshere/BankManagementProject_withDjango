from django.contrib import admin
from .models import Transaction
from .views import send_transaction_mail



@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['account', 'amount', 'balance_after_transaction', 'transaction_type', 'loan_approve']
    
    def save_model(self, request, obj, form, change):
        obj.account.balance += obj.amount
        obj.balance_after_transaction = obj.account.balance
        obj.account.save()

        # Send email to the actual account owner, not the admin
        send_transaction_mail(
            user=obj.account.user,  # Corrected
            amount=obj.amount,
            subject='Loan Approved Message',
            template='mail/loan_approved_mail.html'
        )
        
        super().save_model(request, obj, form, change)
