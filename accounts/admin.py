from django.contrib import admin
from .models import UserBankAccout, UserAddress
# Register your models here.

admin.site.register(UserBankAccout)
admin.site.register(UserAddress)