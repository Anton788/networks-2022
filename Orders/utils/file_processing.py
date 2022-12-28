from Orders.models import ProductRequest, ProductRequestImage, ProductRequestFile
from Documents.utils.storage import add_file_to_storage, delete_file_from_storage
from Documents.constants.storage import MAX_FILE_SIZE, MAX_IMAGE_SIZE


def add_image_to_request(image, request: ProductRequest, description: str = ""):
    """
    Save image to storage and create ProductRequestImage object

    :param image: open image-file
    :param request: object of ProductRequest
    :param description: description of the image
    :return: created ProductRequestImage object
    """
    if image.size > MAX_IMAGE_SIZE:
        raise ValueError(f"Размер фото не может быть более {MAX_IMAGE_SIZE // (1024 * 1024)}МБ")
    product_request = ProductRequestImage.objects.create(
        link="-",
        request=request,
        description=description
    )

    link = add_file_to_storage(image, product_request.id, is_image=True)
    product_request.link = link
    product_request.save()

    return product_request


def delete_request_image(product_request: ProductRequestImage):
    if product_request.link:
        delete_file_from_storage(product_request.link)

    product_request.delete()


def add_file_to_request(file, request: ProductRequest, name: str = None, description: str = ""):
    """
    Save file to storage and create ProductFile object

    :param file: open file for current product
    :param request: object of ProductRequest
    :param name: name to this file
    :param description: description of the file
    :return: created ProductRequestFile object
    """

    if file.size > MAX_FILE_SIZE:
        raise ValueError(f"Размер файла не может быть более {MAX_FILE_SIZE // (1024 * 1024)}МБ")

    request_file = ProductRequestFile.objects.create(
        link="-",
        request=request,
        name=file.name[:50] if name is None else name[:50],
        description=description
    )

    link = add_file_to_storage(file, request_file.id, is_image=False)
    request_file.link = link
    request_file.save()

    return request_file


def delete_request_file(request_file: ProductRequestFile):
    if request_file.link:
        delete_file_from_storage(request_file.link)

    request_file.delete()
