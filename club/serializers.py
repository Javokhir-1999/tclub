from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import (ProductType, ProductList, Shipper, 
    Store, Client, CustomUser, Table, ProductSell, Payment, 
    ProductSellCheck, StoreAll, Discount, Order, OrderCheck, Barcode)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomUserTokenSerializer(serializers.ModelSerializer):
    tokens = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ['id','role', 'tokens']

    def get_tokens(self, user):
        tokens = CustomUsersTokenObtainPairSerializer.get_token(user)
        refresh = str(tokens)
        access = str(tokens.access_token)
        data = {
            "refresh": refresh,
            "access": access
        }
        return data

class CustomUsersTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)   
        token['role'] = user.role
        token['username'] = user.username
        token['email'] = user.email
        return token

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = '__all__'

class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductList
        fields = '__all__'
        depth = 2
        
class ProductListCSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductList
        fields = '__all__'

class StoreAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreAll
        fields = '__all__'

class StoreAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreAll
        fields = '__all__'

class StoreSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(label='ID')
    payment = serializers.SerializerMethodField('get_payment')
    sales = serializers.SerializerMethodField('get_sales')
    class Meta:
        model = Store
        fields = '__all__'
        extra = 'payment'
        depth = 2
    def get_payment(self, obj):
        total_pay = 0
        try:
            payment_list = Payment.objects.filter(shipment=obj.id).values_list('amount')
            for amount in payment_list:
                total_pay += amount[0]
            return total_pay
        except Exception as ex:
            raise ValidationError(ex)

    def get_sales(self, obj):
        total_sell_count = 0
        total_sell_price = 0
        try:
            sales = ProductSell.objects.filter(barcode=obj.barcode)
            for sale in sales:
                total_sell_count += sale.count
                total_sell_price += sale.count*sale.price_sell
            return {
                "total_sell_count": total_sell_count,
                "total_sell_price": total_sell_price,
            }
        except Exception as ex:
            raise ValidationError(ex)
            
class StoreCSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'

class ShipperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipper
        fields = '__all__'

class BarcodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barcode
        fields = '__all__'

class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = '__all__'

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'