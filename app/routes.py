from app import app , db, bcrypt
from flask import render_template, flash, redirect , url_for , request, session , g
from app.forms import LoginForm, RegistrationForm , UpdateAccountForm, AddressForm , SearchForm
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
from app.auth import OAuthSignIn
from app.emailSend import EmailClass
from app.__init__ import searchInProducts
from difflib import get_close_matches


app.config['OAUTH_CREDENTIALS'] = {
    'google': {
        'id': '356186709623-6tb84gjrptp1ss0cificl90ia45qufa4.apps.googleusercontent.com',
        'secret': 'gJ5hLx6ikRTAC8NlONLZ67Kx'
    }}
# class Auth:
#     """Google Project Credentials"""
#     CLIENT_ID = ('356186709623-6tb84gjrptp1ss0cificl90ia45qufa4.apps.googleusercontent.com')
#     CLIENT_SECRET = 'gJ5hLx6ikRTAC8NlONLZ67Kx'
#     REDIRECT_URI = 'https://localhost:5000/gCallback'
#     AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
#     TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
#     USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'
#     SCOPE = ['profile', 'email']

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

@app.before_request
def before_request():
    g.search_form = SearchForm()

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
            cur.execute("SELECT productId, name, price, product_img,brand , family ,model ,produced ,materials ,glass ,diameter ,height ,wr ,color ,finish ,type ,display ,chronograph ,acoustic ,additional ,description, brand_img  FROM products WHERE productId = " +str(productId) )
            product=cur.fetchone()
    conn.close()
    return render_template('productdescription.html' , product=product, noOfItem=noOfItems)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        next = request.args.get('next')
        return redirect(next) if next else redirect(url_for('index'))
    # google = get_google_auth()
    # auth_url, state = google.authorization_url(
    #     Auth.AUTH_URI, access_type='offline', prompt="select_account")
    # session['oauth_state'] = state
    # print(state)
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next = request.args.get('next')
            return redirect(next) if next else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form, noOfItem=noOfItems)

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
            cur.execute("SELECT count(productId),quantity FROM cart WHERE productId = '" + str(products[0])+"' AND userId="+str(id))
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
    return redirect(url_for('cart'))

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
    if(noOfItems==0):
        flash('Cart Empty')
        return redirect(url_for('cart'))
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
            order_email = []
            for row in products:
                tp = [row[1], row[2], row[4]]
                order_email.append(tp)
                cur.execute("INSERT INTO orders (userId, productId, quantity, price) VALUES (?, ?, ?, ?)", (current_user.id, row[0],row[4],row[2]))
        flash('Your order has been placed!', 'success')
        EmailClass.sendEmail(current_user.name, current_user.email, order_email)
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

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/gCallback/<provider>')
def oauth_callback(provider):
    print(provider)
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    email = oauth.callback()
    if email is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user=User.query.filter_by(email=email).first()
    if not user:
        username = email.split('@')[0]
        stri=" "
        user=User(username=username, email=email,password=bcrypt.generate_password_hash(stri).decode('utf-8'))
        db.session.add(user)
        db.session.commit()

    login_user(user, remember=True)
    return redirect(url_for('index'))


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
        flash('Email Id not registered. Please Sign Up.')
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

@app.route('/search', methods=['POST'])
def search():
    print(g.search_form.search.data)
    search=g.search_form.search.data.lower()
    print(search)
    data=[]
    i=1
    q = 0
    with sqlite3.connect('app/site.db') as conn:
            cur = conn.cursor()
            while(i<64):
                cur.execute("SELECT productId, name, price, product_img,brand , family ,model ,produced ,materials ,glass ,diameter ,height ,wr ,color ,finish ,type ,display ,chronograph ,acoustic ,additional ,description, brand_img  FROM products WHERE productId = " +str(i) )
                product=cur.fetchone()
                c=product[1].lower()
                if c.find(search) != -1:
                    print(product[1])
                    data.append(product)
                    q = q+1
                i+=1
    if q==0:
        xxx= ['Rolex', 'Datejust', 'Stainless', 'Steel', 'Diamond', 'Black', 'Oyster', 'Rolex', 'Sky-Dweller', 'Everose', 'White', 'Alligator', 'Rolex', 'Cellini', 'Time', 'Everose', 'Black', 'Alligator', 'Rolex', 'Yacht-Master', 'Everose', 'Cerachrom', 'Diamond', 'Rolex', 'Sea-Dweller', 'Stainless', 'Steel', 'Yellow', 'Gold', 'Black', 'Omega', 'Speedmaster', 'Co-Axial', 'Yellow', 'Gold', 'Rory', 'McIlroy', 'Bracelet', 'Omega', 'Seamaster', '1948', 'Small', 'Seconds', 'Platinum', 'Silver', 'Alligator', 'Omega', 'Dynamic', 'III', 'Chronograph', 'Stainless', 'Steel', 'Black', 'Red', 'Coramide', 'Longines', 'DolceVita', 'Quartz', 'Stainless', 'Steel', 'Diamond', 'Longines', 'Conquest', 'Heritage', 'Black', 'Longines', 'Equestrian', '26.5', 'Diamond', 'Black', 'IWC', 'Portuguese', 'Chrono-Rattrapante', 'Rose', 'Gold', 'Black', 'IWC', "Pilot's", 'Watch', 'Grey', 'IWC', 'Big', 'Pilot', 'ETA', 'Style', 'Stainless', 'Steel', 'Silver', 'Strap', 'Tudor', 'Heritage', 'Black', 'Bay', 'Ceramic', 'One', 'for', 'Only', 'Watch', 'ETA', 'Fastrider', 'Black', 'Shield', 'Ceramic', 'Black-Sand', 'Alcantara', 'Rolex', 'Radiomir', '47mm', 'Rolex', 'Marina', 'Militare', '6152-1', 'Crown', 'Guard', 'Panerai', 'Ferrari', 'Scuderia', 'Rattrapante', 'Patek', 'Philippe', 'Moonphase', '4968', 'White', 'Gold', 'White', 'Mother', 'Pearl', 'Patek', 'Philippe', 'Perpetual', 'Calendar', 'Chronograph', '1518', 'Patek', 'Philippe', 'Calatrava', '3718', '150th', 'Anniversary', 'Japanese', 'Market', 'Slate', 'Audemars', 'Piguet', 'Jules', 'Audemars', '15180', 'Extra-Thin', 'Pink', 'Gold', 'Black', 'Audemars', 'Piguet', 'Royal', 'Oak', 'Offshore', 'Diver', 'Stainless', 'Steel', 'White', 'Audemars', 'Piguet', 'Millenary', 'Quincy', 'Jones', 'TAG', 'Heuer', 'Khaki', 'Aviation', 'Day', 'Date', 'Stainless', 'Steel', 'Blue', 'Strap', 'Hamilton', 'Frogman', 'Auto', 'Black', 'Strap', 'Hamilton', 'Intra-Matic', 'Autochrono', 'Stainless', 'Steel', 'Blue', 'Strap', 'ETA', 'Quartz', 'Chronograph', 'Stainless', 'Steel', 'Carbon', 'Strap', 'Alpine', 'ETA', 'Couturier', 'Automatic', 'Small', 'Second', 'Stainless', 'Steel', 'Silver', 'Strap', 'Romania', 'Centenary', 'ETA', 'Gentleman', 'Powermatic', 'Stainless', 'Steel', 'Red', 'Gold', 'Cream', 'Strap', 'Glash�tte', 'Original', 'Senator', 'Observer', 'Stainless', 'Steel', 'Grey', 'Calf', 'Folding', 'Glash�tte', 'Original', 'PanoMatic', 'Lunar', 'Stainless', 'Steel', 'Rose', 'Alligator', 'Folding', 'Glash�tte', 'Original', 'SeaQ', 'Panorama', 'Date', 'Stainless', 'Steel', 'Blue', 'Textile', 'Folding', 'ETA', 'Podium', 'Big', 'Size', 'Chrono', 'Precidrive', 'PVD', 'Black', 'Strap', 'ETA', 'Action', 'Diver', 'Powermatic', 'Stainless', 'Steel', 'Black', 'Rubber', 'Sea', 'Turtle', 'Conservancy', 'ETA', 'First', 'Lady', 'Ceramic', 'Rose', 'Black', 'TAG', 'Heuer', 'Carrera', 'Calibre', 'Heuer', 'DBS', 'Edition', 'TAG', 'Heuer', 'Aquaracer', '43mm', 'Automatic', 'Titanium', 'Jungle', 'TAG', 'Heuer', 'Autavia', 'Calibre', 'Stainless', 'Steel', 'Black', 'Leather', 'Jaeger-LeCoultre', 'Rendez-Vous', 'Moon', 'Medium', 'Pink', 'Gold', 'Diamond', 'Silver', 'Jaeger-LeCoultre', 'Duom�tre', 'Chronographe', 'Pink', 'Gold', 'Silver', 'Jaeger-LeCoultre', 'Master', 'Compressor', 'Chronograph', 'Ceramic', 'Vacheron', 'Constantin', 'Patrimony', '36.5mm', 'Self-Winding', 'White', 'Gold', 'Diamond', 'Silver', 'Vacheron', 'Constantin', 'Overseas', 'Chronograph', 'Pink', 'Gold', 'Brown', 'Bracelet', 'Vacheron', 'Constantin', 'Les', 'Cabinotiers', 'Minute', 'Repeater', 'Perpetual', 'Calendar', 'Pink', 'Gold', 'Brown', 'Breitling', 'Navitimer', '1461', 'Stainless', 'Steel', 'Black', 'Croco', 'Pin', 'Breitling', 'Superocean', 'Heritage', 'Chronograph', 'Stainless', 'Steel', 'Black', 'Black', 'Croco', 'Folding', 'Breitling', 'Transocean', 'Chronograph', 'Stainless', 'Steel', 'Panda', 'Croco', 'Folding', 'Apple', 'Watch', '38mm', 'Apple', 'Watch', '38mm', 'Apple', 'Watch', '38mm', 'Apple', 'Watch', 'Sport', 'Rose', 'Gold', '42mm', 'Apple', 'Watch', 'Edition', '42mm', 'Apple', 'Watch', 'Edition', '42mm', 'Apple', 'Watch', 'Sport', '38mm', 'Apple', 'Watch', 'Sport', 'Gold', '42mm', 'Casio', 'GD-X6900PM-1', 'Electric', 'Casio', 'DW-6900DS-1', 'Black', 'Diamond', 'Pattern', 'Casio', 'DW-6900HM-2', 'Navy', 'Blue', 'Brushed', 'Steel', 'Casio', 'GD-X6900-1', 'Black', 'Casio', 'DW-6900WW-7', 'Basic', 'White', 'Casio', 'GA-100C-8A', 'Blue', 'Hands', 'Casio', 'G-Shock', 'Mudmaster', 'Twin', 'Sensor', 'Black', 'Green', 'Casio', 'G-Shock', 'Mudmaster', 'Triple', 'Sensor', 'Black', 'Black', 'Casio', 'G-Shock', 'Mudmaster', 'Triple', 'Sensor', 'Black', 'Yellow', 'Casio', 'G-Shock', 'Mudmaster', 'Triple', 'Sensor', 'Black', 'Red', 'Casio', 'G-Shock', 'Mudmaster', 'Twin', 'Sensor', 'Black', 'Beige', 'ETA', 'T-Touch', 'Expert', 'Carbon', 'Rubber', 'ETA', 'T-Touch', 'Orange', 'Rubber', 'ETA', 'T-Touch', 'Black', 'Rubber', 'ETA', 'T-Touch', 'Expert', 'Solar', 'Ti/', 'Rubber', 'ETA', 'T-Touch', 'Expert', 'Leather', 'ETA', 'T-Touch', 'Black', 'Bracelet']
        tt = get_close_matches(search, xxx, 1)
        tt=tt[0].lower()
        print(tt)
        flash("No Results Found. Showing Results For " + tt)
        print("XXXXx")
        data=[]
        i=1
        with sqlite3.connect('app/site.db') as conn:
                cur = conn.cursor()
                while(i<64):
                    print(i)
                    cur.execute("SELECT productId, name, price, product_img,brand , family ,model ,produced ,materials ,glass ,diameter ,height ,wr ,color ,finish ,type ,display ,chronograph ,acoustic ,additional ,description, brand_img  FROM products WHERE productId = " +str(i) )
                    product=cur.fetchone()
                    c=product[1].lower()
                    if c.find(str(tt)) != -1:
                        print(product[1])
                        data.append(product)
                    i+=1


    return render_template('productsdisplay.html', data= data, categoryName=search, noOfItem=noOfItems)
