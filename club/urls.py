from django.urls import path
from . import views

urlpatterns = [
    path('login', views.LoginView.as_view()),
    path('product-type', views.ProductTypeListCreateView.as_view()),
    path('product-store', views.ProductStoreListAPIView.as_view()),
    path('product-store-add', views.AddProductView.as_view()),
    path('product-store/<int:pk>', views.ProductStoreRetrieveDestroyView.as_view()),
    path('product-type/<int:pk>', views.ProductTypeRetrieveDestroyView.as_view()),
    
    path('product-list', views.ProductListCreateAPIView.as_view()),
    path('product-list-update/<int:pk>', views.ProductListUpdateAPIView.as_view()),
    path('product-list/<int:pk>', views.ProductRetrieveDestroyView.as_view()),

    path('table', views.TableListCreateAPIView.as_view()),
    path('table-update/<int:pk>', views.TableUpdateAPIView.as_view()),
    path('table/<int:pk>', views.TableRetrieveDestroyView.as_view()),

    path('discount', views.DiscountListCreateAPIView.as_view()),
    path('discount-update/<int:pk>', views.DiscounUpdateAPIView.as_view()),
    path('discount/<int:pk>', views.DiscountRetrieveDestroyView.as_view()),


    path('product-list/filter', views.ProductListFindView.as_view()),

    path('shipper', views.ShipperListCreateAPIView.as_view()),
    path('shipper-update/<int:pk>', views.ShipperUpdateAPIView.as_view()),
    path('shipper/<int:pk>', views.ShipperRetrieveDestroyView.as_view()),
    path('generate-barcode', views.GenBarcodeView.as_view()),
]
