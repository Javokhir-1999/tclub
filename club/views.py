from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import (DestroyAPIView, ListAPIView,
                                     RetrieveAPIView, ListCreateAPIView, UpdateAPIView)
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator
from django.contrib.auth import authenticate
from django.db.models import Sum
from django.db.models import Q
from datetime import date, datetime, timedelta, time
date = date.today()
from .models import (ProductType, ProductList, Shipper, StoreGroup,
    Store, Payment, Client, CustomUser, Table, ProductSell, 
    ProductSellCheck, Stock, Discount, Order, OrderCheck, Barcode)
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
    OrderSerializer,
    OrderCUSerializer,
    ProductShipmentSerializer,
    StockSerializer)

class ResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

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

class ProductStoreByGroupIDListAPIView(ListAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    def list(self, request):
        shipment_id = self.request.GET.get('shipment_id', None)
        if not shipment_id:
            raise ValidationError("param 'shipment_id' is required")

        queryset = Store.objects.filter(group_id = shipment_id)
        try:
            serializer = StoreSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as err:
            return Response(err)


class ProductShipmentListAPIView(ListAPIView):
    queryset = StoreGroup.objects.all()
    serializer_class = ProductShipmentSerializer

class ProductStoreRetrieveDestroyView(RetrieveAPIView, DestroyAPIView):
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
        shipper_id = data.get('shipper_id', None)
        products = data.get('products', None)
        payment = data.get('payment', None)


        if shipper_id == None or products == None or payment== None:
            raise ValidationError(detail={
                "products": "required", 
                "shipper_id": "required", 
                "payment": "required"
            })

        try:
            shipper = Shipper.objects.get(id=shipper_id)
            cost = 0
            for p in products:
                cost += p['price_buy'] * p['count']

            group = StoreGroup.objects.create(payment=payment, shipper=shipper, cost=cost)

        except Exception as ex:
                raise ValidationError(detail=ex)

        for p in products:
            try:
                product = ProductList.objects.get(id=p['product_id'])
                product_add = Store.objects.create(
                    product=product,
                    barcode=product.barcode,
                    shipper=shipper,
                    group=group,
                    price_buy=p['price_buy'],
                    count=p['count']
                )
            except Exception as ex:
                raise ValidationError(ex)
                
            try:
                in_store = Stock.objects.get(barcode=product_add.barcode)
                in_store.total_left += product_add.count
                in_store.save() 
                Stock.objects.get(barcode=product_add.barcode)
            except Exception as ex:
                Stock.objects.create(
                    barcode=product_add.barcode,
                    total_left=product_add.count)

        return Response("Done!")

class ProductListFindView(ListAPIView):
    serializer_class = ProductListSerializer
    def get_queryset(self):
        filter = self.request.GET.get('filter', None)
        try:
            result = []
            pls =  ProductList.objects.filter(Q(barcode__contains=filter) | Q(name__contains=filter))
            for p in pls:
                if Stock.objects.filter(Q(barcode=p.barcode) & Q(total_left__gte=1)):
                    result.append(p)
            return result
        except Exception as ex:
            raise ValidationError()

class ProductListAdminFindView(ListAPIView):
    serializer_class = ProductListSerializer
    def get_queryset(self):
        filter = self.request.GET.get('filter', None)
        try:
            return ProductList.objects.filter(Q(barcode__contains=filter) | Q(name__contains=filter))
        except Exception as ex:
            raise ValidationError()

class ClientListFindView(ListAPIView):
    serializer_class = ClientSerializer
    def get_queryset(self):
        filter = self.request.GET.get('filter', None)
        try:
            return Client.objects.filter(name__contains=filter)
        except Exception as ex:
            try:
                return Client.objects.filter(phone__contains=filter)
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

class StoreHistoryAPIView(APIView):
    def get(self, request):
        product_id = self.request.GET.get('product_id', None)
        shipper_id = self.request.GET.get('shipper_id', None)
        timeframe = self.request.GET.get('timeframe', None)
        if product_id==None and shipper_id==None:
            raise ValidationError({"product_id or shipper_id": "param: required", "timeframe": "param: not required", "page_size": "param: not required", })
        
        query_filter: Q = Q()
        try:
            
            if timeframe == None:
                pass
            elif timeframe == 'day':
                today_time_min = datetime.combine(date, time.min)
                today_time_max = datetime.now()
                query_filter = query_filter & Q(created_at__range=(today_time_min, today_time_max))

            elif timeframe == 'week':
                start_week = datetime.now() - timedelta(weeks=1)
                end_week = datetime.now()
                query_filter = query_filter & Q(created_at__range=(start_week, end_week))

            elif timeframe == 'month':
                start_month = datetime.now() - timedelta(weeks=4)
                end_month = datetime.now()
                query_filter = query_filter & Q(created_at__range=(start_month, end_month))

            elif timeframe == 'year':
                start_year = datetime.now() - timedelta(days=365)
                end_year = datetime.now()
                query_filter = query_filter & Q(created_at__range=(start_year, end_year))

            else:
                raise ValidationError(detail="not valid 'timeframe'")
            if product_id:
                product = ProductList.objects.get(id=product_id)
                queryset = Store.objects.filter(Q(product=product) & query_filter)
            elif shipper_id:
                shipper = Shipper.objects.get(id=shipper_id)
                queryset = Store.objects.filter(Q(shipper=shipper) & query_filter)

            serializer = StoreSerializer(queryset, many=True)
        except Exception as ex:
            raise ValidationError(detail=ex)

        return Response(serializer.data)

class ShipmentHistoryAPIView(APIView):
    def get(self, request):
        shipper_id = self.request.GET.get('shipper_id', None)
        timeframe = self.request.GET.get('timeframe', None)
        if shipper_id==None:
            raise ValidationError({"shipper_id": "param: required", "timeframe": "param: not required", "page_size": "param: not required", })
        
        query_filter: Q = Q()
        try:
            
            if timeframe == None:
                pass
            elif timeframe == 'day':
                today_time_min = datetime.combine(date, time.min)
                today_time_max = datetime.now()
                query_filter = query_filter & Q(created_at__range=(today_time_min, today_time_max))

            elif timeframe == 'week':
                start_week = datetime.now() - timedelta(weeks=1)
                end_week = datetime.now()
                query_filter = query_filter & Q(created_at__range=(start_week, end_week))

            elif timeframe == 'month':
                start_month = datetime.now() - timedelta(weeks=4)
                end_month = datetime.now()
                query_filter = query_filter & Q(created_at__range=(start_month, end_month))

            elif timeframe == 'year':
                start_year = datetime.now() - timedelta(days=365)
                end_year = datetime.now()
                query_filter = query_filter & Q(created_at__range=(start_year, end_year))

            else:
                raise ValidationError(detail="not valid 'timeframe'")

            if shipper_id:
                shipper = Shipper.objects.get(id=shipper_id)
                queryset = StoreGroup.objects.filter(Q(shipper=shipper) & query_filter)

            serializer = ProductShipmentSerializer(queryset, many=True)
        except Exception as ex:
            raise ValidationError(detail=ex)
        
        try:
            page_number = self.request.query_params.get('page', 1)
            page_size = self.request.query_params.get('page_size', 10)
            paginator = Paginator(serializer.data, page_size)

            return Response({
                'count': paginator.count,
                'history': paginator.page(page_number).object_list,
            })
        except Exception as err:
            raise ValidationError(err)

        # return Response(serializer.data)

class ProductSellHistoryAPIView(APIView):
    def get(self, request):
        product_id = self.request.GET.get('product_id', None)
        operator_id = self.request.GET.get('operator_id', None)
        timeframe = self.request.GET.get('timeframe', None)
        if product_id==None and operator_id==None:
            raise ValidationError({"product_id or operator_id": "param: required", "timeframe": "param: not required", "page_size": "param: not required", })
        
        query_filter: Q = Q()
        try:
            if timeframe == None:
                pass
            elif timeframe == 'day':
                today_time_min = datetime.combine(date, time.min)
                today_time_max = datetime.now()
                query_filter = query_filter & Q(sold_time__range=(today_time_min, today_time_max))

            elif timeframe == 'week':
                start_week = datetime.now() - timedelta(weeks=1)
                end_week = datetime.now()
                query_filter = query_filter & Q(sold_time__range=(start_week, end_week))

            elif timeframe == 'month':
                start_month = datetime.now() - timedelta(weeks=4)
                end_month = datetime.now()
                query_filter = query_filter & Q(sold_time__range=(start_month, end_month))

            elif timeframe == 'year':
                start_year = datetime.now() - timedelta(days=365)
                end_year = datetime.now()
                query_filter = query_filter & Q(sold_time__range=(start_year, end_year))

            else:
                raise ValidationError(detail="not valid 'timeframe'")
            if operator_id:
                operator = CustomUser.objects.get(id=operator_id)
                queryset = ProductSell.objects.filter(Q(operator=operator) & query_filter)
            else:
                product = ProductList.objects.get(id=product_id)
                queryset = ProductSell.objects.filter(Q(product=product) & query_filter)

            serializer = ProductSellSerializer(queryset, many=True)
        except Exception as ex:
            raise ValidationError(detail=ex)

        return Response(serializer.data)

class TableListCreateAPIView(ListCreateAPIView):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    def list(self, request):
        filter = self.request.GET.get('filter', None)
        try:
            if filter:
                queryset = Table.objects.filter(in_use=filter, active=True)
            else:
                queryset = self.get_queryset()
        except Exception as ex:
            raise ValidationError(ex)

        serializer = TableSerializer(queryset, many=True)
        return Response(serializer.data)

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
    pagination_class = ResultsSetPagination

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

class OrderCloseAPIView(APIView):
    def post(self, request, format=None):
        data = request.data
        order_id = data.get('order_id', None)
        action = data.get('action', "preview")

        try:    
            try:
                order = Order.objects.get(Q(id=order_id) & Q(play_status="active") | Q(play_status="paused"))
            except:
                raise ValidationError("order not found, wrong id or orderis already closed")
            total_play_price=0
            total_product_price=0
            total_price = 0

            timer = int(round((datetime.now() - order.time_open).total_seconds() / 60.0, 2))
            try:
                discount = Discount.objects.filter(minute__lte=timer).order_by('minute').last()
            except:
                discount = None

            total_play_price = int(order.table.price * timer / order.table.minute)
            if discount: 
                total_play_price_with_discount = total_play_price - total_play_price * (discount.percent / 100)
            else:
                total_play_price_with_discount = total_play_price

            product_sell_list = ProductSell.objects.filter(order=order, pay_status=True)
            if product_sell_list:
                for product in product_sell_list:
                    total_product_price += product.price_sell * product.count
                product_check_list = ProductSellSerializer(product_sell_list, many=True).data
            else:
                product_check_list = None

            total_price = total_play_price_with_discount + total_product_price

            if action == "preview":
                return Response({
                    "product_check_list": product_check_list,
                    "total_product_price": total_product_price,
                    "order": OrderSerializer(order, many=False).data,
                    "timer": timer,
                    "total_play_price": total_play_price,
                    "discount": DiscountSerializer(discount, many=False).data,
                    "total_price": total_price,
                })
            elif action == "close":
                order.play_status = "ended"
                order.time_close = datetime.now()
                order.pay_status = False
                order.save()
                order.table.in_use = False    
                order.table.save()

                if product_sell_list:
                    for product in product_sell_list:
                        product.pay_status = False
                        product.save()

                return Response("good, order is closed")
            else:
                raise ValidationError("worng 'action', choices are: preview, close")

        except Exception as ex:
            raise ValidationError(ex)

class ProductSellListCreateAPIView(ListCreateAPIView):
    queryset = ProductSell.objects.all()
    serializer_class = ProductSellCUSerializer
    def list(self, request):
        queryset = self.get_queryset()
        serializer = ProductSellSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = request.data
        order_id = data.get('order_id', None)
        operator_id = data.get('operator_id', None)
        products = data.get('products', None)
        if operator_id == None or products==None:
            raise ValidationError(detail={
                "operator_id": "required", 
                "order_id": "not required",
                "products":[
                    {
                        "product_barcode": "required", 
                        "count": "required", 
                        "price_sell": "required",
                    },
                ]
                
            })
            
        try:
            operator = CustomUser.objects.get(id=operator_id)
            if order_id:
                order = Order.objects.get(id=int(order_id))
            else:
                order = None

            if order:
                pay_status = True
            else:
                pay_status = False
    
            validated_products = []
            for p in products: 
                store_all = Stock.objects.get(barcode=p['product_barcode'])
                if store_all.total_left < int(p['count']):
                    raise ValidationError(detail="In Store only "+str(store_all.total_left)+" left. "+"but you required "+str(p['count']))
        
            for p in products: 
                product = ProductList.objects.get(barcode=p['product_barcode'])
                store_all = Stock.objects.get(barcode=p['product_barcode'])
                
                if store_all.total_left >= int(p['count']):
                    product_sell = ProductSell.objects.create(
                        product = product,
                        barcode = product.barcode,
                        count = p['count'],
                        order = order,
                        operator = operator,
                        pay_status = pay_status,
                        price_sell = p['price_sell'],
                    )

                    store_all.total_left -= int(p['count'])
                    store_all.save()
                    validated_products.append({
                        "product_sell":ProductSellSerializer(product_sell).data,
                        "total_left":StockSerializer(store_all).data['total_left'],
                    })
                else:
                    raise ValidationError(detail="In Store only "+str(store_all.total_left)+" left. "+"but you required "+str(p['count']))

        except Exception as ex:
            raise ValidationError(ex)

        return Response(validated_products)

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

class OrderListCreateAPIView(ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderCUSerializer
    def list(self, request):
        queryset = self.get_queryset()
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = request.data
        client_id = data.get('client_id', None)
        operator_id = data.get('operator_id', None)
        table_id = data.get('table_id', None)
        vip = data.get('vip', None)
        limit = data.get('limit', None)
        if operator_id == None or table_id == None or vip == None:
            raise ValidationError(detail={
                "operator_id": "required",
                "table_id": "required",
                "vip": "boolean, required", 
                "client_id": "not required",
            })
        try:
            operator = CustomUser.objects.get(id=int(operator_id))
            table = Table.objects.get(id=int(table_id), in_use=False)
            if client_id:
                client = Client.objects.get(id=int(client_id))
            else:
                client = None
            if vip:
                vip = True
            order = Order.objects.create(
                client = client,
                table = table,
                operator = operator,
                vip = vip,
                limit = limit,
                play_status = "active",
                time_open = datetime.now(),
            )
            table.in_use = True
            table.save()
            return Response(OrderSerializer(order, many=False).data)
        except Exception as ex:
            raise ValidationError(ex)
            
class  OrderUpdateAPIView(UpdateAPIView):
    queryset =  Order.objects.all()
    serializer_class =  OrderSerializer
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

class OrderRetrieveDestroyView(RetrieveAPIView, DestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            data = self.perform_destroy(instance)
            return Response('Deleted Successfully', status=201)
        except Exception as ex:
            raise ValidationError(detail=ex)