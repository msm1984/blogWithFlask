from flask import Flask, request, render_template, make_response,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_wtf import FlaskForm
from wtforms import StringField,BooleanField,PasswordField,TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import LoginManager,UserMixin,login_user,current_user,logout_user,login_required
app = Flask(__name__)
app.config['SECRET_KEY'] = '0cd2bff86d4c16c1b7ce22799bc0ec41'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)



class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(),Length(min=4, max=25)])
    email = StringField('Email Address', validators=[DataRequired(),Email(),Length(min=6, max=35)])
    password = PasswordField('New Password', validators=[DataRequired(),EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('this username already exists')
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('this email already exists')
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(),Length(min=4, max=25)])
    password = PasswordField('New Password', validators=[DataRequired()])
    remember = BooleanField('remember me', default = False)
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    posts = db.relationship('Post', backref = 'author', lazy = True)

    def __repr__(self):
        return f'User({self.id},{self.user})'
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable = False)
    content = db.Column(db.String(20), nullable = False)
    User_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

    def __repr__(self):
        return f'Post({self.title},{self.content})'

@app.route("/", methods=["GET", "POST"])
def mainpage():
    posts = db.session.query(Post).order_by(desc(Post.id))
    return render_template("mainpage.html", posts=posts)
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        flash('you cant access to this page','info')
        return redirect('home')
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username = form.username.data,email = form.email.data,password = form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect('login')
    response =  make_response(render_template("signup.html", form=form))
    return response
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash('you already logged in','info')
        return redirect('home')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user and (user.password == form.password.data):
            login_user(user, remember = form.remember.data)
            flash('you logged successfully','success')
            return redirect('home')
        else:
            flash('your email or password is wrong', 'danger')
    response = make_response(render_template("login.html", form=form))
    return response
@app.route("/home", methods=["GET", "POST"])
def home():
    posts = db.session.query(Post).order_by(desc(Post.id))
    return render_template("mainpage.html", posts=posts)
@app.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    flash('you logged out successfully','success')
    return redirect('/')
@app.route("/createpost", methods=["GET", "POST"])
def createpost():
    if current_user.is_authenticated:
        form = PostForm()
        if form.validate_on_submit():
            post = Post(title = form.title.data, content = form.content.data, author = current_user)
            db.session.add(post)
            db.session.commit()
            flash('your post is created successfully', 'success')
            return redirect('home')
        response = make_response(render_template("create.html", form=form))
        return response
    else:
        flash('access denied','info')
        return redirect('/')

@app.route("/count")
def getCount():
    count = db.session.query(User).count()
    return make_response(str(count))
if __name__ == "__main__":
    app.run(host='0.0.0.0')    