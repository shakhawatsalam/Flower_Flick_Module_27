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
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        OrderService.cancel_order(order=order, user=request.user)
        
        return Response({'status': 'Order cancled'})
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        serializer = UpdateOrderSerialier(order, data=request.data, partial=True)
        serializer.is_valid()
        serializer.save()
        return Response({'status': f'Order status updated to {request.data['status']}'})
    
    def get_serializer_class(self):
        if self.action == 'cancel':
            return serializers.EmptyOrderSerializer
        if self.action  == 'create':
            return serializers.CreateOrderSerializer
        elif self.action  == 'update_status':
            return serializers.UpdateOrderSerialier
        return serializers.OrderSerializer
    
    def get_serializer_context(self):
        if getattr(self,'swagger_fake_view',False):
            return super().get_serializer_context()
        return {'user_id': self.request.user.id, 'user': self.request.user}
                                 
    def get_queryset(self):
        if getattr(self,'swagger_fake_view',False):
            return Cart.objects.none()
        if self.request.user.is_staff:
            return Order.objects.prefetch_related('items__flower').all()
        return Order.objects.prefetch_related('items__flower').filter(user=self.request.user)
