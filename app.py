
from flask import Flask, render_template, redirect, url_for, session, request
from db import db_connection
from model.predict import predict_demand

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
        query = '''
        INSERT INTO orders (user_id, food_id, quantity)
        VALUES (%s, %s, %s)
        '''
        cursor.execute(query, (user_id, food_id, quantity))
        conn.commit()

    except Exception as e:
        conn.rollback()
        return str(e)

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('order_page'))


# =========================
# USER ORDER PAGE
# =========================
@app.route('/order',methods=['GET','POST'])
def order_page():

    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    conn = db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
        orders.id,
        food_items.name AS food_item,
        orders.quantity,
        orders.status
        FROM orders
        JOIN food_items ON orders.food_id = food_items.id
        WHERE orders.user_id = %s
        ORDER BY orders.id DESC
    """, (user_id,))

    orders = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('order.html', orders=orders)


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


# =========================
# RUN APP
# =========================
if __name__ == '__main__':
    app.run(debug=True)

