from django.urls import path
from .views import ProductListView, ProductDetailView, ProductRecommendationsView

app_name = 'api'

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('recommendations/<int:user_id>/', ProductRecommendationsView.as_view(), name='product-recommendations'),
]
