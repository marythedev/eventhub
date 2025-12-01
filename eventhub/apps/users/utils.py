import os

from api.location_utils import validate_location
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.files.storage import FileSystemStorage
from PIL import Image
from pyuploadcare import Uploadcare

MAX_FILE_SIZE_MB = 5
TARGET_SIZE = (300, 300)
ALLOWED_IMAGE_FORMATS = ['JPEG', 'PNG', 'GIF', 'WEBP']

uploadcare = Uploadcare(public_key=settings.UPLOADCARE['pub_key'], secret_key=settings.UPLOADCARE['secret'])


def anonymous_required(redirect_url='home'):
    """
    Restrict access to views (i.e. login/register) for authenticated users.
        Checks that user is not authenticated in the system.
        Otherwise redirects user to the home page (or provided redirect_url).

    Args:
        redirect_url (str): URL name to redirect authenticated users to.
    """

    return user_passes_test(
        lambda u: not u.is_authenticated,
        login_url=redirect_url,
        redirect_field_name=''
    )


def is_valid_image_format(file):
    """
    Validate if the file is in a supported image format.

    Supported formats:
        JPEG, PNG, GIF, or WEBP

    Args:
        file: File object uploaded by the user.

    Returns:
        bool: True if format is allowed; False otherwise.
    """

    try:
        image = Image.open(file)
        return image.format in ALLOWED_IMAGE_FORMATS
    except Exception:       # pylint: disable=broad-exception-caught
        return False


def crop_to_center(image):
    """
    Crop the center of the image with 1:1 ratio.

    Args:
        image (PIL.Image): The original image.

    Returns:
        PIL.Image: Cropped square image centered within the original.
    """

    try:
        width, height = image.size
        min_side = min(width, height)
        left = (width - min_side) // 2
        top = (height - min_side) // 2
        right = left + min_side
        bottom = top + min_side
        return image.crop((left, top, right, bottom))
    except Exception as e:
        raise ValueError(f"Error cropping image: {e}") from e


def cloud_upload_img(file_path):
    """
    Upload a local image file to Uploadcare cloud storage.

    Args:
        file_path (str): Full local file path to the image.

    Returns:
        url(str): URL by which uploaded image can be accessed.
    """

    try:
        with open(file_path, 'rb') as image_file:
            ucare_file = uploadcare.upload(image_file)
            return f"{settings.CDN_DOMAIN}/{ucare_file.uuid}/"
    except Exception as e:
        raise Exception(f"Failed to upload image to cloud: {e}") from e     # pylint: disable=broad-exception-raised


def cloud_delete_img(url):
    """
    Delete image from Uploadcare cloud storage based on url.

    Arg:
        url (str): Access link to image ( https://cdn.domain/UUID/ ).
    """

    try:
        uuid = url.strip('/').split('/')[-1]
        file = uploadcare.file(uuid)
        file.delete()
    except Exception as e:
        raise Exception(f"Failed to delete image from cloud: {e}") from e   # pylint: disable=broad-exception-raised


def set_avatar(user, file_path):
    """
    Upload an image file to cloud storage and save url in user's profile.

    Args:
        user (Profile): Profile (user) instance whose avatar is being updated.
        file_path (str): Local path to the image file.
    """

    user.avatar = cloud_upload_img(file_path)
    user.save()


def set_default_avatar(user):
    """
    Set the system default avatar for the user.

    Args:
        user (Profile): Profile (user) instance whose avatar is being updated.
    """

    file_path = os.path.join(settings.APP_ROOT, 'static/img/avatar.jpg')
    set_avatar(user, file_path)


def set_custom_avatar(user, file, filename):
    """
    Set a custom avatar provided by the user on user's profile.

    Behavior:
        - Save the file temporarily to disk.
        - Upload it to cloud
        - Assign new avatar to the user.
        - Clean up the local file.

    Args:
        user (Profile): Profile (user) instance whose avatar is being updated.
        file (file-like object): The image file to upload.
        filename (str): Original filename.
    """

    fs = FileSystemStorage()
    file_path = None

    try:
        # save the file and get the full path of it
        filename = fs.save(filename, file)
        file_path = fs.path(filename)

        # upload new avatar to cloud and save to db
        set_avatar(user, file_path)
    finally:
        # cleanup
        if file_path and os.path.exists(file_path):
            os.remove(file_path)


def clean_and_update_location(form, location):
    """
    Validate and normalize location.
    If location is valid, get its latitude and longitude.
    
    Args:
        form: form instance that calls this method.
        location: location string to be validated and normalized.
    
    Returns:
        The normalized location string.
    """

    if location:
        location, lat, lon = validate_location(location)

        # update location on form
        form.data = form.data.copy()
        form.data['location'] = location
        form.cleaned_data['latitude'] = lat
        form.cleaned_data['longitude'] = lon

    return location
