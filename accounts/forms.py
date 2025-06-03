from django.contrib.auth.forms import UserCreationForm
from .constans import GENDER_TYPE, ACCOUNT_TYPE
from django import forms
from django.contrib.auth.models import User
from .models import UserBankAccout, UserAddress


class UserRegistrationForm(UserCreationForm):    
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices= GENDER_TYPE)
    account_type = forms.ChoiceField( choices= ACCOUNT_TYPE)
    street_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length= 100)
    postal_code = forms.IntegerField()
    country = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email' ,'birth_date', 'account_type', 'gender', 'postal_code' ,'city', 'country', 'street_address']

    # forms.save()
    def save(self, commit =True):
        our_user = super().save(commit=False) # this mean i am not gonna save data base right now
        if commit == True:
            our_user.save() # saving data in user model
            account_type = self.cleaned_data.get('account_type')
            gender = self.cleaned_data.get('gender')
            postal_code = self.cleaned_data.get('postal_code')
            country = self.cleaned_data.get('country')
            birth_date = self.cleaned_data.get('birth_date')
            city = self.cleaned_data.get('city')
            street_address = self.cleaned_data.get('street_address')
            
            UserAddress.objects.create(
                user = our_user,                
                postal_code = postal_code,
                country = country,
                city = city,
                street_address = street_address,
            )

            UserBankAccout.objects.create(
                user = our_user,
                account_type = account_type,
                gender = gender,
                birth_date = birth_date,
                account_no = 10000 + our_user.id
            )
        return our_user

    # def __init__(self, *args, **kwargs):
        # super().__init__(*args, **kwargs)      
            #   
        # for field in self.fields:
            # self.fields[field].widget.attrs.update({
                # 'class' : (
                    # 'class="appearance-none block w-full bg-gray-200 '
                    # 'text-gray-700 border border-gray-200 rounded '
                    # 'py-3 px-4 leading-tight focus:outline-none '
                    # 'focus:bg-white focus:border-gray-500"'
# 
                # )
# 
            # }) 
            # using custom tailwind file so i will be not using this but i cause this to show styling from the backend


class UserUpdateForm(forms.ModelForm):
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=GENDER_TYPE)
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    street_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    postal_code = forms.IntegerField()
    country = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email',
                  'birth_date', 'account_type', 'gender',
                  'postal_code', 'city', 'country', 'street_address']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400'
        
        if user:
            self.fields['username'].initial = user.username
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email

            # Prefill UserAddress fields
            try:
                user_address = UserAddress.objects.get(user=user)
                self.fields['street_address'].initial = user_address.street_address
                self.fields['city'].initial = user_address.city
                self.fields['postal_code'].initial = user_address.postal_code
                self.fields['country'].initial = user_address.country
            except UserAddress.DoesNotExist:
                pass
            
            # Prefill UserBankAccout fields
            try:
                user_account = UserBankAccout.objects.get(user=user)
                self.fields['account_type'].initial = user_account.account_type
                self.fields['gender'].initial = user_account.gender
                self.fields['birth_date'].initial = user_account.birth_date
            except UserBankAccout.DoesNotExist:
                pass

    def save(self, commit=True):
        user = super().save(commit=commit)
        
        # Save or update UserAddress
        try:
            user_address = UserAddress.objects.get(user=user)
        except UserAddress.DoesNotExist:
            user_address = UserAddress(user=user)
        
        user_address.street_address = self.cleaned_data['street_address']
        user_address.city = self.cleaned_data['city']
        user_address.postal_code = self.cleaned_data['postal_code']
        user_address.country = self.cleaned_data['country']
        user_address.save()

        # Save or update UserBankAccout
        try:
            user_account = UserBankAccout.objects.get(user=user)
        except UserBankAccout.DoesNotExist:
            user_account = UserBankAccout(user=user, account_no=10000 + user.id)
        
        user_account.account_type = self.cleaned_data['account_type']
        user_account.gender = self.cleaned_data['gender']
        user_account.birth_date = self.cleaned_data['birth_date']
        user_account.save()

        return user
