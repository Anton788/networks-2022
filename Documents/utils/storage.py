from rest_framework.exceptions import ParseError
import hashlib
import string
import random
from Documents.utils.storage_api import upload_to_storage, delete_from_storage
from Documents.constants.storage import STORAGE_LINK

from Organizations.models import *

from PIL import Image
from Documents.constants.image_size import MEDIUM, SMALL


def get_random_string(amount=12):
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits  # '0123456789'
    return ''.join(random.choice(letters) for _ in range(amount))


def add_file_to_storage(file, index, is_image: bool = True, name_length=36):
    b_count = bytes(str(index), encoding='utf-8')

    hs_file_str = hashlib.md5(file.read()).hexdigest()  # 32-len str
    hs_count_str = hashlib.md5(b_count).hexdigest()  # 32-len str
    key = hs_file_str + hs_count_str  # 64-len str [unique for unique index]

    file_type = ""

    name_splitting = file.name.rsplit(".", 1)
    if len(name_splitting) >= 2:
        file_type = f".{name_splitting[-1].lower()}"

    if is_image:

        image_formats = [".jpg", ".jpeg", ".png"]
        if file_type not in image_formats:
            raise ParseError(detail=f"Картинка должна быть в одном из форматов: {', '.join(image_formats)}")

        img = Image.open(file)
        img = img.convert("RGB")
        file_type = ".jpg"

        MAX = max(img.size)
        sizes = [MAX, MEDIUM, SMALL]
        sizes.sort(reverse=True)

        links = []
        filename = get_random_string()

        for size in sizes:
            img.thumbnail((size, size))
            storage_file_name = filename + "_" + str(size) + file_type
            img.save(storage_file_name)
            with open(storage_file_name, 'rb',
                      ) as file:
                storage_path = f"{key}/{storage_file_name}"
                upload_to_storage(file, storage_path)
                links.append(f"{STORAGE_LINK}{storage_path}")
            os.remove(storage_file_name)

        links.reverse()
        return links

    else:
        storage_file_name = name_splitting[0][:name_length] + file_type
        storage_path = f"{key}/{storage_file_name}"
        upload_to_storage(file, storage_path)
        return f"{STORAGE_LINK}{storage_path}"


def delete_file_from_storage(link: str):
    """
    Delete file from storage by link
    :param link: link to the file in storage
    :return: None
    """
    file_path = link[len(STORAGE_LINK):]
    delete_from_storage(file_path)


def add_excel_to_storage(file, index, name_length=36):
    b_count = bytes(str(index), encoding='utf-8')

    hs_file_str = hashlib.md5(file.read()).hexdigest()  # 32-len str
    hs_count_str = hashlib.md5(b_count).hexdigest()  # 32-len str
    key = hs_file_str + hs_count_str  # 64-len str [unique for unique index]

    file_type = ".xlsx"

    name_splitting = file.name.rsplit(".", 1)
    if len(name_splitting) >= 2:
        file_type = f".{name_splitting[-1].lower()}"

    storage_file_name = name_splitting[0][:name_length] + file_type

    # print("Key:", key)
    storage_path = f"{key}/{storage_file_name}"
    upload_to_storage(file, storage_path)

    return f"{STORAGE_LINK}{storage_path}"