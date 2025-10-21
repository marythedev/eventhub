import io
from PIL import Image
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required

from .utils import *
from .forms import RegisterValidator, LoginValidator, ProfileValidator, SecurityValidator
from .models import Profile


def register(request):
    """
    Handle user registration.

    GET:
        - Serve register form page.

    POST:
        - Register user with fullname, email, password and confirm password.
        - Return register form with errors or redirect to home on success.
    """
    
    if request.method == "POST":
        form = RegisterValidator(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data['full_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            avatar = ""

            # Create new user profile
            Profile.objects.create_user(
                full_name=full_name,
                email=email,
                password=password,
                avatar=avatar
            )

            # Authenticate and log in the new user
            user = authenticate(request, email=email, password=password)
            if user is not None:
                set_default_avatar(user)
                auth_login(request, user)
                return redirect('core:home')
            else:
                return redirect('users:login')
    else:
        form = RegisterValidator()
        
    return render(request, 'users/register.html', {'form': form})


def login(request):
    """
    Handle user login.

    GET:
        - Serve login form page.

    POST:
        - Authenticate user with email and password.
        - Return login form with errors or redirect to home on success.
    """
    
    if request.method == "POST":
        form = LoginValidator(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            auth_login(request, user)
            return redirect('core:home')
    else:
        form = LoginValidator()

    return render(request, 'users/login.html', {'form': form})


@login_required
def account(request):
    """
    Display the account page and handle basic profile updates.

    GET:
        - Render the account page with user information.

    Returns: Rendered account page.
    """
    return render(request, 'users/account.html')


@login_required
def avatar_upload(request):
    """Handles POST requests for avatar validation and upload."""
    
    """
    Handle avatar validation, preprocessing and upload.
    
    GET:
        - Redirects to account page (does nothing).
    
    POST:
        - Validates and processes (crops & resizes) submitted file.
        - Deletes previous avatar from cloud storage.
        - Uploads new avatar to cloud storage and stores access link in user's instance.

    Validations:
        - Must be JPG, PNG, GIF or WEBP format.
        - Must be smaller than 5MB.

    Returns: Rendered account page (with error messages if any).
    """
    
    MAX_FILE_SIZE_MB = 5
    TARGET_SIZE = (300, 300)
    avatar_error = None
    user = request.user
    
    if request.method == "POST":
        uploaded_file = request.FILES['imageFile']
        
        if not uploaded_file:
            avatar_error = "Error uploading the file."
        
        elif not is_valid_image_format(uploaded_file):
            avatar_error = "Unsupported image format. Please upload a JPG, PNG, GIF or WEBP file."
            
        # check file size
        elif uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
            avatar_error = "Image file is too large (max 5MB)."
            
        else:
            try:
                image = Image.open(uploaded_file)
                image_format = image.format
                
                # process new image
                image = crop_to_center(image)          # crop image 1:1 in the center
                image = image.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
            
                # saves the image so it can be read or uploaded like a real file
                buffer = io.BytesIO()
                image.save(buffer, format=image_format)
                buffer.seek(0)
                
                # delete previous avatar from cloud
                cloud_delete_img(user.avatar)
            
                # set new avatar
                set_custom_avatar(user, buffer, uploaded_file.name)
                
            except Exception:
                avatar_error = "Something went wrong."

        return render(request, 'users/account.html', {'avatar_error': avatar_error})
    return redirect('users:account')


@login_required
def avatar_delete(request):
    """
    Handle deletion of the user's current avatar.
    
    GET:
        - Redirects to account page (does nothing).

    POST:
        - Deletes avatar from cloud storage.
        - Sets default avatar for the user.

    Returns: Rendered account page (with error messages if any).
    """
    
    if request.method == "POST":
        user = request.user
        avatar_error = None
                
        try:
            # delete user's avatar from could
            cloud_delete_img(user.avatar)
            
            # set default avatar
            set_default_avatar(user)
            
        except Exception:
            avatar_error = "Failed to delete an avatar."
            
        return render(request, 'users/account.html', {'avatar_error': avatar_error})
    return redirect('users:account')


@login_required
def profile_update(request):
    """Update profile information for the user (name, email, phone, location)."""
    if request.method == "POST":
        user = request.user
        form = ProfileValidator(request.POST, user=user)
        if form.is_valid():
            full_name = form.cleaned_data['full_name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            location = form.cleaned_data['location']
            
            user.full_name = full_name
            user.email = email
            user.phone = phone
            user.location = location
            user.save()
        return render(request, 'users/account.html', {'form': form})
    return redirect('users:account')


@login_required
def security_update(request):
    """Handle user password update."""
    if request.method == "POST":
        user = request.user
        form = SecurityValidator(request.POST, user=user)
        success_password_update = None
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            success_password_update = "Your password has been updated."
        return render(request, 'users/account.html', {'form': form, 'success_password_update': success_password_update})
    return redirect('users:account')


@login_required
def logout(request):
    """Terminate current user session and redirect to the homepage."""
    auth_logout(request)
    return redirect('core:home')
