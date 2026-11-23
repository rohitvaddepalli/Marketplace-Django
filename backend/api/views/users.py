import uuid
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.models import Product
from api.serializers import ProductSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_wishlist(request):
    wishlist_ids = request.user.wishlist or []
    products = Product.objects.filter(id__in=wishlist_ids, is_active=True)
    return Response({'success': True, 'wishlist': ProductSerializer(products, many=True).data})

@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_wishlist_item(request, product_id):
    try:
        p_uuid = uuid.UUID(str(product_id))
    except ValueError:
        return Response({'success': False, 'message': 'Invalid product ID'}, status=400)

    user = request.user
    wishlist = list(user.wishlist or [])

    if request.method == 'POST':
        if p_uuid not in wishlist:
            wishlist.append(p_uuid)
            user.wishlist = wishlist
            user.save(update_fields=['wishlist'])
        return Response({'success': True, 'message': 'Added to wishlist', 'wishlist': user.wishlist})

    elif request.method == 'DELETE':
        if p_uuid in wishlist:
            wishlist.remove(p_uuid)
            user.wishlist = wishlist
            user.save(update_fields=['wishlist'])
        return Response({'success': True, 'message': 'Removed from wishlist', 'wishlist': user.wishlist})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recently_viewed(request):
    items = request.user.recently_viewed or []
    product_ids = [item.get('product') for item in items if isinstance(item, dict) and item.get('product')]
    products = Product.objects.filter(id__in=product_ids, is_active=True)
    prod_map = {str(p.id): ProductSerializer(p).data for p in products}

    results = []
    for item in items:
        pid = str(item.get('product'))
        if pid in prod_map:
            results.append({
                'product': prod_map[pid],
                'viewedAt': item.get('viewedAt')
            })

    return Response({'success': True, 'recentlyViewed': results})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_recently_viewed(request, product_id):
    user = request.user
    items = [i for i in (user.recently_viewed or []) if i.get('product') != str(product_id)]
    items.insert(0, {
        'product': str(product_id),
        'viewedAt': timezone.now().isoformat()
    })
    user.recently_viewed = items[:20]
    user.save(update_fields=['recently_viewed'])
    return Response({'success': True, 'recentlyViewed': user.recently_viewed})
