from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import (ProductType, ProductList, Shipper, 
    Store, Client, CustomUser, Table, ProductSell, Payment, 
    ProductSellCheck, Stock, Discount, Order, OrderCheck, StoreGroup,Barcode)
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
        fields = [
            'id',
            'username',
            'password',
            'role',
        ]

class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = '__all__'

class ProductListSerializer(serializers.ModelSerializer):
    total_left = serializers.SerializerMethodField('get_total_left')
    class Meta:
        model = ProductList
        fields = '__all__'
        extra = ['sales', 'shipment']
        depth = 2

    def get_total_left(self, obj):
        total_count=0
        try:
            total = Stock.objects.get(barcode=obj.barcode)
            return total.total_left
        except Exception as ex:
            Stock.objects.create(barcode=obj.barcode, total_left=0)
            return 0
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
        
class ProductListCUSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductList
        fields = '__all__'

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'

class ShipperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipper
        fields = '__all__'

class ProductShipmentSerializer(serializers.ModelSerializer):
    shipper = ShipperSerializer()
    class Meta:
        model = StoreGroup
        fields = '__all__'
        
class StoreSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(label='ID')
    product = ProductListSerializer()
    shipper = ShipperSerializer()
    group = ProductShipmentSerializer()
    total_price = serializers.SerializerMethodField('get_total_price')
    class Meta:
        model = Store
        fields = '__all__'
        extra = ['total_price']

    def get_total_price(self, obj):
        return obj.count * obj.price_buy

            
class StoreCSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'

class BarcodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barcode
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        depth=2

class TableSerializer(serializers.ModelSerializer):
    order = serializers.SerializerMethodField('get_order')
    check_list = serializers.SerializerMethodField('get_check_list')
    class Meta:
        model = Table
        fields = '__all__'

    def get_order(self, obj):
        try:
            return OrderSerializer(Order.objects.get(table__id=obj.id, play_status="active"), many=False).data
        except Exception as ex:
            return None
    
    def get_check_list(self, obj):
        try:
            total_price=0
            order = Order.objects.get(table__id=obj.id, play_status="active")
            product_sell_list = ProductSell.objects.filter(order=order, pay_status=True)
            for product in product_sell_list:
                total_price += product.price_sell * product.count
            return{
                "list": ProductSellSerializer(product_sell_list, many=True).data,
                "total_price": total_price
            } 
        except Exception as ex:
            return None

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class ProductSellSerializer(serializers.ModelSerializer):
    # product = ProductListSerializer()
    class Meta:
        model = ProductSell
        fields = '__all__'
        depth=2

class ProductSellCUSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSell
        fields = '__all__'
    
    def create(self, validated_data):
        try:
            in_store = Stock.objects.get(barcode=validated_data.barcode)
            in_store.total_left -= validated_data.count
            in_store.save()
        except Exception as ex:
            raise ValidationError(ex)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

class OrderCUSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


