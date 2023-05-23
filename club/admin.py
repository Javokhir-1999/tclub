from django.contrib import admin
from django.contrib.auth.models import Group as DjGroup

from .models import (ProductType, ProductList, Shipper, 
    Product, Client, CustomUser, Table, ProductSell, 
    ProductSellCheck, Store, Discount, Order, OrderCheck, Barcode)

admin.site.unregister(DjGroup)
# admin.site.unregister(DjUser)

class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
class ProductListAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'barcode','type', 'price_sell', 'created_at')
class ShipperAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'created_at', 'updated_at')
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'shipper', 'barcode', 'price_buy', 'count', 'created_at', 'updated_at')
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'photo', 'phone', 'created_at')
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role')
class TableAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'minute', 'in_use', 'active')
class ProductSellAdmin(admin.ModelAdmin):
    list_display = ('client', 'table', 'barcode', 'product', 'operator', 'price_sell', 'count', 'sold_time')
class ProductSellCheckAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_sell', 'operator', 'client', 'total_price', 'created_at', 'updated_at')
class StoreAdmin(admin.ModelAdmin):
    list_display = ('barcode', 'total_left', 'updated_at')
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('title', 'minute', 'percent', 'created_at', 'updated_at')
class OrderAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'client', 'table', 'operator', 'vip', 'time_open', 'time_close', 'status', 'created_at', 'updated_at')

class OrderCheckAdmin(admin.ModelAdmin):
    list_display = ('order_uuid', 'client', 'operator', 'time_open', 'time_close', 'played_minute', 'table_minute_price', 'discount_percent', 'total_price', 'created_at', 'updated_at')

class BarcodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'updated_at')

admin.site.register(ProductType, ProductTypeAdmin)
admin.site.register(ProductList, ProductListAdmin)
admin.site.register(Shipper, ShipperAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Table, TableAdmin)
admin.site.register(ProductSell, ProductSellAdmin)
admin.site.register(ProductSellCheck, ProductSellCheckAdmin)
admin.site.register(Store, StoreAdmin)
admin.site.register(Discount, DiscountAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderCheck, OrderCheckAdmin)
admin.site.register(Barcode, BarcodeAdmin)