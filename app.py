from flask import Flask, redirect, render_template, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import RegistrationForm, LoginForm, FeedbackForm, DeleteForm
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Unauthorized

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = '123secret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)
connect_db(app)

@app.route('/')
def home():
    """Redirect to /register"""
    return redirect('/register')

@app.route('/register', methods=["GET", "POST"])
def new_user():
    """show registration form"""
    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = RegistrationForm()

    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('This username has been taken, please try another one!')
            return render_template('registration_form.html', form=form)
        session['username'] = new_user.username
        flash(f"Welcome, {new_user.username}! Your account has been successfully created!", "success")
        return redirect('/users/<username>')
    return render_template('registration_form.html', form=form)

# @app.route('/secret')
# def secret_page():
#     if "username" not in session:
#         flash('Sorry, you must be logged in to see this page!', 'danger')
#         return redirect('/login')
#     return render_template('secret.html')


@app.route('/login', methods=['GET', 'POST'])
def existing_user():
    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            session['username'] = user.username
            flash(f"Welcome back, {user.username}!", 'info')
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ['Invalid username/password']
            return render_template('login_form.html', form=form)

    return render_template('login_form.html', form=form)

@app.route('/logout')
def Logout_user():
    session.pop('username')
    return redirect('/login')


@app.route('/users/<username>')
def user_page(username):

    if "username" not in session or username != session['username']:
        return redirect('/login')
    user = User.query.get_or_404(username)
    form = DeleteForm()

    return render_template('user.html', user=user, form=form)

@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    if "username" not in session or username != session['username']:
        flash("Sorry, you are not allowed to delete this user!", 'danger')
        return redirect('/users/<username>')
    user = User.query.get_or_404(username)
    db.session.delete(user)
    db.session.commit()
    session.pop('username')
    return redirect('/register')

@app.route('/users/<username>/feedback/new', methods=["GET", "POST"])
def new_feedback(username):
    if "username" not in session or username != session['username']:
        flash("Sorry, you are not allowed to perform this action!", 'danger')

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        feedback = Feedback(title=title, content=content, username=username)
        db.session.add(feedback)
        db.session.commit()
        # flash(f"Your feedback {feedback.title} has been successfully added!", 'success')
        return redirect(f"/users/{feedback.username}")
    else:
        return render_template('new_feedback.html', form=form)

@app.route('/feedback/<int:feedback_id>/update', methods=["GET", "POST"])
def update_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)

    if "username" not in session or username != session['username']:
        flash("Sorry, you are not allowed to perform this action!", 'danger')
        raise Unauthorized()
    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        flash("Your changes have been saved!", 'info')
        return redirect(f"/users/{feedback.username}")
    return render_template('edit_feedback.html', form=form, feedback=feedback)


@app.route('/feedback/<int:feedback_id>/delete', methods=["POST"])
def delete_feedback(feedback_id):

    feedback = Feedback.query.get(feedback_id)

    if "username" not in session or username != session['username']:
        flash("Sorry, you are not allowed to perform this action!", 'danger')
        raise Unauthorized()

    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()
        flash("Feedback deleted!", 'info')
    return redirect(f"/users/{feedback.username}")

