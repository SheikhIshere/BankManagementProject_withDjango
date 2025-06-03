from django import forms
from .models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_type']
    
    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account', None)
        super(TransactionForm, self).__init__(*args, **kwargs)  # Fixed super() call
        self.fields['transaction_type'].disabled = True  # This field will be disabled
        self.fields['transaction_type'].widget = forms.HiddenInput()  # This will remain hidden
    
    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super(TransactionForm, self).save(commit)
        
        
class DepositForm(TransactionForm):  # Fixed class name (spelling) and inheritance
    def clean_amount(self):
        min_deposit_amount = 100  # Fixed spelling
        amount = self.cleaned_data.get('amount')
        if amount < min_deposit_amount:
            raise forms.ValidationError(
                f'You need to deposit at least {min_deposit_amount}$'  # Fixed spelling
            )
        return amount


class WithdrawForm(TransactionForm):
    def clean_amount(self):
        account = self.account
        min_withdraw_amount = 500
        max_withdraw_amount = 20000
        balance = account.balance
        amount = self.cleaned_data.get('amount')
        
        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at least {min_withdraw_amount}$'
            )
        if amount > max_withdraw_amount:
            raise forms.ValidationError(
                f'You cannot withdraw more than {max_withdraw_amount}$'  # Fixed "then" to "than"
            )
        if amount > balance:
            raise forms.ValidationError(
                f'You have {balance}$ in your account. '
                'You cannot withdraw more than your account balance'  # Fixed concatenation
            )
        return amount


class LoanRequestForm(TransactionForm):  # Fixed class name (spelling)
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        # You might want to add loan-specific validation here
        return amount