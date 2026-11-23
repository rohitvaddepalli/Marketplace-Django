from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.models import Store, Product
from api.serializers import StoreSerializer, ProductSerializer
from api.permissions import IsSeller

@api_view(['GET', 'POST'])
def stores_list(request):
    if request.method == 'GET':
        qs = Store.objects.filter(is_active=True)
        category = request.GET.get('category')
        search = request.GET.get('search')

        if category:
            qs = qs.filter(category__iexact=category)
        if search:
            qs = qs.filter(name__icontains=search)

        serializer = StoreSerializer(qs.order_by('-rating', '-created_at'), many=True)
        return Response({'success': True, 'stores': serializer.data})

    elif request.method == 'POST':
        if not request.user or not request.user.is_authenticated:
            return Response({'success': False, 'message': 'Authentication required'}, status=401)
        if getattr(request.user, 'role', '') != 'seller':
            return Response({'success': False, 'message': 'Only sellers can create a store'}, status=403)

        if Store.objects.filter(owner_id=request.user.id).exists():
            return Response({'success': False, 'message': 'Seller already has a store'}, status=400)

        data = request.data.copy()
        serializer = StoreSerializer(data=data)
        if serializer.is_valid():
            store = Store.objects.create(
                owner=request.user,
                name=serializer.validated_data['name'],
                description=serializer.validated_data.get('description', ''),
                category=serializer.validated_data['category'],
                logo=serializer.validated_data.get('logo', 'https://via.placeholder.com/150'),
                banner=serializer.validated_data.get('banner', 'https://via.placeholder.com/1200x300'),
                address=serializer.validated_data.get('address', {}),
                contact=serializer.validated_data.get('contact', {}),
                business_hours=serializer.validated_data.get('business_hours', '')
            )
            return Response({'success': True, 'store': StoreSerializer(store).data}, status=201)
        return Response({'success': False, 'message': serializer.errors}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSeller])
def get_my_store(request):
    try:
        store = Store.objects.get(owner_id=request.user.id)
        return Response({'success': True, 'store': StoreSerializer(store).data})
    except Store.DoesNotExist:
        return Response({'success': False, 'message': 'Store not found'}, status=404)

@api_view(['GET', 'PUT', 'DELETE'])
def store_detail(request, pk):
    try:
        store = Store.objects.get(pk=pk)
    except Store.DoesNotExist:
        return Response({'success': False, 'message': 'Store not found'}, status=404)

    if request.method == 'GET':
        products = Product.objects.filter(store=store, is_active=True).order_by('-created_at')
        return Response({
            'success': True,
            'store': StoreSerializer(store).data,
            'products': ProductSerializer(products, many=True).data
        })

    # Mutation endpoints require authentication and ownership/admin
    if not request.user or not request.user.is_authenticated:
        return Response({'success': False, 'message': 'Authentication required'}, status=401)

    if store.owner_id != request.user.id and getattr(request.user, 'role', '') != 'admin':
        return Response({'success': False, 'message': 'Not authorized'}, status=403)

    if request.method == 'PUT':
        serializer = StoreSerializer(store, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'store': serializer.data})
        return Response({'success': False, 'message': serializer.errors}, status=400)

    elif request.method == 'DELETE':
        store.delete()
        return Response({'success': True, 'message': 'Store deleted successfully'})
