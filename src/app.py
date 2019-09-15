import os

from flask import Flask, redirect, render_template, session, request
from flask_session import Session
from tempfile import mkdtemp
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import login_required

# Configure application 
app = Flask(__name__)

# secret key
app.secret_key = os.urandom(16)

# Auto-reload templates
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# declare db file
db_file = 'test.sqlite'


@app.route("/")
@login_required
def index():

    # remove project_id if it exits to remove email nav items
    if session.get("project_id"):
        session.pop("project_id", None)

    id = session.get("user_id")

    projects = []
    with sqlite3.connect(db_file) as conn:
        c = conn.cursor()

        #query database
        c.execute("SELECT project_id, project_name FROM projects WHERE user_id=? GROUP BY project_id", (id,))

        projects = c.fetchall()
    
    if len(projects) == 0:
        projects[0] = "You don't have any projects!"

    return render_template("index.html", projects=projects)


@app.route("/login", methods=["GET", "POST"])
def login():
    '''Log user in'''

    if request.method == "POST":

        email = request.form.get("email")
        pw = request.form.get("pw")

        if not email or not pw:
            return render_template("apology.html", error="Please make sure all fields are filled out.")
        
        rows = []

        with sqlite3.connect(db_file) as conn:
            c = conn.cursor()

            # query database
            c.execute("SELECT * FROM users WHERE email=?", (email,))

            rows = c.fetchall()
        
        # ensure user exits and password is correct
        if len(rows) != 1:
            return render_template("apology.html", error="Sorry, user not found.")

        # remember user
        session["user_id"] = rows[0][0]
        print(session.get("user_id"))

        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    
    session.clear()

    return redirect("/")


@app.route("/email/<project_id>")
@login_required
def email(project_id):

    session["project_id"] = project_id

    rows = []
    with sqlite3.connect(db_file) as conn:
        c = conn.cursor()

        c.execute("SELECT project_name, project_code FROM projects WHERE project_id=? AND user_id=?", 
            (project_id, session.get("user_id"),))

        rows = c.fetchall()
    
    return render_template("email.html",project_id=project_id)


@app.route("/generator/<email>/<proj_id>")
@login_required
def generator(email, proj_id):

    rows = []

    with sqlite3.connect(db_file) as conn:

        c = conn.cursor()

        c.execute("SELECT * FROM projects WHERE project_id=? AND user_id=?", 
            (proj_id, session.get("user_id"),))

        rows = c.fetchall()

    if len(rows) < 1:
        return render_template("apology.html", error=proj_id)

    if email == 'break' or email == 'wrap':
        return render_template("generator.html", dist_type=email)
    