from PIL import Image, UnidentifiedImageError
import datetime
import os


class DateNotFoundException(Exception):
    """The EXIF data for the image contains no date shot"""
    def __init__(self):
        super()


def get_image_taken_date(image_path: str) -> datetime.datetime:
    """Get the date taken according to the EXIF data

    :param image_path: Path to the image file
    :return: Date and time the image was taken
    :raises FileNotFoundError: The image file specified was not found
    :raises UnidentifiedImageError: The image file specified was not in a supported format
    :raises DateNotFoundException: The exif data for the image contains no date
    """
    if not os.path.isfile(image_path):
        raise FileNotFoundError
    with Image.open(image_path) as img:
        try:
            # Attempt to get the date taken from the exif data (36867 is the key for date shot)
            str_datetime = img.getexif()[36867]
        except KeyError as exc:
            # The date does not exist. Convert the key not found error into a more readable DateNotFoundException
            raise DateNotFoundException from exc
    # The date exists. Parse it into a datetime.datetime object
    datetime_shot = datetime.datetime.strptime(str_datetime, "%Y:%m:%d %H:%M:%S")
    return datetime_shot


def get_image_data_type(image_path: str) -> str:
    """Obtain the image data type (and therefore extension)

    :param image_path: Path to the image file
    :return: File extension, as recognised from the image by the Python Imaging Library
    """
    with Image.open(image_path) as img:
        img_datatype = img.format
    return img_datatype
