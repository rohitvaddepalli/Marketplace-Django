import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace.settings')
django.setup()

from rest_framework.test import APIClient

client = APIClient()

print("Running API self-check...")

# 1. Health check
res = client.get('/api/health')
assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.data}"
assert res.data['status'] == 'ok', "Health check failed"
print("✓ /api/health passed")

# 2. Public settings
res = client.get('/api/settings')
assert res.status_code == 200, f"Expected 200, got {res.status_code}"
assert res.data['success'] is True, "Settings success flag missing"
print("✓ /api/settings passed")

# 3. Products list
res = client.get('/api/products')
assert res.status_code == 200, f"Expected 200, got {res.status_code}"
assert res.data['success'] is True, "Products success flag missing"
assert 'products' in res.data, "Products array missing"
if res.data['products']:
    first = res.data['products'][0]
    assert '_id' in first, "MERN compatible '_id' field missing from product"
    print(f"✓ /api/products passed (found {len(res.data['products'])} products, sample _id: {first['_id']})")
else:
    print("✓ /api/products passed (empty catalog)")

# 4. Featured products
res = client.get('/api/products/featured')
assert res.status_code == 200, f"Expected 200, got {res.status_code}"
assert res.data['success'] is True, "Featured products success flag missing"
print("✓ /api/products/featured passed")

# 5. Public stores list
res = client.get('/api/stores')
assert res.status_code == 200, f"Expected 200, got {res.status_code}"
assert res.data['success'] is True, "Stores success flag missing"
print(f"✓ /api/stores passed (found {len(res.data['stores'])} stores)")

# 6. Auth protection check (unauthenticated access to /api/auth/me should return 401)
res = client.get('/api/auth/me')
assert res.status_code == 401, f"Expected 401 for unauthenticated /api/auth/me, got {res.status_code}"
assert res.data['success'] is False, "Expected success: False for 401"
print(f"✓ /api/auth/me correctly blocked unauthenticated request with 401 ({res.data['message']})")

print("\nAll 6 API self-check assertions passed successfully!")
