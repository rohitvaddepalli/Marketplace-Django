from django.urls import path
from api.views import (
    auth, stores, products, orders, users, admin, analytics, chat, upload, settings
)

urlpatterns = [
    # Auth
    path('auth/me', auth.get_me),
    path('auth/updateprofile', auth.update_profile),
    path('auth/logout', auth.logout_view),

    # Stores
    path('stores', stores.stores_list),
    path('stores/my/store', stores.get_my_store),
    path('stores/<uuid:pk>', stores.store_detail),

    # Products
    path('products', products.products_list),
    path('products/featured', products.featured_products),
    path('products/my/products', products.get_my_products),
    path('products/low-stock', products.get_low_stock_products),
    path('products/bulk-import', products.bulk_import_products),
    path('products/export', products.export_products),
    path('products/<uuid:pk>', products.product_detail),
    path('products/<uuid:pk>/reviews', products.product_reviews),
    path('products/<uuid:product_id>/reviews/<uuid:review_id>/helpful', products.mark_review_helpful),

    # Orders
    path('orders', orders.orders_root),
    path('orders/myorders', orders.get_my_orders),
    path('orders/seller/orders', orders.get_seller_orders),
    path('orders/<uuid:pk>', orders.get_order_detail),
    path('orders/<uuid:pk>/status', orders.update_order_status),
    path('orders/<uuid:pk>/cancel', orders.cancel_order),

    # Users
    path('users/wishlist', users.get_wishlist),
    path('users/wishlist/<uuid:product_id>', users.manage_wishlist_item),
    path('users/recently-viewed', users.get_recently_viewed),
    path('users/recently-viewed/<uuid:product_id>', users.add_recently_viewed),

    # Analytics
    path('analytics/sales', analytics.seller_sales_analytics),
    path('analytics/customers', analytics.seller_customer_analytics),
    path('analytics/inventory-forecast', analytics.seller_inventory_forecast),
    path('analytics/products', analytics.seller_product_analytics),
    path('analytics/admin/sales', analytics.admin_sales_analytics),
    path('analytics/admin/customers', analytics.admin_customer_analytics),
    path('analytics/admin/products', analytics.admin_product_analytics),

    # Admin
    path('admin/stats', admin.get_dashboard_stats),
    path('admin/users', admin.admin_users),
    path('admin/users/<uuid:pk>', admin.admin_delete_user),
    path('admin/stores', admin.admin_stores),
    path('admin/stores/<uuid:pk>/status', admin.admin_store_status),
    path('admin/stores/<uuid:pk>/verify', admin.admin_store_verify),
    path('admin/stores/<uuid:pk>', admin.admin_delete_store),
    path('admin/products', admin.admin_products),
    path('admin/products/<uuid:pk>', admin.admin_delete_product),
    path('admin/orders', admin.admin_orders),
    path('admin/orders/<uuid:pk>', admin.admin_delete_order),
    path('admin/settings', admin.admin_settings),

    # Settings
    path('settings', settings.get_public_settings),

    # Chat
    path('chat/<str:room_id>', chat.get_chat_messages),

    # Upload
    path('upload', upload.upload_files),
    path('upload/signature', upload.get_upload_signature),
]
