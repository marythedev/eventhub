import io

from api.stripe_utils import get_stripe_account
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from events.models import Event, Order
from PIL import Image

from .forms import (LoginValidator, ProfileValidator, RegisterValidator,
                    SecurityValidator)
from .models import Profile, StripeAccount
from .utils import (MAX_FILE_SIZE_MB, TARGET_SIZE, anonymous_required,
                    cloud_delete_img, crop_to_center, is_valid_image_format,
                    set_custom_avatar, set_default_avatar)

EVENT_PREVIEW_NUM = 2
ORDER_PREVIEW_NUM = 2

@anonymous_required()
def register(request):
    """
    Handle user registration.

    GET:
        - Serve register form page.

    POST:
        Validate registration input.

        On Validation success:
            - Register user with fullname, email, password and confirm password.
            - Create Stripe account, set default avatar, authenticate, and log the user in.
            - Redirect to home or the flow they have browsed before.

        On Validation fail:
            - Return register form with errors.
    """

    next_url =  request.POST.get('next', '') or request.GET.get('next', '')
    if next_url in [None, "", "None"]:
        next_url = None

    if request.method == "POST":
        form = RegisterValidator(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data['full_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            avatar = ""

            # Create new user profile
            user = Profile.objects.create_user(
                full_name=full_name,
                email=email,
                password=password,
                avatar=avatar
            )
            StripeAccount.objects.create(account_owner=user)

            # Authenticate and log in the new user
            user = authenticate(request, email=email, password=password)
            if user is not None:
                set_default_avatar(user)
                auth_login(request, user)
                return redirect(next_url or 'home')
            return redirect('users:login')
    else:
        form = RegisterValidator()

    return render(request, 'users/register.html', {'form': form, 'next': next_url})


@anonymous_required()
def login(request):
    """
    Handle user login.

    GET:
        - Serve login form page.

    POST:
        Validate login input.

        On Validation success:
            - Authenticate user with email and password.
            - Set session expiry.
            - Redirect to home or the flow they have browsed before.

        On Validation fail:
            - Return login form with errors.
    """

    next_url =  request.POST.get('next', '') or request.GET.get('next', '')
    if next_url in [None, "", "None"]:
        next_url = None

    if request.method == "POST":
        form = LoginValidator(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            auth_login(request, user)

            remember_me = request.POST.get('remember_me')
            if remember_me:
                request.session.set_expiry(int(settings.SESSION_EXPIRY_TIME))
            else:
                request.session.set_expiry(0)

            return redirect(next_url or 'home')
    else:
        next_url = request.GET.get('next')
        form = LoginValidator()

    return render(request, 'users/login.html', {'form': form, 'next': next_url})


@login_required
def account(request):
    """
    Display the account page.

    Shows:
        - Basic profile information to handle basic profile update.
        - Security section to handle password update.
        - Stripe account status.
        - Recent events created by the user (previews EVENT_PREVIEW_NUM events).
        - Recent orders made by the user (previews ORDER_PREVIEW_NUM orders).

    GET:
        - Render the account page with user information.

    Returns: Rendered account page.
    """

    stripe_account = get_stripe_account(request.user)

    # previews only EVENT_PREVIEW_NUM events, rest user can view in events dedicated page
    user_events = Event.objects.filter(organizer=request.user).order_by('date')
    events_count = user_events.count()
    preview_events = user_events[:EVENT_PREVIEW_NUM]
    unpreview_events_count = events_count - EVENT_PREVIEW_NUM

    # previews only ORDER_PREVIEW_NUM events, rest user can view in orders dedicated page
    user_orders = Order.objects.filter(acquirer=request.user).order_by('-date')
    order_count = user_orders.count()
    preview_orders = user_orders[:ORDER_PREVIEW_NUM]
    unpreview_order_count = order_count - ORDER_PREVIEW_NUM

    return render(request, 'users/account.html', {
        'stripe_account': stripe_account,
        'events': preview_events,
        'events_more': unpreview_events_count,
        'orders': preview_orders,
        'orders_more': unpreview_order_count
    })


@login_required
def avatar_upload(request):
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

            except Exception:       # pylint: disable=broad-exception-caught
                avatar_error = "Something went wrong."

        return render(request, 'users/account.html', {'avatar_error': avatar_error})
    return redirect('users:account')


@login_required
def avatar_delete(request):
    """
    Handle current user's avatar deletion.

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

        except Exception:       # pylint: disable=broad-exception-caught
            avatar_error = "Failed to delete an avatar."

        return render(request, 'users/account.html', {'avatar_error': avatar_error})
    return redirect('users:account')


@login_required
def profile_update(request):
    """
    Update profile information for the user (name, email, phone, location).

    POST:
        Validate profile information input.

        On success:
            - Updates profile information.
            - Redirect to account page.

        On fail:
            - Return profile information form on account page with errors.
    """

    if request.method == "POST":
        user = request.user
        form = ProfileValidator(request.POST, user=user)

        if form.is_valid():
            user.full_name = form.cleaned_data['full_name']
            user.email = form.cleaned_data['email']
            user.phone = form.cleaned_data['phone']
            user.location = form.cleaned_data['location']
            user.location_lat = form.cleaned_data.get('latitude', None)
            user.location_lon = form.cleaned_data.get('longitude', None)
            user.save()

        return render(request, 'users/account.html', {'form': form})
    return redirect('users:account')


@login_required
def security_update(request):
    """
    Handle user password update.

    POST:
        Validate security information (passwords) input.

        On success:
            - Updates security (password) information.
            - Redirect to account page.

        On fail:
            - Return security information form on account page with errors.
    """

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
    return redirect('home')
