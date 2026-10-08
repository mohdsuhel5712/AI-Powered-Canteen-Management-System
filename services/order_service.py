# services/order_service.py
from db import db_connection
# =========================
# CREATE ORDER
# =========================
def create_order(user_id, total_amount, payment_status="pending"):
    conn = db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Get user's cart
        cursor.execute( "SELECT id FROM cart WHERE user_id=%s",(user_id,))
        cart = cursor.fetchone()
        if not cart:
            return None
        cart_id = cart["id"]
        # Get cart items
        cursor.execute("""
                SELECT
                cart_items.food_id,
                cart_items.quantity,
                food_items.price FROM cart_items
            JOIN food_items ON cart_items.food_id = food_items.id
            WHERE cart_items.cart_id=%s
        """, (cart_id,))
        items = cursor.fetchall()
        if not items:
            return None
        # Calculate total from database
        total = sum(float(item["price"]) * item["quantity"] for item in items )
        # Create main order
        cursor.execute(""" INSERT INTO orders(user_id, food_id,  quantity, status,total_amount, payment_status)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (user_id,items[0]["food_id"],items[0]["quantity"],"Pending",total, payment_status))
        
        order_id = cursor.lastrowid
        # Add all cart items into order_items
        for item in items:
            cursor.execute(""" INSERT INTO order_items(order_id, food_id,quantity, price )
                VALUES (%s,%s,%s,%s)
            """, (order_id, item["food_id"], item["quantity"], item["price"] ))
        # Clear cart after order creation
        cursor.execute("""DELETE cart_items FROM cart_items
            JOIN cartON cart_items.cart_id = cart.id WHERE cart.user_id=%s """,(user_id,))
        conn.commit()
        return order_id
    
    except Exception as e:
        conn.rollback()
        print("Order Creation Error:", e)
        return None
    finally:
        cursor.close()
        conn.close()
# =========================
# GET USER ORDERS
# =========================
# =========================
# GET USER ORDERS
# =========================
def get_user_orders(user_id):
    conn = db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT
                id,
                total_amount,
                status,
                payment_status,
                order_time
            FROM orders
            WHERE user_id=%s
            ORDER BY id DESC
        """, (user_id,))
        orders = cursor.fetchall()
        print("USER ORDERS:", orders)
        return orders
    finally:
        cursor.close()
        conn.close()
# =========================
# GET ORDER DETAILS
# =========================
def get_order_details(user_id, order_id):
    conn = db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Main order
        cursor.execute("""
            SELECT
                id,
                user_id,
                food_id,
                quantity,
                status,
                total_amount,
                payment_status,
                order_time
            FROM orders
            WHERE id=%s
            AND user_id=%s
        """, (order_id, user_id))
        order = cursor.fetchone()
        if not order:
            return None
        # Order items
        cursor.execute("""
            SELECT
                order_items.food_id,
                food_items.name,
                order_items.quantity,
                order_items.price,
                (
                    order_items.quantity * order_items.price
                ) AS subtotal
            FROM order_items
            JOIN food_items
                ON order_items.food_id = food_items.id
            WHERE order_items.order_id=%s
        """, (order_id,))
        order["items"] = cursor.fetchall()
        return order
    finally:
        cursor.close()
        conn.close()
# =========================
# UPDATE ORDER STATUS
# =========================
def update_order_status(order_id, status):
    conn = db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE orders
            SET status=%s
            WHERE id=%s
            """,
            (status, order_id)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Order Status Error:", e)
        return False
    finally:
        cursor.close()
        conn.close()
# =========================
# UPDATE PAYMENT STATUS
# =========================
def update_payment_status(order_id, payment_status):
    conn = db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE orders
            SET payment_status=%s
            WHERE id=%s
            """,
            (payment_status, order_id)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Payment Status Error:", e)
        return False
    finally:
        cursor.close()
        conn.close()
