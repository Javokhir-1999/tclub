from django.db import models
from uuid import uuid4
from phonenumber_field.modelfields import PhoneNumberField
from core.settings import MEDIA_URL

from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    role = models.CharField(max_length=50, choices=(("admin", "Админ"),("operator", "Оператор")), blank=True)
    # def save(self, *args, **kwargs):
    #     if not self.pk:
    #         self.role = self.base_role
    #         self.password = self.password
    #     return super().save(*args, **kwargs)
    def __str__(self):
        return self.username

class ProductType(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class ProductList(models.Model):
    name = models.CharField(max_length=255)
    type = models.ForeignKey(ProductType, on_delete=models.PROTECT)
    barcode = models.PositiveBigIntegerField(null=False, unique=True)
    price_sell = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class Shipper(models.Model):
    name = models.CharField(max_length=128)
    phone = PhoneNumberField(null=False, blank=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

class Product(models.Model):
    product = models.ForeignKey(ProductList, on_delete=models.PROTECT)
    shipper = models.ForeignKey(Shipper, on_delete=models.PROTECT)
    barcode = models.PositiveBigIntegerField(null=False, unique=True)
    price_buy = models.PositiveBigIntegerField()
    count = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.product.name  

class Client(models.Model):
    name = models.CharField(max_length=128, unique=True)
    photo = models.ImageField(
        upload_to = MEDIA_URL,
        null=True,
        blank=True,
        default=False)
    phone = PhoneNumberField(null=False, blank=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class Table(models.Model):
    name = models.CharField(max_length=128)
    price = models.PositiveBigIntegerField()
    minute = models.PositiveBigIntegerField()
    in_use = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

class ProductSell(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT, null=True, blank=True)
    table = models.ForeignKey(Table, on_delete=models.PROTECT, null=True, blank=True)
    barcode = models.PositiveBigIntegerField(null=False, unique=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    operator = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    price_sell = models.PositiveBigIntegerField(null=False, help_text='price for one')
    count = models.PositiveBigIntegerField()
    sold_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.product.name

class ProductSellCheck(models.Model):
    product_sell = models.TextField(help_text="contains a list of sold products")
    operator = models.CharField(max_length=255, help_text="operator ID-name")
    client = models.CharField(max_length=255, help_text="client ID-name", null=True, blank=True)
    total_price = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.order_uuid

class Store(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    barcode = models.PositiveBigIntegerField(null=False, unique=True)
    total_left = models.PositiveBigIntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.product.product.name+"|"+str(self.barcode)

class Discount(models.Model):
    title = models.CharField(max_length=255, unique=True)
    minute = models.PositiveBigIntegerField()
    percent = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title

class Order(models.Model):
    uuid = models.UUIDField(default=uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    table = models.ForeignKey(Table, on_delete=models.PROTECT)
    operator = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    vip = models.BooleanField(null=False)
    time_open = models.DateTimeField()
    time_close = models.DateTimeField(null=True, blank=True)
    status = models.BooleanField(
        default=True, 
        help_text="True = Open (not payed)", 
        choices=((True, "Open - no payed"), (False, "Closed - payed")))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.uuid

class OrderCheck(models.Model):
    order_uuid = models.UUIDField(default=uuid4, editable=False)
    client = models.CharField(max_length=255, help_text="client ID-name")
    operator = models.CharField(max_length=255,help_text="operator ID-name")
    time_open = models.DateTimeField()
    time_close = models.DateTimeField()
    played_minute = models.PositiveBigIntegerField(help_text="Timer")
    table_minute_price = models.PositiveBigIntegerField()
    discount_percent = models.PositiveBigIntegerField()
    total_price = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.order_uuid