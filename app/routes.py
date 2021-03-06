from flask import render_template, flash, redirect, url_for, request, session
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db
from app.form import LoginForm, FundingResourceForm, FundingResourceUpdateForm, FundingResourceCommentForm, EditProfileForm, EditProfilePhotoForm
import pandas as pd
import datetime
from app.models import User, Main_Categories, FundingResources, FundingResourceComments
import dateutil.parser
from _pydecimal import Decimal
import re
from werkzeug.utils import secure_filename
import os


### Load init data:
df = pd.read_csv("./data/funding_opt.csv", names = ['name', 'source', 'URL', 'deadline', 'description',
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
FundingResourceComments.query.delete()
# create sample admin user:
u = User(username='admin', email='admin@example.com')
u.set_password('mypassword')
u.make_admin()
db.session.add(u)
# create sample non admin user:
u = User(username='editor', email='editor@example.com')
u.set_password('mypassword')
u.make_editor()
db.session.add(u)
db.session.commit()

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
                             main_cat=categories,
                             user_id=1,
                             is_enabled=True)
        db.session.add(f)
    except:
        continue

db.session.commit()


@app.route('/')
@app.route('/resources')
def index():
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

@app.route('/user/<int:id>',methods=['GET'])
def find_by_user(id):
    resources = FundingResources.query.filter_by(user_id=id).all()
    user = User.query.filter_by(id=id).first()
    return render_template('resources.html', resources=resources,
                           datetime=datetime, user=user)

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
    if funding_for == "personal":
        filter_criteria = myself_funding
    elif funding_for == "organization":
        filter_criteria = orgfund
    elif funding_for == "research":
        filter_criteria = res_fund

    resources = FundingResources.query.filter(
        FundingResources.main_cat.contains(funding_for))
    if filter_criteria != "gen":
        print(filter_criteria,funding_for)
        resources = FundingResources.query.filter(FundingResources.main_cat == funding_for, FundingResources.keywords.like("%{}%".format(filter_criteria))).all()
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
@login_required
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
                             main_cat=form.main_cat.data,
                             user_id=current_user.id,
                             is_enabled=True
                             )
        print(f.__dict__)
        db.session.add(f)
        db.session.commit()
        return redirect(url_for('manage'))
    return render_template('new_resource.html', title='Sign In', form=form)

@app.route('/edit_resource', methods=['GET', 'POST'])
@login_required
def edit_resource():
    form = FundingResourceUpdateForm()
    if form.validate_on_submit():
        id = form.id.data
        current_resource = FundingResources.query.filter_by(id=id).first()
        current_resource.name = form.name.data
        current_resource.deadline = form.deadline.data
        current_resource.source = form.source.data
        current_resource.URL = form.URL.data
        current_resource.description = form.description.data
        current_resource.criteria = form.criteria.data
        current_resource.amount = form.amount.data
        current_resource.restrictions = form.restrictions.data
        current_resource.timeline = form.timeline.data
        current_resource.point_of_contact = form.point_of_contact.data
        current_resource.ga_contact = form.ga_contact.data
        current_resource.keywords = form.keywords.data
        current_resource.main_cat = form.main_cat.data
        current_resource.is_enabled = form.is_enabled.data
        if (current_resource.user_id == current_user.id or current_user.is_admin()):
            db.session.commit()
            flash('Your changes have been saved.')
            return redirect(url_for('manage'))
        else:
            flash("you're not allowed to edit this resource...")
            return redirect(url_for('index'))
    if request.method == 'GET':
        id = request.args["id"]
        current_resource = FundingResources.query.filter_by(id=id).first()
        if (current_resource.user_id == current_user.id or current_user.is_admin()):
            form.id.data = id
            form.name.data = current_resource.name
            form.deadline.data = current_resource.deadline
            form.source.data = current_resource.source
            form.URL.data = current_resource.URL
            form.description.data = current_resource.description
            form.criteria.data = current_resource.criteria
            form.amount.data = current_resource.amount
            form.restrictions.data = current_resource.restrictions
            form.timeline.data = current_resource.timeline
            form.point_of_contact.data = current_resource.point_of_contact
            form.ga_contact.data = current_resource.ga_contact
            form.keywords.data = current_resource.keywords
            form.is_enabled.data = current_resource.is_enabled
            if current_resource.main_cat:
                form.main_cat.data = current_resource.main_cat.value
            else:
                form.main_cat.data = current_resource.main_cat
        else:
            flash("you're not allowed to edit this resource...")
            return redirect(url_for('index'))
    return render_template('edit_resource.html', title='Edit Resource',
                           form=form)

@app.route('/manage', methods=['GET', 'POST'])
@login_required
def manage():
    if current_user.is_admin():
        resources = FundingResources.query.all()
        return render_template('resources.html', resources=resources,
                               datetime=datetime, editable=True, user=current_user)
    else:
        resources = FundingResources.query.filter_by(user_id=current_user.id)
        return render_template('resources.html', resources=resources,
                               datetime=datetime, editable=True, user=current_user)
@app.route('/switchenable/<int:id>', methods=['GET'])
def switchenable(id):
    if current_user.is_anonymous:
        flash('You are not allowed to edit this resource - please login')
        return redirect(url_for('index'))
    current_resource = FundingResources.query.filter_by(id=id).first()
    if current_user.id != current_resource.user_id or not current_user.is_admin():
        flash('You are not allowed to edit this resource...')
        return redirect(url_for('index'))
    current_resource.is_enabled = not current_resource.is_enabled
    db.session.commit()
    flash('Enabled has been set to {}'.format(current_resource.is_enabled))
    return redirect(url_for('manage'))

@app.route('/resource/<int:id>', methods=['GET', 'POST'])
def view_resource(id):
    current_resource = FundingResources.query.filter_by(id=id).first()
    form = FundingResourceCommentForm()


    if form.validate_on_submit():
        c = FundingResourceComments(posted_date=datetime.date.today(),
                                    comment_title=form.comment_title.data,
                                    comment=form.comment.data,
                                    user_id=current_user.id,
                                    funding_id=current_resource.id,
                                    comment_type=form.comment_type.data)
        db.session.add(c)
        db.session.commit()
        return render_template('view_resource.html', resource=current_resource,
                           datetime=datetime, form=form)

    return render_template('view_resource.html', resource=current_resource,
                           datetime=datetime, form=form)

@app.route('/deletecomment/<id>', methods=['GET'])
def deletecomment(id):
    if current_user.is_anonymous:
        flash('You are not allowed to edit this resource - please login')
        return redirect(url_for('index'))
    current_comment = FundingResourceComments.query.filter_by(id=id).first()
    if current_user.id != current_comment.user_id and current_user.is_admin():
        flash('You are not allowed to edit this resource...')
        return redirect(url_for('index'))
    r_id = current_comment.funding_id
    FundingResourceComments.query.filter_by(id=id).delete()
    current_resource = FundingResources.query.filter_by(id=r_id).first()
    db.session.commit()
    comments = FundingResourceComments.query.filter_by(funding_id=r_id)
    form = FundingResourceCommentForm()
    flash('Comment deleted')
    return redirect(url_for('view_resource',id=r_id))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.route('/edit_profile', methods=['GET', 'POST'])
@app.route('/edit_profile/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_profile(id = None):
    session['url'] = 'edit_profile'
    form = EditProfileForm()
    user = current_user
    id = id or request.args.get("id")
    if id:
        if current_user.id != id and not current_user.is_admin():
            flash("you don't have the permission to edit this profile")
            return redirect(url_for('find_by_user', id=id))
        user = user = User.query.filter_by(id=id).first()

    if request.method == 'GET':
        form.center_name.data  = user.center_name
        form.email.data = user.email
        form.center_website.data = user.center_website
        form.center_description.data = user.center_description


    if form.validate_on_submit():
        print(user)
        f = form.center_photo.data
        if f:
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['USER_PHOTO_UPLOAD_PATH'], filename))
            user.center_photo_path = filename

        user.email = form.email.data
        user.center_website = form.center_website.data
        user.center_name = form.center_name.data
        user.center_description = form.center_description.data

        db.session.commit()

        return redirect(url_for('find_by_user', id=user.id))

    return render_template('edit_profile.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    users = User.query.all()
    return render_template('dashboard.html', users=users)



app.run(debug=True,host='0.0.0.0')