import mysql.connector
def db_connection():
      connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Mdsuhail@123',
            database='canteen_db'
      )
      return connection
