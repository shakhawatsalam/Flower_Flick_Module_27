from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Cart, CartItem, Order, OrderItem
from orders import serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import  OrderService
# Create your views here.


class CartViewSet(viewsets.ModelViewSet):
    queryset =  Cart.objects.all()
    serializer_class = serializers.CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Create a new cart for the authenticated user.

        This method ensures that the cart is associated with the currently authenticated user.
        """
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """
        Retrieve a list of carts for the authenticated user.

        This endpoint returns a list of carts associated with the currently authenticated user.
        """
        if getattr(self, 'swagger_fake_view', False):
            return Cart.objects.none()
        return Cart.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """
        Retrieve a list of carts for the authenticated user.

        This endpoint returns a paginated list of carts associated with the currently authenticated user.
        """
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific cart by ID.

        This endpoint returns details of a specific cart identified by its ID.
        """
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        Create a new cart for the authenticated user.

        This endpoint allows authenticated users to create a new cart.

      
        """
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Update an existing cart.

        This endpoint allows authenticated users to update an existing cart.

        """
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Partially update an existing cart.

        This endpoint allows authenticated users to partially update an existing cart.

        """
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a cart.

        This endpoint allows authenticated users to delete a cart.
        """
        return super().destroy(request, *args, **kwargs)
 
 
    
class CartItemViewSet(viewsets.ModelViewSet):
    http_method_names =['get','post', 'patch', 'delete']
    queryset = CartItem.objects.all()
    
    def get_serializer_class(self):
        """
        Determine the serializer class based on the request method.
        """
        if self.request.method == 'POST':
            return serializers.AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return serializers.UpdateCartItemSerializer
        return serializers.CartItemSerializer

    def get_serializer_context(self):
        """
        Add the cart_id to the serializer context.
        """
        context = super().get_serializer_context()
        if getattr(self, 'swagger_fake_view', False):
            return context
        return {'cart_id': self.kwargs.get('cart_pk')}

    def get_queryset(self):
        """
        Retrieve a list of cart items for a specific cart.

        This endpoint returns a list of cart items associated with a specific cart identified by `cart_pk`.
        """
        return CartItem.objects.select_related('flower').filter(cart_id=self.kwargs.get('cart_pk'))

    def list(self, request, *args, **kwargs):
        """
        Retrieve a list of cart items for a specific cart.

        This endpoint returns a paginated list of cart items associated with a specific cart identified by `cart_pk`.
        """
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific cart item by ID.

        This endpoint returns details of a specific cart item identified by its ID.
        """
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        Add a new item to a specific cart.

        This endpoint allows authenticated users to add a new item to a specific cart identified by `cart_pk`.
        """
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Update an existing cart item.

        This endpoint allows authenticated users to update an existing cart item identified by its ID.

        """
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Partially update an existing cart item.

        This endpoint allows authenticated users to partially update an existing cart item identified by its ID.

        """
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a cart item.

        This endpoint allows authenticated users to delete a cart item identified by its ID.

        """
        return super().destroy(request, *args, **kwargs)
    
    
    
    



      
class OrderViewSet(viewsets.ModelViewSet):
    http_method_names = ['get','post', 'delete', 'patch', 'head', 'options']
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """
        Determine the permission classes based on the action.
        """
        if self.action in ['update_status', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        """
        Determine the serializer class based on the action.
        """
        if self.action == 'cancel':
            return serializers.EmptyOrderSerializer
        if self.action == 'create':
            return serializers.CreateOrderSerializer
        return serializers.OrderSerializer

    def get_serializer_context(self):
        """
        Add the user_id and user to the serializer context.
        """
        context = super().get_serializer_context()
        if getattr(self, 'swagger_fake_view', False):
            return context
        return {'user_id': self.request.user.id, 'user': self.request.user}

    def get_queryset(self):
        """
        Retrieve a list of orders based on the user's role.

        This endpoint returns a list of orders. If the user is an admin, it returns all orders.
        Otherwise, it returns only the orders belonging to the authenticated user.
        """
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        if self.request.user.is_staff:
            return Order.objects.prefetch_related('items__flower').all()
        return Order.objects.prefetch_related('items__flower').filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """
        Retrieve a list of orders.

        This endpoint returns a paginated list of orders. If the user is an admin, it returns all orders.
        Otherwise, it returns only the orders belonging to the authenticated user.
        """
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific order by ID.

        This endpoint returns details of a specific order identified by its ID.
        """
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        Create a new order.

        This endpoint allows authenticated users to create a new order.

        """
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Update an existing order.

        This endpoint allows authenticated users to update an existing order.

     
       
        """
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Partially update an existing order.

        This endpoint allows authenticated users to partially update an existing order.

        """
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Delete an order.

        This endpoint allows admin users to delete an order.


        """
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def cancel(self, request, pk=None):
        """
        Cancel an order.

        This endpoint allows authenticated users to cancel a specific order identified by its ID.

        """
        order = self.get_object()
        OrderService.cancel_order(order=order, user=request.user)
        return Response({'status': 'Order canceled'})

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAuthenticated])
    def update_status(self, request, pk=None):
        """
        Update the status of an order.

        This endpoint allows authenticated users to update the status of a specific order identified by its ID.

        """
        order = self.get_object()
        serializer = UpdateOrderSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)  # Raise exception for validation errors
        serializer.save()
        return Response({'status': f'Order status updated to {request.data["status"]}'})
