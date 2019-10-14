
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, LoginManager, UserMixin, logout_user, login_required, current_user
from flask_migrate import Migrate
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["DEBUG"] = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="unredcoders",
    password="secretkey",
    hostname="unredcoders.mysql.pythonanywhere-services.com",
    databasename="unredcoders$users",
)

app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.secret_key = "cajkhsfghajsgryweqriskandc"
login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.username


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(username=user_id).first()

@app.route('/')
def index():
    return render_template('home_page.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login_page.html", error=False)

    else:
        user = load_user(request.form["username"])
        if user is None:
            return render_template("login_page.html", error=True)
        else:
            if not user.check_password(request.form["password"]):
                return render_template("login_page.html", error=True)

            else:
                login_user(user)
                return redirect(url_for('index'))


@app.route('/logout/', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/signup/', methods=['GET', 'POST'])
def signup():

    if request.method=='GET':
        return render_template('signup_page.html')

    else:
        user = User(username=request.form['username'], password_hash=generate_password_hash(request.form["password"]))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))



