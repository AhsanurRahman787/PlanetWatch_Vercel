from flask import Blueprint

bp = Blueprint("game", __name__, template_folder="templates")

# import routes so they register
from app.game import routes