import os

from flask import Flask, redirect, render_template, session, request, jsonify
from flask_session import Session
from tempfile import mkdtemp
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import login_required
from BreakEmail import camera_rolls, sound_rolls, day_check, body_generation, subject_generation
from sqlhelpers import create_connection, update_break, create_break

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

        conn = create_connection(db_file)

        with conn:
            
            cur = conn.cursor()

            cur.execute("SELECT * FROM projects WHERE project_id=? AND user_id=?", 
                (proj_id, session.get("user_id"),))

            rows = cur.fetchall()

        # check if user has access to project
        if len(rows) < 1:
            return render_template("apology.html", error=proj_id)

        # render break template
        if email == 'break' or email == 'wrap':
            return render_template("distro.html", email=email.capitalize(), project_id=proj_id)
        elif email == 'complete':
            return render_template("complete.html", email=email.capitalize(), project_id=proj_id)
    else:
        print(request.form.getlist("test[]"))
        print(request.form.get('ep'))

        # get all results from AJAX
        results = {}

        results["ep"] = request.form.get("ep")
        results["shoot_day"] = request.form.get("shoot-day")
        results["gb"] = request.form.get("gb")
        # results["trt"] = request.form.getlist("trt")
        results["cm"] = request.form.get("c-masters")
        results["sm"] = request.form.get("s-masters")
        results["email"] = request.form.get("email")

        print(results)

        # check if any information is missing
        for key in results:
            value = results[key]

            if value == '':
                return render_template("apology.html", error="Please fill out all fields.")

        # format master media
        # get current day
        results["cm"] = camera_rolls(results["cm"])
        results["sm"] = sound_rolls(results["sm"])
        results["day"] = day_check()

        if email == 'break' or email == 'wrap':

            # Add media to database
            conn = create_connection(db_crew)
            with conn:
                
                # check which break it is
                # set variables for database
                am = 0
                if results["email"].lower() == "break":
                    am = 1
                else:
                    am = 0

                cur = conn.cursor()

                # check if break row exists in DB                
                cur.execute('SELECT * FROM latest_media WHERE break=? AND project_id=?', 
                           (am, proj_id,))
                
                rows = cur.fetchall()

                # update row in DB
                if len(rows) > 0:
                    update_break(conn,  (results["cm"], results["sm"], results["shoot_day"], proj_id, am))

                # create row in DB                    
                else:
                    create_break(conn, (proj_id, am, results["cm"], results["sm"], results["shoot_day"]))

            conn = create_connection(db_file)
            with conn:
                
                cur = conn.cursor()

                # get show name and show code
                cur.execute('SELECT project_code, project_name FROM projects WHERE project_id=? AND user_id=?',
                    (proj_id, session.get("user_id"),))
            
                rows = cur.fetchall()

                results["show_code"] = rows[0][0]
                
                results["show_name"] = rows[0][1]
            
            distro = []

            distro_email = results['email'].lower() + "_distro"

            # select distro for break email
            conn = create_connection(db_crew)
            with conn:

                cur = conn.cursor()

                cur.execute(f"SELECT email FROM crew WHERE project_id=? AND {distro_email}=1",(proj_id))

                distro = cur.fetchall()

            email = {}

            crew = ''
            for item in distro:
                print(item[0])
                crew += item[0] + ' '
            
            email["distro"] = crew
            email["subject"] = subject_generation(results)
            email["body"] = body_generation(results)
                
            return jsonify(email)

        elif email == "complete":

            print("Complete post request received!")

            # qeue DB get exisiting media from break/wrap
            conn = create_connection(db_crew)
            rows = []
            with conn:

                cur = conn.cursor()

                sql ='''SELECT 
                            camera_masters, sound_masters
                        FROM
                            latest_media
                        WHERE
                            project_id = ?
                        AND
                            shoot_day = ?'''

                cur.execute(sql, (proj_id, results["shoot_day"]))

                rows = cur.fetchall()

           # add in new masters if not in email already
            return "done"