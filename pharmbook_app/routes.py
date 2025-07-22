from pharmbook_app import pharmbook_init, db
from pharmbook_app.models import User, Food, Medicine, StatusEnum
from flask import render_template, redirect, flash, url_for, abort, request
from flask_login import current_user, login_user, logout_user, login_required
from forms import LoginForm, AddFoodForm, AddMedicineForm
from .crypto_api import get_btc_thb_rate, get_btc_trend
from datetime import datetime
import sqlalchemy as sa


def calculate_product_prices(products):
    """Helper function to calculate BTC prices and trends"""
    btc_rate = get_btc_thb_rate()
    for product in products:
        product.btc_price = round(product.price_thb / btc_rate, 8) if btc_rate else 0
        product.price_trend = get_btc_trend()
    return products

@pharmbook_init.route('/')
def index():
    search_query = request.args.get('q', '').strip()
    
    # ค้นหาทั้งอาหารและยา
    food_query = Food.query
    med_query = Medicine.query
    
    if search_query:
        food_query = food_query.filter(Food.name.ilike(f'%{search_query}%'))
        med_query = med_query.filter(Medicine.name.ilike(f'%{search_query}%'))
    
    foods = food_query.order_by(Food.created_at.desc()).all()
    medicines = med_query.order_by(Medicine.created_at.desc()).all()
    
    # รวมผลลัพธ์
    products = foods + medicines
    products = calculate_product_prices(products)
    
    return render_template('index.html', 
                         title='Home',
                         products=products,
                         search_query=search_query)

@pharmbook_init.route('/medicines')
def medicines():
    meds = Medicine.query.order_by(Medicine.created_at.desc()).all()
    meds = calculate_product_prices(meds)
    return render_template('products.html', title='Medicines', products=meds, product_type='medicines')

@pharmbook_init.route('/foods')
def foods():
    foods = Food.query.order_by(Food.created_at.desc()).all()
    foods = calculate_product_prices(foods)
    return render_template('products.html', title='Foods', products=foods, product_type='foods')

@pharmbook_init.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        flash('Login successful', 'success')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@pharmbook_init.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@pharmbook_init.route('/add_product/<product_type>', methods=['GET', 'POST'])
@login_required
def add_product(product_type):
    if product_type == 'food':
        form = AddFoodForm()
        template = 'add_food.html'
    elif product_type == 'medicine':
        form = AddMedicineForm()
        template = 'add_medicine.html'
    else:
        abort(404)

    if form.validate_on_submit():
        product_data = {
            'name': form.name.data,
            'image': form.image.data,
            'detail': form.detail.data,
            'unit': form.unit.data,
            'price_thb': float(form.price_thb.data),
            'status': StatusEnum(form.status.data),
            'created_at': datetime.now()
        }

        if product_type == 'food':
            product_data.update({
                'nutrition_facts': form.nutrition_facts.data,
                'expiry_date': form.expiry_date.data
            })
            new_product = Food(**product_data)
        else:
            product_data.update({
                'dosage': form.dosage.data,
                'side_effects': form.side_effects.data,
                'manufacturer': form.manufacturer.data
            })
            new_product = Medicine(**product_data)

        db.session.add(new_product)
        db.session.commit()
        flash(f'{product_type.capitalize()} added successfully', 'success')
        return redirect(url_for(f'{product_type}s'))

    return render_template(template, title=f'Add {product_type.capitalize()}', form=form)