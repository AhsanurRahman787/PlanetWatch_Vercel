#!/usr/bin/env python3
"""
Single-command launcher for NEO-Defender.
Reads OPENAI_API_KEY from .env in the project root.
"""
import os, sys
from pathlib import Path

# make sure the project folder is on Python path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# load .env manually (so we do NOT rely on flask shell)
from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env", override=True)

# create & run app
from app import create_app
app = create_app()

if __name__ == "__main__":
    # Flask reloader works fine; gunicorn can be swapped in later
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)