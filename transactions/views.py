from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum
from .models import Transaction
from .forms import DepositForm, WithdrawForm, LoanRequestForm
from .constants import DEPOSIT, WITHDRAWAL, LOAN_PAID, LOAN
from datetime import datetime
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.urls import reverse_lazy
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_transaction_mail(user, amount, subject, template):
    message = render_to_string(template, {
        'user': user,
        'amount': amount,
    })
    send_email = EmailMultiAlternatives(subject, '', to=[user.email])
    send_email.attach_alternative(message, "text/html")
    send_email.send()


class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transaction_form.html'
    model = Transaction
    title = ''
    success_url = reverse_lazy('transaction_report')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        account = getattr(self.request.user, 'account', None)
        if not account:
            messages.error(self.request, "You don't have an account yet.")
            self.success_url = reverse_lazy('home')
        kwargs.update({'account': account})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title,
            'account': getattr(self.request.user, 'account', None)  # Add account to context
        })
        return context

class DepositMoneyView(TransactionCreateMixin):
    form_class = DepositForm
    title = 'Deposit'

    def get_initial(self):
        return {'transaction_type': DEPOSIT}

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = getattr(self.request.user, 'account', None)
        if not account:
            messages.error(self.request, "You don't have an account.")
            return redirect('home')
        
        # Create transaction record
        transaction = form.save(commit=False)
        transaction.account = account
        transaction.balance_after_transaction = account.balance + amount  # Correct balance calculation
        transaction.save()
        
        # Update account balance
        account.balance += amount
        account.save(update_fields=['balance'])
        
        messages.success(self.request, f'${amount} was deposited successfully.')
       
        # this thing is sending mail to the user's email
        send_transaction_mail(self.request.user, amount, 'Diposite Messege', 'mail/deposit_mail.html')
        
        return super().form_valid(form)

class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = 'Withdraw'

    def get_initial(self):
        return {'transaction_type': WITHDRAWAL}

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = getattr(self.request.user, 'account', None)
        if not account:
            messages.error(self.request, "You don't have an account.")
            return redirect('home')
        
        # Create transaction record
        transaction = form.save(commit=False)
        transaction.account = account
        transaction.balance_after_transaction = account.balance - amount  # Correct balance calculation
        transaction.save()
        
        # Update account balance
        account.balance -= amount
        account.save(update_fields=['balance'])
        
        messages.success(self.request, f'${amount} was withdrawn successfully.')

        # this thing is sending mail to the user's email
        send_transaction_mail(self.request.user, amount, 'withdrawal Messege', 'mail/withdrawal_mail.html')
        

        return super().form_valid(form)

class LoanRequestView(TransactionCreateMixin):
    template_name = 'loan_request.html'
    form_class = LoanRequestForm
    title = 'Request For Loan'
    success_url = reverse_lazy('loan_list')
    def get_initial(self):
        return {'transaction_type': LOAN}

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = getattr(self.request.user, 'account', None)
        if not account:
            messages.error(self.request, "You don't have an account.")
            return redirect('home')
        
        current_loan_count = Transaction.objects.filter(
            account=account, transaction_type=LOAN, loan_approve=False
        ).count()
        
        if current_loan_count >= 3:
            form.add_error(None, 'You have crossed your loan limit of 3 requests.')
            return self.form_invalid(form)
        
        # Create loan request (balance not affected until approved)
        transaction = form.save(commit=False)
        transaction.account = account
        transaction.balance_after_transaction = account.balance  # Balance remains same for request
        transaction.save()
        
        messages.success(self.request, f'Loan request worth {amount}$ submitted.')

        # this thing is sending mail to the user's email
        send_transaction_mail(self.request.user, amount, 'Loan Request Messege', 'mail/loan_request_mail.html')
        
        return super().form_valid(form)

class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = 'transaction_report.html'
    model = Transaction
    balance = 0

    def get_queryset(self):
        account = getattr(self.request.user, 'account', None)
        if not account:
            return Transaction.objects.none()
        
        queryset = super().get_queryset().filter(account=account)
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            queryset = queryset.filter(timestamp__gte=start_date, timestamp__lte=end_date)
            self.balance = queryset.aggregate(Sum('amount'))['amount__sum']
        else:
            self.balance = account.balance

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': getattr(self.request.user, 'account', None),
            'balance': self.balance
        })
        return context
    
    

class PayLoanView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(Transaction, id=loan_id)
        
        if not loan.loan_approve:
            messages.error(request, 'Loan not approved yet.')
            return redirect('loan_list')

        account = getattr(request.user, 'account', None)
        if not account:
            messages.error(request, "You don't have an account.")
            return redirect('home')

        if loan.amount <= account.balance:
            account.balance -= loan.amount
            loan.balance_after_transaction = account.balance
            account.save()
            loan.transaction_type = LOAN_PAID
            loan.save()

            # ✅ Send email here
            send_transaction_mail(
                user=request.user,
                amount=loan.amount,
                subject='Loan Payment Successful',
                template='mail/loan_payment_mail.html'
            )

            return redirect('transaction_report')

        messages.error(request, 'Not enough balance.')
        return redirect('loan_list')


class LoanListView(LoginRequiredMixin, ListView):  # Fixed typo in class name
    model = Transaction
    template_name = 'loan_list.html'
    context_object_name = 'loans'

    def get_queryset(self):
        account = getattr(self.request.user, 'account', None)
        if not account:
            return Transaction.objects.none()
        return Transaction.objects.filter(account=account, transaction_type=LOAN)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': getattr(self.request.user, 'account', None)
        })
        return context