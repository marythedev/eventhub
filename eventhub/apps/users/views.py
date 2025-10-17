from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .forms import RegisterFormValidator, LoginFormValidator
from .models import Profile
from django.contrib.auth.decorators import login_required

def register(request):
    """
    Handle user registration.

    GET:
        - Serve register form page.

    POST:
        - Register user with fullname, email, password and confirm password.
        - Return register form with errors or redirect to home on success.
    """
    
    error_message = None

    if request.method == "POST":
        form = RegisterFormValidator(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data['full_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Create new user profile
            Profile.objects.create_user(
                full_name=full_name,
                email=email,
                password=password
            )

            # Authenticate and log in the new user
            user = authenticate(request, email=email, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('/login')        #TODO: redirect to home
        else:
            # Capture the first form error only
            error_message = list(form.errors.values())[0][0]
    else:
            form = RegisterFormValidator()
    return render(request, 'users/register.html', {'form': form, 'error_message': error_message})

def login(request):
    """
    Handle user login.

    GET:
        - Serve login form page.

    POST:
        - Authenticate user with email and password.
        - Return login form with errors or redirect to home on success.
    """
    
    error_message = None

    if request.method == "POST":
        form = LoginFormValidator(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            auth_login(request, user)
            return redirect('/register')        #TODO: redirect to home
        else:
            # Capture the first form error only
            error_message = list(form.errors.values())[0][0]
    else:
        form = LoginFormValidator()

    return render(request, 'users/login.html', {'form': form, 'error_message': error_message})

@login_required
def logout(request):
    auth_logout(request)
    return redirect('/login')    #TODO: redirect to home
