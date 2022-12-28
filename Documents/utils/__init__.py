from Documents.constants.storage import MAX_FILE_SIZE
from Documents.utils.storage import add_file_to_storage, delete_file_from_storage
from Documents.models import Document
from Users.models import User



def add_file(file, user: User, name: str = None, description: str = ""):

    if file.size > MAX_FILE_SIZE:
        raise ValueError(f"Размер файла не может быть более {MAX_FILE_SIZE // (1024 * 1024)}МБ")

    document = Document.objects.create(
        link="-",
        name=file.name[:get_max_filed_length('name')] if name is None else name[:get_max_filed_length('name')],
        description=description[:get_max_filed_length('description')],
        user=user
    )

    link = add_file_to_storage(file, document.id, is_image=False)
    document.link = link
    document.save()

    return document



def get_max_filed_length(field_name):
    return Document._meta.get_field(field_name).__dict__["max_length"]