from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError

from orders.models import Cart, CartItem, Order, OrderItem


class OrderService:
    @staticmethod
    def create_order(user_id, cart_id):
        with transaction.atomic():
            # 1. Fetch Cart
            try:
                cart = Cart.objects.get(pk=cart_id)
            except Cart.DoesNotExist:
                raise ValidationError({"detail": "Cart does not exist."})

            cart_items = CartItem.objects.select_related('flower').filter(cart_id=cart_id)

            if not cart_items.exists():
                raise ValidationError({"detail": "Cannot create order from an empty cart."})

            # 2. Check stock availability before deducting
            for item in cart_items:
                if item.flower.quantity < item.quantity:
                    raise ValidationError({
                        "detail": f"Not enough stock for '{item.flower.title}'. Available: {item.flower.quantity}, Requested: {item.quantity}"
                    })

            # 3. Calculate Total Price
            total_price = sum(item.flower.price * item.quantity for item in cart_items)

            # 4. Create Order
            order = Order.objects.create(
                user_id=user_id,
                total_price=total_price,
                status='Pending'
            )

            # 5. Create Order Items
            order_items = [
                OrderItem(
                    order=order,
                    flower=item.flower,
                    price=item.flower.price,
                    quantity=item.quantity,
                    total_price=item.flower.price * item.quantity
                )
                for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)

            # 6. Reduce Flower Stock
            for item in cart_items:
                flower = item.flower
                flower.quantity -= item.quantity
                flower.save(update_fields=['quantity'])

            # 7. Safely Send Email (will not crash the request if SMTP fails)
            user_email = order.user.email
            if user_email:
                subject = 'Order Confirmation'
                message = f'Thank you for your order! Your order ID is {order.id}.'
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER)
                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=from_email,
                        recipient_list=[user_email],
                        fail_silently=True  # <-- Prevents 500 error if mail server fails
                    )
                except Exception as e:
                    print(f"Email failed to send: {e}")

            # 8. Delete Cart
            cart.delete()

            return order

    @staticmethod
    def cancel_order(order, user):
        if user.is_staff:
            order.status = Order.CANCELED
            order.save()
            return order

        if order.user != user:
            raise PermissionDenied({'detail': "You can only cancel your own order"})

        if order.status == Order.COMPLETED:
            raise ValidationError({'detail': 'You cannot cancel a completed order'})

        order.status = Order.CANCELED
        order.save()
        return order