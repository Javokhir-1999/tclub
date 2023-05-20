from django.urls import path
from . import views

urlpatterns = [
    path('login', views.LoginView.as_view()),
    path('product-type', views.ProductTypeListCreateView.as_view()),
    path('product-add', views.AddProductView.as_view()),
    path('product-store', views.ProductStoreListAPIView.as_view()),
    path('product-type/<int:pk>', views.ProductTypeRetrieveDestroyView.as_view()),
    path('product-list-update/<int:pk>', views.ProductListUpdateAPIView.as_view()),

    path('product-list', views.ProductListCreateAPIView.as_view()),
    path('product-list/filter', views.ProductListFindView.as_view()),
    path('product-list/<int:pk>', views.ProductRetrieveDestroyView.as_view()),

    path('shipper', views.ShipperListCreateAPIView.as_view()),
    path('shipper/<int:pk>', views.ShipperRetrieveDestroyView.as_view()),
]
