from django.db.models import Sum, Count, Avg
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.models import Order, OrderItem, Product, User
from api.permissions import IsSeller, IsAdmin

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSeller])
def seller_sales_analytics(request):
    seller_items = OrderItem.objects.filter(seller_id=request.user.id)
    total_sales = seller_items.aggregate(total=Sum('price'))['total'] or 0.0
    total_units = seller_items.aggregate(units=Sum('quantity'))['units'] or 0
    distinct_orders = seller_items.values('order_id').distinct().count()

    return Response({
        'success': True,
        'analytics': {
            'totalRevenue': round(total_sales, 2),
            'totalUnitsSold': total_units,
            'totalOrders': distinct_orders
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSeller])
def seller_customer_analytics(request):
    customer_ids = OrderItem.objects.filter(seller_id=request.user.id).values_list('order__customer_id', flat=True).distinct()
    count = User.objects.filter(id__in=customer_ids).count()
    return Response({'success': True, 'totalCustomers': count})

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSeller])
def seller_inventory_forecast(request):
    low_stock = Product.objects.filter(seller_id=request.user.id, stock__lte=10).values('id', 'name', 'stock')
    return Response({'success': True, 'forecast': list(low_stock)})

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSeller])
def seller_product_analytics(request):
    top_products = OrderItem.objects.filter(seller_id=request.user.id)\
        .values('name')\
        .annotate(total_sold=Sum('quantity'), revenue=Sum('price'))\
        .order_by('-total_sold')[:10]
    return Response({'success': True, 'topProducts': list(top_products)})

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_sales_analytics(request):
    agg = Order.objects.filter(status__in=['processing', 'shipped', 'delivered'])\
        .aggregate(rev=Sum('total_price'), cnt=Count('id'))
    return Response({
        'success': True,
        'analytics': {
            'totalRevenue': round(agg['rev'] or 0.0, 2),
            'totalOrders': agg['cnt'] or 0
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_customer_analytics(request):
    customers = User.objects.filter(role='customer').count()
    sellers = User.objects.filter(role='seller').count()
    return Response({'success': True, 'customers': customers, 'sellers': sellers})

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_product_analytics(request):
    total = Product.objects.count()
    active = Product.objects.filter(is_active=True).count()
    return Response({'success': True, 'total': total, 'active': active})
