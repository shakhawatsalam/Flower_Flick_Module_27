from django.urls import path, include
from flowers.views import FlowerViewSet, CategoryViewSet
from orders.views import CartViewSet, OrderViewSet, CartItemViewSet
from  rest_framework_nested import routers

router = routers.DefaultRouter()

router.register('flowers', FlowerViewSet, basename='flowers')
router.register('categories', CategoryViewSet , basename="category")
router.register('carts', CartViewSet , basename='carts')
router.register('orders', OrderViewSet, basename='orders')


cart_router = routers.NestedDefaultRouter(router, 'carts', lookup= 'cart')
cart_router.register('items', CartItemViewSet, basename='cart-item')



urlpatterns = [
    path('', include(router.urls)),
    path('', include(cart_router.urls)),
    
]
