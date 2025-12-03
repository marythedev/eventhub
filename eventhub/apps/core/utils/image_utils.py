import io
import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from PIL import Image
from pyuploadcare import Uploadcare

uploadcare = Uploadcare(
    public_key=settings.UPLOADCARE['pub_key'],
    secret_key=settings.UPLOADCARE['secret']
)

def _resize_image(img, max_dimension):
    """Resize image so that its largest side no more than max_dimension."""
    width, height = img.size

    # no resizing needed
    if max(width, height) <= max_dimension:
        return img

    scale = max_dimension / max(width, height)
    new_size = (int(width * scale), int(height * scale))
    return img.resize(new_size, Image.LANCZOS)

def _optimize_img_to_webp(img, max_bytes):
    """
    Compress Pillow Image to Webp under max_bytes size with highest possible quality.
    Quality range: 50-95
    Default quality: 75
    
    Args:
        img (Pillow image): Image to compress.
        max_bytes (int): Maximum compressed image size in bytes.

    Returns: Compressed Webp image buffer.
    """

    # finding the optimal quality
    low, high = 50, 95
    best_buffer = None

    while low <= high:
        q = (low + high) // 2
        buffer = io.BytesIO()
        img.save(buffer, format="WEBP", quality=q)
        size = buffer.tell()

        if size <= max_bytes:
            best_buffer = buffer
            low = q + 1
        else:
            high = q - 1

    # couldn't meet the size limit, compresses at default quality of 75
    if best_buffer is None:
        buffer = io.BytesIO()
        img.save(buffer, format="WEBP", quality=75)
        best_buffer = buffer

    return best_buffer


def is_valid_image_format(file):
    """
    Validate if the file is in a supported image format.

    Supported formats: JPEG, PNG, WEBP

    Args:
        file: File object uploaded by the user.

    Returns:
        bool: True if format is allowed; False otherwise.
    """

    try:
        image = Image.open(file)
        return image.format in settings.SUPPORTED_IMAGE_FORMATS
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


def compress_image(
    file,
    max_size_kb=settings.EVENT_IMAGE_SIZE_KB,
    max_dimension=settings.EVENT_IMAGE_DIMENSION
):
    """
    Compress an image to be under max_size_kb and max_dimension.

    Args:
        file (file object): Original image file.
        max_size_kb (int): Maximum compressed file size in KB.
        max_dimension (int): Maximum width or height for the image in pixels.
    
    Returns:
        Original image file, if original image is already under the specified size limit.
        Otherwise, returns compressed image file in WebP format, with the original file name.
    """

    compressed_img = None
    max_bytes = max_size_kb * 1024

    img = Image.open(file)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # check if image is already in the optimal size
    if file.size <= max_bytes:
        file.seek(0)
        compressed_img = ContentFile(file.read(), name=file.name)

    # compression is needed
    else:
        img = _resize_image(img, max_dimension)
        compressed_buffer = _optimize_img_to_webp(img, max_bytes)
        compressed_img = ContentFile(compressed_buffer.getvalue(), name=file.name)

    return compressed_img


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
    Delete image from Uploadcare cloud storage if image url exists.

    Arg:
        url (str): Access link to image ( https://cdn.domain/UUID/ ).
    """

    if url:
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
