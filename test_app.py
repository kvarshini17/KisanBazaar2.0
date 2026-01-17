"""
KisanBazaar Unit Tests
Tests all major functionality including authentication, CRUD operations, and order management
"""

import unittest
import sys
import os
import sqlite3
import tempfile

# Import after ensuring test environment
os.environ['TESTING'] = 'True'

from app import app, get_msp_price, compare_with_msp

# Test database functions
def get_test_db():
    conn = sqlite3.connect('test_kisanbazaar.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_test_db():
    """Initialize test database with schema and data"""
    conn = get_test_db()
    cursor = conn.cursor()
    
    # Create all tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS farmers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            location TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            district TEXT,
            state TEXT,
            pincode TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            pincode TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id INTEGER NOT NULL,
            crop_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price INTEGER NOT NULL,
            location TEXT NOT NULL,
            msp_price INTEGER,
            msp_status TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (farmer_id) REFERENCES farmers (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            crop_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            added_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (id),
            FOREIGN KEY (crop_id) REFERENCES crops (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            crop_id INTEGER NOT NULL,
            farmer_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total_price INTEGER NOT NULL,
            status TEXT DEFAULT 'Pending',
            order_date TEXT DEFAULT CURRENT_TIMESTAMP,
            status_updated_at TEXT,
            customer_address TEXT,
            customer_phone TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (id),
            FOREIGN KEY (crop_id) REFERENCES crops (id),
            FOREIGN KEY (farmer_id) REFERENCES farmers (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS msp (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop_name TEXT NOT NULL UNIQUE,
            msp_price INTEGER NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schemes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            eligibility TEXT NOT NULL,
            benefits TEXT NOT NULL,
            description TEXT
        )
    ''')
    
    # Insert MSP data
    msp_data = [
        ('Rice', 24), ('Wheat', 23), ('Maize', 21), ('Jowar', 32),
        ('Bajra', 25), ('Ragi', 38), ('Tur (Arhar)', 72), ('Moong', 85),
        ('Urad', 70), ('Groundnut', 64), ('Soyabean', 46), ('Sunflower', 68),
        ('Cotton', 66), ('Sugarcane', 4), ('Potato', 15), ('Onion', 18), ('Tomato', 20)
    ]
    
    for crop, price in msp_data:
        cursor.execute('INSERT OR IGNORE INTO msp (crop_name, msp_price) VALUES (?, ?)', (crop, price))
    
    conn.commit()
    conn.close()

# Monkey patch the database functions in app module
import app as app_module
original_get_db = app_module.get_db
app_module.get_db = get_test_db

class KisanBazaarTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and initialize test database"""
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_secret_key'
        self.client = app.test_client()
        
        # Remove existing test database if it exists
        if os.path.exists('test_kisanbazaar.db'):
            os.remove('test_kisanbazaar.db')
        
        # Initialize test database
        init_test_db()
    
    def tearDown(self):
        """Clean up after tests"""
        # Clean up test database
        if os.path.exists('test_kisanbazaar.db'):
            try:
                os.remove('test_kisanbazaar.db')
            except:
                pass
    
    # ==================== DATABASE TESTS ====================
    
    def test_database_initialization(self):
        """Test that database tables are created correctly"""
        conn = get_test_db()
        cursor = conn.cursor()
        
        # Check if all tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row['name'] for row in cursor.fetchall()]
        
        required_tables = ['farmers', 'customers', 'crops', 'cart', 'orders', 'msp', 'schemes']
        for table in required_tables:
            self.assertIn(table, tables, f"Table {table} should exist")
        
        # Check MSP data is populated
        cursor.execute("SELECT COUNT(*) as count FROM msp")
        msp_count = cursor.fetchone()['count']
        self.assertGreater(msp_count, 0, "MSP table should have data")
        
        conn.close()
    
    def test_msp_functions(self):
        """Test MSP price retrieval and comparison"""
        # Test get_msp_price
        rice_msp = get_msp_price('Rice')
        self.assertEqual(rice_msp, 24, "Rice MSP should be 24")
        
        wheat_msp = get_msp_price('Wheat')
        self.assertEqual(wheat_msp, 23, "Wheat MSP should be 23")
        
        # Test with non-existent crop
        unknown_msp = get_msp_price('UnknownCrop')
        self.assertIsNone(unknown_msp, "Unknown crop should return None")
        
        # Test compare_with_msp
        self.assertEqual(compare_with_msp(30, 24), 'Above MSP', "30 > 24 should be Above MSP")
        self.assertEqual(compare_with_msp(20, 24), 'Below MSP', "20 < 24 should be Below MSP")
        self.assertEqual(compare_with_msp(30, None), 'MSP Not Available', "None MSP should return N/A")
    
    # ==================== FARMER TESTS ====================
    
    def test_farmer_registration(self):
        """Test farmer registration"""
        response = self.client.post('/farmer/register', data={
            'name': 'Test Farmer',
            'password': 'testpass123',
            'location': 'Test Village',
            'phone': '9876543210',
            'address': 'Test Address',
            'district': 'Test District',
            'state': 'Test State',
            'pincode': '123456'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verify farmer was added to database
        conn = get_test_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM farmers WHERE name = ?", ('Test Farmer',))
        farmer = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(farmer, "Farmer should be added to database")
        self.assertEqual(farmer['name'], 'Test Farmer')
        self.assertEqual(farmer['phone'], '9876543210')
    
    def test_farmer_login_valid(self):
        """Test farmer login with valid credentials"""
        # First register a farmer
        self.client.post('/farmer/register', data={
            'name': 'Login Test Farmer',
            'password': 'password123',
            'location': 'Test Location',
            'phone': '9876543210',
            'address': 'Address',
            'district': 'District',
            'state': 'State',
            'pincode': '123456'
        })
        
        # Now try to login
        with self.client as client:
            response = client.post('/farmer/login', data={
                'name': 'Login Test Farmer',
                'password': 'password123'
            }, follow_redirects=True)
            
            self.assertEqual(response.status_code, 200)
            
            # Check if session was set
            with client.session_transaction() as sess:
                self.assertIn('farmer_id', sess, "farmer_id should be in session")
                self.assertEqual(sess['farmer_name'], 'Login Test Farmer')
    
    def test_farmer_login_invalid(self):
        """Test farmer login with invalid credentials"""
        response = self.client.post('/farmer/login', data={
            'name': 'NonExistent',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid credentials', response.data)
    
    # ==================== CUSTOMER TESTS ====================
    
    def test_customer_registration(self):
        """Test customer registration"""
        response = self.client.post('/customer/register', data={
            'name': 'Test Customer',
            'email': 'test@example.com',
            'password': 'testpass123',
            'phone': '9876543210',
            'address': 'Test Address',
            'city': 'Test City',
            'state': 'Test State',
            'pincode': '123456'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verify customer was added to database
        conn = get_test_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE email = ?", ('test@example.com',))
        customer = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(customer, "Customer should be added to database")
        self.assertEqual(customer['email'], 'test@example.com')
    
    def test_customer_login_valid(self):
        """Test customer login with valid credentials"""
        # Register customer first
        self.client.post('/customer/register', data={
            'name': 'Login Customer',
            'email': 'login@example.com',
            'password': 'password123',
            'phone': '9876543210',
            'address': 'Address',
            'city': 'City',
            'state': 'State',
            'pincode': '123456'
        })
        
        # Login
        with self.client as client:
            response = client.post('/customer/login', data={
                'email': 'login@example.com',
                'password': 'password123'
            }, follow_redirects=True)
            
            self.assertEqual(response.status_code, 200)
            
            # Check session
            with client.session_transaction() as sess:
                self.assertIn('customer_id', sess, "customer_id should be in session")
    
    # ==================== CROP TESTS ====================
    
    def test_add_crop(self):
        """Test adding a crop"""
        # Register and login farmer
        self.client.post('/farmer/register', data={
            'name': 'Crop Farmer',
            'password': 'pass123',
            'location': 'Farm Location',
            'phone': '9876543210',
            'address': 'Address',
            'district': 'District',
            'state': 'State',
            'pincode': '123456'
        })
        
        with self.client as client:
            client.post('/farmer/login', data={
                'name': 'Crop Farmer',
                'password': 'pass123'
            })
            
            # Add crop
            response = client.post('/add_crop', data={
                'crop_name': 'Rice',
                'quantity': 100,
                'price': 30,
                'location': 'Farm Location'
            }, follow_redirects=True)
            
            self.assertEqual(response.status_code, 200)
            
            # Verify crop in database
            conn = get_test_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM crops WHERE crop_name = ?", ('Rice',))
            crop = cursor.fetchone()
            conn.close()
            
            self.assertIsNotNone(crop, "Crop should be added")
            self.assertEqual(crop['price'], 30)
            self.assertEqual(crop['quantity'], 100)
            self.assertEqual(crop['msp_status'], 'Above MSP')
    
    # ==================== CART & ORDER TESTS ====================
    
    def test_cart_workflow(self):
        """Test complete cart workflow: add, update, view"""
        # Setup: Register farmer and add crop
        self.client.post('/farmer/register', data={
            'name': 'Cart Farmer',
            'password': 'pass123',
            'location': 'Location',
            'phone': '9876543210',
            'address': 'Address',
            'district': 'District',
            'state': 'State',
            'pincode': '123456'
        })
        
        with self.client as client:
            client.post('/farmer/login', data={'name': 'Cart Farmer', 'password': 'pass123'})
            client.post('/add_crop', data={
                'crop_name': 'Wheat',
                'quantity': 50,
                'price': 25,
                'location': 'Location'
            })
            client.get('/farmer/logout')
            
            # Get crop_id
            conn = get_test_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM crops WHERE crop_name = 'Wheat'")
            crop_id = cursor.fetchone()['id']
            conn.close()
            
            # Register and login customer
            client.post('/customer/register', data={
                'name': 'Cart Customer',
                'email': 'cart@example.com',
                'password': 'pass123',
                'phone': '9876543210',
                'address': 'Address',
                'city': 'City',
                'state': 'State',
                'pincode': '123456'
            })
            client.post('/customer/login', data={'email': 'cart@example.com', 'password': 'pass123'})
            
            # Add to cart
            response = client.post(f'/cart/add/{crop_id}', data={'quantity': 5}, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            
            # View cart
            response = client.get('/cart')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Wheat', response.data)
    
    # ==================== ROUTE ACCESS TESTS ====================
    
    def test_home_page_accessible(self):
        """Test that home page is accessible"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'KisanBazaar', response.data)
    
    def test_marketplace_accessible(self):
        """Test that marketplace is accessible"""
        response = self.client.get('/marketplace')
        self.assertEqual(response.status_code, 200)
    
    def test_msp_page_accessible(self):
        """Test that MSP page is accessible"""
        response = self.client.get('/msp')
        self.assertEqual(response.status_code, 200)
    
    def test_schemes_page_accessible(self):
        """Test that schemes page is accessible"""
        response = self.client.get('/schemes')
        self.assertEqual(response.status_code, 200)
    
    def test_protected_routes(self):
        """Test that protected routes redirect when not logged in"""
        # Farmer dashboard should redirect
        response = self.client.get('/farmer/dashboard', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        
        # Cart should redirect
        response = self.client.get('/cart', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
    
    # ==================== LANGUAGE TESTS ====================
    
    def test_language_switching(self):
        """Test language switching functionality"""
        with self.client as client:
            # Set language to Hindi
            response = client.get('/set_language/hi', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            
            with client.session_transaction() as sess:
                self.assertEqual(sess.get('language'), 'hi')
            
            # Set to Telugu
            response = client.get('/set_language/te', follow_redirects=True)
            with client.session_transaction() as sess:
                self.assertEqual(sess.get('language'), 'te')
            
            # Set back to English
            response = client.get('/set_language/en', follow_redirects=True)
            with client.session_transaction() as sess:
                self.assertEqual(sess.get('language'), 'en')

def run_tests():
    """Run all tests and display results"""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(KisanBazaarTestCase)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
