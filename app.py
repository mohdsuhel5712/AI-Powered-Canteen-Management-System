from flask import Flask, render_template, redirect, url_for, session, request
from db import db_connection
# from model.predict import predict_demand
from services.cart_service import (add_to_cart,
                                   get_cart_items,
                                   get_cart_count,
                                   get_cart_total,
                                   get_or_create_cart,
                                   update_cart_item,
                                   remove_cart_item,
                                   clear_cart
                                   )
from services.order_service import (
    create_order,
    get_user_orders,
    get_order_details,
    update_order_status,
    update_payment_status
)
# admin login route 
from routes import register_blueprints
from routes.admin_routes import admin
from routes.auth_routes import auth
app = Flask(__name__)
app.secret_key = 'SUHAIL_KEY'
register_blueprints(app)
# =========================
# REGISTER
# =========================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        conn = db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            'INSERT INTO customer(name,email,password) VALUES(%s,%s,%s)',
            (name, email, password)
        )
        conn.commit()
        # cursor.close()
        # conn.close()
        return redirect('/login')
    return render_template('register.html')
# =========================
# LOGIN
# =========================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM customer WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cursor.fetchone()
        # cursor.close()
        # conn.close()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['name']
            session['role'] = user['role']
            if user['role'] == 'admin':
                return redirect('/admin')
            else:
                return redirect('/')
        else:
            return "invalid email and password "
    return render_template('login.html')
# =========================
# LOGOUT
# =========================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
# =========================
# HOME PAGE
# =========================
@app.route('/')
def home():
    conn = db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM food_items WHERE availability=TRUE')
    foods = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('home.html', foods=foods)
# =========================
# sklearn prediction 
# =========================
@app.route('/ai-predict', methods=['GET', 'POST'])
def ai_predict():
    if request.method == 'POST':
        prev_day = int(request.form['prev_day_sales'])
        avg3 = int(request.form['avg_last_3_days'])
        day = request.form['day']      # string
        item = request.form['item']    # string
        result = predict_demand(prev_day, avg3, day, item)
        return render_template('result.html', prediction=result)
    return render_template('predict.html')
# =========================
# TOP SELLING ITEM 
# =========================
# =========================
# SEARCH
# =========================
@app.route('/search', methods=['GET','POST'])
def search():
    if request.method == 'POST':
        keyword = request.form.get('keyword')
    else:
        keyword = request.args.get('keyword')
    if not keyword:
        return redirect('/')   # safe fallback
    conn = db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM food_items WHERE name LIKE %s"
    cursor.execute(query, ("%" + keyword + "%",))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('home.html', foods=result)
# cart addding 
# =========================
# CART
# =========================
@app.route('/cart')
def cart():
    user_id = session.get('user_id')
    # User login check
    if not user_id:
        return redirect('/login')
    # Get cart data
    items = get_cart_items(user_id)
    # Get total
    total = get_cart_total(user_id)
    # Get number of products
    cart_count = get_cart_count(user_id)
    return render_template('cart.html',items=items, total=total, cart_count=cart_count )
# =========================
# ADD TO CART
# =========================
@app.route('/cart/add/<int:food_id>', methods=['POST'])
def add_food_to_cart(food_id):
    user_id = session.get('user_id')
    # Login required
    if not user_id:
        return redirect('/login')
    # Get quantity
    quantity = request.form.get('quantity', 1)
    try:
        quantity = int(quantity)
        if quantity < 1:
            quantity = 1
    except ValueError:
        quantity = 1
    # Add food
    success = add_to_cart(user_id,food_id, quantity)
    if not success:
        return "Unable to add item to cart"
    return redirect('/cart')
# =========================
# UPDATE CART
# =========================
@app.route('/cart/update/<int:cart_item_id>', methods=['POST'])
def update_cart(cart_item_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')
    quantity = request.form.get('quantity', 1)
    try:
        quantity = int(quantity)
    except ValueError:
        quantity = 1
    update_cart_item(user_id,cart_item_id, quantity )
    return redirect('/cart')
# =========================
# REMOVE FROM CART
# =========================
@app.route('/cart/remove/<int:cart_item_id>', methods=['POST'])
def remove_from_cart(cart_item_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')
    remove_cart_item(user_id,cart_item_id )
    return redirect('/cart')
# =========================
# CLEAR CART
# ========================
@app.route('/cart/clear', methods=['POST'])
def clear_user_cart():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')
    clear_cart(user_id)
    return redirect('/cart')




# =========================
# PLACE ORDER (POST)
# =========================
@app.route('/orders/<int:food_id>', methods=['POST'])
def place_order(food_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')
    
    quantity = request.form.get('quantity')
    conn = db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = '''INSERT INTO orders (user_id, food_id, quantity) VALUES (%s, %s, %s)'''
        cursor.execute(query, (user_id, food_id, quantity))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return str(e)
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('order_page'))


# checkout order pages 
# =========================
# CHECKOUT
# =========================
# =========================
# CHECKOUT
# =========================
@app.route('/checkout')
def checkout():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')
    
    # Get cart items
    items = get_cart_items(user_id)
    # Empty cart check
    if not items:
        return redirect('/cart')
    # Cart total
    total = get_cart_total(user_id)
    # Cart count
    cart_count = get_cart_count(user_id)
    return render_template('checkout.html', items=items,total=total, cart_count=cart_count)
# =========================
# CONFIRM ORDER
# =========================
# =========================
# ORDER SUCCESS
# =========================

@app.route('/order-success/<int:order_id>')
def order_success(order_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')
    
    # Get order
    order = get_order_details(user_id,order_id)
    if not order:
        return "Order not found"
    return render_template('order_success.html',order=order)
# =========================
# PAYMENT PAGE
# =========================


@app.route('/payment/<int:order_id>')
def payment(order_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')
    
    # Get order
    order = get_order_details(user_id, order_id)
    if not order:
        return "Order not found"
    return render_template('payment.html',order=order )
# =========================
# PAYMENT SUCCESS
# =========================
@app.route('/payment-success/<int:order_id>')
def payment_success(order_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')
    
    # Check order belongs to logged-in user
    order = get_order_details( user_id,order_id )
    if not order:
        return "Order not found"
    # Update payment
    update_payment_status(order_id, "paid" )
    # Confirm order
    update_order_status( order_id, "Confirmed" )
    # Show success page
    return redirect(url_for( 'order_success',order_id=order_id ) )
# =========================
# USER ORDER PAGE
# =========================
# =========================
# CONFIRM ORDER
# =========================
@app.route('/confirm-order',methods=['POST'])
def confirm_order():
    user_id=session.get('user_id')
    if not user_id:
        return redirect('/login')
    
    payment_method=request.form.get('payment_method')
    if payment_method=="cash":
        payment_status="pending"
    else:
        payment_status="pending"
        
    total=get_cart_total(user_id)
    if total<=0:
        return redirect('/cart')
    order_id=create_order(user_id,total, payment_status )
    if not order_id:
        return "Unable to create order"
    
    session['order_id']=order_id
    
    if payment_method=="cash":
        return redirect(url_for('order_success',order_id=order_id))
    return redirect(url_for('payment',order_id=order_id))
# =========================
# ORDER SUCCESS
# =========================
# =========================
# PAYMENT PAGE
# =========================
# =========================
# PAYMENT SUCCESS
# =========================
# =========================
# USER ORDER PAGE
# =========================
@app.route('/order')
def order_page():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')
    
    orders = get_user_orders(user_id)
    return render_template('order.html',orders=orders)
# =========================
# ADMIN DASHBOARD
# =========================
@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        return redirect('/login')
    
    conn = db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
        orders.id,
        customer.name AS user,
        food_items.name AS food_item,
        orders.quantity,
        orders.status
        FROM orders
        JOIN customer ON orders.user_id = customer.id
        JOIN food_items ON orders.food_id = food_items.id
        ORDER BY orders.id DESC
    """)
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin.html', orders=orders)
# =========================
# COMPLETE ORDER
# =========================
@app.route('/complete/<int:order_id>')
def complet(order_id):
    conn = db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "UPDATE orders SET status='completed' WHERE id=%s",
        (order_id,)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/admin')
# =========================
# DELETE ORDER
# =========================
@app.route('/delete', methods=['POST'])
def delete():
    order_id = request.form['order_id']
    conn = db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('DELETE FROM orders WHERE id=%s', (order_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/admin')
# 
# =========================
# RUN APP
# =========================
if __name__ == '__main__':
    app.run(debug=True)
