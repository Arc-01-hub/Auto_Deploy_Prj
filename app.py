import os
from pathlib import Path
import json
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'replace-with-secure-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'mysql+pymysql://root:root@192.168.11.238:3306/formations_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', '0') == '1'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

DATA_FILE = Path(__file__).resolve().parent / 'data' / 'formations.json'

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
    total_seats = db.Column(db.Integer, nullable=False, default=12)
    registrations = db.relationship('Registration', back_populates='formation', lazy='dynamic')

    @property
    def reserved_seats(self):
        return self.registrations.count()

    @property
    def available_seats(self):
        return max(self.total_seats - self.reserved_seats, 0)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'duration': self.duration,
            'description': self.description,
            'total_seats': self.total_seats,
            'reserved_seats': self.reserved_seats,
            'available_seats': self.available_seats,
        }

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    formation_id = db.Column(db.Integer, db.ForeignKey('formation.id'), nullable=False)
    user = db.relationship('User', backref='registrations')
    formation = db.relationship('Formation', back_populates='registrations')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'formation_id', name='unique_user_formation'),
    )

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def seed_formations():
    if Formation.query.first():
        return

    with DATA_FILE.open('r', encoding='utf-8') as file:
        for item in json.load(file):
            formation = Formation(
                title=item['title'],
                category=item['category'],
                duration=item['duration'],
                description=item['description'],
                total_seats=item.get('total_seats', 12),
            )
            db.session.add(formation)
    db.session.commit()


@app.route('/')
@login_required
def home():
    return render_template('index.html')


@app.route('/admin/formations/create', methods=['GET', 'POST'])
@login_required
def create_formation():
    if current_user.username != 'admin':
        abort(403)

    message = None
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        duration = request.form.get('duration', '').strip()
        description = request.form.get('description', '').strip()
        total_seats = request.form.get('total_seats', '12').strip()

        if not title or not category or not duration or not description:
            message = 'All fields are required.'
        else:
            formation = Formation(
                title=title,
                category=category,
                duration=duration,
                description=description,
                total_seats=int(total_seats),
            )
            db.session.add(formation)
            db.session.commit()
            message = 'Formation created successfully.'

    return render_template('create_formation.html', message=message)


@app.route('/admin/formations/<int:formation_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_formation(formation_id):
    if current_user.username != 'admin':
        abort(403)

    formation = Formation.query.get_or_404(formation_id)
    message = None

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        duration = request.form.get('duration', '').strip()
        description = request.form.get('description', '').strip()
        total_seats = request.form.get('total_seats', '12').strip()

        if not title or not category or not duration or not description:
            message = 'All fields are required.'
        else:
            formation.title = title
            formation.category = category
            formation.duration = duration
            formation.description = description
            formation.total_seats = int(total_seats)
            db.session.commit()
            message = 'Formation updated successfully.'

    return render_template('edit_formation.html', formation=formation, message=message)


@app.route('/admin/formations/<int:formation_id>/delete', methods=['POST'])
@login_required
def delete_formation(formation_id):
    if current_user.username != 'admin':
        abort(403)

    formation = Formation.query.get_or_404(formation_id)
    db.session.delete(formation)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/formations/<int:formation_id>', methods=['GET', 'POST'])
@login_required
def formation_detail(formation_id):
    formation = Formation.query.get_or_404(formation_id)
    registered = Registration.query.filter_by(user_id=current_user.id, formation_id=formation.id).first() is not None
    message = None

    if request.method == 'POST':
        if registered:
            message = 'You are already registered for this formation.'
        elif formation.available_seats <= 0:
            message = 'This formation is fully reserved.'
        else:
            registration = Registration(user_id=current_user.id, formation_id=formation.id)
            db.session.add(registration)
            db.session.commit()
            registered = True
            message = 'Registration completed successfully.'

    return render_template(
        'formation_detail.html',
        formation=formation,
        registered=registered,
        message=message,
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid username or password')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/api/formations')
@login_required
def get_formations():
    formations = Formation.query.order_by(Formation.category, Formation.title).all()
    return jsonify({'formations': [formation.to_dict() for formation in formations]})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin')
            admin.set_password('password')
            db.session.add(admin)
        seed_formations()
        db.session.commit()

    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=app.config['DEBUG'],
    )
