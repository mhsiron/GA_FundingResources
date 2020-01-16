
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user
from app import app, db
from app.form import LoginForm, FundingResourceForm
import pandas as pd
import datetime
from app.models import User, Main_Categories
from app.models import FundingResources
import dateutil.parser
from _pydecimal import Decimal
import re


### Load init data:
df = pd.read_csv("data/funding_opt.csv", names = ['name', 'source', 'URL', 'deadline', 'description',
       'criteria', 'amount', 'restrictions', 'timeline', 'point_of_contact',
       'ga_contact', 'keywords','main_cat'])
df = df.drop(df.index[0])
df = df.fillna(False)
df['deadline'] = pd.to_datetime(df['deadline'], errors='ignore')
df = df.replace('\n','', regex=True)


#reset everything
db.create_all()
User.query.delete()
FundingResources.query.delete()
# create sample admin user:
u = User(username='admin', email='admin@example.com')
u.set_password('mypassword')
u.make_admin()
db.session.add(u)

# populate resources
for iloc in range(1,len(df)):
    deadline = datetime.datetime(2019, 1, 1)

    # clean up amount
    amount = 0
    try:
        amount = Decimal(re.sub("[^0-9]", "", df.iloc[iloc].get("amount")))
    except:
        amount = 0

    # clean up deadline
    try:
        deadline = dateutil.parser.parse(df.iloc[iloc].get("deadline"),fuzzy=True)
    except:
        deadline = datetime.datetime(2019, 1, 1)

    # clean up categories:
    categories=  df.iloc[iloc].get("categories")
    if not categories in [e.value for e in Main_Categories]:
        categories = None

    #insert
    try:
        f = FundingResources(name = df.iloc[iloc]["name"],
               source = df.iloc[iloc]['source'],
               URL=df.iloc[iloc]['URL'],
               deadline=deadline,
               description=df.iloc[iloc]['description'],
               criteria=df.iloc[iloc]['criteria'],
               amount=amount,
               restrictions=df.iloc[iloc]['restrictions'],
               timeline=df.iloc[iloc]['timeline'],
               point_of_contact=df.iloc[iloc]['point_of_contact'],
               ga_contact=df.iloc[iloc]['ga_contact'],
               keywords=df.iloc[iloc]['keywords'],
               main_cat=categories
               )
        db.session.add(f)
    except:
        continue

db.session.commit()


@app.route('/')
@app.route('/resources')
def index():
    #resources = fd.funding_resources
    resources = FundingResources.query.all()
    return render_template('resources.html', resources=resources, datetime=datetime)

@app.route('/keyword/', methods=['GET'])
def findby():
    if request.method == 'GET':
        keyword, value = request.args.get('keyword',"description"),request.args.get('value',"")
        column_name = getattr(FundingResources, keyword)
        resources = FundingResources.query.filter(column_name.contains(value)).all()
        return render_template('resources.html', resources=resources, datetime=datetime)
@app.route('/keyword/<keyword>/<value>', methods=['GET'])
def findby_url(keyword, value):
    column_name = getattr(FundingResources, keyword)
    resources = FundingResources.query.filter(column_name.contains(value)).all()
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


    resources = FundingResources.query.filter(
        FundingResources.main_cat.contains(funding_for)).filter(
        FundingResources.keywords.contains(filter_criteria)).all()

    return render_template('resources.html', resources=resources, datetime=datetime)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/new_resource', methods=['GET', 'POST'])
def new_resource():
    if current_user.is_anonymous:
        return redirect(url_for('index'))
    form = FundingResourceForm()
    if form.validate_on_submit():
        f = FundingResources(name=form.name.data,
                             source=form.source.data,
                             URL=form.URL.data,
                             deadline=form.deadline.data,
                             description=form.description.data,
                             criteria=form.criteria.data,
                             amount=form.amount.data,
                             restrictions=form.restrictions.data,
                             timeline=form.timeline.data,
                             point_of_contact=form.point_of_contact.data,
                             ga_contact=form.ga_contact.data,
                             keywords=form.keywords.data,
                             main_cat=form.main_cat.data
                             )
        db.session.add(f)
        return redirect(url_for('index'))
    return render_template('new_resource.html', title='Sign In', form=form)

app.run(debug=True)