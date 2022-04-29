from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, \
    TextAreaField, DateField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from wtforms.widgets import TextArea

from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'),
                             validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))


class PostForm(FlaskForm):
    title = StringField(_l('Title'), validators=[DataRequired()])
    body = TextAreaField(_l('Say something'), validators=[DataRequired()], render_kw={"rows": 6, "cols": 40})
    submit = SubmitField(_l('Submit'))


class CommentForm(FlaskForm):
    comment = TextAreaField(_l(' '), validators=[DataRequired()], render_kw={"rows": 1, "cols": 30})
    submit = SubmitField(_l('Submit'))


class HottopicForm(FlaskForm):
    title = StringField(_l('Title'), validators=[DataRequired()])
    description = StringField(_l('description'))
    exlink = StringField(_l('Link'))
    submit = SubmitField(_l('Submit'))

class EditHottopicForm(FlaskForm):
    title = StringField(_l('Title'), validators=[DataRequired()])
    description = StringField(_l('description'), widget=TextArea())
    exlink = StringField(_l('Link'))
    submit = SubmitField(_l('Submit'))


class JournalForm(FlaskForm):
    date = StringField(_l('Date'), validators=[DataRequired()])
    issue = StringField(_l('Description'), widget=TextArea())
    submit = SubmitField(_l('Submit'))

class Did_you_knowForm(FlaskForm):
    topic = StringField(_l('Topic'), validators=[DataRequired()])
    date = StringField(_l('Date'), validators=[DataRequired()])
    content = StringField(_l('Content'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

class Other_projectsForm(FlaskForm):
    Pname = StringField(_l('Project Name'), validators=[DataRequired()])
    description = StringField(_l('description'), widget=TextArea())
    submit = SubmitField(_l('Submit'))

class CategoriesForm(FlaskForm):
    category = StringField(_l('Categories'), validators=[DataRequired()])
    content = StringField(_l('Content'), widget=TextArea())
    submit = SubmitField(_l('Submit'))

class ContactForm(FlaskForm):
    title = StringField(_l('Title'), validators=[DataRequired()])
    details = TextAreaField(_l('Details'), validators=[DataRequired()], render_kw={"rows": 1, "cols": 30})
    submit = SubmitField(_l('Submit'))

class NewsForm(FlaskForm):
    title = StringField(_l('Title'), validators=[DataRequired()])
    date = StringField(_l('Date'), validators=[DataRequired()])
    details = TextAreaField(_l('Details'), validators=[DataRequired()], render_kw={"rows": 1, "cols": 30})
    url = StringField(_l('URL'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

class QuizForm(FlaskForm):
    question = StringField(_l('Question'), validators=[DataRequired()])
    answer = TextAreaField(_l('Answer'), validators=[DataRequired()], render_kw={"rows": 1, "cols": 30})
    submit = SubmitField(_l('Submit'))

class AboutForm(FlaskForm):
    title = StringField(_l('Title'), validators=[DataRequired()])
    date = StringField(_l('Date'), validators=[DataRequired()])
    details = TextAreaField(_l('Details'), validators=[DataRequired()], render_kw={"rows": 1, "cols": 30})
    submit = SubmitField(_l('Submit'))

class CurrentForm(FlaskForm):
    title = StringField(_l('Title'), validators=[DataRequired()])
    date = StringField(_l('Date'), validators=[DataRequired()])
    details = TextAreaField(_l('Details'), validators=[DataRequired()], render_kw={"rows": 1, "cols": 30})
    submit = SubmitField(_l('Submit'))

class RandomForm(FlaskForm):
    title = StringField(_l('Title'), validators=[DataRequired()])
    details = TextAreaField(_l('Details'), validators=[DataRequired()], render_kw={"rows": 1, "cols": 30})
    submit = SubmitField(_l('Submit'))