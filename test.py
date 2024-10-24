import pytest
from flask import Flask
from app import app, products, cart

@pytest.fixture
def client():
    """Create a test client for the app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
    # Clear cart after each test
    cart.clear()

class TestEcommerceApp:
    """Test cases for E-commerce Flask application"""
    
    def test_home_page(self, client):
        """Test if home page loads correctly"""
        response = client.get('/')
        assert response.status_code == 200
        # Check if all products are present in the response
        for product in products:
            assert bytes(product['name'], 'utf-8') in response.data
            assert bytes(str(product['price']), 'utf-8') in response.data

    def test_initial_cart_empty(self, client):
        """Test if cart is initially empty"""
        response = client.get('/')
        assert len(cart) == 0
        assert response.status_code == 200

    def test_add_to_cart_valid_product(self, client):
        """Test adding a valid product to cart"""
        # Add Laptop (ID: 1) to cart
        response = client.get('/add_to_cart/1')
        assert response.status_code == 200
        
        # Verify cart contents
        assert len(cart) == 1
        assert cart[0]['id'] == 1
        assert cart[0]['name'] == 'Laptop'
        assert cart[0]['price'] == 999.99

    def test_add_to_cart_invalid_product(self, client):
        """Test adding an invalid product ID to cart"""
        # Try to add non-existent product (ID: 999)
        response = client.get('/add_to_cart/999')
        assert response.status_code == 200
        
        # Cart should remain empty
        assert len(cart) == 0

    def test_add_multiple_products(self, client):
        """Test adding multiple products to cart"""
        # Add Laptop and Smartphone
        client.get('/add_to_cart/1')
        client.get('/add_to_cart/2')
        
        assert len(cart) == 2
        assert cart[0]['name'] == 'Laptop'
        assert cart[1]['name'] == 'Smartphone'
        
        # Verify total items and prices
        total_price = sum(item['price'] for item in cart)
        assert total_price == 1499.98  # 999.99 + 499.99

    def test_product_data_structure(self, client):
        """Test if product data is properly structured"""
        for product in products:
            assert isinstance(product, dict)
            assert all(key in product for key in ['id', 'name', 'price'])
            assert isinstance(product['id'], int)
            assert isinstance(product['name'], str)
            assert isinstance(product['price'], (int, float))

    def test_cart_persistence(self, client):
        """Test if cart maintains state between requests"""
        # Add a product to cart
        client.get('/add_to_cart/1')
        assert len(cart) == 1
        
        # Get home page again
        response = client.get('/')
        assert response.status_code == 200
        assert len(cart) == 1  # Cart should still contain the item
        assert cart[0]['name'] == 'Laptop'

if __name__ == '__main__':
    pytest.main(['-v'])