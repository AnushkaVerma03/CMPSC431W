import re

from flask import Flask, render_template, request, redirect, url_for, session
from requests import Session
from sqlalchemy.exc import SQLAlchemyError

import service
from CheckoutPage import CheckoutForm

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
sess = Session()


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/books')
def books():
    books = service.get_books()
    return render_template('books.html', books=books)


@app.route('/contact-us')
def contact_us():
    return render_template('ContactUs.html')


@app.route('/accounts')
def accounts():
    return render_template('Account.html')


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    # Your create account logic goes here
    return render_template('create_account.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Your login logic goes here
    return render_template('login.html')


@app.route('/shoppingcart')
def shopping_cart():
    # Check if the 'cart' key is present in the session
    if 'cart' in session:
        shopping_cart_items = session['cart']
    else:
        shopping_cart_items = []

    # shopping_cart_items = service.get_shopping_cart_items()
    # Render the shopping cart template with the cart items
    total_price = 0
    for item in shopping_cart_items[0]:
        price = float(re.findall("\d+\.\d+", item['PRICE'])[0])
        print('price: ', price)
        total_price += price
    return render_template('shoppingcart.html', shopping_cart_items=shopping_cart_items[0], total_price=total_price)


@app.route('/recommend-us')
def recommend_us():
    return render_template('RecommendUs.html')

@app.route('/delete_customer', methods=['POST'])
def delete_customer_get():
    # Retrieve the selected customer ID from the form
    customer_id = request.form['customer_id']

    # Perform the deletion operation in the database
    success = service.delete_customer(customer_id)

    if success:
        return redirect(url_for('index'))
    else:
        return 'Failed to delete customer. Please try again.'

    @app.route('delete_customer')
    def delete_customer():
        return render_template('delete_customer.html')

# Add this route for submitting recommendations
@app.route('/submit-recommendation', methods=['POST'])
def submit_recommendation():
    book_isbn = request.form['isbn']
    book_name = request.form['bookTitle']
    author_name = request.form['Author']
    recommendation = request.form['Recommendation']
    result = service.add_recommendation(book_isbn, book_name, author_name, recommendation)
    print(result)
    if result:
        return 'Thanks for adding the book! You\'ve got great recommendations. Keep an eye on the email to get updates'
    else:
        return 'Sorry, we could not add the book. Please try again later.'


# def get_book_details_by_name(book_name):
# Assuming 'books' is your list of books
# for book in Books:
# if book['name'].lower() == book_name.replace('-', ' ').lower():
# return book

# Return None if the book is not found
# return None


@app.route('/book/<isbn>')
def book_detail_page(isbn):
    book = service.get_book_details_by_isbn(isbn)
    print(book)
    return render_template('book_details_page.html', book=book[0])


@app.route('/ContactUs', methods=['POST'])
def process_return():
    if request.method == 'POST':
        # Retrieve form data
        order_id = request.form['order_id']
        issue = request.form['issue']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        customer_id = request.form['customer_id']

        # TODO: Insert data into the ContactUs table
        # Uncomment and modify the code according to your database schema
        # Assuming you have a service method to handle database operations
        result = service.process_return(order_id, issue, first_name, last_name, customer_id)

        if result:
            # Redirect to a page confirming the return processing
            return render_template('return_processed.html', result='success', order_id=order_id)
        else:
            # Handle the case where return processing fails
            return render_template('return_processed.html', result='failure')

    # If the request method is not POST, you might want to handle it differently
    return redirect(url_for('index'))  # Redirect to the home page or another suitable route


@app.route('/refund_page')
def refund_page():
    # Logic for refund page goes here
    return render_template('refund_page.html')


@app.route('/replacement_page')
def replacement_page():
    # Logic for replacement page goes here
    return render_template('replacement_page.html')


@app.route('/add-to-cart/<isbn>')
def add_to_cart(isbn):
    success = service.add_to_cart(isbn)
    if success:
        return redirect('/shoppingcart')
    else:
        return render_template('books.html')




@app.route('/add-book', methods=['GET'])
def add_book_get():
    return render_template('Addbook.html')


@app.route('/add-book', methods=['POST'])
def add_book_post():
    # Extract data from the form
    title = request.form['title']
    author_id = request.form['author_id']
    genre_name = request.form['genre_name']
    publication_date = request.form['publication_date']
    isbn = request.form['isbn']
    availability = request.form['availability']
    price = request.form['price']

    genre_id = service.get_genre_id(genre_name)

    availability = 1 if availability == 'on' else 0

    # Create a new Book instance
    new_book = dict(
        TITLE=title,
        AUTHOR_ID=author_id,
        GENRE_ID=genre_id,
        PUBLICATION_DATE=publication_date,
        ISBN=isbn,
        AVAILABILITY=availability,
        PRICE=price
    )

    service.add_book(new_book)

    return redirect('/books')


@app.route('/delete-book/<isbn>')
def delete_book(isbn):
    service.delete_book(isbn)
    return redirect('/books')

@app.route('/add-customer', methods=['GET'])
def add_customer_get():
    return render_template('addcustomer.html')

@app.route('/add-customer', methods=['POST'])
def add_customer():
    # Retrieve data from the form
    customer_id = request.form['customer_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']
    zip_code = request.form['zip_code']

    # Create a new Customer instance
    new_customer = dict(
        CUSTOMER_ID=customer_id,
        FIRST_NAME=first_name,
        LAST_NAME=last_name,
        EMAIL=email,
        PHONE=phone,
        ADDRESS=address,
        ZIP_CODE=zip_code
    )
    service.add_customer(new_customer)

    return redirect('/index')


def update_user(user_id):
    if request.method == 'GET':
        # Retrieve the existing user information
        user = service.get_user_by_id(user_id)
        if user:
            return render_template('update-customer.html', CUSTOMERS=user)
        else:
            return 'User not found'  # Handle the case where the user is not found
    elif request.method == 'POST':
        # Handle the form submission to update user information
        updated_user = {
            'user_id': user_id,
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': request.form['email'],
            'phone': request.form['phone'],
            'address': request.form['address'],
            'zip_code': request.form['zip_code']
        }
        success = service.update_user(updated_user)
        if success:
            return redirect(url_for('index'))
        else:
            return 'User not found'


@app.route('/update-customer/<user_id>', methods=['GET'])
def update_user_get(user_id):
    user = service.get_user_by_id(user_id)
    return render_template('update-customer.html', user=user)

@app.route('/update-customer/<user_id>', methods=['POST'])
def update_customer():
    return render_template('update-customer.html')


@app.route('/update-books/<book_id>', methods=['GET'])
def update_book_get(book_id):
    book = service.get_book_by_id(book_id)
    return render_template('update-books.html', book=book)

@app.route('/update-books/<book_id>', methods=['POST'])
def update_book(book_id):
    if request.method == 'POST':
        # Handle the form submission to update book information
        updated_book = {
            'book_id': book_id,
            'title': request.form['title'],
            'genre_id': request.form['genre_id'],
            'publication_date': request.form['publication_date'],
            'isbn': request.form['isbn'],
            'availability': request.form['availability'],
            'price': request.form['price'],
            'author_id': request.form['author_id'],
            # Add other fields as needed
        }
        success = service.update_book(updated_book)
        if success:
            return redirect(url_for('index'))
        else:
            return 'Book not found'


@app.route('/create-report')
def sales_report():
    report_data = service.get_sales_report()
    return render_template('create-report.html', report_data=report_data)


@app.route('/contact')
def contact():
    return render_template('contact.html')

def db():
    return None


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    # sess.init_app(app)
    app.run(debug=True, host='0.0.0.0', port=8000)
