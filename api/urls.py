from django.urls import path, include
from flowers.views import FlowerViewSet, CategoryViewSet,  FlowerImageViewSet
from orders.views import CartViewSet, OrderViewSet, CartItemViewSet
from  rest_framework_nested import routers

router = routers.DefaultRouter()

router.register('flowers', FlowerViewSet, basename='flowers')
router.register('categories', CategoryViewSet , basename="category")
router.register('carts', CartViewSet , basename='carts')
router.register('orders', OrderViewSet, basename='orders')


flower_router = routers.NestedDefaultRouter(router, 'flowers', lookup='flower')
flower_router.register('images', FlowerImageViewSet, basename='flower-image' )
cart_router = routers.NestedDefaultRouter(router, 'carts', lookup= 'cart')
cart_router.register('items', CartItemViewSet, basename='cart-item')



urlpatterns = [
    path('', include(router.urls)),
    path('', include(cart_router.urls)),
    path('', include(flower_router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
      
    
]
