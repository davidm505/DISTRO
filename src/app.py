import os

from flask import Flask, redirect, render_template, session, request
import sqlite3
from helpers import login_required

# Configure application 
app = Flask(__name__)

# Auto-reload templates
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route("/")
@login_required
def index():
    pass


@app.route("/login", methods=["GET", "POST"])
def login():
    '''Log user in'''

    print("user name is:", session.get("user_id"))

    if request.method == "POST":
        pass
        # user is attempting to log in
    else:
        return render_template("login.html")