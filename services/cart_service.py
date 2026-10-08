# services/cart_service.py
from db import db_connection
# ==========================================
# GET OR CREATE CART
# ==========================================

def get_or_create_cart(user_id):
    conn = db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check existing cart
        cursor.execute(
            "SELECT id FROM cart WHERE user_id = %s",(user_id,))

        cart = cursor.fetchone()
        # If cart already exists for get
        if cart:
            return cart["id"]
        
        # Create new cart for new creation 
        cursor.execute(
            "INSERT INTO cart (user_id) VALUES (%s)",(user_id,))
        conn.commit()
        return cursor.lastrowid

    finally:
        cursor.close()
        conn.close()


# ==========================================
# ADD FOOD TO CART
# ==========================================

def add_to_cart(user_id, food_id, quantity=1):
    conn = db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get or create user's cart
        cursor.execute("SELECT id FROM cart WHERE user_id = %s",(user_id,))
        cart = cursor.fetchone()
        if cart:
            cart_id = cart["id"]

        else:
            cursor.execute(
                "INSERT INTO cart (user_id) VALUES (%s)",(user_id,))
            cart_id = cursor.lastrowid

        # Check whether food already exists in cart
        cursor.execute(""" SELECT id, quantity FROM cart_items WHERE cart_id = %s AND food_id = %s """,(cart_id, food_id))
    
        item = cursor.fetchone()
        
        if item:
            # Increase quantity
            new_quantity = item["quantity"] + quantity
            cursor.execute(""" UPDATE cart_items SET quantity = %s WHERE id = %s """, (new_quantity, item["id"]))
        else:
            # Add new item
            cursor.execute( """ INSERT INTO cart_items(cart_id, food_id, quantity) VALUES (%s, %s, %s) """, (cart_id, food_id, quantity)  )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Cart Add Error:", e)
        return False
    finally:
        cursor.close()
        conn.close()


# ==========================================
# GET CART ITEMS
# ==========================================
def get_cart_items(user_id):
    
    conn = db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
                SELECT
                cart_items.id AS cart_item_id,
                food_items.id AS food_id,
                food_items.name,
                food_items.description,
                food_items.price,
                cart_items.quantity,
                (food_items.price * cart_items.quantity) AS subtotal FROM cart
                
            JOIN cart_items ON cart.id = cart_items.cart_id

            JOIN food_items ON cart_items.food_id = food_items.id

            WHERE cart.user_id = %s ORDER BY cart_items.id DESC """,  (user_id,))
        
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

# ==========================================
# UPDATE CART ITEM QUANTITY
# ==========================================
def update_cart_item(user_id, cart_item_id, quantity):
    conn = db_connection()
    cursor = conn.cursor()

    try:
        if quantity <= 0:
            cursor.execute( """DELETE cart_items FROM cart_items
                JOIN cart ON cart_items.cart_id = cart.id
                WHERE cart_items.id = %s AND cart.user_id = %s """, (cart_item_id, user_id) )
        else:

            cursor.execute(""" UPDATE cart_items
                JOIN cart ON cart_items.cart_id = cart.id
                SET cart_items.quantity = %s
                WHERE cart_items.id = %s
                AND cart.user_id = %s
                """,
                (quantity, cart_item_id, user_id)
            )

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Cart Update Error:", e)
        return False
    finally:
        cursor.close()
        conn.close()


# ==========================================
# REMOVE ITEM FROM CART
# ==========================================

def remove_cart_item(user_id, cart_item_id):
    conn = db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute( """ DELETE cart_items FROM cart_items
            JOIN cart ON cart_items.cart_id = cart.id
            WHERE cart_items.id = %s AND cart.user_id = %s """,(cart_item_id, user_id))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Remove Cart Error:", e)
        return False
    finally:
        cursor.close()
        conn.close()


# ==========================================
# CLEAR CART
# ==========================================

def clear_cart(user_id):
    conn = db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(""" DELETE cart_items FROM cart_items 
                       JOIN cart ON cart_items.cart_id = cart.id WHERE cart.user_id = %s """,(user_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Clear Cart Error:", e)
        return False
    finally:
        cursor.close()
        conn.close()


# ==========================================
# CALCULATE CART TOTAL
# ==========================================

def get_cart_total(user_id):
    conn = db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT COALESCE(SUM(food_items.price * cart_items.quantity), 0) AS total FROM cart
            JOIN cart_items ON cart.id = cart_items.cart_id
            JOIN food_items ON cart_items.food_id = food_items.id
            WHERE cart.user_id = %s """, (user_id,))
        result = cursor.fetchone()
        return result["total"] if result else 0

    finally:
        cursor.close()
        conn.close()


# ==========================================
# CART ITEM COUNT
# ==========================================

def get_cart_count(user_id):
    conn = db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""SELECT COALESCE(SUM(cart_items.quantity), 0) AS count FROM cart
            JOIN cart_items ON cart.id = cart_items.cart_id
            WHERE cart.user_id = %s""",(user_id,))
        result = cursor.fetchone()
        return result["count"] if result else 0
    finally:
        cursor.close()
        conn.close()