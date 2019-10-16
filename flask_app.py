
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, request, url_for, redirect, jsonify
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

class UserChoice(db.Model):
    __tablename__ = "userchoice"

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    gender = db.Column(db.Integer)  #0 is male, 1 is female
    top_choice = db.Column(db.Integer)
    bottom_choice = db.Column(db.Integer)
    footwear_choice = db.Column(db.Integer)

    user = db.relationship('User', foreign_keys=user_id)

class Variable(db.Model):
    __tablename__ = "variables"

    name = db.Column(db.String(128), primary_key=True)
    value = db.Column(db.Integer)

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(username=user_id).first()

@app.route('/')
def index():
    is_challenge_declared = db.session.query(Variable).filter_by(name="challenge_declared").first().value

    if not current_user.is_authenticated:
        return render_template('home_page.html', challenge_attempted=False, challenge_declared=is_challenge_declared)

    else:
        if db.session.query(db.session.query(UserChoice).filter_by(user_id=current_user.id).exists()).scalar():
            gender = db.session.query(Variable).filter_by(name="gender").first().value
            winning_top = db.session.query(Variable).filter_by(name="winning_top").first().value
            winning_bottom = db.session.query(Variable).filter_by(name="winning_bottom").first().value
            winning_footwear = db.session.query(Variable).filter_by(name="winning_footwear").first().value

            gender_chosen = db.session.query(UserChoice).filter_by(user_id=current_user.id).first().gender
            top_choice = db.session.query(UserChoice).filter_by(user_id=current_user.id).first().top_choice
            bottom_choice = db.session.query(UserChoice).filter_by(user_id=current_user.id).first().bottom_choice
            footwear_choice = db.session.query(UserChoice).filter_by(user_id=current_user.id).first().footwear_choice

            is_correct_submission = gender == gender_chosen and winning_top == top_choice and winning_bottom == bottom_choice and winning_footwear == footwear_choice

            return render_template('home_page.html', challenge_attempted=True, challenge_declared=is_challenge_declared, correct_submission=is_correct_submission)

        else:
            return render_template('home_page.html', challenge_attempted=False, challenge_declared=is_challenge_declared, correct_submission=False)

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
        return render_template('signup_page.html', username_error=False, password_error=False)

    else:
        exists = db.session.query(db.session.query(User).filter_by(username=request.form["username"]).exists()).scalar()

        if exists:
            return render_template("signup_page.html", username_error=False, password_error=False, repeated_username=True)

        else:
            if len(request.form['username'])>=4 and len(request.form['password'])>=4:
                user = User(username=request.form['username'], password_hash=generate_password_hash(request.form["password"]))
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))

            if len(request.form['username'])<4 and len(request.form['password'])<4:
                return render_template("signup_page.html", username_error=True, password_error=True, repeated_username=False)

            if len(request.form['username'])<4:
                return render_template("signup_page.html", username_error=True, password_error=False, repeated_username=False)

            if len(request.form['password'])<4:
                return render_template("signup_page.html", username_error=False, password_error=True, repeated_username=False)


@app.route('/admin/', methods=['GET', 'POST'])
def admin():
    if request.method=='GET':
        return render_template('admin_page.html')

    else:
        gender = request.form["gender"]
        winning_top = request.form["winning_top"]
        winning_bottom = request.form["winning_bottom"]
        winning_footwear = request.form["winning_footwear"]
        challenge_declared = 0

        if request.form.get("declare_challenge"):
            challenge_declared = 1

        if db.session.query(db.session.query(Variable).filter_by(name="gender").exists()).scalar():
            db.session.delete(Variable.query.filter_by(name="gender").first())
            db.session.commit()

        db.session.add(Variable(name="gender", value=gender))
        db.session.commit()

        if db.session.query(db.session.query(Variable).filter_by(name="winning_top").exists()).scalar():
            db.session.delete(Variable.query.filter_by(name="winning_top").first())
            db.session.commit()

        db.session.add(Variable(name="winning_top", value=winning_top))
        db.session.commit()

        if db.session.query(db.session.query(Variable).filter_by(name="winning_bottom").exists()).scalar():
            db.session.delete(Variable.query.filter_by(name="winning_bottom").first())
            db.session.commit()

        db.session.add(Variable(name="winning_bottom", value=winning_bottom))
        db.session.commit()

        if db.session.query(db.session.query(Variable).filter_by(name="winning_footwear").exists()).scalar():
            db.session.delete(Variable.query.filter_by(name="winning_footwear").first())
            db.session.commit()

        db.session.add(Variable(name="winning_footwear", value=winning_footwear))
        db.session.commit()

        if db.session.query(db.session.query(Variable).filter_by(name="challenge_declared").exists()).scalar():
            db.session.delete(Variable.query.filter_by(name="challenge_declared").first())
            db.session.commit()

        db.session.add(Variable(name="challenge_declared", value=challenge_declared))
        db.session.commit()



        return redirect(url_for('admin'))


@app.route('/challenge/', methods=['GET', 'POST'])
def challenge():
    return render_template("challenge_page.html")

@app.route('/challengefemale/', methods=["GET", "POST"])
def challengefemale():

    if request.method=="GET":
        return render_template("challengefemale_page.html")

    else:
        if not current_user.is_authenticated:
            return redirect(url_for('index'))

        user_choice = UserChoice(user=current_user, gender=1, top_choice=request.form["top_choice"], bottom_choice=request.form["bottom_choice"], footwear_choice=request.form["footwear_choice"])

        if db.session.query(db.session.query(UserChoice).filter_by(user_id=current_user.id).exists()).scalar():
            db.session.delete(UserChoice.query.filter_by(user_id=current_user.id).first())
            db.session.commit()

        db.session.add(user_choice)
        db.session.commit()

        return jsonify(dict(redirect=url_for('index')))

@app.route('/challengemale/', methods=["GET", "POST"])
def challengemale():

    if request.method=="GET":
        return render_template("challengemale_page.html")

    else:
        if not current_user.is_authenticated:
            return redirect(url_for('index'))

        user_choice = UserChoice(user=current_user, gender=0, top_choice=request.form["top_choice"], bottom_choice=request.form["bottom_choice"], footwear_choice=request.form["footwear_choice"])

        if db.session.query(db.session.query(UserChoice).filter_by(user_id=current_user.id).exists()).scalar():
            db.session.delete(UserChoice.query.filter_by(user_id=current_user.id).first())
            db.session.commit()

        db.session.add(user_choice)
        db.session.commit()

        return jsonify(dict(redirect=url_for('index')))

