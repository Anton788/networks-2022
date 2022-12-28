from Organizations.models import Company, Factory
from Products.models import ProductImage, Product, ProductFile, ProductsProcessingFile
from Documents.utils.storage import add_file_to_storage, delete_file_from_storage
from Documents.constants.storage import MAX_FILE_SIZE, MAX_IMAGE_SIZE, MAX_FILE_IN_PROCESSING_SIZE
from Documents.models import Photo
from Users.models import User


def add_image_to_product(image, product: Product, user: User):
    """
    Save image to storage and create ProductImage object

    :param image: open image-file
    :param product: object of Product
    :param description: description of the image
    :return: created ProductImage object
    """
    if image.size > MAX_IMAGE_SIZE:
        raise ValueError(f"Размер фото не может быть более {MAX_IMAGE_SIZE // (1024 * 1024)}МБ")
    photo = Photo.objects.create(
        name=image.name,
        user=user
    )

    links = add_file_to_storage(image, photo.id, is_image=True)
    photo.links = links
    photo.save(update_fields=["links"])

    product_image = ProductImage.objects.create(photo=photo,
                                                product=product)

    return product_image


def delete_product_image(product_image: ProductImage):
    if product_image.link:
        delete_file_from_storage(product_image.link)

    product_image.delete()




# ЭТА ФУНКЦИЯ НИГДЕ НЕ ИСПОЛЬЗУЕТСЯ,
# ПОЭТОМУ ПОКА ЧТО ОНА НЕ ПЕРЕДЕЛАЛАСЬ ЧЕРЕЗ "ДОКУМЕНТЫ" -
# ВОТ КАК БУДЕТ ИСПОЛЬЗОВАТЬСЯ, ТОГДА И ПЕРЕДЕЛАЮ :)
# (А ВООБЩЕ ПРОСТО В views/poducts/AddFileView И БЕЗ НЕЕ НОРМ ОБОШЛОСЬ)

def add_file_to_product(file, product: Product, name: str = None, description: str = ""):
    """
    Save file to storage and create ProductFile object

    :param file: open file for current product
    :param product: object of Product
    :param name: name to this file
    :param description: description of the file
    :return: created ProductFile object
    """

    if file.size > MAX_FILE_SIZE:
        raise ValueError(f"Размер файла не может быть более {MAX_FILE_SIZE // (1024 * 1024)}МБ")

    product_file = ProductFile.objects.create(
        link="-",
        product=product,
        name=file.name[:50] if name is None else name[:50],
        description=description
    )

    link = add_file_to_storage(file, product_file.id, is_image=False)
    product_file.link = link
    product_file.save()

    return product_file


def add_file_to_processing(
        file,
        user,
        company: Company = None,
        factory: Factory = None,
        name: str = None,
        annotation: str = ""
):
    """
    Save file to storage and create ProductFile object

    :param file: open file for current product
    :param company: object of Company
    :param factory: object of Factory
    :param user: object of User
    :param name: name to this file
    :param annotation: description of the file
    :return: created ProductFile object
    """

    if file.size > MAX_FILE_IN_PROCESSING_SIZE:
        raise ValueError(f"Размер файла не может быть более {MAX_FILE_IN_PROCESSING_SIZE // (1024 * 1024)}МБ")

    product_file = ProductsProcessingFile.objects.create(
        link="-",
        user=user,
        name=file.name[:50] if name is None else name[:50],
        annotation=annotation,
    )

    if company:
        product_file.company = company

    if factory:
        product_file.factory = factory

    link = add_file_to_storage(file, product_file.id, is_image=False)
    product_file.link = link
    product_file.save()

    return product_file


def delete_product_file(product_file: ProductFile):
    if product_file.link:
        delete_file_from_storage(product_file.link)

    product_file.delete()
