from flask_wtf import FlaskForm
from wtforms import StringField, DateField
from wtforms.validators import InputRequired, Length

class CheckoutForm(FlaskForm):
    card_number = StringField('Card Number', validators=[InputRequired(), Length(min=16, max=16)])
    cvv = StringField('CVV', validators=[InputRequired(), Length(min=3, max=5)])
    zip_code = StringField('ZIP Code', validators=[InputRequired(), Length(min=5, max=20)])
    exp_date = DateField('Expiration Date (YYYY-MM)', format='%Y-%m', validators=[InputRequired()])
    address = StringField('Billing Address', validators=[InputRequired(), Length(max=250)])