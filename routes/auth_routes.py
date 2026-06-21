from flask import Blueprint, render_template, request, redirect, session
from db import db_connection   # adjust if needed

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = db_connection()
        cursor = conn.cursor(dictionary=True,buffered=True)

        cursor.execute(
            "SELECT * FROM customer WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['name']
            session['role'] = user['role']
            return redirect('/')
        else:
            return "Invalid Email or Password"

    return render_template('login.html')