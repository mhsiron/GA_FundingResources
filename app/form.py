from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, DateField, FloatField, SelectField, IntegerField
from wtforms.validators import DataRequired, URL, Email, Optional
from wtforms.widgets import HiddenInput
from app.models import Main_Categories, Alert_Type
from flask_wtf.file import FileField, FileAllowed, FileRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class FundingResourceForm(FlaskForm):
    name = StringField('Funding Name', validators=[DataRequired()])
    source = StringField('Source')
    URL = StringField('URL', validators=[URL(), Optional()])
    deadline = DateField('Deadline',validators=[Optional()])
    description = TextAreaField('Description')
    criteria = TextAreaField('Criteria')
    amount = FloatField('Amount', validators=[Optional()])
    restrictions = TextAreaField('Restrictions')
    timeline = TextAreaField('Timeline')
    point_of_contact = StringField('Point of Contact', validators=[Email(), Optional()])
    ga_contact = StringField('GA Contact', validators=[Email(), Optional()])
    keywords = StringField('Keywords')
    main_cat = SelectField('Type of Funding',choices=[(choice.name, choice.value) for choice in Main_Categories])
    submit = SubmitField('Add Resource')

class FundingResourceUpdateForm(FundingResourceForm):
    is_enabled = BooleanField('Enabled')
    submit = SubmitField('Update Resource')
    id = IntegerField(label="",widget=HiddenInput())

class FundingResourceCommentForm(FlaskForm):
    comment = TextAreaField('Comment')
    comment_type = SelectField('Comment Type',
                           choices=[(choice.name, choice.value) for choice in
                                    Alert_Type])
    submit = SubmitField('Add comment')

class EditProfileForm(FlaskForm):
    email = StringField('Email', validators=[Email(), Optional()])
    center_name = StringField('Center Name')
    center_website = StringField('Center Website', validators=[URL(), Optional()])
    center_description = TextAreaField('Center Description')
    center_photo = FileField('Center Photo', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Edit Profile')

class EditProfilePhotoForm(FlaskForm):
    center_photo = FileField('Center Photo', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Edit Profile')