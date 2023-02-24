
from flask import render_template,request
import datetime
from app import app


@app.route("/time")
def time():
    return str(datetime.datetime.now())