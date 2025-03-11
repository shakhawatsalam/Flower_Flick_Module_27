from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Cart, CartItem, Order, OrderItem
from orders import serializers
from rest_framework.response import Response
from rest_framework.decorators import action
# Create your views here.


class CartViewSet(viewsets.ModelViewSet):
    # queryset =  Cart.objects.all()
    serializer_class = serializers.CartSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
 
 
    
class CartItemViewSet(viewsets.ModelViewSet):
    http_method_names =['get','post', 'patch', 'delete']
    queryset = CartItem.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return serializers.UpdateCartItemSerializer
        
        return serializers.CartItemSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        if getattr(self, 'swagger_fake_view', False):
            return context
        return {'cart_id': self.kwargs.get('cart_pk')}
    def get_queryset(self):
        return CartItem.objects.select_related('flower').filter(cart_id=self.kwargs.get('cart_pk'))
    
    
    
    
        
        
        
class OrderViewSet(viewsets.ModelViewSet):
    http_method_names = ['get','post', 'delete', 'patch', 'head', 'options']
