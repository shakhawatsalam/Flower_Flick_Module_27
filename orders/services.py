from orders.models import Order, Cart, OrderItem
from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.conf import settings
from django.core.mail import send_mail
class OrderService:
    @staticmethod
    def create_order(user_id, cart_id):
        with transaction.atomic():
            
            cart = Cart.objects.get(pk=cart_id)
            cart_items = cart.items.select_related('flower').all()
            
            total_price = sum([item.flower.price * item.quantity for item in cart_items])
            
            order = Order.objects.create(user_id=user_id, total_price=total_price)
            

            order_items = [
                OrderItem(
                    order = order,
                    flower = item.flower,
                    price = item.flower.price,
                    quantity = item.quantity,
                    total_price = item.flower.price * item.quantity 
                ) for item in cart_items
            ]
        
            OrderItem.objects.bulk_create(order_items)
            
            # Reduce flower quantities
            for item in cart_items:
                flower = item.flower
                flower.quantity -= item.quantity
                flower.save()

            # Send order confirmation email
            user_email = order.user.email
            subject = 'Order Confirmation'
            message = f'Thank you for your order! Your order ID is {order.id}.'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [user_email]

            send_mail(subject, message, from_email, recipient_list)
          
            
            cart.delete()
        
            return order
        
        
    @staticmethod
    def cancel_order(order, user):
        if  user.is_staff:
            order.status = Order.CANCELED
            order.save()
            return order
        if order.user != user:
            raise PermissionDenied({'detail': "You can only cancel your own order"})

        if order.status == Order.COMPLETED:
            raise ValidationError({'detail': 'You can not cancel an order'})
        
        
        order.status = Order.CANCELED
        order.save()
        return order
        
        
        
        
