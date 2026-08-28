from django.utils.timezone import localtime
from rest_framework import serializers

from flowers.models import Flower
from flowers.serializers import FlowerImageSerializer, FlowerSerializer
from orders.services import OrderService
from .models import Cart, CartItem, Order, OrderItem


# ==========================================
# FLOWER SERIALIZERS (FOR NESTING)
# ==========================================
class SimpleFlowerSerializer(serializers.ModelSerializer):
    images = FlowerImageSerializer(many=True, read_only=True)

    class Meta:
        model = Flower
        fields = ['id', 'title', 'price', 'images']


# ==========================================
# CART SERIALIZERS
# ==========================================
class AddCartItemSerializer(serializers.ModelSerializer):
    flower_id = serializers.IntegerField()

    class Meta:
        model = CartItem
        fields = ['id', 'flower_id', 'quantity']

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        flower_id = self.validated_data['flower_id']
        quantity = self.validated_data['quantity']

        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, flower_id=flower_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)

        return self.instance

    def validate_flower_id(self, value):
        if not Flower.objects.filter(pk=value).exists():
            raise serializers.ValidationError(f"flower with id {value} does not exist")
        return value


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class CartItemSerializer(serializers.ModelSerializer):
    flower = SimpleFlowerSerializer(read_only=True)
    total_price = serializers.SerializerMethodField(method_name="get_total_price")

    class Meta:
        model = CartItem
        fields = ['id', 'flower', 'quantity', 'total_price']
        read_only_fields = ['cart']

    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.flower.price


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name='get_total_price')

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price', 'created_at']
        read_only_fields = ['user']

    def get_total_price(self, obj):
        return sum([item.quantity * item.flower.price for item in obj.items.all()])

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['items'] = sorted(rep['items'], key=lambda item: item['id'])
        return rep


# ==========================================
# ORDER SERIALIZERS
# ==========================================
class EmptyOrderSerializer(serializers.Serializer):
    pass


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError("No Cart with this Id")
        if not CartItem.objects.filter(cart_id=cart_id).exists():
            raise serializers.ValidationError("Cart is Empty")
        return cart_id

    def create(self, validated_data):
        user_id = self.context['user_id']
        cart_id = validated_data['cart_id']
        return OrderService.create_order(user_id=user_id, cart_id=cart_id)

    def to_representation(self, instance):
        # Pass self.context so nested serializers (like flower images) resolve absolute URLs properly
        return OrderSerializer(instance, context=self.context).data


class OrderItemSerializer(serializers.ModelSerializer):
    flower = SimpleFlowerSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'flower', 'quantity', 'price', 'total_price']


class UpdateOrderSerialier(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    created_at = serializers.SerializerMethodField(method_name='get_formatted_created_at')

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total_price', 'created_at', 'items']

    def get_formatted_created_at(self, obj):
        if obj.created_at:
            return localtime(obj.created_at).strftime("%B %d, %Y, %I:%M %p")
        return None