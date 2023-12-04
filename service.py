import pymysql
from flask import redirect, session, render_template
import wtforms
from flask_wtf import FlaskForm
from wtforms import StringField, DateField
from wtforms.validators import InputRequired, Length



def execute_query(query):
    # Connect to the database
    connection = pymysql.connect(host='localhost',
                                 user='anushka',
                                 password='Jeonjungkook97',
                                 db='BookshopDB',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        # Execute the query
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
    except Exception as e:
        return e
    finally:
        connection.close()


def get_books():
    # Do a join for genre and author
    query = "SELECT * FROM BOOKS"
    books = execute_query(query)
    return books


def get_authors():
    # Get all authors from the database and return as a json
    query = "SELECT * FROM AUTHORS"
    return execute_query(query)


print(get_authors())


def add_recommendation(book_isbn, book_name, author_name, recommendation):
    try:
        num = execute_query("SELECT COUNT(*) FROM RECOMMENDATIONS")
        num = num[0]['COUNT(*)'] + 1
        print(num)

        execute_query(
            "INSERT INTO RECOMMENDATIONS (Reco_ID, ISBN, BOOK_NAME, AUTHOR_NAME, RECOMMENDATION_TEXT) VALUES ('{}', '{}', '{}', '{}', '{}');".
            format(num, book_isbn, book_name, author_name, recommendation))
        return True
    except Exception as e:
        return False


def get_book_details_by_isbn(isbn):
    return execute_query("SELECT * FROM BOOKS WHERE ISBN = '{}'".format(isbn))


def add_book(book):
    # Add the book to the database
    try:
        num = execute_query("SELECT COUNT(*) FROM BOOKS")
        num = num[0]['COUNT(*)'] + 1

        execute_query(
            "INSERT INTO BOOKS (PRODUCT_ID, TITLE, GENRE_ID, AUTHOR_ID, PUBLICATION_DATE, ISBN, AVAILABILITY, "
            "PRICE) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".
            format(num, book['TITLE'], book['GENRE_ID'], book['AUTHOR_ID'], book['PUBLICATION_DATE'], book['ISBN'],
                   book['AVAILABILITY'], book['PRICE']))
        return True
    except Exception as e:
        return False

def login_details(username, password):
    query = "SELECT * FROM USERS WHERE USERNAME = '{}' AND PASSWORD = '{}'".format(username, password)
    result = execute_query(query)

    # Assuming the result is a dictionary representing the user details
    if result:
        role = result[0]['ROLE']

        if role == 'Customer':
            # Redirect to the customer index page
            return redirect('/customer_index')
        else:
            # Redirect to the default index page for non-customers
            return redirect('/default_index')

    # Return an error or handle the case where the login details are incorrect
    return "Invalid username or password"


def checkout():
    form = checkout()

    if form.validate_on_submit():
        # Assuming you have a 'customer_id' stored in the session
        customer_id = session.get('customer_id')
        card_number = form.card_number.data
        cvv = form.cvv.data
        zip_code = form.zip_code.data
        exp_date = form.exp_date.data
        address = form.address.data

        # Save payment information to the database (you might want to use an ORM for this)
        # Here, I'm using a simple SQL statement as an example
        sql = """
            INSERT INTO PAYMENT_INFO (PAYMENT_ID, CUSTOMER_ID, CARD_NUM, CVV, ZIP_CODE, EXP_DATE, ADDRESS)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        # Execute the SQL statement with the appropriate parameters

        return redirect('/thank-you')  # Redirect to a thank-you page after successful checkout

    return render_template('checkout.html', form=form)


def initialize_shopping_cart():
    # Initialize the shopping cart in the session
    # Initialize the cart in the session if it doesn't exist
    if 'cart' not in session:
        session['cart'] = []


def add_to_cart(isbn):
    # Get book details by ISBN (you might want to implement this function)
    book = get_book_details_by_isbn(isbn)

    # Initialize the cart in the session if it doesn't exist
    if 'cart' not in session:
        session['cart'] = []

    # Add the book details to the cart in the session
    session['cart'].append(book[0])
    return True


def get_genre_id(genre_name):
    # Get the genre ID from the database
    query = "SELECT * FROM GENRE WHERE GENRE_NAME = '{}'".format(genre_name)
    result = execute_query(query)

    print(result)

    if result:
        return result[0]['GENRE_ID']

    return None


def get_author_id(author):
    # Get the author ID from the database
    query = "SELECT * FROM AUTHORS WHERE AUTHOR_NAME = '{}'".format(author)
    result = execute_query(query)

    print(result)

    if result:
        return result[0]['AUTHOR_ID']

    return None


def add_customer(customer):
    try:
        num = execute_query("SELECT COUNT(*) FROM CUSTOMERS")
        num = num[0]['COUNT(*)'] + 1

        execute_query(
            "INSERT INTO CUSTOMERS (CUSTOMER_ID, F_NAME, L_NAME, EMAIL, PHONE_NO, ADDRESS, ZIP_CODE) "
            "VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}')".
            format(num, customer[ 'CUSTOMER_ID'], customer['FIRST_NAME'], customer['LAST_NAME'], customer['EMAIL'], customer['PHONE'], customer['ADDRESS'], customer['ZIP_CODE']))
        return True
    except Exception as e:
        return False

def get_user_by_id(user_id):
    # Get the user details from the database
    query = "SELECT * FROM CUSTOMERS WHERE CUSTOMER_ID = {}".format(user_id)
    result = execute_query(query)

    print(result)

    if result:
        return result[0]

    return None

def delete_customer(customer_id):
    try:
        # Delete customer from the database based on the provided customer_id
        query = "DELETE FROM CUSTOMERS WHERE CUSTOMER_ID = {}".format(customer_id)
        execute_query(query)
        return True
    except Exception as e:
        return False


def update_user(customer):
    try:
        # Update user information in the database
        query = """
            UPDATE CUSTOMERS
            SET FIRST_NAME = '{}', LAST_NAME = '{}', EMAIL = '{}', 
                PHONE_NO = '{}', ADDRESS = '{}', ZIP_CODE = '{}'
            WHERE CUSTOMER_ID = {}
        """.format(
            customer['CUSTOMER.F_NAME'], customer['CUSTOMER.L_NAME'], customer['CUSTOMER.EMAIL'],
            customer['CUSTOMER.PHONE'], customer['CUSTOMER.ADDRESS'], customer['CUSTOMER.ZIP_CODE'],
            customer['CUSTOMER_ID']
        )
        execute_query(query)
        return True
    except Exception as e:
        return False


def delete_book(isbn):
    # Delete the book from the database
    query = "DELETE FROM BOOKS WHERE ISBN = '';".format(isbn)
    execute_query(query)
    return True



def get_sales_report():
    # Modify this function to fetch data from the REVIEWS table
    # For example, fetch books with their ratings from the REVIEWS table
    query = """
        SELECT B.TITLE, B.ISBN, R.RATING
        FROM BOOKS B
        JOIN REVIEWS R ON B.PRODUCT_ID = R.PRODUCT_ID
        ORDER BY R.RATING DESC;
    """
    result = execute_query(query)

    # Return the result as a list of dictionaries
    return result

