from django.views.generic import FormView
from .forms import UserRegistrationForm, UserUpdateForm
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required


class UserRegistrationView(FormView):
    template_name = 'accounts/user_registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('register')

    def form_valid(self, form):
        # Get cleaned form data
        form_data = form.cleaned_data
        print(form_data)
        
        # Save user and log them in
        user = form.save()        
        login(self.request, user)
        
        return super().form_valid(form)

class UserLoginView(LoginView):
    template_name = 'accounts/user_login.html'
    def get_success_url(self):
        return reverse_lazy('home')



def UserLogoutView(request):
    logout(request)
    return redirect('home')



@login_required
def user_profile_view(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, user=request.user, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserUpdateForm(user=request.user, instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})