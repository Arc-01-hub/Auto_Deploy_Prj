import os
import time
from pathlib import Path
import json

from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# ======================
# CONFIG
# ======================
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'replace-with-secure-key')

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'mysql+pymysql://root:root@mysql:3306/formations_db'
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

DATA_FILE = Path(__file__).resolve().parent / 'data' / 'formations.json'


# ======================
# MODELS
# ======================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Formation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(120), nullable=False)
    duration = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=False)
    total_seats = db.Column(db.Integer, default=12)

    @property
    def reserved_seats(self):
        return Registration.query.filter_by(formation_id=self.id).count()

    @property
    def available_seats(self):
        return max(self.total_seats - self.reserved_seats, 0)


class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    formation_id = db.Column(db.Integer, db.ForeignKey('formation.id'))


# ======================
# LOGIN
# ======================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ======================
# DB SAFE INIT (IMPORTANT FIX)
# ======================
def init_db():
    with app.app_context():
        for i in range(10):  # retry system
            try:
                db.create_all()
                print("✅ DB connected & tables created")
                break
            except Exception as e:
                print("⏳ Waiting for MySQL...", e)
                time.sleep(3)


# ======================
# SEED DATA
# ======================
def seed_formations():
    if Formation.query.first():
        return

    if DATA_FILE.exists():
        with DATA_FILE.open('r', encoding='utf-8') as f:
            data = json.load(f)

            for item in data:
                db.session.add(Formation(
                    title=item['title'],
                    category=item['category'],
                    duration=item['duration'],
                    description=item['description'],
                    total_seats=item.get('total_seats', 12)
                ))

            db.session.commit()


# ======================
# ROUTES
# ======================
@app.route('/')
@login_required
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()

        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('home'))

        flash("Invalid credentials")

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ======================
# MAIN
# ======================
if __name__ == '__main__':
    init_db()

    # create admin if not exists
    with app.app_context():
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin')
            admin.set_password('password')
            db.session.add(admin)
            db.session.commit()

        seed_formations()

    app.run(host='0.0.0.0', port=5000, debug=True)