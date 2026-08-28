from django.conf import settings as main_settings
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from sslcommerz_lib import SSLCOMMERZ

from orders import serializers
from orders.services import OrderService
from .models import Cart, CartItem, Order, OrderItem


# ==========================================
# CART VIEWS
# ==========================================
class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = serializers.CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Cart.objects.none()
        return Cart.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        existing_cart = Cart.objects.filter(user=request.user).first()
        if existing_cart:
            serializer = self.get_serializer(existing_cart)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return super().create(request, *args, **kwargs)


class CartItemViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

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
        # Optimized with select_related + prefetch_related for images
        return (
            CartItem.objects
            .select_related('flower')
            .prefetch_related('flower__images')
            .filter(cart_id=self.kwargs.get('cart_pk'))
            .order_by('-quantity')
        )


# ==========================================
# ORDER VIEWS
# ==========================================
class OrderViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'patch', 'head', 'options']
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['update_status', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CreateOrderSerializer
        if self.action == 'update_status':
            return serializers.UpdateOrderSerialier
        return serializers.OrderSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if getattr(self, 'swagger_fake_view', False):
            return context
        return {'user_id': self.request.user.id, 'user': self.request.user}

    def get_queryset(self):
        """
        Optimized with prefetch_related down to 'items__flower__images'
        to avoid N+1 query timeouts (504).
        """
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()

        base_queryset = Order.objects.prefetch_related('items__flower__images')

        if self.request.user.is_staff:
            return base_queryset.all()
        return base_queryset.filter(user=self.request.user)

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAdminUser])
    def update_status(self, request, pk=None):
        order = self.get_object()
        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': f'Order status updated to {request.data.get("status")}'})


# ==========================================
# PAYMENT INTEGRATION (SSLCOMMERZ)
# ==========================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    user = request.user
    amount = request.data.get("amount")
    order_id = request.data.get('orderId')

    settings = {
        'store_id': 'flowe6810bec8ccd8a',
        'store_pass': 'flowe6810bec8ccd8a@ssl',
        'issandbox': True
    }
    sslcz = SSLCOMMERZ(settings)
    
    frontend_url = getattr(main_settings, 'FRONTEND_URL', 'http://localhost:5173')
    backend_url = getattr(main_settings, 'BACKEND_URL', 'http://localhost:8000')

    post_body = {
        'total_amount': amount,
        'currency': "BDT",
        'tran_id': f"trx_{order_id}",
        'success_url': f"{backend_url}/api/v1/payment/success/",
        'fail_url': f"{frontend_url}/payment-failed",
        'cancel_url': f"{frontend_url}/orders",
        'emi_option': 0,
        'cus_name': f"{user.first_name} {user.last_name}".strip() or "Customer",
        'cus_email': user.email or "customer@example.com",
        'cus_phone': "01700000000",
        'cus_add1': "customer address",
        'cus_city': "Dhaka",
        'cus_country': "Bangladesh",
        'shipping_method': "NO",
        'num_of_item': 1,
        'product_name': "Order Payment",
        'product_category': "Flowers",
        'product_profile': "general"
    }

    response = sslcz.createSession(post_body)
    if response.get("status") == "SUCCESS":
        return Response({"payment_url": response["GatewayPageURL"]})
    return Response({"error": "Payment initiation failed", "details": response}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def payment_success(request):
    tran_id = request.data.get("tran_id")
    if not tran_id or '_' not in tran_id:
        return Response({"error": "Invalid transaction ID"}, status=status.HTTP_400_BAD_REQUEST)

    order_id = tran_id.split('_')[1]
    order = get_object_or_404(Order, id=order_id)
    order.status = "Completed"
    order.save()

    frontend_url = getattr(main_settings, 'FRONTEND_URL', 'http://localhost:5173')
    return redirect(f"{frontend_url}/payment-success")