import os

from flask import Flask, redirect, render_template, session, request, jsonify
from flask_session import Session
from tempfile import mkdtemp
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import login_required
from BreakEmail import camera_rolls, sound_rolls, day_check, body_generation, subject_generation

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

# declare db files
db_file = 'test.sqlite'
db_crew = 'distro.sqlite3'


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

    with sqlite3.connect(db_file) as conn:
        c = conn.cursor()

        c.execute("SELECT project_name, project_code FROM projects WHERE project_id=? AND user_id=?", 
            (project_id, session.get("user_id"),))

        c.fetchall()
    
    return render_template("email.html",project_id=project_id)


@app.route("/generator/<email>/<proj_id>", methods=["GET", "POST"])
@login_required
def generator(email, proj_id):

    rows = []
    if request.method == "GET":
    
        with sqlite3.connect(db_file) as conn:

            c = conn.cursor()

            c.execute("SELECT * FROM projects WHERE project_id=? AND user_id=?", 
                (proj_id, session.get("user_id"),))

            rows = c.fetchall()

        if len(rows) < 1:
            return render_template("apology.html", error=proj_id)

        if email == 'break' or email == 'wrap':
            return render_template("distro.html", email=email.capitalize(), project_id=proj_id)
    else:
        
        if email == 'break' or email == 'wrap':

            results = {}

            results["ep"] = request.form.get("ep")
            results["shoot_day"] = request.form.get("shoot-day")
            results["gb"] = request.form.get("gb")
            results["trt"] = request.form.get("trt")
            results["cm"] = request.form.get("c-masters")
            results["sm"] = request.form.get("s-masters")
            results["email"] = request.form.get("email")

            for key in results:
                value = results[key]

                if value == '':
                    return render_template("apology.html", error="Please fill out all fields.")

            results["cm"] = camera_rolls(results["cm"])
            results["sm"] = sound_rolls(results["sm"])
            results["day"] = day_check()

            # Add media to database
            with sqlite3.connect(db_crew) as conn:
                

                # check which break it is
                # set variables for database
                am = 0
                if results["email"].lower() == "break":
                    am = 1
                else:
                    am = 0

                c = conn.cursor()

                c.execute('SELECT * FROM latest_media WHERE break=? AND project_id=?', 
                    (am, proj_id,))
                
                rows = c.fetchall()

                
                if len(rows) > 0:
                    
                    # update table
                    sql ='''UPDATE latest_media
                            SET camera_masters = ?,
                                sound_masters = ?,
                                shoot_day = ?
                            WHERE project_id = ?
                            AND break = ?'''
                    
                    c.execute(sql, (results["cm"], results["sm"], results["shoot_day"], proj_id, am))

                else:

                    #create row
                    c.execute('''INSERT INTO latest_media VALUES 
                        (?,?,?,?,?)''',
                        (proj_id, am, results["cm"], results["sm"], results["shoot_day"]))
            
            with sqlite3.connect(db_file) as conn:
                
                c = conn.cursor()

                c.execute('SELECT project_code, project_name FROM projects WHERE project_id=? AND user_id=?',
                    (proj_id, session.get("user_id"),))
            
                rows = c.fetchall()

                results["show_code"] = rows[0][0]
                
                results["show_name"] = rows[0][1]
            
            distro = []

            distro_email = results['email'].lower() + "_distro"

            with sqlite3.connect(db_crew) as conn:

                c = conn.cursor()

                c.execute(f"SELECT email FROM crew WHERE project_id=? AND {distro_email}=1",(proj_id))

                distro = c.fetchall()

            email = {}

            crew = ''
            for item in distro:
                print(item[0])
                crew += item[0] + ' '
            
            email["distro"] = crew
            email["subject"] = subject_generation(results)
            email["body"] = body_generation(results)
                
            return jsonify(email)