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
    Store, Payment, Client, CustomUser, Table, ProductSell, 
    ProductSellCheck, StoreAll, Discount, Order, OrderCheck, Barcode)
from .serializers import (CustomUserSerializer,CustomUserTokenSerializer, ProductListCSerializer, TableSerializer, DiscountSerializer, BarcodeSerializer, StoreSerializer, StoreCSerializer, ProductTypeSerializer,ProductListSerializer,ShipperSerializer, StoreAllSerializer)

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

class CustomUserListCreateView(ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    def perform_create(self, serializer):
        instance = serializer.save()
        instance.set_password(instance.password)
        instance.save()

class CustomUserUpdateAPIView(UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
    def perform_update(self, serializer):
        instance = serializer.save()
        instance.set_password(instance.password)
        instance.save()

class CustomUserRetrieveDestroyView(RetrieveAPIView, DestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class ProductTypeListCreateView(ListCreateAPIView):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer

class ProductStoreListAPIView(ListAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

class ProductStoreAllRetrieveDestroyView(RetrieveAPIView, DestroyAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            data = self.perform_destroy(instance)
            return Response('Deleted Successfully', status=201)
        except Exception as ex:
            raise ValidationError(detail=ex)

class ProductTypeRetrieveDestroyView(RetrieveAPIView, DestroyAPIView):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            data = self.perform_destroy(instance)
            return Response('Deleted Successfully', status=201)
        except Exception as ex:
            raise ValidationError(detail=ex)

class ProductListCreateAPIView(ListCreateAPIView):
    queryset = ProductList.objects.all()
    serializer_class = ProductListCSerializer

    def list(self, request):
        queryset = self.get_queryset()
        serializer = ProductListSerializer(queryset, many=True)
        return Response(serializer.data)

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
        try:
            data = self.perform_destroy(instance)
            return Response('Deleted Successfully', status=201)
        except Exception as ex:
            raise ValidationError(detail=ex)

class ShipperListCreateAPIView(ListCreateAPIView):
    queryset = Shipper.objects.all()
    serializer_class = ShipperSerializer

class ShipperRetrieveDestroyView(RetrieveAPIView, DestroyAPIView):
    queryset = Shipper.objects.all()
    serializer_class = ShipperSerializer
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            data = self.perform_destroy(instance)
            return Response('Deleted Successfully', status=201)
        except Exception as ex:
            raise ValidationError(detail=ex)

class ShipperUpdateAPIView(UpdateAPIView):
    queryset = Shipper.objects.all()
    serializer_class = ShipperSerializer
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

class AddToStoreAPIView(APIView):
    def post(self, request, format=None):
        data = request.data
        product_id = data.get('product_id', None)
        shipper_id = data.get('shipper_id', None)
        price_buy = data.get('price_buy', None)
        count = data.get('count', None)
        payment = data.get('payment', None)


        if product_id == None or shipper_id == None or price_buy == None or count == None:
            raise ValidationError(detail={"product_id": "int", "shipper_id": "int", "price_buy": "int", "count": "int"})
        try:
            product = ProductList.objects.get(id=product_id)
            shipper = Shipper.objects.get(id=shipper_id)
        except Exception as ex:
            raise ValidationError(detail=ex)

        try:
            product_add = Store.objects.create(
                product=product,
                barcode=product.barcode,
                shipper=shipper,
                price_buy=price_buy,
                count=count
            )
            if payment:
                Payment.objects.create(
                    shipment=product_add,
                    amount=payment 
                )
        except Exception as ex:
            raise ValidationError(ex)


        try:
            in_store = StoreAll.objects.get(barcode=product_add.barcode)
            in_store.total_left += product_add.count
            in_store.save() 
            # Because the super class save method doesn't return anything
            stored_product = StoreAll.objects.get(barcode=product_add.barcode)
        except Exception as ex:
            stored_product = StoreAll.objects.create(
                barcode=product_add.barcode,
                total_left=product_add.count)

        return Response({"product": StoreCSerializer(product_add, many=False).data, "total_left": stored_product.total_left})

class ProductListFindView(ListAPIView):
    serializer_class = ProductListSerializer
    def get_queryset(self):
        data = self.request.data
        # filter = data.get('filter', None)
        filter = self.request.GET.get('filter', None)
        try:
            return ProductList.objects.filter(barcode=filter)
        except Exception as ex:
            try:
                return ProductList.objects.filter(name__contains=filter)
            except:
                raise ValidationError()

class GenBarcodeView(APIView):
    def get(self, request):
        try:
            barcode = Barcode.objects.create()
            barcode = int(str(barcode.id).ljust(11,'0'))
        except Exception as ex:
            raise ValidationError(detail=ex)

        return Response({"barcode":barcode})

class TableListCreateAPIView(ListCreateAPIView):
    queryset = Table.objects.all()
    serializer_class = TableSerializer

class TableUpdateAPIView(UpdateAPIView):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

class TableRetrieveDestroyView(RetrieveAPIView, DestroyAPIView):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            data = self.perform_destroy(instance)
            return Response('Deleted Successfully', status=201)
        except Exception as ex:
            raise ValidationError(detail=ex)

class DiscountListCreateAPIView(ListCreateAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer

class DiscounUpdateAPIView(UpdateAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

class DiscountRetrieveDestroyView(RetrieveAPIView, DestroyAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            data = self.perform_destroy(instance)
            return Response('Deleted Successfully', status=201)
        except Exception as ex:
            raise ValidationError(detail=ex)

class ProductStatisticsView(APIView):
    def get(self, request, format=None):
        product_ids = ProductList.objects.all().values_list("id", flat=True)
        products = []
        for id in product_ids:
            product = ProductList.objects.get(id=id)
            store = StoreAll.objects.get(barcode=product.barcode)

            products.append({
                "product": ProductListSerializer(product, many=False).data,
                "total_left": store.total_left,
            })

        return Response({})