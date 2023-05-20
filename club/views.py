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
        product_list_id = data.get('product_list_id', None)
        shipper_id = data.get('shipper_id', None)
        barcode = "product_list_id"
        price_buy = data.get('price_buy', None)
        count = data.get('count', None)

class ProductListFindView(ListAPIView):
    serializer_class = ProductListSerializer
    def get_queryset(self):
        data = self.request.data
        barcode = data.get('barcode', None)
        print(ProductList.objects.filter(barcode=barcode))
        return ProductList.objects.filter(barcode=barcode)