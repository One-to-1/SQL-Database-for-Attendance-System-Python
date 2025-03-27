import unittest
from src.services.identity_service import IdentityService

class TestIdentityService(unittest.TestCase):

    def setUp(self):
        self.identity_service = IdentityService()

    def test_add_identity(self):
        identity_data = {'name': 'John Doe', 'email': 'john@example.com'}
        result = self.identity_service.add_identity(identity_data)
        self.assertTrue(result)
        self.assertIsNotNone(self.identity_service.get_identity(identity_data['email']))

    def test_remove_identity(self):
        identity_data = {'name': 'Jane Doe', 'email': 'jane@example.com'}
        self.identity_service.add_identity(identity_data)
        result = self.identity_service.remove_identity(identity_data['email'])
        self.assertTrue(result)
        self.assertIsNone(self.identity_service.get_identity(identity_data['email']))

    def test_get_identity(self):
        identity_data = {'name': 'Alice Smith', 'email': 'alice@example.com'}
        self.identity_service.add_identity(identity_data)
        retrieved_identity = self.identity_service.get_identity(identity_data['email'])
        self.assertEqual(retrieved_identity['name'], identity_data['name'])

    def test_add_identity_invalid(self):
        identity_data = {'name': '', 'email': 'invalid-email'}
        result = self.identity_service.add_identity(identity_data)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()