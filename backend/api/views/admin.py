from django.db.models import Sum, Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.models import User, Store, Product, Order, Settings
from api.serializers import UserPublicSerializer, StoreSerializer, ProductSerializer, OrderSerializer, SettingsSerializer
from api.permissions import IsAdmin

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def get_dashboard_stats(request):
    total_users = User.objects.count()
    active_stores = Store.objects.filter(is_active=True).count()
    total_products = Product.objects.filter(is_active=True).count()
    total_orders = Order.objects.count()
    revenue_agg = Order.objects.filter(status__in=['processing', 'shipped', 'delivered']).aggregate(rev=Sum('total_price'))
    total_revenue = round(revenue_agg['rev'] or 0.0, 2)

    return Response({
        'success': True,
        'stats': {
            'totalUsers': total_users,
            'activeStores': active_stores,
            'totalProducts': total_products,
            'totalOrders': total_orders,
            'totalRevenue': total_revenue
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_users(request):
    role = request.GET.get('role')
    qs = User.objects.all().order_by('-created_at')
    if role:
        qs = qs.filter(role=role)
    return Response({'success': True, 'users': UserPublicSerializer(qs, many=True).data})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_delete_user(request, pk):
    try:
        user = User.objects.get(pk=pk)
        user.delete()
        return Response({'success': True, 'message': 'User deleted'})
    except User.DoesNotExist:
        return Response({'success': False, 'message': 'User not found'}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_stores(request):
    qs = Store.objects.all().order_by('-created_at')
    return Response({'success': True, 'stores': StoreSerializer(qs, many=True).data})

@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_store_status(request, pk):
    try:
        store = Store.objects.get(pk=pk)
        store.is_active = bool(request.data.get('isActive', store.is_active))
        store.save(update_fields=['is_active'])
        return Response({'success': True, 'store': StoreSerializer(store).data})
    except Store.DoesNotExist:
        return Response({'success': False, 'message': 'Store not found'}, status=404)

@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_store_verify(request, pk):
    try:
        store = Store.objects.get(pk=pk)
        store.is_verified = bool(request.data.get('isVerified', True))
        store.save(update_fields=['is_verified'])
        return Response({'success': True, 'store': StoreSerializer(store).data})
    except Store.DoesNotExist:
        return Response({'success': False, 'message': 'Store not found'}, status=404)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_delete_store(request, pk):
    try:
        store = Store.objects.get(pk=pk)
        store.delete()
        return Response({'success': True, 'message': 'Store deleted'})
    except Store.DoesNotExist:
        return Response({'success': False, 'message': 'Store not found'}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_products(request):
    qs = Product.objects.all().order_by('-created_at')
    return Response({'success': True, 'products': ProductSerializer(qs, many=True).data})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_delete_product(request, pk):
    try:
        prod = Product.objects.get(pk=pk)
        prod.delete()
        return Response({'success': True, 'message': 'Product deleted'})
    except Product.DoesNotExist:
        return Response({'success': False, 'message': 'Product not found'}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_orders(request):
    qs = Order.objects.all().order_by('-created_at')
    return Response({'success': True, 'orders': OrderSerializer(qs, many=True).data})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_delete_order(request, pk):
    try:
        order = Order.objects.get(pk=pk)
        order.delete()
        return Response({'success': True, 'message': 'Order deleted'})
    except Order.DoesNotExist:
        return Response({'success': False, 'message': 'Order not found'}, status=404)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_settings(request):
    settings, _ = Settings.objects.get_or_create(id=True)
    if request.method == 'GET':
        return Response({'success': True, 'settings': SettingsSerializer(settings).data})
    elif request.method == 'PUT':
        if 'tax_rate' in request.data:
            settings.tax_rate = float(request.data['tax_rate'])
        if 'shipping_fee' in request.data:
            settings.shipping_fee = float(request.data['shipping_fee'])
        if 'fixed_fee_per_order' in request.data:
            settings.fixed_fee_per_order = float(request.data['fixed_fee_per_order'])
        settings.updated_by = request.user
        settings.save()
        return Response({'success': True, 'settings': SettingsSerializer(settings).data})
