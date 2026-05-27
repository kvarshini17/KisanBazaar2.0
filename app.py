"""
KisanBazaar - Direct Farmer to Consumer Marketplace
MVP Flask Application with Multi-language, Cart, and Order Management
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'kisanbazaar_secret_key_2024'

# ==================== TRANSLATIONS ====================

TRANSLATIONS = {
    'en': {
        'app_name': 'KisanBazaar',
        'home': 'Home',
        'marketplace': 'Marketplace',
        'msp_rates': 'MSP Rates',
        'govt_schemes': 'Govt Schemes',
        'dashboard': 'Dashboard',
        'logout': 'Logout',
        'farmer_login': 'Farmer Login',
        'customer_login': 'Customer Login',
        'welcome': 'Welcome',
        'connecting_farmers': 'Connecting Farmers Directly to Consumers',
        'tagline': 'Empowering Indian agriculture with fair pricing, MSP transparency, and zero middlemen',
        'browse_marketplace': 'Browse Marketplace',
        'no_middlemen': 'No Middlemen',
        'msp_transparency': 'MSP Transparency',
        'fair_pricing': 'Fair Pricing',
        'add_to_cart': 'Add to Cart',
        'view_cart': 'View Cart',
        'place_order': 'Place Order',
        'order_status': 'Order Status',
        'pending': 'Pending',
        'accepted': 'Accepted',
        'rejected': 'Rejected',
        'delivered': 'Delivered',
        'accept': 'Accept',
        'reject': 'Reject',
        'my_orders': 'My Orders',
        'track_orders': 'Track Orders',
        'farmer_details': 'Farmer Details',
        'location': 'Location',
        'phone': 'Phone',
        'cart': 'Cart',
        'total': 'Total',
        'checkout': 'Checkout',
        'above_msp': 'Above MSP',
        'below_msp': 'Below MSP',
        'available': 'Available',
        'price_per_kg': 'Price per kg',
        'quantity': 'Quantity',
        'register': 'Register',
        'login': 'Login',
        'name': 'Name',
        'password': 'Password',
        'email': 'Email',
        'address': 'Address',
        'crops_listed': 'Crops Listed',
        'orders_received': 'Orders Received',
        'manage_orders': 'Manage Orders',
        'order_placed': 'Order Placed Successfully!',
        'order_accepted': 'Order Accepted',
        'order_rejected': 'Order Rejected',
        'empty_cart': 'Your cart is empty',
        'add_crop': 'Add Crop',
        'crop_name': 'Crop Name',
        'select_language': 'Select Language'
    },
    'hi': {
        'app_name': 'किसान बाज़ार',
        'home': 'होम',
        'marketplace': 'बाज़ार',
        'msp_rates': 'एमएसपी दरें',
        'govt_schemes': 'सरकारी योजनाएं',
        'dashboard': 'डैशबोर्ड',
        'logout': 'लॉग आउट',
        'farmer_login': 'किसान लॉगिन',
        'customer_login': 'ग्राहक लॉगिन',
        'welcome': 'स्वागत है',
        'connecting_farmers': 'किसानों को सीधे उपभोक्ताओं से जोड़ना',
        'tagline': 'उचित मूल्य, एमएसपी पारदर्शिता और शून्य बिचौलियों के साथ भारतीय कृषि को सशक्त बनाना',
        'browse_marketplace': 'बाज़ार देखें',
        'no_middlemen': 'कोई बिचौलिया नहीं',
        'msp_transparency': 'एमएसपी पारदर्शिता',
        'fair_pricing': 'उचित मूल्य',
        'add_to_cart': 'कार्ट में जोड़ें',
        'view_cart': 'कार्ट देखें',
        'place_order': 'ऑर्डर करें',
        'order_status': 'ऑर्डर स्थिति',
        'pending': 'लंबित',
        'accepted': 'स्वीकृत',
        'rejected': 'अस्वीकृत',
        'delivered': 'वितरित',
        'accept': 'स्वीकार करें',
        'reject': 'अस्वीकार करें',
        'my_orders': 'मेरे ऑर्डर',
        'track_orders': 'ऑर्डर ट्रैक करें',
        'farmer_details': 'किसान विवरण',
        'location': 'स्थान',
        'phone': 'फोन',
        'cart': 'कार्ट',
        'total': 'कुल',
        'checkout': 'चेकआउट',
        'above_msp': 'एमएसपी से ऊपर',
        'below_msp': 'एमएसपी से नीचे',
        'available': 'उपलब्ध',
        'price_per_kg': 'प्रति किलो कीमत',
        'quantity': 'मात्रा',
        'register': 'रजिस्टर करें',
        'login': 'लॉगिन',
        'name': 'नाम',
        'password': 'पासवर्ड',
        'email': 'ईमेल',
        'address': 'पता',
        'crops_listed': 'सूचीबद्ध फसलें',
        'orders_received': 'प्राप्त ऑर्डर',
        'manage_orders': 'ऑर्डर प्रबंधन',
        'order_placed': 'ऑर्डर सफलतापूर्वक दिया गया!',
        'order_accepted': 'ऑर्डर स्वीकृत',
        'order_rejected': 'ऑर्डर अस्वीकृत',
        'empty_cart': 'आपका कार्ट खाली है',
        'add_crop': 'फसल जोड़ें',
        'crop_name': 'फसल का नाम',
        'select_language': 'भाषा चुनें'
    },
    'te': {
        'app_name': 'కిసాన్ బజార్',
        'home': 'హోమ్',
        'marketplace': 'మార్కెట్',
        'msp_rates': 'MSP రేట్లు',
        'govt_schemes': 'ప్రభుత్వ పథకాలు',
        'dashboard': 'డాష్‌బోర్డ్',
        'logout': 'లాగ్ అవుట్',
        'farmer_login': 'రైతు లాగిన్',
        'customer_login': 'కస్టమర్ లాగిన్',
        'welcome': 'స్వాగతం',
        'connecting_farmers': 'రైతులను నేరుగా వినియోగదారులతో అనుసంధానం చేయడం',
        'tagline': 'న్యాయమైన ధర, MSP పారదర్శకత మరియు సున్నా దళారులతో భారతీయ వ్యవసాయాన్ని శక్తివంతం చేయడం',
        'browse_marketplace': 'మార్కెట్ చూడండి',
        'no_middlemen': 'దళారులు లేరు',
        'msp_transparency': 'MSP పారదర్శకత',
        'fair_pricing': 'న్యాయమైన ధర',
        'add_to_cart': 'కార్ట్‌కి జోడించు',
        'view_cart': 'కార్ట్ చూడండి',
        'place_order': 'ఆర్డర్ చేయండి',
        'order_status': 'ఆర్డర్ స్థితి',
        'pending': 'పెండింగ్',
        'accepted': 'ఆమోదించబడింది',
        'rejected': 'తిరస్కరించబడింది',
        'delivered': 'డెలివరీ అయింది',
        'accept': 'ఆమోదించు',
        'reject': 'తిరస్కరించు',
        'my_orders': 'నా ఆర్డర్లు',
        'track_orders': 'ఆర్డర్లను ట్రాక్ చేయండి',
        'farmer_details': 'రైతు వివరాలు',
        'location': 'స్థానం',
        'phone': 'ఫోన్',
        'cart': 'కార్ట్',
        'total': 'మొత్తం',
        'checkout': 'చెక్అవుట్',
        'above_msp': 'MSP పైన',
        'below_msp': 'MSP క్రింద',
        'available': 'అందుబాటులో ఉంది',
        'price_per_kg': 'కిలోకు ధర',
        'quantity': 'పరిమాణం',
        'register': 'రిజిస్టర్',
        'login': 'లాగిన్',
        'name': 'పేరు',
        'password': 'పాస్‌వర్డ్',
        'email': 'ఇమెయిల్',
        'address': 'చిరునామా',
        'crops_listed': 'జాబితా చేసిన పంటలు',
        'orders_received': 'అందుకున్న ఆర్డర్లు',
        'manage_orders': 'ఆర్డర్ల నిర్వహణ',
        'order_placed': 'ఆర్డర్ విజయవంతంగా ఇవ్వబడింది!',
        'order_accepted': 'ఆర్డర్ ఆమోదించబడింది',
        'order_rejected': 'ఆర్డర్ తిరస్కరించబడింది',
        'empty_cart': 'మీ కార్ట్ ఖాళీగా ఉంది',
        'add_crop': 'పంట జోడించు',
        'crop_name': 'పంట పేరు',
        'select_language': 'భాష ఎంచుకోండి'
    }
}

def get_translation(key):
    """Get translation for current language"""
    lang = session.get('language', 'en')
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)

@app.context_processor
def inject_translations():
    return {
        't': get_translation,
        'current_lang': session.get('language', 'en')
    }

# ==================== DATABASE SETUP ====================

def get_db():
    conn = sqlite3.connect('kisanbazaar.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
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
    
    # MSP prices per kg (converted from per quintal rates for 2025-26)
    msp_data = [
        ('Rice', 24), ('Wheat', 23), ('Maize', 21), ('Jowar', 32),
        ('Bajra', 25), ('Ragi', 38), ('Tur (Arhar)', 72), ('Moong', 85),
        ('Urad', 70), ('Groundnut', 64), ('Soyabean', 46), ('Sunflower', 68),
        ('Cotton', 66), ('Sugarcane', 4), ('Potato', 15), ('Onion', 18), ('Tomato', 20)
    ]
    
    for crop, price in msp_data:
        cursor.execute('INSERT OR IGNORE INTO msp (crop_name, msp_price) VALUES (?, ?)', (crop, price))
    
    schemes_data = [
        ('PM-KISAN', 'Small and marginal farmers with landholding up to 2 hectares',
         '₹6,000 per year in three installments', 'Pradhan Mantri Kisan Samman Nidhi provides income support to farmers.'),
        ('PMFBY', 'All farmers including sharecroppers and tenant farmers',
         'Crop insurance with low premium (2% for Kharif, 1.5% for Rabi)', 'Pradhan Mantri Fasal Bima Yojana provides crop insurance coverage.'),
        ('Soil Health Card', 'All farmers across India',
         'Free soil testing and recommendations for fertilizers', 'Provides information on soil health and nutrient status.'),
        ('Kisan Credit Card', 'Farmers, fishermen, and animal husbandry farmers',
         'Easy credit up to ₹3 lakh at 4% interest rate', 'Provides affordable credit for agricultural needs.'),
        ('e-NAM', 'Farmers, traders, and buyers',
         'Online trading platform with transparent pricing', 'National Agriculture Market for online trading of agricultural commodities.'),
        ('PM Krishi Sinchai Yojana', 'All farmers with focus on water-stressed areas',
         'Subsidies for micro-irrigation up to 55-90%', 'Ensures access to irrigation - "Har Khet Ko Paani".')
    ]
    
    for name, eligibility, benefits, description in schemes_data:
        cursor.execute('''
            INSERT OR IGNORE INTO schemes (name, eligibility, benefits, description) 
            SELECT ?, ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM schemes WHERE name = ?)
        ''', (name, eligibility, benefits, description, name))
    
    demo_farmers = [
        ('Rajesh Kumar', 'farmer123', 'Punjab', '9876543210', 'Village Khanna, Near Gurudwara', 'Ludhiana', 'Punjab', '141401'),
        ('Suresh Patel', 'farmer123', 'Gujarat', '9876543211', 'Farm House, Anand Road', 'Ahmedabad', 'Gujarat', '380001'),
        ('Lakshmi Devi', 'farmer123', 'Maharashtra', '9876543212', 'Krishi Nagar, Nashik Highway', 'Nashik', 'Maharashtra', '422001')
    ]
    
    for name, password, location, phone, address, district, state, pincode in demo_farmers:
        cursor.execute('''
            INSERT OR IGNORE INTO farmers (name, password, location, phone, address, district, state, pincode) 
            SELECT ?, ?, ?, ?, ?, ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM farmers WHERE name = ?)
        ''', (name, password, location, phone, address, district, state, pincode, name))
    
    cursor.execute('''
        INSERT OR IGNORE INTO customers (name, email, password, phone, address, city, state, pincode) 
        SELECT ?, ?, ?, ?, ?, ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM customers WHERE email = ?)
    ''', ('Demo Customer', 'demo@example.com', 'customer123', '9988776655', '123 Main Street', 'Hyderabad', 'Telangana', '500001', 'demo@example.com'))
    
    cursor.execute('SELECT id FROM farmers WHERE name = ?', ('Rajesh Kumar',))
    farmer = cursor.fetchone()
    if farmer:
        demo_crops = [
            (farmer['id'], 'Rice', 500, 2200, 'Punjab', 2183, 'Above MSP'),
            (farmer['id'], 'Wheat', 300, 2300, 'Punjab', 2275, 'Above MSP'),
        ]
        for crop in demo_crops:
            cursor.execute('''
                INSERT OR IGNORE INTO crops (farmer_id, crop_name, quantity, price, location, msp_price, msp_status)
                SELECT ?, ?, ?, ?, ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM crops WHERE farmer_id = ? AND crop_name = ?)
            ''', (*crop, crop[0], crop[1]))
    
    conn.commit()
    conn.close()

def get_msp_price(crop_name):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT msp_price FROM msp WHERE LOWER(crop_name) = LOWER(?)', (crop_name,))
    result = cursor.fetchone()
    conn.close()
    return result['msp_price'] if result else None

def compare_with_msp(farmer_price, msp_price):
    if msp_price is None:
        return "MSP Not Available"
    return "Above MSP" if farmer_price >= msp_price else "Below MSP"

def farmer_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'farmer_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('farmer_login'))
        return f(*args, **kwargs)
    return decorated_function

def customer_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'customer_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('customer_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in ['en', 'hi', 'te']:
        session['language'] = lang
    return redirect(request.referrer or url_for('home'))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/farmer/login', methods=['GET', 'POST'])
def farmer_login():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM farmers WHERE name = ? AND password = ?', (name, password))
        farmer = cursor.fetchone()
        conn.close()
        if farmer:
            session['farmer_id'] = farmer['id']
            session['farmer_name'] = farmer['name']
            session['farmer_location'] = farmer['location']
            session['user_type'] = 'farmer'
            flash(f'Welcome back, {farmer["name"]}!', 'success')
            return redirect(url_for('farmer_dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('farmer_login.html')

@app.route('/farmer/register', methods=['GET', 'POST'])
def farmer_register():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        location = request.form.get('location')
        phone = request.form.get('phone')
        address = request.form.get('address')
        district = request.form.get('district')
        state = request.form.get('state')
        pincode = request.form.get('pincode')
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM farmers WHERE name = ?', (name,))
        if cursor.fetchone():
            flash('Farmer with this name already exists!', 'danger')
            conn.close()
            return render_template('farmer_register.html')
        cursor.execute('''INSERT INTO farmers (name, password, location, phone, address, district, state, pincode) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (name, password, location, phone, address, district, state, pincode))
        conn.commit()
        conn.close()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('farmer_login'))
    return render_template('farmer_register.html')

@app.route('/farmer/logout')
def farmer_logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home'))

@app.route('/customer/login', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM customers WHERE email = ? AND password = ?', (email, password))
        customer = cursor.fetchone()
        conn.close()
        if customer:
            session['customer_id'] = customer['id']
            session['customer_name'] = customer['name']
            session['customer_email'] = customer['email']
            session['user_type'] = 'customer'
            flash(f'Welcome back, {customer["name"]}!', 'success')
            return redirect(url_for('marketplace'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('customer_login.html')

@app.route('/customer/register', methods=['GET', 'POST'])
def customer_register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        pincode = request.form.get('pincode')
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM customers WHERE email = ?', (email,))
        if cursor.fetchone():
            flash('Email already registered!', 'danger')
            conn.close()
            return render_template('customer_register.html')
        cursor.execute('''INSERT INTO customers (name, email, password, phone, address, city, state, pincode) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (name, email, password, phone, address, city, state, pincode))
        conn.commit()
        conn.close()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('customer_login'))
    return render_template('customer_register.html')

@app.route('/customer/logout')
def customer_logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home'))

@app.route('/farmer/dashboard')
@farmer_login_required
def farmer_dashboard():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM crops WHERE farmer_id = ? ORDER BY created_at DESC', (session['farmer_id'],))
    crops = cursor.fetchall()
    cursor.execute('SELECT crop_name, msp_price FROM msp ORDER BY crop_name')
    msp_list = cursor.fetchall()
    cursor.execute('''
        SELECT o.*, c.crop_name, c.price as price_per_kg, cu.name as customer_name, cu.phone as customer_phone,
               cu.address as delivery_address, cu.city, cu.state
        FROM orders o JOIN crops c ON o.crop_id = c.id JOIN customers cu ON o.customer_id = cu.id
        WHERE o.farmer_id = ? ORDER BY o.order_date DESC
    ''', (session['farmer_id'],))
    orders = cursor.fetchall()
    pending_orders = [o for o in orders if o['status'] == 'Pending']
    accepted_orders = [o for o in orders if o['status'] == 'Accepted']
    conn.close()
    return render_template('farmer_dashboard.html', crops=crops, msp_list=msp_list, orders=orders,
                         pending_orders=pending_orders, accepted_orders=accepted_orders)

@app.route('/add_crop', methods=['POST'])
@farmer_login_required
def add_crop():
    crop_name = request.form.get('crop_name')
    quantity = int(request.form.get('quantity'))
    price = int(request.form.get('price'))
    location = request.form.get('location', session.get('farmer_location'))
    msp_price = get_msp_price(crop_name)
    msp_status = compare_with_msp(price, msp_price)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO crops (farmer_id, crop_name, quantity, price, location, msp_price, msp_status) VALUES (?, ?, ?, ?, ?, ?, ?)',
                  (session['farmer_id'], crop_name, quantity, price, location, msp_price, msp_status))
    conn.commit()
    conn.close()
    if msp_status == "Below MSP":
        flash(f'Crop added! ⚠️ Warning: Your price (₹{price}/kg) is below MSP (₹{msp_price}/kg)', 'warning')
    else:
        flash(f'Crop added successfully! ✅ Your price is at or above MSP.', 'success')
    return redirect(url_for('farmer_dashboard'))

@app.route('/delete_crop/<int:crop_id>')
@farmer_login_required
def delete_crop(crop_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM crops WHERE id = ? AND farmer_id = ?', (crop_id, session['farmer_id']))
    conn.commit()
    conn.close()
    flash('Crop listing deleted.', 'info')
    return redirect(url_for('farmer_dashboard'))

@app.route('/farmer/order/<int:order_id>/<action>')
@farmer_login_required
def manage_order(order_id, action):
    if action not in ['accept', 'reject']:
        flash('Invalid action', 'danger')
        return redirect(url_for('farmer_dashboard'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE id = ? AND farmer_id = ?', (order_id, session['farmer_id']))
    order = cursor.fetchone()
    if not order:
        flash('Order not found', 'danger')
        conn.close()
        return redirect(url_for('farmer_dashboard'))
    new_status = 'Accepted' if action == 'accept' else 'Rejected'
    cursor.execute('UPDATE orders SET status = ?, status_updated_at = ? WHERE id = ?',
                  (new_status, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), order_id))
    if action == 'reject':
        cursor.execute('UPDATE crops SET quantity = quantity + ? WHERE id = ?', (order['quantity'], order['crop_id']))
    conn.commit()
    conn.close()
    flash(f'Order {new_status.lower()}!', 'success' if action == 'accept' else 'info')
    return redirect(url_for('farmer_dashboard'))

@app.route('/farmer/order/<int:order_id>/deliver')
@farmer_login_required
def deliver_order(order_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE orders SET status = ?, status_updated_at = ? WHERE id = ? AND farmer_id = ?',
                  ('Delivered', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), order_id, session['farmer_id']))
    conn.commit()
    conn.close()
    flash('Order marked as delivered!', 'success')
    return redirect(url_for('farmer_dashboard'))

@app.route('/marketplace')
def marketplace():
    conn = get_db()
    cursor = conn.cursor()
    crop_filter = request.args.get('crop', '')
    location_filter = request.args.get('location', '')
    query = '''SELECT c.*, f.name as farmer_name, f.phone as farmer_phone, f.address as farmer_address, f.district, f.state as farmer_state, f.pincode
               FROM crops c JOIN farmers f ON c.farmer_id = f.id WHERE c.quantity > 0'''
    params = []
    if crop_filter:
        query += ' AND LOWER(c.crop_name) LIKE LOWER(?)'
        params.append(f'%{crop_filter}%')
    if location_filter:
        query += ' AND LOWER(c.location) LIKE LOWER(?)'
        params.append(f'%{location_filter}%')
    query += ' ORDER BY c.created_at DESC'
    cursor.execute(query, params)
    crops = cursor.fetchall()
    cursor.execute('SELECT DISTINCT location FROM crops')
    locations = cursor.fetchall()
    cursor.execute('SELECT DISTINCT crop_name FROM crops')
    crop_names = cursor.fetchall()
    cart_count = 0
    if session.get('customer_id'):
        cursor.execute('SELECT SUM(quantity) as count FROM cart WHERE customer_id = ?', (session['customer_id'],))
        result = cursor.fetchone()
        cart_count = result['count'] if result['count'] else 0
    conn.close()
    return render_template('marketplace.html', crops=crops, locations=locations, crop_names=crop_names,
                         selected_crop=crop_filter, selected_location=location_filter, cart_count=cart_count)

@app.route('/cart/add/<int:crop_id>', methods=['POST'])
@customer_login_required
def add_to_cart(crop_id):
    quantity = int(request.form.get('quantity', 1))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM crops WHERE id = ? AND quantity >= ?', (crop_id, quantity))
    crop = cursor.fetchone()
    if not crop:
        flash('Crop not available or insufficient quantity', 'danger')
        conn.close()
        return redirect(url_for('marketplace'))
    cursor.execute('SELECT * FROM cart WHERE customer_id = ? AND crop_id = ?', (session['customer_id'], crop_id))
    existing = cursor.fetchone()
    if existing:
        cursor.execute('UPDATE cart SET quantity = quantity + ? WHERE id = ?', (quantity, existing['id']))
    else:
        cursor.execute('INSERT INTO cart (customer_id, crop_id, quantity) VALUES (?, ?, ?)', (session['customer_id'], crop_id, quantity))
    conn.commit()
    conn.close()
    flash(f'Added {quantity} kg to cart!', 'success')
    return redirect(url_for('marketplace'))

@app.route('/cart')
@customer_login_required
def view_cart():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''SELECT cart.*, c.crop_name, c.price as price_per_kg, c.location, c.msp_status, c.quantity as available_qty,
                      f.id as farmer_id, f.name as farmer_name, f.phone as farmer_phone, f.address as farmer_address, f.district, f.state, f.pincode as farmer_pincode
                      FROM cart JOIN crops c ON cart.crop_id = c.id JOIN farmers f ON c.farmer_id = f.id WHERE cart.customer_id = ?''',
                  (session['customer_id'],))
    cart_items = cursor.fetchall()
    total = sum(item['quantity'] * item['price_per_kg'] for item in cart_items)
    conn.close()
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/cart/remove/<int:cart_id>')
@customer_login_required
def remove_from_cart(cart_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM cart WHERE id = ? AND customer_id = ?', (cart_id, session['customer_id']))
    conn.commit()
    conn.close()
    flash('Item removed from cart', 'info')
    return redirect(url_for('view_cart'))

@app.route('/cart/update/<int:cart_id>', methods=['POST'])
@customer_login_required
def update_cart(cart_id):
    quantity = int(request.form.get('quantity', 1))
    conn = get_db()
    cursor = conn.cursor()
    if quantity <= 0:
        cursor.execute('DELETE FROM cart WHERE id = ? AND customer_id = ?', (cart_id, session['customer_id']))
    else:
        cursor.execute('UPDATE cart SET quantity = ? WHERE id = ? AND customer_id = ?', (quantity, cart_id, session['customer_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@customer_login_required
def checkout():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''SELECT cart.*, c.crop_name, c.price as price_per_kg, c.farmer_id, c.quantity as available_qty, f.name as farmer_name, f.district, f.state
                      FROM cart JOIN crops c ON cart.crop_id = c.id JOIN farmers f ON c.farmer_id = f.id WHERE cart.customer_id = ?''',
                  (session['customer_id'],))
    cart_items = cursor.fetchall()
    if not cart_items:
        flash('Your cart is empty!', 'warning')
        conn.close()
        return redirect(url_for('marketplace'))
    cursor.execute('SELECT * FROM customers WHERE id = ?', (session['customer_id'],))
    customer = cursor.fetchone()
    if request.method == 'POST':
        delivery_address = request.form.get('delivery_address')
        delivery_phone = request.form.get('phone')
        for item in cart_items:
            if item['quantity'] > item['available_qty']:
                flash(f'Not enough {item["crop_name"]} available', 'danger')
                continue
            total_price = item['quantity'] * item['price_per_kg']
            cursor.execute('''INSERT INTO orders (customer_id, crop_id, farmer_id, quantity, total_price, status, order_date, customer_address, customer_phone)
                             VALUES (?, ?, ?, ?, ?, 'Pending', ?, ?, ?)''',
                          (session['customer_id'], item['crop_id'], item['farmer_id'], item['quantity'], total_price,
                           datetime.now().strftime('%Y-%m-%d %H:%M:%S'), delivery_address, delivery_phone))
            cursor.execute('UPDATE crops SET quantity = quantity - ? WHERE id = ?', (item['quantity'], item['crop_id']))
        cursor.execute('DELETE FROM cart WHERE customer_id = ?', (session['customer_id'],))
        conn.commit()
        conn.close()
        flash('Orders placed successfully! You can track them in My Orders.', 'success')
        return redirect(url_for('customer_orders'))
    total = sum(item['quantity'] * item['price_per_kg'] for item in cart_items)
    conn.close()
    return render_template('checkout.html', cart_items=cart_items, total=total, customer=customer)

@app.route('/customer/orders')
@customer_login_required
def customer_orders():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''SELECT o.*, c.crop_name, c.price as price_per_kg, o.total_price as total_amount,
                      f.name as farmer_name, f.phone as farmer_phone,
                      f.address as farmer_address, f.district as farmer_district, 
                      f.state as farmer_state, f.pincode as farmer_pincode
                      FROM orders o JOIN crops c ON o.crop_id = c.id JOIN farmers f ON o.farmer_id = f.id
                      WHERE o.customer_id = ? ORDER BY o.order_date DESC''', (session['customer_id'],))
    orders = cursor.fetchall()
    conn.close()
    return render_template('customer_orders.html', orders=orders)

@app.route('/order/<int:crop_id>', methods=['GET', 'POST'])
def order_crop(crop_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''SELECT c.*, f.name as farmer_name, f.phone as farmer_phone,
                      f.address as farmer_address, f.district, f.state as farmer_state, f.pincode
                      FROM crops c JOIN farmers f ON c.farmer_id = f.id WHERE c.id = ?''', (crop_id,))
    crop = cursor.fetchone()
    if not crop:
        flash('Crop not found!', 'danger')
        return redirect(url_for('marketplace'))
    if request.method == 'POST':
        if 'customer_id' not in session:
            flash('Please login to place an order', 'warning')
            return redirect(url_for('customer_login'))
        quantity = int(request.form.get('quantity'))
        if quantity > crop['quantity']:
            flash('Requested quantity exceeds available stock!', 'danger')
        else:
            total_price = quantity * crop['price']
            cursor.execute('SELECT * FROM customers WHERE id = ?', (session['customer_id'],))
            customer = cursor.fetchone()
            cursor.execute('''INSERT INTO orders (customer_id, crop_id, farmer_id, quantity, total_price, status, order_date, customer_address, customer_phone)
                             VALUES (?, ?, ?, ?, ?, 'Pending', ?, ?, ?)''',
                          (session['customer_id'], crop_id, crop['farmer_id'], quantity, total_price,
                           datetime.now().strftime('%Y-%m-%d %H:%M:%S'), customer['address'], customer['phone']))
            cursor.execute('UPDATE crops SET quantity = quantity - ? WHERE id = ?', (quantity, crop_id))
            conn.commit()
            flash('🎉 Order placed successfully! The farmer will review your order.', 'success')
            conn.close()
            return redirect(url_for('customer_orders'))
    conn.close()
    return render_template('order.html', crop=crop)

@app.route('/order/success')
def order_success():
    return render_template('order_success.html')

@app.route('/schemes')
def schemes():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM schemes')
    schemes_list = cursor.fetchall()
    conn.close()
    return render_template('schemes.html', schemes=schemes_list)

@app.route('/msp')
def msp_info():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM msp ORDER BY crop_name')
    msp_list = cursor.fetchall()
    conn.close()
    return render_template('msp_info.html', msp_list=msp_list)

@app.route('/api/msp/<crop_name>')
def api_msp(crop_name):
    msp_price = get_msp_price(crop_name)
    if msp_price:
        return {'crop': crop_name, 'msp_price': msp_price, 'status': 'found'}
    return {'crop': crop_name, 'msp_price': None, 'status': 'not_found'}

@app.route('/api/cart/count')
def api_cart_count():
    if 'customer_id' not in session:
        return {'count': 0}
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(quantity) as count FROM cart WHERE customer_id = ?', (session['customer_id'],))
    result = cursor.fetchone()
    conn.close()
    return {'count': result['count'] if result['count'] else 0}

if __name__ == '__main__':
    init_db()
    print("🌾 KisanBazaar MVP Server Starting...")
    print("📍 Access at: http://localhost:5000")
    print("🌐 Languages: English, Hindi, Telugu")
    app.run(debug=True, port=5000)
