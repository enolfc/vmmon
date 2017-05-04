from flask import render_template, flash, redirect
from flask_login import login_user, logout_user, current_user, login_required

from app import app, lm
from .forms import LoginForm
from .model import User, create_user, update_resources

@app.route('/')
@login_required
def index():
    if not current_user.valid_proxy():
        flash('proxy expired!')
        logout_user()
        return redirect('/login')
    res = update_resources(app.config['OCCI_EP'],
                           current_user.proxy,
                           current_user.csv_file)
    return render_template('index.html',
                           user_id = current_user.user_id,
                           res=res) 

@app.route('/reset')
@login_required
def reset():
    current_user.reset_data()
    return redirect('/')

@lm.user_loader
def load_user(uid):
    u = User(uid)
    if not u.valid_proxy:
        return None
    return u

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = create_user(form.username.data, form.passwd.data) 
        if user:
            login_user(user)
            return redirect('/')
        else:
            flash('Unable to login!')
    return render_template('login.html', form=form)
