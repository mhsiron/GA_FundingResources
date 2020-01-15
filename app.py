from flask import Flask, render_template, request
import pandas as pd



app = Flask(__name__)



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
    return render_template('resources.html', resources=resources)

@app.route('/keyword/', methods=['GET'])
def findby():
    if request.method == 'GET':
        keyword, value = request.args.get('keyword',"description"),request.args.get('value',"")
        resources = fd.find_by(keyword,value)
        return render_template('resources.html', resources=resources)
@app.route('/keyword/<keyword>/<value>', methods=['GET'])
def findby_url(keyword, value):
    resources = fd.find_by(keyword, value)
    return render_template('resources.html', resources=resources)

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

    return render_template('resources.html', resources=resources)





app.run(debug=True)