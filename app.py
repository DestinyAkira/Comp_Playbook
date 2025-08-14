import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Initialize Flask App and database
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comp_playbook.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the secret code for lead registration
LEAD_REGISTRATION_CODE = "SUPERSECRET123"

# --- Database Models ---

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    account_type = db.Column(db.String(20), default='analyst') # 'analyst' or 'lead'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class SignOff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('sign_offs', lazy=True))

# Create database and tables
with app.app_context():
    db.create_all()

# --- Routes ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        code = request.form.get('lead_code')

        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('register'))

        if code and code == LEAD_REGISTRATION_CODE:
            account_type = 'lead'
        else:
            account_type = 'analyst'

        new_user = User(username=username, account_type=account_type)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash(f'Account created successfully as {account_type}.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['account_type'] = user.account_type
            flash('Logged in successfully.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('account_type', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/sign_off', methods=['GET', 'POST'])
def sign_off():
    if 'user_id' not in session:
        flash('You must be logged in to view this page.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    account_type = session['account_type']

    if request.method == 'POST':
        if account_type == 'analyst':
            existing_sign_off = SignOff.query.filter_by(user_id=user_id).first()
            if not existing_sign_off:
                new_sign_off = SignOff(user_id=user_id)
                db.session.add(new_sign_off)
                db.session.commit()
                flash('You have successfully signed off on the playbook.', 'success')
            return redirect(url_for('sign_off'))
        else:
            flash('Leads cannot sign off on the playbook.', 'error')
            return redirect(url_for('sign_off'))

    if account_type == 'lead':
        all_sign_offs = SignOff.query.order_by(SignOff.timestamp.desc()).all()
        return render_template('sign_off.html', account_type=account_type, sign_offs=all_sign_offs)
    else: # analyst
        signed_off = SignOff.query.filter_by(user_id=user_id).first()
        return render_template('sign_off.html', account_type=account_type, signed_off=signed_off)


# --- Example routes (can be extended) ---

@app.route('/roles')
def roles():
    # Example data for demonstration
    roles_data = [
        {"title": "Role 1", "description": "Description of Role 1."},
        {"title": "Role 2", "description": "Description of Role 2."}
    ]
    return render_template('roles.html', roles=roles_data)

@app.route('/lifecycle')
def lifecycle():
    # Example data
    lifecycle_data = [
        {"stage": "Stage 1", "description": "Details for Stage 1."},
        {"stage": "Stage 2", "description": "Details for Stage 2."}
    ]
    return render_template('lifecycle.html', lifecycle=lifecycle_data)

@app.route('/audit_form')
def audit_form():
    return render_template('audit_form.html')

@app.route('/score_calculator')
def score_calculator():
    return render_template('score_calculator.html')

@app.route('/supporting_files')
def supporting_files():
    return render_template('supporting_files.html')

@app.route('/interactive_workflow')
def interactive_workflow():
    return render_template('interactive_workflow.html')

if __name__ == '__main__':
    app.run(debug=True)