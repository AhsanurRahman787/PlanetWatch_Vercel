from flask import Blueprint

bp = Blueprint("quiz", __name__, template_folder="templates")

# import routes so they register
from app.quiz import routes