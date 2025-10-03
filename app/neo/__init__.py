from flask import Blueprint

bp = Blueprint("neo", __name__, template_folder="templates")

# import routes so they register
from app.neo import routes