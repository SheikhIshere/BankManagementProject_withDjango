from django.urls import path
from .views import DepositMoneyView, WithdrawMoneyView, LoanRequestView, PayLoanView, TransactionReportView, LoanListView

urlpatterns = [
    path('deposit/', DepositMoneyView.as_view(), name='deposit'),
    path('withdraw/', WithdrawMoneyView.as_view(), name='withdraw'),
    path('loan-request/', LoanRequestView.as_view(), name='loan_request'),
    path('loan-list/', LoanListView.as_view(), name='loan_list'),
    path('pay-loan/<int:loan_id>/', PayLoanView.as_view(), name='pay_loan'),
    path('transaction-report/', TransactionReportView.as_view(), name='transaction_report'),
]
