import csv
from django.http import HttpResponse
from django.db.models import F, Avg
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.models import Product, Store, Review
from api.serializers import ProductSerializer, ReviewSerializer
from api.permissions import IsSeller

@api_view(['GET', 'POST'])
def products_list(request):
    if request.method == 'GET':
        qs = Product.objects.filter(is_active=True)

        category = request.GET.get('category')
        search = request.GET.get('search')
        min_price = request.GET.get('minPrice')
        max_price = request.GET.get('maxPrice')
        brand = request.GET.get('brand')
        sort = request.GET.get('sort')

        if category:
            qs = qs.filter(category__iexact=category)
        if search:
            qs = qs.filter(name__icontains=search)
        if min_price:
            try:
                qs = qs.filter(price__gte=float(min_price))
            except ValueError:
                pass
        if max_price:
            try:
                qs = qs.filter(price__lte=float(max_price))
            except ValueError:
                pass
        if brand:
            qs = qs.filter(brand__iexact=brand)

        if sort == 'price-asc':
            qs = qs.order_by('price')
        elif sort == 'price-desc':
            qs = qs.order_by('-price')
        elif sort == 'rating':
            qs = qs.order_by('-rating')
        else:
            qs = qs.order_by('-created_at')

        total = qs.count()
        page = max(1, int(request.GET.get('page', 1)))
        limit = max(1, min(100, int(request.GET.get('limit', 12))))
        start = (page - 1) * limit
        end = start + limit

        serializer = ProductSerializer(qs[start:end], many=True)
        return Response({
            'success': True,
            'products': serializer.data,
            'count': total,
            'totalPages': (total + limit - 1) // limit,
            'currentPage': page
        })

    elif request.method == 'POST':
        if not request.user or not request.user.is_authenticated:
            return Response({'success': False, 'message': 'Authentication required'}, status=401)
        if getattr(request.user, 'role', '') != 'seller':
            return Response({'success': False, 'message': 'Only sellers can create products'}, status=403)

        store = Store.objects.filter(owner_id=request.user.id).first()
        if not store:
            return Response({'success': False, 'message': 'No store found for this seller'}, status=400)

        data = request.data.copy()
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            product = Product.objects.create(
                store=store,
                seller=request.user,
                name=serializer.validated_data['name'],
                description=serializer.validated_data['description'],
                price=serializer.validated_data['price'],
                compare_at_price=serializer.validated_data.get('compare_at_price'),
                category=serializer.validated_data['category'],
                subcategory=serializer.validated_data.get('subcategory', ''),
                brand=serializer.validated_data.get('brand', ''),
                images=serializer.validated_data.get('images', []),
                stock=serializer.validated_data.get('stock', 0),
                tags=serializer.validated_data.get('tags', []),
                specifications=serializer.validated_data.get('specifications', {}),
                variants=serializer.validated_data.get('variants', []),
                low_stock_threshold=serializer.validated_data.get('low_stock_threshold', 10),
                bulk_discounts=serializer.validated_data.get('bulk_discounts', [])
            )
            return Response({'success': True, 'product': ProductSerializer(product).data}, status=201)
        return Response({'success': False, 'message': serializer.errors}, status=400)

@api_view(['GET'])
def featured_products(request):
    products = Product.objects.filter(is_active=True).order_by('-rating')[:8]
    return Response({'success': True, 'products': ProductSerializer(products, many=True).data})

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSeller])
def get_my_products(request):
    qs = Product.objects.filter(seller_id=request.user.id).order_by('-created_at')
    page = max(1, int(request.GET.get('page', 1)))
    limit = max(1, min(100, int(request.GET.get('limit', 20))))
    start = (page - 1) * limit
    end = start + limit
    total = qs.count()

    serializer = ProductSerializer(qs[start:end], many=True)
    return Response({
        'success': True,
        'products': serializer.data,
        'count': total,
        'totalPages': (total + limit - 1) // limit
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSeller])
def get_low_stock_products(request):
    qs = Product.objects.filter(seller_id=request.user.id, stock__lte=F('low_stock_threshold')).order_by('stock')
    serializer = ProductSerializer(qs, many=True)
    return Response({'success': True, 'products': serializer.data})

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSeller])
def bulk_import_products(request):
    store = Store.objects.filter(owner_id=request.user.id).first()
    if not store:
        return Response({'success': False, 'message': 'Store required'}, status=400)

    items = request.data if isinstance(request.data, list) else request.data.get('products', [])
    created = 0
    for item in items:
        try:
            Product.objects.create(
                store=store,
                seller=request.user,
                name=item['name'],
                description=item.get('description', ''),
                price=float(item['price']),
                category=item['category'],
                stock=int(item.get('stock', 0)),
                brand=item.get('brand', '')
            )
            created += 1
        except Exception:
            continue

    return Response({'success': True, 'imported': created})

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSeller])
def export_products(request):
    products = Product.objects.filter(seller_id=request.user.id)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Price', 'Category', 'Stock', 'Rating'])
    for p in products:
        writer.writerow([p.id, p.name, p.price, p.category, p.stock, p.rating])

    return response

@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({'success': False, 'message': 'Product not found'}, status=404)

    if request.method == 'GET':
        return Response({'success': True, 'product': ProductSerializer(product).data})

    if not request.user or not request.user.is_authenticated:
        return Response({'success': False, 'message': 'Authentication required'}, status=401)

    if product.seller_id != request.user.id and getattr(request.user, 'role', '') != 'admin':
        return Response({'success': False, 'message': 'Not authorized'}, status=403)

    if request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'product': serializer.data})
        return Response({'success': False, 'message': serializer.errors}, status=400)

    elif request.method == 'DELETE':
        product.delete()
        return Response({'success': True, 'message': 'Product removed successfully'})

@api_view(['GET', 'POST'])
def product_reviews(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({'success': False, 'message': 'Product not found'}, status=404)

    if request.method == 'GET':
        reviews = Review.objects.filter(product=product).order_by('-created_at')
        return Response({'success': True, 'reviews': ReviewSerializer(reviews, many=True).data})

    elif request.method == 'POST':
        if not request.user or not request.user.is_authenticated:
            return Response({'success': False, 'message': 'Authentication required'}, status=401)

        rating = request.data.get('rating')
        comment = request.data.get('comment', '').strip()
        if not rating or not comment:
            return Response({'success': False, 'message': 'Rating and comment are required'}, status=400)

        review, _ = Review.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={
                'rating': int(rating),
                'comment': comment,
                'media': request.data.get('media', [])
            }
        )

        # Update product average rating and review_count
        agg = Review.objects.filter(product=product).aggregate(avg=Avg('rating'))
        product.rating = round(agg['avg'] or 0, 1)
        product.review_count = Review.objects.filter(product=product).count()
        product.save(update_fields=['rating', 'review_count'])

        return Response({'success': True, 'review': ReviewSerializer(review).data}, status=201)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def mark_review_helpful(request, product_id, review_id):
    try:
        review = Review.objects.get(id=review_id, product_id=product_id)
        review.helpful_votes = F('helpful_votes') + 1
        review.save(update_fields=['helpful_votes'])
        review.refresh_from_db()
        return Response({'success': True, 'helpfulVotes': review.helpful_votes})
    except Review.DoesNotExist:
        return Response({'success': False, 'message': 'Review not found'}, status=404)
