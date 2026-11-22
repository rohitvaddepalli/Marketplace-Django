import uuid
from django.db import transaction
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.models import Order, OrderItem, Product, Store
from api.serializers import OrderSerializer
from api.permissions import IsSeller, IsAdmin, IsCustomer

@api_view(['GET', 'POST'])
def orders_root(request):
    if request.method == 'POST':
        user = request.user if (request.user and request.user.is_authenticated) else None
        data = request.data

        items_data = data.get('items', [])
        if not items_data:
            return Response({'success': False, 'message': 'Order must contain items'}, status=400)

        shipping_address = data.get('shippingAddress', {})
        payment_method = data.get('paymentMethod', 'card')
        guest_info = data.get('guestInfo', {}) if not user else {}

        with transaction.atomic():
            items_price = 0.0
            order_items_to_create = []

            for index, item in enumerate(items_data):
                product_id = item.get('product')
                quantity = int(item.get('quantity', 1))

                product = Product.objects.select_for_update().filter(id=product_id, is_active=True).first()
                if not product:
                    return Response({'success': False, 'message': f'Product not found: {product_id}'}, status=404)

                if product.stock < quantity:
                    return Response({'success': False, 'message': f'Insufficient stock for {product.name}'}, status=400)

                product.stock -= quantity
                product.save(update_fields=['stock'])

                line_price = product.price * quantity
                items_price += line_price

                order_items_to_create.append({
                    'line_no': index + 1,
                    'product': product,
                    'store': product.store,
                    'seller': product.seller,
                    'name': product.name,
                    'price': product.price,
                    'quantity': quantity,
                    'image': product.images[0] if product.images else ''
                })

            shipping_price = float(data.get('shippingPrice', 10.0))
            tax_price = round(items_price * 0.08, 2)
            total_price = items_price + shipping_price + tax_price

            order = Order.objects.create(
                order_number=f"ORD-{uuid.uuid4().hex[:8].upper()}",
                customer=user,
                guest_info=guest_info,
                shipping_address=shipping_address,
                payment_method=payment_method,
                payment_status='pending',
                items_price=items_price,
                shipping_price=shipping_price,
                tax_price=tax_price,
                total_price=total_price,
                status='pending'
            )

            for oi in order_items_to_create:
                OrderItem.objects.create(
                    order=order,
                    line_no=oi['line_no'],
                    product=oi['product'],
                    store=oi['store'],
                    seller=oi['seller'],
                    name=oi['name'],
                    price=oi['price'],
                    quantity=oi['quantity'],
                    image=oi['image']
                )

        return Response({'success': True, 'order': OrderSerializer(order).data}, status=201)

    elif request.method == 'GET':
        if not request.user or not request.user.is_authenticated or getattr(request.user, 'role', '') != 'admin':
            return Response({'success': False, 'message': 'Admin access required'}, status=403)
        orders = Order.objects.all().order_by('-created_at')
        return Response({'success': True, 'orders': OrderSerializer(orders, many=True).data})

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsCustomer])
def get_my_orders(request):
    orders = Order.objects.filter(customer_id=request.user.id).order_by('-created_at')
    return Response({'success': True, 'orders': OrderSerializer(orders, many=True).data})

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSeller])
def get_seller_orders(request):
    order_ids = OrderItem.objects.filter(seller_id=request.user.id).values_list('order_id', flat=True).distinct()
    orders = Order.objects.filter(id__in=order_ids).order_by('-created_at')
    return Response({'success': True, 'orders': OrderSerializer(orders, many=True).data})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_detail(request, pk):
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response({'success': False, 'message': 'Order not found'}, status=404)

    is_customer = order.customer_id == request.user.id
    is_seller = OrderItem.objects.filter(order=order, seller_id=request.user.id).exists()
    is_admin = getattr(request.user, 'role', '') == 'admin'

    if not (is_customer or is_seller or is_admin):
        return Response({'success': False, 'message': 'Access denied'}, status=403)

    return Response({'success': True, 'order': OrderSerializer(order).data})

@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsSeller])
def update_order_status(request, pk):
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response({'success': False, 'message': 'Order not found'}, status=404)

    new_status = request.data.get('status')
    if new_status not in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
        return Response({'success': False, 'message': 'Invalid status'}, status=400)

    order.status = new_status
    if new_status == 'delivered':
        order.delivered_at = timezone.now()
        order.payment_status = 'completed'
    order.save()

    return Response({'success': True, 'order': OrderSerializer(order).data})

@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsCustomer])
def cancel_order(request, pk):
    try:
        order = Order.objects.get(pk=pk, customer_id=request.user.id)
    except Order.DoesNotExist:
        return Response({'success': False, 'message': 'Order not found'}, status=404)

    if order.status in ['shipped', 'delivered', 'cancelled']:
        return Response({'success': False, 'message': f'Cannot cancel order with status: {order.status}'}, status=400)

    with transaction.atomic():
        order.status = 'cancelled'
        order.save(update_fields=['status'])

        # Restore product stock
        for item in order.items.all():
            if item.product:
                Product.objects.filter(id=item.product.id).update(stock=F('stock') + item.quantity)

    return Response({'success': True, 'message': 'Order cancelled successfully'})
