from django.db import models
from django.core.exceptions import ValidationError
import Products.constants.products_file_check_status as PRODUCTS_FILE_CHECK_STATUS
import Products.constants.product_ratings as PRODUCT_RATINGS
import Products.constants.product_condition as PRODUCT_CONDITION
import Products.constants.product_available as PRODUCT_AVAILABLE


PRODUCTS_FILE_CHECK_STATUS_CHOICE = [
    (PRODUCTS_FILE_CHECK_STATUS.IN_PROGRESS, "In progress"),
    (PRODUCTS_FILE_CHECK_STATUS.CONFIRMED, "Confirmed"),
    (PRODUCTS_FILE_CHECK_STATUS.REJECTED, "Rejected"),
]

PRODUCT_RATING_CHOICE = [
    (PRODUCT_RATINGS.NONE, "-"),
    (PRODUCT_RATINGS.ONE, "1"),
    (PRODUCT_RATINGS.TWO, "2"),
    (PRODUCT_RATINGS.THREE, "3"),
    (PRODUCT_RATINGS.FOUR, "4"),
    (PRODUCT_RATINGS.FIVE, "5"),
    ]

PRODUCT_CONDITION_CHOICE = [
    (PRODUCT_CONDITION.NEW, "New"),
    (PRODUCT_CONDITION.USED, "Used"),
    ]

PRODUCT_AVAILABLE_CHOICE = [
    (PRODUCT_AVAILABLE.UNAVAILABLE, "Unavailable"),
    (PRODUCT_AVAILABLE.AVAILABLE, "Available"),
    ]


class Tag(models.Model):
    name = models.CharField(verbose_name='Tag name', max_length=40)
    description = models.CharField(max_length=250, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(verbose_name='product name', max_length=150)
    factory = models.ForeignKey('Organizations.Factory', on_delete=models.SET_NULL, null=True, blank=True)
    company = models.ForeignKey('Organizations.Company', on_delete=models.SET_NULL, null=True, blank=True)
    #############################################################################
    # TODO: 'CATEGORY' FIELD - ANOTHER STRUCTURE? YES, SKIP FOR NOW
    # category = models.CharField(verbose_name='product category', max_length=30)
    price = models.PositiveIntegerField(verbose_name='Price in rubles', blank=True)
    description = models.CharField(verbose_name='Product description', max_length=4000, blank=True)
    tags_text = models.CharField(verbose_name='Tags for the product', max_length=1000, blank=True)
    main_image = models.ForeignKey('Products.ProductImage', verbose_name="Main image",
                                   on_delete=models.SET_NULL, blank=True, null=True, related_name="main_image")

    meta_information = models.TextField(default="[]", verbose_name="JSON meta information")
    condition = models.PositiveSmallIntegerField(verbose_name="Состояние товара", default=PRODUCT_CONDITION.NEW,
                                                 choices=PRODUCT_CONDITION_CHOICE)
    is_available = models.PositiveSmallIntegerField(verbose_name="Наличие товара", default=PRODUCT_AVAILABLE.AVAILABLE,
                                                 choices=PRODUCT_AVAILABLE_CHOICE)
    company_producer = models.ForeignKey('Organizations.CompanyProducer', verbose_name="Company producer", null=True, blank=True,
                                         on_delete=models.SET_NULL)
    factory_producer = models.ForeignKey('Organizations.FactoryProducer', verbose_name="Factory producer", null=True, blank=True,
                                         on_delete=models.SET_NULL)
    # То же соответствие, что и текстовые теги, но оптимизированно для поиска
    tags = models.ManyToManyField(
        'Products.Tag',
        through='Products.TagProductRelation',
        related_name='product_tags',
        blank=True,
    )

    # TODO: Add field for file with documentation (link) (not more than 50 Mb)

    # def save(self, *args, **kwargs):
    #     if (self.company is None) and (self.factory is None):
    #         raise ValidationError('Factory and company cannot be null at the same time')
    #
    #     super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.id}: {self.name}"


class TagProductRelation(models.Model):
    tag = models.ForeignKey('Products.Tag', on_delete=models.CASCADE)
    product = models.ForeignKey('Products.Product', on_delete=models.CASCADE)
    verification = models.NullBooleanField(null=True)
    # пока не проверен - NULL (дефолтно), если после проверки False - надо удалять


class ProductImage(models.Model):
    product = models.ForeignKey('Products.Product', on_delete=models.SET_NULL, null=True, related_name="product")
    photo = models.ForeignKey('Documents.Photo', on_delete=models.SET_NULL, null=True, related_name="photo")

    def __str__(self):
        return f"Image [{self.id}] for {self.product}"


class ProductFile(models.Model):
    product = models.ForeignKey('Products.Product', on_delete=models.SET_NULL, null=True, related_name="product_file")
    document = models.ForeignKey('Documents.Document', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"File [{self.id}] for {self.product}"


class ProductsProcessingFile(models.Model):
    name = models.CharField(verbose_name='File name', max_length=50, blank=True)
    datetime = models.DateTimeField(auto_now_add=True)
    factory = models.ForeignKey('Organizations.Factory', on_delete=models.SET_NULL, null=True, blank=True)
    company = models.ForeignKey('Organizations.Company', on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey('Users.User', on_delete=models.SET_NULL, null=True, blank=True)
    link = models.CharField(verbose_name="Link to file", max_length=300)
    annotation = models.CharField(verbose_name='File annotation', max_length=500, blank=True)
    status = models.IntegerField(
        choices=PRODUCTS_FILE_CHECK_STATUS_CHOICE,
        default=PRODUCTS_FILE_CHECK_STATUS.IN_PROGRESS
    )
    comment = models.CharField(verbose_name='File comment', max_length=500, blank=True)
    

class ProductRating(models.Model):
    product = models.ForeignKey('Products.Product', on_delete=models.CASCADE)
    #user = models.ForeignKey('Users.user', on_delete=models.SET_NULL, null=True)
    company = models.ForeignKey('Organizations.Company', on_delete=models.SET_NULL, null=True)
    rating = models.PositiveSmallIntegerField(choices=PRODUCT_RATING_CHOICE,
                                              null=True, default=None)
    description = models.CharField(max_length=700, blank=True, null=True)
    last_changed_at = models.DateTimeField(auto_now=True)
    

class ProductTable(models.Model):
    name = models.CharField(verbose_name='File name', max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.CharField(verbose_name="Link to file", max_length=300)
