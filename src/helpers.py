from flask import Flask, render_template, request, session, redirect
from functools import wraps

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper

def clear_project_id(s):
    if s.get("project_id"):
        s.pop("project_id", None)