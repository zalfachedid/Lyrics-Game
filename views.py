from flask import Blueprint, render_template, request,session

views = Blueprint('views',__name__)

@views.route('/')
def base():
    return render_template("base.html")


