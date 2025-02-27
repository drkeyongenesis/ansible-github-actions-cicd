from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField
from wtforms.validators import InputRequired, Length, Email
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# Initialize Flask app and extensions
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('posts', lazy=True))

# Forms
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=100)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])

class PostForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired(), Length(min=5, max=200)])
    content = TextAreaField('Content', validators=[InputRequired()])

# Routes

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route to display all posts
@app.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)

# Route to view a specific post
@app.route('/post/<int:id>')
def post_detail(id):
    post = Post.query.get(id)
    return render_template('post_detail.html', post=post)

# Create post route (only accessible by logged-in users)
@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        new_post = Post(title=form.title.data, content=form.content.data, author_id=current_user.id)
        db.session.add(new_post)
        db.session.commit()
        flash("Post created successfully!", "success")
        return redirect(url_for('index'))
    return render_template('create_post.html', form=form)

# Edit post route (only accessible by post owner)
@app.route('/edit_post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    if post.author_id != current_user.id:
        flash("You can only edit your own posts.", "danger")
        return redirect(url_for('index'))
    form = PostForm(obj=post)
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Post updated successfully!", "success")
        return redirect(url_for('post_detail', id=post.id))
    return render_template('create_post.html', form=form)

# Delete post route
@app.route('/delete_post/<int:id>', methods=['GET'])
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    if post.author_id == current_user.id:
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted successfully!", "success")
    else:
        flash("You cannot delete someone else's post.", "danger")
    return redirect(url_for('index'))

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully!", "success")
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:  # In a real app, hash passwords!
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for('index'))
        flash("Invalid login credentials.", "danger")
    return render_template('login.html', form=form)

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for('login'))

if __name__ == "__main__":
    db.create_all()  # Creates the database
    app.run(debug=True)
