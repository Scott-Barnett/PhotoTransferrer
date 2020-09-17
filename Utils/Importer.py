import shutil
import os
import datetime
from Utils import Exif


def get_dir_name(date_shot: datetime.datetime, description: str = "") -> str:
    """Obtains the name of a directory based on the date shot and the description (appended with -<description>)

    :param date_shot: The date and time the photo was shot (only date is required)
    :param description: Description to go into the folder name
    :return: Format is yyyy_mm_dd-description or yyyy_mm_dd if description is unfilled
    """
    folder_name = f"{date_shot.year}_{date_shot.month}_{date_shot.day}"
    # Only append a "-" if the description is non-empty
    if description != "":
        folder_name += f"-{description}"
    return folder_name


def get_image_date_name(date_shot: datetime.datetime):
    """Converts a datetime.datetime object into a string of the yyyymmdd_hhmmss format

    :param date_shot: Date the photo was shot
    :return: Valid file name for the image and directory
    """
    return f"{date_shot.year}{date_shot.month}{date_shot.day}_{date_shot.hour}{date_shot.minute}{date_shot.second}"


def ensure_unique(img_name: str, img_extension: str, dest_dir: str) -> str:
    """Ensures the image name is unique to avoid overwriting another image

    :param img_name: Initial name of the image (without the extension) to check if it's unique
    :param img_extension: The extension of the image (in order to complete the full image name)
    :param dest_dir: The location the image will be copied to
    :return: A name for the image that is verified to be unique, possibly by appending a number to it
    """
    full_path = f"{os.path.join(dest_dir, img_name)}"
    if os.path.isfile(f"{full_path}.{img_extension}"):
        counter = 1
        while os.path.isfile(f"{full_path}_{counter}.{img_extension}"):
            counter += 1
        return f"{img_name}_{counter}"
    else:
        return img_name


def import_images(source_dir: str, dest_dir: str, files: list,
                  folder_description: str = "", rename_to_date: bool = False) -> bool:
    """Imports images from the source dir to the destination dir

    :param source_dir: Dir that contains the photos
    :param dest_dir: Dir that will contain the photos
    :param files: Contains the list of files to be imported
    :param folder_description: Contains a tag to append after the folder date
    :param rename_to_date: Determines whether to rename the files or not
    :return: Success or failure of the operation
    """
    for file in files:
        src_path = os.path.join(source_dir, file)
        # Attempt to get the date a photo was shot and it's extension. Even if we are not renaming based on date we
        # need it to place it in the appropriately dated folder
        try:
            date_shot = Exif.get_image_taken_date(src_path)
            extension = Exif.get_image_data_type(src_path)
        except Exif.DateNotFoundException:
            print(f"A date was not found in the file {src_path}, therefore it has not been transferred")
            continue
        except Exif.UnidentifiedImageError:
            print(f"The specified file, {src_path}, is not a valid picture file. It has not been transferred")
            continue
        # This error is not expected during normal use, therefore halt the operation of the program
        except FileNotFoundError:
            print(f"An error has occurred (the specified file {src_path} does not exist). Please try again")
            return False

        # File is valid
        # Get folder name that will contain the photo (of the format date-description)
        folder_name = os.path.join(dest_dir, get_dir_name(date_shot, folder_description))
        # Create the folder if it doesn't already exist
        if not os.path.isdir(folder_name):
            os.makedirs(folder_name)
        if rename_to_date:
            # Generate the new image name using the date the photo was shot
            new_name = get_image_date_name(date_shot)
        else:
            # We are not renaming the photo so find the name without the image extension
            decimal_position = file.find('.')
            new_name = file[:decimal_position]
        # Ensure the name is unique in the receiving folder
        new_name = ensure_unique(new_name, extension, folder_name)
        # new_name is now unique, add the file extension to it
        new_name += f".{extension}"
        new_path = os.path.join(folder_name, new_name)
        # Use copy2 as it also copies metadata unlike copy
        shutil.copy2(src_path, new_path)
    return True
