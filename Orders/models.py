from django.db import models
import Orders.constants.request_delivery_types as REQUEST_DELIVERY_TYPES
import Orders.constants.order_chain_status as ORDER_CHAIN_STATUS
import Orders.constants.product_request_status as PRODUCT_REQUEST_STATUS


ORDER_CHAIN_STATUS_CHOICES = [
    (ORDER_CHAIN_STATUS.REJECT, "Reject"),
    (ORDER_CHAIN_STATUS.WAITING, "Waiting"),
    (ORDER_CHAIN_STATUS.CONFIRMED, "Confirmed"),
    (ORDER_CHAIN_STATUS.COMPLETED, "Completed")
]

REQUEST_DELIVERY_TYPES_CHOICE = [
    (REQUEST_DELIVERY_TYPES.ON_FACTORY, "On factory"),
    (REQUEST_DELIVERY_TYPES.BY_ADDRESS, "By address"),
    (REQUEST_DELIVERY_TYPES.CONTACT_LATER, "Contact later"),
]

PRODUCT_REQUEST_STATUS_CHOICE = [
    (PRODUCT_REQUEST_STATUS.HISTORY, "HISTORY"),
    (PRODUCT_REQUEST_STATUS.CONSTRUCTION, "CONSTRUCTION"),
    (PRODUCT_REQUEST_STATUS.ACTIVE, "ACTIVE"),
]


class ProductRequest(models.Model):
    customer = models.ForeignKey('Organizations.Company', on_delete=models.CASCADE)
    user = models.ForeignKey('Users.User', on_delete=models.SET_NULL, null=True)
    request_time = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey('Products.Product', null=True, blank=True, on_delete=models.SET_NULL)
    request = models.CharField(max_length=200)
    amount = models.PositiveIntegerField(default=1)
    description = models.CharField(max_length=4000, null=True, blank=True)
    preferable_time = models.DateTimeField(blank=True, null=True)
    preferable_price = models.IntegerField(blank=True, null=True)

    company_executor = models.ForeignKey('Organizations.Company', on_delete=models.SET_NULL,
                                         null=True, blank=True, related_name="company_executor_request")
    factory_executor = models.ForeignKey('Organizations.Factory', on_delete=models.SET_NULL,
                                         null=True, blank=True, related_name="factory_executor_request")

    # Delivery prams
    delivery_type = models.IntegerField(choices=REQUEST_DELIVERY_TYPES_CHOICE)
    address = models.CharField(max_length=300, blank=True)
    status = models.IntegerField(default=PRODUCT_REQUEST_STATUS.HISTORY, choices=PRODUCT_REQUEST_STATUS_CHOICE)
    # images = models.CharField(max_length=5000, blank=True)  # ARRAY OF LINKS TO IMAGES [0..5]
    # files = models.CharField(max_length=5000, blank=True)  # ARRAY OF LINKS TO FILES [0..5]

    def __str__(self):
        return f"{self.customer}: {self.request_time} | Price: {self.preferable_price} RUB"


class ProductRequestImage(models.Model):
    # NULL, потому что будет потребоваться удалить ее и с хостинга в случае удаления продукта
    request = models.ForeignKey('Orders.ProductRequest', on_delete=models.SET_NULL, null=True)
    link = models.CharField(verbose_name="Link to image", max_length=300)
    description = models.CharField(verbose_name='Image description', max_length=300, blank=True)

    def __str__(self):
        return f"Image [{self.id}] for "


class ProductRequestFile(models.Model):
    # NULL, потому что будет потребоваться удалить и с хостинга в случае удаления продукта
    request = models.ForeignKey('Orders.ProductRequest', on_delete=models.SET_NULL, null=True)
    link = models.CharField(verbose_name="Link to file", max_length=300)
    name = models.CharField(verbose_name='File name', max_length=50, blank=True)
    description = models.CharField(verbose_name='File description', max_length=300, blank=True)

    def __str__(self):
        return f"File [{self.id}] for"


class OrderChain(models.Model):
    product_request = models.ForeignKey('Orders.ProductRequest', on_delete=models.CASCADE)
    company_executor = models.ForeignKey('Organizations.Company', on_delete=models.SET_NULL,
                                         null=True, blank=True, related_name="company_executor")
    factory_executor = models.ForeignKey('Organizations.Factory', on_delete=models.SET_NULL,
                                         null=True, blank=True, related_name="factory_executor")
    transport_company = models.ForeignKey('Organizations.Company', on_delete=models.SET_NULL,
                                          null=True, blank=True, related_name="transport_company")
    time = models.DateTimeField(blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)

    status = models.IntegerField(default=ORDER_CHAIN_STATUS.WAITING, choices=ORDER_CHAIN_STATUS_CHOICES)
    created_time = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=4000, blank=True)

    def __str__(self):
        if self.company_executor:
            executor = f"COMP ({self.company_executor})"
        else:
            executor = f"FACT ({self.factory_executor})"
        return f"[Request id {self.product_request.id}] executor: {executor}"
