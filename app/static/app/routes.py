from app import app , db, bcrypt
from flask import render_template, flash, redirect , url_for , request
from app.forms import LoginForm, RegistrationForm , UpdateAccountForm, AddressForm
from app.models import User
import sqlite3
from flask_login import login_user, current_user, logout_user, login_required
from app.forms import ResetPasswordRequestForm
from app.emailPasswordReset import send_password_reset_email
from app.forms import ResetPasswordForm


def getLoginDetails():
    with sqlite3.connect('/Users/raj.burad7/Desktop/APproject/project/app/site.db') as conn:
        cur.execute("SELECT id, FROM users WHERE email = '" + session['email'] + "'")
        id = cur.fetchone()
        cur.execute("SELECT count(productId) FROM cart WHERE userId = " + str(id))
        noOfItems = cur.fetchone()[0]
    conn.close()
    return (firstName, noOfItems)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/analogue')
def analogue():
    with sqlite3.connect('/Users/raj.burad7/Desktop/APproject/project/app/site.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT products.productId, products.name, products.price, products.image FROM products WHERE products.categoryId = '1'")
            data = cur.fetchall()
    return render_template('productsdisplay.html', data= data, categoryName='Analogue')

@app.route('/digital')
def digital():
    with sqlite3.connect('/Users/raj.burad7/Desktop/APproject/project/app/site.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT products.productId, products.name, products.price, products.image FROM products WHERE products.categoryId = '2'")
            data = cur.fetchall()
    return render_template('productsdisplay.html', data= data, categoryName='Digital')

@app.route('/productdescription/<string:id>', methods=['GET','POST'])
def productdescription(id):
    productId= int(id)
    print(productId)
    with sqlite3.connect('/Users/raj.burad7/Desktop/APproject/project/app/site.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT productId, name, price, image FROM products WHERE productId = " +str(productId) )
            product=cur.fetchone()
    conn.close()
    return render_template('productdescription.html' , product=product)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        next = request.args.get('next')
        return redirect(next) if next else redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next = request.args.get('next')
            return redirect(next) if next else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.password.data=current_user.password
    return render_template('account.html',form=form)

@app.route("/updateaddress", methods=['GET', 'POST'])
@login_required
def updateaddress():
    form = AddressForm()
    if form.validate_on_submit():
        current_user.name=form.name.data
        current_user.address1=form.address1.data
        current_user.address2=form.address2.data
        current_user.city=form.city.data
        current_user.state=form.state.data
        current_user.zipcode=form.zipcode.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('updateaddress'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.address1.data=current_user.address1
        form.address2.data=current_user.address2
        form.city.data=current_user.city
        form.state.data=current_user.state
        form.zipcode.data=current_user.zipcode
    return render_template('updateaddress.html',form=form)

@app.route('/cart')
@login_required
def cart():
    with sqlite3.connect('/Users/raj.burad7/Desktop/APproject/project/app/site.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM user WHERE email = '" + current_user.email + "'")
        id = cur.fetchone()[0]
        cur.execute("SELECT products.productId, products.name, products.price, products.image FROM products, cart WHERE products.productId = cart.productId AND cart.userId = " + str(id))
        products = cur.fetchall()
        cur.execute("SELECT count(productId) FROM cart WHERE userId = " + str(id))
        noOfItems = cur.fetchone()[0]
    totalPrice = 0
    for row in products:
        totalPrice += row[2]
    return render_template("cart.html", data = products, totalPrice=totalPrice, noOfItems=noOfItems)

@app.route("/addToCart")
@login_required
def addToCart():
    productId = int(request.args.get('productId'))
    with sqlite3.connect('/Users/raj.burad7/Desktop/APproject/project/app/site.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM user WHERE email = '" + current_user.email + "'")
            id = cur.fetchone()[0]
            try:
                cur.execute("INSERT INTO cart (userId, productId) VALUES (?, ?)", (id, productId))
                conn.commit()
                flash('Added', 'success')
            except:
                conn.rollback()
                flash('Error Occured', 'Failed')
    conn.close()
    return redirect(url_for('index'))

@app.route("/RemoveFromCart")
@login_required
def RemoveFromCart():
    productId = int(request.args.get('productId'))
    with sqlite3.connect('/Users/raj.burad7/Desktop/APproject/project/app/site.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM user WHERE email = '" + current_user.email + "'")
            id = cur.fetchone()[0]
            # try:
            cur.execute("DELETE FROM cart (userId, productId) VALUES (?, ?)", (id, productId))
            conn.commit()
            flash('Removed', 'success')
            # except:
            #     conn.rollback()
            #     flash('Error Occured', 'Failed')
    conn.close()
    return redirect(url_for('cart'))


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)



@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', title = 'Reset Password', form=form)
