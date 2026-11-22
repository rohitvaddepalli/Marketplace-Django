import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField

class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clerk_user_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=[('customer', 'Customer'), ('seller', 'Seller'), ('admin', 'Admin')],
        default='customer'
    )
    avatar = models.TextField(default='https://api.dicebear.com/7.x/avataaars/svg?seed=default')
    phone = models.CharField(max_length=50, null=True, blank=True)
    address = models.JSONField(default=dict, blank=True)
    wishlist = ArrayField(models.UUIDField(), default=list, blank=True)
    recently_viewed = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'
        managed = False

    def __str__(self):
        return f"{self.name} ({self.email}) - {self.role}"

    @property
    def is_authenticated(self):
        return True


class Store(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, db_column='owner_id', related_name='store')
    name = models.CharField(max_length=255)
    description = models.TextField(default='', blank=True)
    logo = models.TextField(default='https://via.placeholder.com/150')
    banner = models.TextField(default='https://via.placeholder.com/1200x300')
    category = models.CharField(max_length=100)
    address = models.JSONField(default=dict, blank=True)
    contact = models.JSONField(default=dict, blank=True)
    rating = models.FloatField(default=0.0)
    review_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    business_hours = models.TextField(default='', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'stores'
        managed = False

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, db_column='store_id', related_name='products')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, db_column='seller_id', related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.FloatField()
    compare_at_price = models.FloatField(null=True, blank=True)
    category = models.CharField(max_length=100)
    subcategory = models.CharField(max_length=100, null=True, blank=True)
    brand = models.CharField(max_length=100, null=True, blank=True)
    images = ArrayField(models.TextField(), default=list, blank=True)
    stock = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    review_count = models.IntegerField(default=0)
    tags = ArrayField(models.CharField(max_length=50), default=list, blank=True)
    specifications = models.JSONField(default=dict, blank=True)
    variants = models.JSONField(default=list, blank=True)
    low_stock_threshold = models.IntegerField(default=10)
    bulk_discounts = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        managed = False

    def __str__(self):
        return self.name


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_column='customer_id', related_name='orders')
    guest_info = models.JSONField(default=dict, blank=True)
    shipping_address = models.JSONField(default=dict, blank=True)
    payment_method = models.CharField(max_length=20)
    payment_status = models.CharField(max_length=20, default='pending')
    items_price = models.FloatField()
    shipping_price = models.FloatField(default=0.0)
    tax_price = models.FloatField(default=0.0)
    total_price = models.FloatField()
    status = models.CharField(max_length=20, default='pending')
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'orders'
        managed = False

    def __str__(self):
        return self.order_number or str(self.id)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, db_column='order_id', related_name='items')
    line_no = models.IntegerField()
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, db_column='product_id')
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, db_column='store_id')
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_column='seller_id')
    name = models.CharField(max_length=255, null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    quantity = models.IntegerField()
    image = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'order_items'
        unique_together = (('order', 'line_no'),)
        managed = False


class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id', related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id', related_name='reviews')
    rating = models.IntegerField()
    comment = models.TextField(max_length=1000)
    is_verified_purchase = models.BooleanField(default=False)
    media = models.JSONField(default=list, blank=True)
    helpful_votes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reviews'
        unique_together = (('product', 'user'),)
        managed = False


class Settings(models.Model):
    id = models.BooleanField(primary_key=True, default=True)
    tax_rate = models.FloatField(default=8.0)
    shipping_fee = models.FloatField(default=10.0)
    fixed_fee_per_order = models.FloatField(default=2.0)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_column='updated_by')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'settings'
        managed = False


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_id = models.CharField(max_length=255)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, db_column='sender_id', related_name='messages')
    text = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'messages'
        managed = False
