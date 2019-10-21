from app import app , db, bcrypt
from flask import render_template, flash, redirect , url_for , request, session
from app.forms import LoginForm, RegistrationForm , UpdateAccountForm, AddressForm
from app.models import User, Post
import sqlite3
from flask_login import login_user, current_user, logout_user, login_required
from requests_oauthlib import OAuth2Session
from requests.exceptions import HTTPError
import os
import json
from app.forms import ResetPasswordRequestForm
from app.emailPasswordReset import send_password_reset_email
from app.forms import ResetPasswordForm

class Auth:
    """Google Project Credentials"""
    CLIENT_ID = ('356186709623-6tb84gjrptp1ss0cificl90ia45qufa4.apps.googleusercontent.com')
    CLIENT_SECRET = 'gJ5hLx6ikRTAC8NlONLZ67Kx'
    REDIRECT_URI = 'https://localhost:5000/gCallback'
    AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
    USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'
    SCOPE = ['profile', 'email']

noOfItems=0

def noOfItem():
    if current_user.is_authenticated:
        with sqlite3.connect('app/site.db') as conn:
            cur=conn.cursor()
            cur.execute("SELECT quantity FROM cart WHERE userId = " + str(current_user.id))
            noOfItems = cur.fetchall()
            item=0
            for row in noOfItems:
                item+=row[0]
        conn.close()
        return item
    else:
        return 0


@app.route('/')
@app.route('/index')
def index():
    noOfItems=noOfItem()
    return render_template('index.html', noOfItem=noOfItems)

@app.route('/analogue')
def analogue():
    noOfItems=noOfItem()

    with sqlite3.connect('app/site.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT products.productId, products.name, products.price, products.product_img FROM products WHERE products.categoryId = '1'")
            data = cur.fetchall()
    return render_template('productsdisplay.html', data= data, categoryName='Analogue', noOfItem=noOfItems)

@app.route('/digital')
def digital():
    noOfItems=noOfItem()
    with sqlite3.connect('app/site.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT products.productId, products.name, products.price, products.product_img FROM products WHERE products.categoryId = '2'")
            data = cur.fetchall()
    return render_template('productsdisplay.html', data= data, categoryName='Digital', noOfItem=noOfItems)

@app.route('/productdescription/<string:id>', methods=['GET','POST'])
def productdescription(id):
    productId= int(id)
    noOfItems=noOfItem()
    with sqlite3.connect('app/site.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT productId, name, price, image FROM products WHERE productId = " +str(productId) )
            product=cur.fetchone()
    conn.close()
    return render_template('productdescription.html' , product=product, noOfItem=noOfItems)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        next = request.args.get('next')
        return redirect(next) if next else redirect(url_for('index'))
    google = get_google_auth()
    auth_url, state = google.authorization_url(
        Auth.AUTH_URI, access_type='offline', prompt="select_account")
    session['oauth_state'] = state
    print(state)
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next = request.args.get('next')
            return redirect(next) if next else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form, noOfItem=noOfItems,auth_url=auth_url)

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    noOfItems=noOfItem()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, type="native")
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form, noOfItem=noOfItems)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    noOfItems=noOfItem()
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
    return render_template('account.html',form=form , noOfItem=noOfItems)

@app.route("/updateaddress", methods=['GET', 'POST'])
@login_required
def updateaddress():
    noOfItems=noOfItem()
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
    return render_template('updateaddress.html',form=form , noOfItem=noOfItems)

@app.route('/cart')
@login_required
def cart():
    noOfItems=noOfItem()
    with sqlite3.connect('app/site.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM user WHERE email = '" + current_user.email + "'")
        id = cur.fetchone()[0]
        cur.execute("SELECT cart.productId, cart.name, cart.price, cart.image, cart.quantity FROM cart WHERE cart.userId = " + str(id))
        products = cur.fetchall()
        cur.execute("SELECT count(productId) FROM cart WHERE userId = " + str(id))
    totalPrice = 0
    for row in products:
        totalPrice += row[4]*row[2]
    return render_template("cart.html", data = products, totalPrice=totalPrice, noOfItem=noOfItems)

@app.route("/addToCart")
@login_required
def addToCart():
    noOfItems=noOfItem()
    productId = int(request.args.get('productId'))
    with sqlite3.connect('app/site.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM user WHERE email = '" + current_user.email + "'")
            id = cur.fetchone()[0]
            # try:
            cur.execute("SELECT products.productId, products.name, products.price, products.product_img FROM products WHERE products.productId=" + str(productId))
            products=cur.fetchone()
            cur.execute("SELECT count(productId),quantity FROM cart WHERE productId = " + str(products[0]))
            count=cur.fetchone()
            cur.execute("DELETE FROM wishlist WHERE userId=" + str(id)+ " AND productId=" +str(productId))
            print(count)
            if count[0]!=1:
                cur.execute("INSERT INTO cart (userId, productId, name , price , image , quantity) VALUES (?, ?, ?, ?, ?, ?)", (id, productId,products[1],products[2],products[3], +1))
            else:
                a=count[1]+1
                cur.execute("UPDATE cart SET quantity ='" +str(a) +"'WHERE productId=" +str(products[0]))
            conn.commit()
            flash('Added', 'success')
            # except:
            #     conn.rollback()
            #     flash('Error Occured', 'Failed')
    conn.close()
    return redirect(url_for('index'))

@app.route("/RemoveFromCart")
@login_required
def RemoveFromCart():
    noOfItems=noOfItem()
    productId = int(request.args.get('productId'))
    with sqlite3.connect('app/site.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM user WHERE email = '" + current_user.email + "'")
            id = cur.fetchone()[0]
            # try:
            cur.execute("SELECT count(productId),quantity FROM cart WHERE productId = " + str(productId))
            count=cur.fetchone()
            print(count)
            if count[1]==1:
                cur.execute("DELETE FROM cart WHERE userId=" + str(id)+ " AND productId=" +str(productId))
            else:
                a=count[1]-1
                cur.execute("UPDATE cart SET quantity ='" +str(a) +"'WHERE productId=" +str(productId))
            conn.commit()
            flash('Removed', 'success')
            # except:
            #     conn.rollback()
            #     flash('Error Occured', 'Failed')
    conn.close()
    return redirect(url_for('cart'))

@app.route("/checkout", methods=['GET', 'POST'])
@login_required
def checkout():
    noOfItems=noOfItem()
    form = AddressForm()
    if form.validate_on_submit():
        current_user.name=form.name.data
        current_user.address1=form.address1.data
        current_user.address2=form.address2.data
        current_user.city=form.city.data
        current_user.state=form.state.data
        current_user.zipcode=form.zipcode.data
        db.session.commit()
        with sqlite3.connect('app/site.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM user WHERE email = '" + current_user.email + "'")
            id = cur.fetchone()[0]
            cur.execute("SELECT cart.productId, cart.name, cart.price, cart.image, cart.quantity FROM cart WHERE cart.userId = " + str(id))
            products = cur.fetchall()
            cur.execute("DELETE FROM cart WHERE userId = " + str(current_user.id))
            for row in products:
                cur.execute("INSERT INTO orders (userId, productId, quantity, price) VALUES (?, ?, ?, ?)", (current_user.id, row[0],row[4],row[2]))
        flash('Your order has been placed!', 'success')
        return redirect(url_for('index'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.address1.data=current_user.address1
        form.address2.data=current_user.address2
        form.city.data=current_user.city
        form.state.data=current_user.state
        form.zipcode.data=current_user.zipcode
    return render_template('updateaddress.html',form=form , noOfItem=noOfItems)

@app.route("/orders")
@login_required
def orders():
    noOfItems=noOfItem()
    with sqlite3.connect('app/site.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM user WHERE email = '" + current_user.email + "'")
            id = cur.fetchone()[0]
            # try:
            cur.execute("SELECT products.productId, products.name, products.price, products.product_img, orders.orderId, orders.quantity FROM products, orders WHERE products.productId = orders.productId AND orders.userId = " + str(current_user.id))
            products=cur.fetchall()
    conn.close()
    return render_template("order.html", data = products,  noOfItem=noOfItems)

@app.route("/MovetoWishlist")
@login_required
def MovetoWishlist():
    noOfItems=noOfItem()
    productId = int(request.args.get('productId'))
    with sqlite3.connect('app/site.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM user WHERE email = '" + current_user.email + "'")
            id = cur.fetchone()[0]
            cur.execute("INSERT INTO wishlist (userId,productId) VALUES (?, ?)", (id, productId))
            cur.execute("DELETE FROM cart WHERE userId=" + str(id)+ " AND productId=" +str(productId))
            conn.commit()
            flash('Moved', 'success')
            # except:
            #     conn.rollback()
            #     flash('Error Occured', 'Failed')
    conn.close()
    return redirect(url_for('wishlist'))

@app.route('/wishlist')
@login_required
def wishlist():
    noOfItems=noOfItem()
    with sqlite3.connect('app/site.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM user WHERE email = '" + current_user.email + "'")
        id = cur.fetchone()[0]
        cur.execute("SELECT products.productId, products.name, products.price, products.product_img FROM products , wishlist WHERE products.productId=wishlist.productId AND wishlist.userId = " + str(id))
        products = cur.fetchall()
    return render_template("wishlist.html", data=products, noOfItem=noOfItems)

@app.route("/RemoveFromWishlist")
@login_required
def RemovetoWishlist():
    noOfItems=noOfItem()
    productId = int(request.args.get('productId'))
    with sqlite3.connect('app/site.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM user WHERE email = '" + current_user.email + "'")
            id = cur.fetchone()[0]
            cur.execute("DELETE FROM wishlist WHERE userId=" + str(id)+ " AND productId=" +str(productId))
            conn.commit()
            flash('Removed', 'success')
            # except:
            #     conn.rollback()
            #     flash('Error Occured', 'Failed')
    conn.close()
    return redirect(url_for('wishlist'))

@app.route('/gCallback', methods=["GET"])
def callback():
    # Redirect user to home page if already logged in.
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('index'))
    if 'error' in request.args:
        if request.args.get('error') == 'access_denied':
            flash('Error Occured', 'Failed')
            return redirect(url_for('wishlist'))
        flash('Error Occured', 'Failed')
        return redirect(url_for('wishlist'))
    if 'code' not in request.args and 'state' not in request.args:
        return redirect(url_for('login'))
    else:
        # Execution reaches here when user has
        # successfully authenticated our app.
        google = get_google_auth()
        auth_url, state = google.authorization_url(
        Auth.AUTH_URI, access_type='offline', prompt="select_account")
        print(state)
        google = OAuth2Session(Auth.CLIENT_ID, state=state)
        try:
            token = google.fetch_token(
                Auth.TOKEN_URI,
                client_secret=Auth.CLIENT_SECRET,
                authorization_response=request.url)
        except HTTPError:
            return redirect(url_for('wishlist'))
        google = get_google_auth(token=token)
        resp = google.get(Auth.USER_INFO)
        if resp.status_code == 200:
            user_data = resp.json()
            email = user_data['email']
            user = User.query.filter_by(email=email).first()
            if user is None:
                user = User()
                user.email = email
            user.name = user_data['name']
            print(token)
            user.tokens = json.dumps(token)
            user.type="google"
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('index'))
        return 'Could not fetch your information.'

def get_google_auth(state=None, token=None):
    if token:
        return OAuth2Session(Auth.CLIENT_ID, token=token)
    if state:
        return OAuth2Session(Auth.CLIENT_ID,state=state,redirect_uri=Auth.REDIRECT_URI)

    oauth = OAuth2Session(Auth.CLIENT_ID,redirect_uri=Auth.REDIRECT_URI,scope=Auth.SCOPE)

    return oauth

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
