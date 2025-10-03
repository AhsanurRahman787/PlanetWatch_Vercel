from flask import Blueprint

bp = Blueprint("impact", __name__, template_folder="templates")

# Import routes so they register with this blueprint
from app.impact import routes
