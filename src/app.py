import os
import json
from flask import Flask, redirect, render_template, session, request, jsonify
from flask_session import Session
from tempfile import mkdtemp
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import login_required, clear_project_id
from BreakEmail import camera_rolls, sound_rolls, day_check, body_generation, subject_generation
from DailiesComplete import episode_organizer, complete_subject, complete_body, camera_roll_organizer, str_to_lst, append_mags, shuttle_organizer, sound_roll_organizer
from sqlhelpers import create_connection, update_break, create_break, get_show_code, get_show_name, get_distro

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
    clear_project_id(session)

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


@app.route("/dashboard/<project_id>")
@login_required
def dashboard(project_id):

    session["project_id"] = project_id

    with sqlite3.connect(db_file) as conn:
        c = conn.cursor()

        c.execute("SELECT project_name, project_code FROM projects WHERE project_id=? AND user_id=?", 
            (project_id, session.get("user_id"),))

        c.fetchall()
    
    return render_template("dashboard.html",project_id=project_id)


@app.route("/createshow", methods=["GET", "POST"])
@login_required
def create_show():

    # remove email nav items
    clear_project_id(session)

    if request.method == "GET":
        return render_template("createshow.html")
    else:
        results = {}

        results["project_name"] = request.form.get("project-name")
        results["project_code"] = request.form.get("project-code")

        if not results["project_name"] or not results["project_code"]:
            return render_template("apology.html", error="Please complete both fields!")
        
        conn = create_connection(db_file)

        with conn:
            cur = conn.cursor()

            sql = '''
                    INSERT INTO 
                        projects(user_id, project_name, project_code)
                    VALUES(?,?,?)'''

            cur.execute(sql, (session.get("user_id"), results["project_name"], results["project_code"]))
            conn.commit()

        return render_template("apology.html", error="Page not built!")




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

        print("post request received!")

        # get all results from AJAX
        results = {}

        results["ep"] = request.form.get("ep")
        results["shoot_day"] = request.form.get("shoot-day")
        results["gb"] = request.form.get("gb")
        results["trt"] = request.form["test"]
        results["email"] = request.form.get("email")

        # check if any information is missing
        for key in results:
            value = results[key]

            if value == '':
                return render_template("apology.html", error="Please fill out all fields.")

        # get current day
        results["day"] = day_check()

        if email == 'break' or email == 'wrap':

            results["cm"] = request.form.get("c-masters")
            results["sm"] = request.form.get("s-masters")

            results["cm"] = camera_rolls(results["cm"])
            results["sm"] = sound_rolls(results["sm"])

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
                
                # get show code and show name

                results["show_code"] = get_show_code(conn, (proj_id, session.get("user_id")))
                
                results["show_name"] = get_show_name(conn, (proj_id, session.get("user_id")))
            
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

            print('Complete POST request received!')
            
            results["discrepancies"] = request.form.get("discrepancies")

            results["shuttles"] = request.form.get("shuttles")

            results["cm"] = request.form.get("c-masters")
            results["sm"] = request.form.get("s-masters")

            print(results)

            conn = create_connection(db_file)
            with conn:

                # get show code and show name

                results["show_code"] = get_show_code(conn, (proj_id, session.get("user_id")))

                results["show_name"] = get_show_name(conn, (proj_id, session.get("user_id")))

            # load JSON trt data
            ep_group = json.loads(results['trt'])

            # get organized html string of trts
            results["trts"] = episode_organizer(ep_group, results["shoot_day"])

            # qeue DB get exisiting media from break/wrap
            conn = create_connection(db_crew)
            rows = []
            distro = ''
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

                distro = get_distro(conn, 'complete_distro', proj_id)
            
            # add in new masters if not in database already
            # if no new maasters, insert databas masters
            
            if results['cm'] != "":
                results["cm"] = append_mags(rows[0][0], results["cm"])
            else:
                results['cm'] = camera_roll_organizer(rows[0][0])

            if results["sm"] != "":
                results["sm"] = append_mags(rows[0][1], results["sm"])
            else:
                results["sm"] = sound_roll_organizer(rows[0][1])

            # organize shuttles
            results["shuttles"] = shuttle_organizer(results["shuttles"])

            email = {}

            # create email distro
            email["distro"] = distro

            # create email subject
            email["subject"] = complete_subject(results)

            # create email body
            email["body"] = complete_body(results)

            return jsonify(email)