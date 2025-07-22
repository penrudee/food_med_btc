from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, PasswordField, BooleanField, SubmitField, DateField
from wtforms.validators import DataRequired, NumberRange
from enum import Enum

class StatusEnum(Enum):
    AVAILABLE = 'available'
    NON_AVAILABLE = 'non-available'
    SPECIAL_ORDER = 'Special Order'
    PRE_ORDER = 'Pre-Order'

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class BaseProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    image = StringField('Image URL', validators=[DataRequired()])
    detail = TextAreaField("Detail", validators=[DataRequired()], 
                         render_kw={"class": "form-control", "rows": 5})
    unit = StringField('Unit', validators=[DataRequired()])
    price_thb = StringField('Price (THB)', validators=[
        DataRequired(),
        NumberRange(min=0, message="Price must be positive")
    ])
    status = SelectField(
        "Status",
        choices=[(status.value, status.value.replace('-', ' ')) for status in StatusEnum],
        validators=[DataRequired()]
    )

class AddFoodForm(BaseProductForm):
    nutrition_facts = TextAreaField("Nutrition Facts", 
                                  render_kw={"class": "form-control", "rows": 3})
    expiry_date = DateField('Expiry Date', format='%Y-%m-%d')
    submit = SubmitField('Add Food')

class AddMedicineForm(BaseProductForm):
    dosage = TextAreaField("Dosage Instructions", 
                         render_kw={"class": "form-control", "rows": 3})
    side_effects = TextAreaField("Side Effects", 
                               render_kw={"class": "form-control", "rows": 3})
    manufacturer = StringField('Manufacturer', validators=[DataRequired()])
    submit = SubmitField('Add Medicine')