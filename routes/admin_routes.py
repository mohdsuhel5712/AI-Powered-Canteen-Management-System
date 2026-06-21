from flask import Blueprint, render_template, request, redirect, session
from db import db_connection   # adjust if needed


admin = Blueprint('admin', __name__)

# 👉 Admin Login
@admin.route('/admin_login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM customer WHERE email=%s AND password=%s AND role='admin'",
            (email, password)
        )

        admin_user = cursor.fetchall()

        cursor.close()
        conn.close()

        if admin_user:
            session['role'] = 'admin'
            return redirect('/view_orders')
        else:
            return "Invalid Admin Login"

    return render_template('admin_login.html')


# 👉 View Orders
@admin.route('/view_orders')
def view_orders():

    if session.get('role') != 'admin':
        return redirect('/admin_login')

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