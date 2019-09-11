from flask import Flask, render_template, request, session, redirect
from functools import wraps

def login_required(f):
    @wraps(f)
    def func(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return func