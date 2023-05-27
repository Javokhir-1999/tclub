from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import (DestroyAPIView, ListAPIView,
                                     RetrieveAPIView, ListCreateAPIView, UpdateAPIView)
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q

from .models import (ProductType, ProductList, Shipper, 
    Store, Payment, Client, CustomUser, Table, ProductSell, 
    ProductSellCheck, StoreAll, Discount, Order, OrderCheck, Barcode)
from .serializers import (
    ProductSellSerializer,
    ProductSellCUSerializer,
    ClientSerializer,
    CustomUserSerializer,
    CustomUserTokenSerializer,
    ProductListCUSerializer,
    TableSerializer,
    DiscountSerializer,
    BarcodeSerializer,
    StoreSerializer,
    StoreCSerializer,
    ProductTypeSerializer,
    ProductListSerializer,
    ShipperSerializer,
    StoreAllSerializer)

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

class ProductTypeUpdateAPIView(UpdateAPIView):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

class ProductListCreateAPIView(ListCreateAPIView):
    queryset = ProductList.objects.all()
    serializer_class = ProductListCUSerializer

    def list(self, request):
        queryset = self.get_queryset()
        serializer = ProductListSerializer(queryset, many=True)
        return Response(serializer.data)

class ProductListUpdateAPIView(UpdateAPIView):
    queryset = ProductList.objects.all()
    serializer_class = ProductListCUSerializer
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


        if product_id == None or shipper_id == None or price_buy == None or count == None or payment== None:
            raise ValidationError(detail={
                "product_id": "required", 
                "shipper_id": "required", 
                "price_buy": "required", 
                "count": "required",
                "payment": "required"
            })
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

class ShipmentHistoryAPIView(APIView):
    def get(self, request):
        data = request.data
        product_id = data.get('product_id', None)
        if product_id==None:
            raise ValidationError({"product_id": "required"})
        try:
            product = ProductList.objects.get(id=product_id)
            shipments = Store.objects.filter(product=product)
            serializer = StoreSerializer(shipments, many=True)
        except Exception as ex:
            raise ValidationError(detail=ex)

        return Response(serializer.data)

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

class ClientListCreateAPIView(ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

class ClientUpdateAPIView(UpdateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

class ClientRetrieveDestroyView(RetrieveAPIView, DestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            data = self.perform_destroy(instance)
            return Response('Deleted Successfully', status=201)
        except Exception as ex:
            raise ValidationError(detail=ex)

class ProductSellListCreateAPIView(ListCreateAPIView):
    queryset = ProductSell.objects.all()
    serializer_class = ProductSellCUSerializer
    def list(self, request):
        queryset = self.get_queryset()
        serializer = ProductSellSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = request.data
        client_id = data.get('client_id', None)
        table_id = data.get('table_id', None)
        operator_id = data.get('operator_id', None)
        product_barcode = data.get('product_barcode', None)
        count = int(data.get('count', None))
        price_sell = int(data.get('price_sell', None))

        if operator_id == None or product_barcode == None or count == None or price_sell == None:
            raise ValidationError(detail={
                "operator_id": "required", 
                "product_barcode": "required", 
                "count": "required", 
                "price_sell": "required",
                "table_id": "not required",
                "client_id": "not required",
            })

        try:
            product = ProductList.objects.get(barcode=product_barcode)
            store_all = StoreAll.objects.get(barcode=product_barcode)
            operator = CustomUser.objects.get(id=operator_id)
            if client_id:
                client = Client.objects.get(id=int(client_id))
            else:
                client = None
            if table_id:
                table = Table.objects.get(id=int(table_id))
            else:
                table = None
        except Exception as ex:
            raise ValidationError(ex)
        
        if store_all.total_left >= count:
            product_sell = ProductSell.objects.create(
                product = product,
                barcode = product.barcode,
                count = count,
                client = client,
                table = table,
                operator = operator,
                price_sell = price_sell,
            )
            store_all.total_left -= count
            store_all.save()
            return Response({
                "product_sell":ProductSellSerializer(product_sell).data,
                "total_left":StoreAllSerializer(store_all).data['total_left'],
            })
        else:
            raise ValidationError(detail="In Store only "+str(store_all.total_left)+" left. "+"but you required "+str(count)) 

class ProductSellUpdateAPIView(UpdateAPIView):
    queryset = ProductSell.objects.all()
    serializer_class = ProductSellSerializer
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

class ProductSellRetrieveDestroyView(RetrieveAPIView, DestroyAPIView):
    queryset = ProductSell.objects.all()
    serializer_class = ProductSellSerializer
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            data = self.perform_destroy(instance)
            return Response('Deleted Successfully', status=201)
        except Exception as ex:
            raise ValidationError(detail=ex)
