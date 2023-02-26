"""
Define the routes for the app
"""
from flask import Blueprint, render_template
from .myFunctions import getrandomrecipe
views = Blueprint('views', __name__)

@views.route('/')
def home():
    recipe = getrandomrecipe()
    return render_template('index.html', recipe=recipe)
