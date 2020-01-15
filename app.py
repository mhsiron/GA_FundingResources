from flask import Flask, render_template, request, flash, redirect
import pandas as pd
import datetime
from config import Config
from data.form import LoginForm
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)



### Load data:
df = pd.read_csv("data/funding_opt.csv", names = ['name', 'source', 'URL', 'deadline', 'description',
       'criteria', 'ammount', 'restrictions', 'timeline', 'point_of_contact',
       'ga_contact', 'keywords','main_cat'])
df = df.fillna(False)
df = df.replace('\n','', regex=True)

### Load data into data structure
from data.models import FundingResource, FundingResources
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
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect('/')
    return render_template('login.html', title='Sign In', form=form)





app.run(debug=True)