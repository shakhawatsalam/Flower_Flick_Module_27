from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from flowers.serializers import FlowerSerializer
from flowers.models import Flower


class SimpleFlowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flower
        fields = ['id', 'title', 'price']
        

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
            self.instance = cart_item.save()
            
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
            
        return self.instance
    def validate_flower_id(self, value):
        if not Flower.objects.filter(pk=value).exists():
            raise serializers.ValidationError(f"flower with id {value} does not exists")
        return value
        
        
class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class CartItemSerializer(serializers.ModelSerializer):
    flower = SimpleFlowerSerializer()
    total_price = serializers.SerializerMethodField(method_name="get_total_price")

    class Meta:
        model = CartItem
        fields = ['id', 'flower', 'quantity', 'total_price']
        read_only_fields = ['cart']
    
    def get_total_price(self, obj):
        return obj.quantity * obj.flower.price
    
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
    
    

class OrderItemSerializer(serializers.ModelSerializer):
    flower = FlowerSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'flower', 'quantity', 'price', 'total_price']
        
        

class OrderSerializer(serializers.ModelSerializer):
    items =  OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total_price', 'created_at', 'items']