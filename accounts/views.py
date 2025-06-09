from django.views.generic import FormView
from .forms import UserRegistrationForm, UserUpdateForm, LoginForm
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages


class UserRegistrationView(FormView):
    template_name = 'accounts/user_registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Registration successful. You are now logged in.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Registration failed. Please correct the errors below.")
        return super().form_invalid(form)


class UserLoginView(LoginView):
    template_name = 'accounts/user_login.html'
    authentication_form = LoginForm

    def get_success_url(self):
        messages.success(self.request, "Login successful. Welcome back!")
        return reverse_lazy('home')

    def form_invalid(self, form):
        messages.error(self.request, "Login failed. Please check your credentials.")
        return super().form_invalid(form)


def UserLogoutView(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


@login_required
def user_profile_view(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, user=request.user, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = UserUpdateForm(user=request.user, instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})
