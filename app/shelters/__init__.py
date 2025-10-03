from flask import Blueprint

bp = Blueprint("shelters", __name__, template_folder="templates")

# import routes so they register
from app.shelters import routes