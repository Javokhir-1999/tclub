from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import (DestroyAPIView, ListAPIView,
                                     RetrieveAPIView, ListCreateAPIView, UpdateAPIView)
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from .models import (ProductType, ProductList, Shipper, 
    Product, Client, CustomUser, Table, ProductSell, 
    ProductSellCheck, Store, Discount, Order, OrderCheck)
from .serializers import (CustomUserTokenSerializer,ProductSerializer,ProductTypeSerializer,ProductListSerializer,ShipperSerializer)

class LoginView(APIView):
    permission_classes = []
    def post(self, request, format=None):
        data = request.data
        username = data.get('username', None)
        password = data.get('password', None)

        user = authenticate(username=username, password=password)
    
        if user is not None:
            if user.is_active:
                return Response(CustomUserTokenSerializer(user, many=False).data)
            else:
                raise ValidationError(detail={'detail':'user status is not active'})
        else:
            raise ValidationError(detail={'detail':'login or password is wrong'})

class ProductTypeListCreateView(ListCreateAPIView):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer

class ProductTypeRetrieveDestroyView(RetrieveAPIView, DestroyAPIView):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.perform_destroy(instance)
        return Response('Deleted Successfully', status=201)

class ProductListCreateAPIView(ListCreateAPIView):
    queryset = ProductList.objects.all()
    serializer_class = ProductListSerializer

class ProductListUpdateAPIView(UpdateAPIView):
    queryset = ProductList.objects.all()
    serializer_class = ProductListSerializer
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

class ProductRetrieveDestroyView(RetrieveAPIView, DestroyAPIView):
    queryset = ProductList.objects.all()
    serializer_class = ProductListSerializer
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.perform_destroy(instance)
        return Response('Deleted Successfully', status=201)

class ShipperListCreateAPIView(ListCreateAPIView):
    queryset = Shipper.objects.all()
    serializer_class = ShipperSerializer

class ShipperRetrieveDestroyView(RetrieveAPIView, DestroyAPIView):
    queryset = Shipper.objects.all()
    serializer_class = ShipperSerializer
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.perform_destroy(instance)
        return Response('Deleted Successfully', status=201)

class AddProductView(APIView):
    def post(self, request, format=None):
        data = request.data
        product_id = data.get('product_id', None)
        shipper_id = data.get('shipper_id', None)
        price_buy = data.get('price_buy', None)
        count = data.get('count', None)

        if product_id == None or shipper_id == None or price_buy == None or count == None:
            raise ValidationError(detail={"product_id": "int", "shipper_id": "int", "price_buy": "int", "count": "int"})
        try:
            product = ProductList.objects.get(id=product_id)
            shipper = Shipper.objects.get(id=shipper_id)
        except Exception as ex:
            raise ValidationError(detail=ex)

        result = Product.objects.create(
            product=product,
            barcode=product.barcode,
            shipper=shipper,
            price_buy=price_buy,
            count=count
        )

        return Response(ProductSerializer(result, many=False).data)

class ProductListFindView(ListAPIView):
    serializer_class = ProductListSerializer
    def get_queryset(self):
        data = self.request.data
        filter = data.get('filter', None)
        try:
            return ProductList.objects.filter(barcode=filter)
        except Exception as ex:
            try:
                return ProductList.objects.filter(name__contains=filter)
            except:
                raise ValidationError()
