import os
import json
from flask import Flask, redirect, render_template, session, request, jsonify, url_for
from flask_session import Session
from tempfile import mkdtemp
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import login_required, clear_project_id
from BreakEmail import camera_rolls, sound_rolls, day_check, body_generation, subject_generation
from DailiesComplete import episode_organizer, complete_subject, complete_body, camera_roll_organizer, str_to_lst, append_mags, shuttle_organizer, sound_roll_organizer
from sqlhelpers import create_connection, add_new_show, update_break, create_break, get_show_code, get_show_name, get_distro, remove_show

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
            return render_template("apology.html", error="Please ensure that the username or password is correct.")

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

        add_new_show(conn, (session.get("user_id"), results["project_name"], results["project_code"]))

        return redirect("/")


@app.route("/account", methods=["GET"])
@login_required
def account():
    return render_template("account.html")


@app.route("/shows", methods=["GET"])
@login_required
def shows():
    
    if request.method == "GET":

        id = session.get("user_id")
        project = []

        with sqlite3.connect(db_file) as conn:
            c = conn.cursor()

            c.execute('''
                        SELECT 
                            project_id, project_name 
                        FROM 
                            projects
                        WHERE
                            user_id=?
                        GROUP BY
                            project_id''', (id,)
                    )
            
            project = c.fetchall()

        return render_template("shows.html", projects=project)


@app.route("/shows/edit/<proj_id>", methods=["GET", "POST"])
@login_required
def show_details(proj_id):

    if request.method == "GET":
        # TODO: Make sure user has access to project
        id = session.get("user_id")
        project = []

        conn = create_connection(db_file)
        with conn:
            c = conn.cursor()

            c.execute('''
                        SELECT
                            project_name, project_code
                        FROM
                            projects
                        WHERE
                            user_id=?
                        AND
                            project_id=?
                        ''', (id,proj_id,)
            )

            project = c.fetchall()

        if len(project) < 1:
            return render_template("apology.html", error="The project does not exist or you do not have access to the project.")
        else:
            return render_template("showedit.html", project=project, proj_id=proj_id)
    else:
        id = session.get("user_id")

        conn = create_connection(db_file)

        if not remove_show(conn, proj_id, id):
            return render_template("apology.html", error="Unexpected error!")
        else:
            remove_show(conn, proj_id, id)



@app.route("/shows/edit/<proj_id>/<value>", methods=["GET", "POST"])
@login_required
def show_edit(proj_id, value):

    possible_values = ["show-name", "show-code", "delete"]

    if value not in possible_values:
        print(value)
        return render_template("apology.html", error="Sorry, something seems to have gone wrong!")
    
    if request.method == "GET":
        
        if value == "show-name":

            result = []

            conn = create_connection(db_file)
            with conn:

                result = get_show_name(conn, (proj_id, session.get("user_id")))

            return render_template("memberedit.html", proj_id=proj_id, data=result, value=value)

        elif value == "show-code":

            result = []
            with sqlite3.connect(db_file) as conn:

                result = get_show_code(conn, (proj_id, session.get("user_id")))
            
            return render_template("memberedit.html", proj_id=proj_id, value=value, data=result)

        elif value == "delete":

            return render_template("apology.html", error="Sorry, not ready!")

        else:

            return render_template("apology.html", error="Sorry, something seems to have gone wrong!")
    
    else:

        if value == "show-name":

            new_show_name = request.form.get("inputShowName")

            conn = create_connection(db_file)

            with conn:
                sql = '''
                        UPDATE
                            projects
                        SET
                            project_name = ?
                        WHERE
                            project_id = ?
                        AND
                            user_id = ?'''

                cur = conn.cursor()
                cur.execute(sql, (new_show_name, proj_id, session.get("user_id")))
                conn.commit()

        elif value == "show-code":
            
            new_show_code = request.form.get("inputShowCode")

            conn = create_connection(db_file)
            with conn:

                sql = '''
                        UPDATE
                            projects
                        SET
                            project_code = ?
                        WHERE
                            project_id = ?
                        AND
                            user_id = ?'''
                
                cur = conn.cursor()
                cur.execute(sql,(new_show_code, proj_id, session.get("user_id")))
                conn.commit()

        else:
            return render_template("apology.html", error="Sorry, something seems to have gone wrong!")

        return redirect(url_for("show_details", proj_id=proj_id))

@app.route("/security", methods=["GET"])
@login_required
def security():
    return render_template("apology.html", error="In Progress")


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

        # get all results from AJAX
        results = {}

        results["ep"] = request.form.get("ep")
        results["shoot_day"] = request.form.get("shoot-day")
        results["gb"] = request.form.get("gb")
        results["trt"] = request.form["trt"]
        results["email"] = request.form.get("email")

        # check if any information is missing
        for key in results:
            value = results[key]

            if value == '':
                return render_template("apology.html", error="Please fill out all fields.")

        # get current day
        results["day"] = day_check()


        if email == 'break' or email == 'wrap':

            print("Break or wrap request received!")

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


@app.route("/crew/<proj_id>", methods=["GET", "POST"])
@login_required
def crew(proj_id):

    departments = ["Accounting", "Art Department", "Camera", "Catering", "Construction", "Continuity",
                    "Costumes", "Dailies", "Editorial", "Greens", "Grip", "Hair", "Lighting", "Locations",
                    "Makeup", "Paint", "Production Office", "Props", "Set Decoration", 
                    "Set Production", "Sound", "Transportation", "VFX"]

    if request.method == "GET":

        crew = []
        conn = create_connection(db_crew)
        with conn:
            sql ='''SELECT
                        department, name, position, email, member_id
                    FROM
                        crew
                    WHERE
                        project_id = ?
                    ORDER BY
                        department,
                        name'''

            cur = conn.cursor()
            cur.execute(sql, (proj_id))

            crew = cur.fetchall()

        print(crew)
        return render_template("crew.html", project_id=proj_id, departments=departments, crew=crew, len=len(crew))
    else:

        results = {}

        results['name'] = request.form.get('name')
        results['email'] = request.form.get('email') + ";"
        results["position"] = request.form.get("position")
        results['department'] = request.form.get('department')
        results['break_distro'] = request.form.get('break-distro')
        results['complete_distro'] = request.form.get('complete-distro')
        results['stills_distro'] = request.form.get('stills-distro')
        results['project_id'] = proj_id

        for key in results:
            value = results[key]

            if value == "" or value == "Choose...":
                return render_template("apology.html", error="Please fill out all fields!")

        if request.form.get("break-distro") == None:
            results["break_distro"] = 0
        else:
            results["break_distro"] = 1

        if results["complete_distro"] == None:
            results["complete_distro"] = 0
        else:
            results["complete_distro"] = 1

        if results["stills_distro"] == None:
            results["stills_distro"] = 0
        else:
            results["stills_distro"] = 1

        conn = create_connection(db_crew)
        with conn:
            cur = conn.cursor()

            sql = '''INSERT INTO
                            crew(project_id, department, name, position, email, 
                            break_distro, complete_distro, stills_distro)
                    VALUES(?,?,?,?,?,?,?,?)'''

            cur.execute(sql, (results['project_id'], results['department'], results['name'], 
                                results['position'], results['email'], results['break_distro'], 
                                results['complete_distro'], results['stills_distro']))
            conn.commit()

        print(results)
        return redirect(url_for('crew', proj_id=proj_id))
    

@app.route("/crew/<proj_id>/member/<member_id>", methods=["GET", "POST"])
@login_required
def member(proj_id, member_id):

    if request.method == "GET":
        member = []

        conn = create_connection(db_crew)
        with conn:
            sql ='''SELECT
                        member_id, name, department, position, email,
                        break_distro, complete_distro, stills_distro
                    FROM
                        crew
                    WHERE
                        project_id = ?
                    AND
                        member_id = ?'''

            cur = conn.cursor()
            cur.execute(sql, (proj_id, member_id))
            member = cur.fetchall()

        print(member)
    return render_template('member.html', project_id=proj_id, member_id=member_id, member=member)

@app.route("/crew/<proj_id>/member/<member_id>/edit/<value>", methods=["GET", "POST"])
@login_required
def edit_member(proj_id, member_id, value):

    possible_values = ["name", "department", "position", "email", "distro"]

    if value not in possible_values:
        return render_template("apology.html", error="Something seems to have gone wrong")

    if value == "distro":
        value = "break_distro, complete_distro, stills_distro"

    if request.method == "GET":

        departments = ["Accounting", "Art Department", "Camera", "Catering", "Construction", "Continuity",
                    "Costumes", "Dailies", "Editorial", "Greens", "Grip", "Hair", "Lighting", "Locations",
                    "Makeup", "Paint", "Production Office", "Props", "Set Decoration", 
                    "Set Production", "Sound", "Transportation", "VFX"]
        
        member = []

        conn = create_connection(db_crew)
        with conn:
            sql =f'''SELECT
                        {value}
                    FROM
                        crew
                    WHERE
                        project_id = ?
                    AND
                        member_id = ?'''
            cur = conn.cursor()
            cur.execute(sql, (proj_id, member_id))
            member = cur.fetchall()

        return render_template("memberedit.html", project_id=proj_id, 
                                member_id=member_id, value=value, member=member, departments=departments)
    else:      
        if value == "name":

            data = request.form.get("inputName")

            conn = create_connection(db_crew)
            with conn:
                sql = '''UPDATE
                            crew
                        SET
                            name = ?
                        WHERE
                            project_id = ?
                        AND
                            member_id = ?
                        '''
                cur = conn.cursor()
                cur.execute(sql, (data, proj_id, member_id))
                conn.commit()
            
        elif value == "department":

            data = request.form.get("inputDepartment")

            conn = create_connection(db_crew)
            with conn:
                sql = '''UPDATE
                            crew
                        SET
                            department = ?
                        WHERE
                            project_id = ?
                        AND
                            member_id = ?
                        '''
                cur = conn.cursor()
                cur.execute(sql, (data, proj_id, member_id))
                conn.commit()

        elif value == "position":

            data = request.form.get("inputPosition")

            conn = create_connection(db_crew)
            with conn:
                sql = '''UPDATE
                            crew
                        SET
                            position = ?
                        WHERE
                            project_id = ?
                        AND
                            member_id = ?
                        '''
                
                cur = conn.cursor()
                cur.execute(sql, (data, proj_id, member_id))
                conn.commit()

        elif value == "email":

            data = request.form.get("inputEmail")

            conn = create_connection(db_crew)
            with conn:
                sql = '''UPDATE
                            crew
                        SET
                            email = ?
                        WHERE
                            project_id = ?
                        AND
                            member_id = ?
                        '''
                cur = conn.cursor()
                cur.execute(sql, (data, proj_id, member_id))
                conn.commit()

        elif value == "break_distro, complete_distro, stills_distro":

            data = {}
            data['break'] = request.form.get("inputBreak")
            data['complete'] = request.form.get("inputComplete")
            data['stills'] = request.form.get("inputStills")

            for key in data:
                if data[key] == None:
                    data[key] = 0
                else:
                    data[key] = 1
            
            conn = create_connection(db_crew)
            with conn:
                sql = '''UPDATE
                            crew
                        SET
                            break_distro = ?,
                            complete_distro = ?,
                            stills_distro = ?
                        WHERE
                            project_id = ?
                        AND
                            member_id = ?
                        '''
                cur = conn.cursor()
                cur.execute(sql, (data['break'], data['complete'], data['stills'], proj_id, member_id))
                conn.commit()

        return redirect(url_for('member', proj_id=proj_id, member_id=member_id))