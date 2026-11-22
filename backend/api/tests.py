from django.test import TestCase
from rest_framework.test import APIClient
from api.models import Product, Settings, Store, User

class MarketplaceAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_check(self):
        res = self.client.get('/api/health')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data.get('status'), 'ok')

    def test_settings_public(self):
        res = self.client.get('/api/settings')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data.get('success'))
        self.assertIn('settings', res.data)

    def test_products_list_public(self):
        res = self.client.get('/api/products')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data.get('success'))
        self.assertIn('products', res.data)
        if res.data['products']:
            first = res.data['products'][0]
            # Verify MERN-compatible _id property is exposed
            self.assertIn('_id', first)

    def test_featured_products(self):
        res = self.client.get('/api/products/featured')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data.get('success'))
        self.assertIn('products', res.data)
