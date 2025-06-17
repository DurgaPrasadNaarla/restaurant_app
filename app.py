from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

app = Flask(__name__)

# Configuration
app.secret_key = 'your_secret_key_here'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'andhra_cuisinee'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Routes
@app.route('/')
def home():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM menu_items WHERE is_available = TRUE LIMIT 6")
    featured_dishes = cursor.fetchall()
    
    cursor.execute("""
        SELECT reviews.*, users.username 
        FROM reviews 
        JOIN users ON reviews.user_id = users.user_id 
        ORDER BY review_date DESC 
        LIMIT 3
    """)
    featured_reviews = cursor.fetchall()
    
    cursor.close()
    
    return render_template('index.html', 
                         featured_dishes=featured_dishes, 
                         featured_reviews=featured_reviews)

@app.route('/menu')
def menu():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute("SELECT * FROM menu_items WHERE is_available = TRUE ORDER BY category, name")
    menu_items = cursor.fetchall()
    
    menu_by_category = {}
    for item in menu_items:
        if item['category'] not in menu_by_category:
            menu_by_category[item['category']] = []
        menu_by_category[item['category']].append(item)
    
    cursor.close()
    
    return render_template('menu.html', menu_by_category=menu_by_category)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cursor.fetchone()
        cursor.close()
        
        if account and check_password_hash(account['password_hash'], password):
            session['loggedin'] = True
            session['user_id'] = account['user_id']
            session['username'] = account['username']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Incorrect email/password!', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        
        if not (username and email and password):
            flash('Please fill out all required fields!', 'danger')
            return redirect(url_for('register'))
        
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!', 'danger')
            return redirect(url_for('register'))
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        if cursor.fetchone():
            flash('Email already exists!', 'danger')
            cursor.close()
            return redirect(url_for('register'))
        
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        if cursor.fetchone():
            flash('Username already exists!', 'danger')
            cursor.close()
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, phone, address)
            VALUES (%s, %s, %s, %s, %s)
        ''', (username, email, hashed_password, phone, address))
        mysql.connection.commit()
        cursor.close()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))

@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    item_ids = list(cart.keys())
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if item_ids:
        format_strings = ','.join(['%s'] * len(item_ids))
        cursor.execute(f"SELECT * FROM menu_items WHERE item_id IN ({format_strings})", tuple(item_ids))
        items = cursor.fetchall()
        for item in items:
            item['quantity'] = cart[str(item['item_id'])]
    else:
        items = []
    cursor.close()
    return render_template('order.html', cart_items=items)

@app.route('/add_to_cart/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    cart = session.get('cart', {})
    cart[str(item_id)] = cart.get(str(item_id), 0) + 1
    session['cart'] = cart
    return jsonify({'message': 'Item added to cart', 'cart': cart})

@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    cart = session.get('cart', {})
    if str(item_id) in cart:
        del cart[str(item_id)]
        session['cart'] = cart
    return jsonify({'message': 'Item removed from cart', 'cart': cart})

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'loggedin' not in session:
        flash('Please login to place an order.', 'warning')
        return redirect(url_for('login'))
    
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('menu'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    item_ids = list(cart.keys())
    format_strings = ','.join(['%s'] * len(item_ids))
    cursor.execute(f"SELECT * FROM menu_items WHERE item_id IN ({format_strings})", tuple(item_ids))
    items = cursor.fetchall()
    
    total_amount = 0
    for item in items:
        item['quantity'] = cart[str(item['item_id'])]
        total_amount += item['price'] * item['quantity']
    
    if request.method == 'POST':
        cursor.execute('''
            INSERT INTO orders (user_id, order_date, total_amount, status)
            VALUES (%s, %s, %s, %s)
        ''', (session['user_id'], datetime.now(), total_amount, 'Pending'))
        order_id = cursor.lastrowid
        
        for item in items:
            cursor.execute('''
                INSERT INTO order_items (order_id, item_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            ''', (order_id, item['item_id'], item['quantity'], item['price']))
        
        mysql.connection.commit()
        cursor.close()
        
        session.pop('cart', None)
        flash('Order placed successfully!', 'success')
        return redirect(url_for('bill', order_id=order_id))
    
    cursor.close()
    return render_template('checkout.html', items=items, total=total_amount)

@app.route('/bill/<int:order_id>')
def bill(order_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT o.order_id, o.order_date, o.total_amount, o.status, u.username, u.email
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        WHERE o.order_id = %s
    ''', (order_id,))
    order = cursor.fetchone()
    
    cursor.execute('''
        SELECT oi.quantity, oi.price, m.name
        FROM order_items oi
        JOIN menu_items m ON oi.item_id = m.item_id
        WHERE oi.order_id = %s
    ''', (order_id,))
    items = cursor.fetchall()
    cursor.close()
    
    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('home'))
    
    return render_template('bill.html', order=order, items=items)

@app.route('/submit_review', methods=['POST'])
def submit_review():
    if 'loggedin' not in session:
        flash('Please login to submit a review.', 'warning')
        return redirect(url_for('login'))
    
    rating = int(request.form.get('rating', 0))
    comment = request.form.get('comment', '')
    
    if rating < 1 or rating > 5 or not comment:
        flash('Please provide a valid rating and comment.', 'danger')
        return redirect(url_for('home'))
    
    cursor = mysql.connection.cursor()
    cursor.execute('''
        INSERT INTO reviews (user_id, rating, comment, review_date)
        VALUES (%s, %s, %s, %s)
    ''', (session['user_id'], rating, comment, datetime.now()))
    mysql.connection.commit()
    cursor.close()
    
    flash('Thank you for your review!', 'success')
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'loggedin' not in session:
        flash('Please login to access the dashboard.', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute('''
        SELECT * FROM orders
        WHERE user_id = %s
        ORDER BY order_date DESC
    ''', (user_id,))
    orders = cursor.fetchall()
    
    cursor.execute('''
        SELECT * FROM reviews
        WHERE user_id = %s
        ORDER BY review_date DESC
    ''', (user_id,))
    reviews = cursor.fetchall()
    
    cursor.close()
    
    return render_template('dashboard.html', orders=orders, reviews=reviews)

if __name__ == '__main__':
    app.run(debug=True)