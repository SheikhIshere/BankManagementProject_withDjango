from django.db import models
from django.contrib.auth.models import User
from .constans import ACCOUNT_TYPE, GENDER_TYPE

# django gives dev a built-in user facilitys
class UserBankAccout(models.Model):
    user = models.OneToOneField(User, related_name='account', on_delete= models.CASCADE)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE)
    #account will be uniq
    account_no = models.IntegerField(unique=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices= GENDER_TYPE, default= 'Male')
    initial_deposite_date = models.DateField(auto_now= True)
    balance = models.DecimalField(default=0, max_digits=12, decimal_places=2)
    # maximum money will be 12 digit and decimla value will be till second

    def __str__(self):
        return str(self.account_no)

class UserAddress(models.Model):
    user = models.OneToOneField(User, related_name='address', on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length= 100)
    postal_code = models.IntegerField()
    country = models.CharField(max_length=100)

    def __str__(self):
        return str(self.user.email)

