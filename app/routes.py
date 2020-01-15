
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.form import LoginForm
import pandas as pd
import datetime
from config import Config
from flask_sqlalchemy import SQLAlchemy
from app.structures import FundingResources
from app.models import User


### Load init data:
df = pd.read_csv("data/funding_opt.csv", names = ['name', 'source', 'URL', 'deadline', 'description',
       'criteria', 'ammount', 'restrictions', 'timeline', 'point_of_contact',
       'ga_contact', 'keywords','main_cat'])
df = df.fillna(False)
df = df.replace('\n','', regex=True)

### Load data into data structure
fd = FundingResources(df)


@app.route('/')
@app.route('/resources')
def index():
    resources = fd.funding_resources
    return render_template('resources.html', resources=resources, datetime=datetime)

@app.route('/keyword/', methods=['GET'])
def findby():
    if request.method == 'GET':
        keyword, value = request.args.get('keyword',"description"),request.args.get('value',"")
        resources = fd.find_by(keyword,value)
        return render_template('resources.html', resources=resources, datetime=datetime)
@app.route('/keyword/<keyword>/<value>', methods=['GET'])
def findby_url(keyword, value):
    resources = fd.find_by(keyword, value)
    return render_template('resources.html', resources=resources, datetime=datetime)

@app.route('/welcome/')
def welcome():
    return render_template('welcome.html')

@app.route('/applyfilter/', methods=['GET'])
def applyfilter():
    funding_for = request.args.get('funding_for',False)
    myself_funding = request.args.get('myself_funding',False)
    orgfund = request.args.get('orgfund',False)
    res_fund = request.args.get('res_fund',False)

    filter_criteria = None
    if myself_funding is not "gen" and myself_funding:
        filter_criteria = myself_funding
    elif orgfund is not "gen" and orgfund:
        filter_criteria = orgfund
    elif res_fund is not "gen" and res_fund:
        filter_criteria = res_fund
    resources = fd.filter_by_type(funding_for,filter_criteria)

    return render_template('resources.html', resources=resources, datetime=datetime)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            print("u not in data")
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


db.create_all()
#create sample admin user:
u = User(username='admin', email='admin@example.com')
u.set_password('mypassword')

db.session.add(u)
db.session.commit()

app.run(debug=True)