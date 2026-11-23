from rest_framework import serializers
from api.models import User, Store, Product, Order, OrderItem, Review, Settings, Message

class UserPublicSerializer(serializers.ModelSerializer):
    _id = serializers.UUIDField(source='id', read_only=True)
    recentlyViewed = serializers.JSONField(source='recently_viewed', required=False)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = User
        fields = [
            '_id', 'name', 'email', 'role', 'avatar', 'phone',
            'address', 'wishlist', 'recentlyViewed', 'createdAt'
        ]

class StoreSerializer(serializers.ModelSerializer):
    _id = serializers.UUIDField(source='id', read_only=True)
    owner = serializers.UUIDField(source='owner_id', read_only=True)
    reviewCount = serializers.IntegerField(source='review_count', read_only=True)
    isActive = serializers.BooleanField(source='is_active', read_only=True)
    isVerified = serializers.BooleanField(source='is_verified', read_only=True)
    rating = serializers.FloatField(read_only=True)
    businessHours = serializers.CharField(source='business_hours', required=False, allow_blank=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Store
        fields = [
            '_id', 'owner', 'name', 'description', 'logo', 'banner', 'category',
            'address', 'contact', 'rating', 'reviewCount', 'isActive', 'isVerified',
            'businessHours', 'createdAt'
        ]

class ProductSerializer(serializers.ModelSerializer):
    _id = serializers.UUIDField(source='id', read_only=True)
    store = serializers.UUIDField(source='store_id', read_only=True)
    seller = serializers.UUIDField(source='seller_id', read_only=True)
    compareAtPrice = serializers.FloatField(source='compare_at_price', required=False, allow_null=True)
    reviewCount = serializers.IntegerField(source='review_count', read_only=True)
    rating = serializers.FloatField(read_only=True)
    lowStockThreshold = serializers.IntegerField(source='low_stock_threshold', required=False)
    bulkDiscounts = serializers.JSONField(source='bulk_discounts', required=False)
    isActive = serializers.BooleanField(source='is_active', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)

    class Meta:
        model = Product
        fields = [
            '_id', 'store', 'seller', 'name', 'description', 'price', 'compareAtPrice',
            'category', 'subcategory', 'brand', 'images', 'stock', 'rating', 'reviewCount',
            'tags', 'specifications', 'variants', 'lowStockThreshold', 'bulkDiscounts',
            'isActive', 'createdAt', 'updatedAt'
        ]

class ReviewUserSerializer(serializers.ModelSerializer):
    _id = serializers.UUIDField(source='id', read_only=True)

    class Meta:
        model = User
        fields = ['_id', 'name', 'avatar']

class ReviewSerializer(serializers.ModelSerializer):
    _id = serializers.UUIDField(source='id', read_only=True)
    user = ReviewUserSerializer(read_only=True)
    productId = serializers.UUIDField(source='product_id', read_only=True)
    isVerifiedPurchase = serializers.BooleanField(source='is_verified_purchase', read_only=True)
    helpfulVotes = serializers.IntegerField(source='helpful_votes', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Review
        fields = [
            '_id', 'productId', 'user', 'rating', 'comment',
            'isVerifiedPurchase', 'media', 'helpfulVotes', 'createdAt'
        ]

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.UUIDField(source='product_id', read_only=True)
    store = serializers.UUIDField(source='store_id', read_only=True)
    seller = serializers.UUIDField(source='seller_id', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['line_no', 'product', 'store', 'seller', 'name', 'price', 'quantity', 'image']

class OrderSerializer(serializers.ModelSerializer):
    _id = serializers.UUIDField(source='id', read_only=True)
    orderNumber = serializers.CharField(source='order_number', read_only=True)
    customer = serializers.UUIDField(source='customer_id', read_only=True)
    guestInfo = serializers.JSONField(source='guest_info', required=False)
    shippingAddress = serializers.JSONField(source='shipping_address')
    paymentMethod = serializers.CharField(source='payment_method')
    paymentStatus = serializers.CharField(source='payment_status', required=False)
    itemsPrice = serializers.FloatField(source='items_price')
    shippingPrice = serializers.FloatField(source='shipping_price', required=False)
    taxPrice = serializers.FloatField(source='tax_price', required=False)
    totalPrice = serializers.FloatField(source='total_price')
    deliveredAt = serializers.DateTimeField(source='delivered_at', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            '_id', 'orderNumber', 'customer', 'guestInfo', 'shippingAddress',
            'paymentMethod', 'paymentStatus', 'itemsPrice', 'shippingPrice',
            'taxPrice', 'totalPrice', 'status', 'deliveredAt', 'createdAt', 'items'
        ]

class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = ['tax_rate', 'shipping_fee', 'fixed_fee_per_order', 'updated_at']

class MessageSerializer(serializers.ModelSerializer):
    _id = serializers.UUIDField(source='id', read_only=True)
    roomId = serializers.CharField(source='room_id', read_only=True)
    sender = ReviewUserSerializer(read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Message
        fields = ['_id', 'roomId', 'text', 'sender', 'createdAt']
