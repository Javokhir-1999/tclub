from rest_framework import serializers
from .models import (ProductType, ProductList, Shipper, 
    Product, Client, CustomUser, Table, ProductSell, 
    ProductSellCheck, Store, Discount, Order, OrderCheck)
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

class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = '__all__'

class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductList
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        depth = 2

class ShipperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipper
        fields = '__all__'
