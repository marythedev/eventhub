import os
import requests
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
from pyuploadcare import Uploadcare
from PIL import Image


uploadcare = Uploadcare(public_key=settings.UPLOADCARE['pub_key'], secret_key=settings.UPLOADCARE['secret'])


def is_valid_image_format(file):
    """
    Checks that the file is in a supported image format.

    Returns:
        True for JPEG, PNG, GIF, or WEBP;
        False for other formats.
    """
    ALLOWED_IMAGE_FORMATS = ['JPEG', 'PNG', 'GIF', 'WEBP']
    try:
        image = Image.open(file)
        return image.format in ALLOWED_IMAGE_FORMATS
    except Exception:
        return False

def crop_to_center(image):
    """
    Crop the center of the image with 1:1 ratio.
    
    Args: 
        image (PIL.Image) - the original image.
    Returns: PIL.Image - cropped square image centered within the original.
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
        raise ValueError(f"Error cropping image: {e}")


def cloud_upload_img(file_path):   
    """
    Upload a local image file to Uploadcare cloud storage.

    Args: 
        file_path (str) - the full local file path to the image.
    Returns: uploaded file object containing UUID and metadata.
    """
    
    try:
        with open(file_path, 'rb') as image_file:
            return uploadcare.upload(image_file)
    except Exception as e:
        raise Exception(f"Failed to upload image to cloud: {e}")


def cloud_delete_img(url):   
    """
    Delete image from Uploadcare cloud storage based on url.
    
    Arg: 
        url (str): access link to image ( https://cdn.domain/UUID/ ).
    Returns: None
    """
    
    try:
        uuid = url.strip('/').split('/')[-1]
        file = uploadcare.file(uuid)
        file.delete()
    except Exception as e:
        raise Exception(f"Failed to delete image from cloud: {e}")
  

def set_avatar(user, file_path):
    """
    Upload an image file to cloud storage and assign access link to user.

    Args:
        user (Profile): Profile (user) instance whose avatar is being updated.
        file_path (str): Local path to the image file.
    Returns: None
    """
    ucare_file = cloud_upload_img(file_path)
    user.avatar = f"{settings.CDN_DOMAIN}/{ucare_file.uuid}/"
    user.save()


def set_default_avatar(user):
    """
    Set the default avatar for the user.

    Args: 
        user (Profile): Profile (user) instance whose avatar is being updated.
    Returns: None
    """
    file_path = os.path.join(settings.APP_ROOT, 'static/img/avatar.jpg')
    set_avatar(user, file_path)


def set_custom_avatar(user, file, filename):
    """
    Save the file temporarily to disk, upload it to cloud, 
    assign new avatar to the user, and clean up the local file.

    Args:
        user (Profile): Profile (user) instance whose avatar is being updated.
        file (file-like object): The image file to upload.
        filename (str): Original filename.
    Returns: None
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

def validate_location(location):
    """
    Helper function that validates location.
    
    Args:
        location (str): Location to be validated.
    
    Raises:
        ValidationError: when location is not valid (not found) or something is wrong with the fetch.
        
    Returns:
        location (str): Location after the validation (either validated or incorrect with raised error).
    """
    try:
        # fetch openstreetmap to check if location exists
        response = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={'q': location, 'format': 'json'},
            headers={
                'User-Agent': f'Eventhub/{os.getenv("APP_VERSION", "1.0")}',
                'Accept-Language': 'en'
            }
        )
        data = response.json()
        
        print(data)
        if len(data) == 0:
            raise ValidationError("Location not found. Please enter a valid place.")

        # transform location to full display name for consistent location format
        location = data[0]['display_name']
        
    except ValidationError:
        raise
    except Exception:
        raise ValidationError("Failed to validate location. Try again later.")
    
    return location

