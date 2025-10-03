from flask import Blueprint, render_template, request, jsonify, send_file, abort
from app.osm import fetch_osm_shelters
from app.map_builder import create_map
from app.chatbot import get_shelter_advice
from pathlib import Path
from app.shelters import bp
from io import BytesIO
import re  # Added for regex
from openai import OpenAI  # Make sure OpenAI SDK is installed

# Initialize OpenAI client
client = OpenAI(api_key="YOUR_API_KEY_HERE")  # Replace with your API key

# Store the last map HTML in memory
last_map_html = ""
last_shelters = []

@bp.route("/")
def index():
    return render_template("shelters.html")

@bp.route("/generate", methods=["POST"])
def generate():
    global last_map_html, last_shelters
    try:
        lat = float(request.form["lat"])
        lon = float(request.form["lon"])
        search = float(request.form.get("search_radius_km", 20))
    except:
        return jsonify({"error": "Invalid input"}), 400

    shelters = fetch_osm_shelters(lat, lon, search)
    last_shelters = shelters

    # Generate map HTML dynamically
    last_map_html = create_map(lat, lon, shelters)

    return jsonify({
        "message": f"Found {len(shelters)} shelter(s).",
        "map_html": last_map_html,
        "shelters_count": len(shelters)
    })

@bp.route("/download-map")
def download_map():
    global last_map_html
    if not last_map_html:
        return abort(404, "No map generated yet.")

    buffer = BytesIO()
    buffer.write(last_map_html.encode("utf-8"))
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="shelter_map.html", mimetype="text/html")

@bp.route("/history")
def history():  # Renamed for clarity
    return render_template("history.html")

@bp.route("/policymaker")
def home():
    return render_template("policymaker.html")

@bp.route("/policy-maker/ask_ai", methods=["POST"])
def ask_ai():
    data = request.json
    user_message = data.get("message", "")
    country = data.get("country", "Unknown")
    mode = data.get("mode", "reply")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        if mode == "reply":
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in asteroid defense and space policy."},
                    {"role": "user", "content": f"Answer this user question regarding {country}: {user_message}"}
                ]
            )
            ai_text = response.choices[0].message.content.strip()
            return jsonify({"ai_reply": ai_text})

        elif mode == "evaluate":
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in asteroid defense and policy evaluation."},
                    {"role": "user", "content": f"Evaluate this asteroid policy: {user_message}. Give a numeric rating out of 100 and explain why it is not perfect."}
                ]
            )
            ai_text = response.choices[0].message.content.strip()
            rating_match = re.search(r'(\d{1,3})', ai_text)
            rating = int(rating_match.group(1)) if rating_match else 0
            reason_match = re.search(r'(Reason[:\-]\s*)(.*)', ai_text, re.IGNORECASE)
            reason = reason_match.group(2).strip() if reason_match else ai_text
            return jsonify({"rating": rating, "reason": reason})

        else:  # generate_policy
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in asteroid defense policy. Generate a concise, actionable asteroid defense policy based on user input."},
                    {"role": "user", "content": f"User input: {user_message}. Generate a suitable policy."}
                ]
            )
            policy_text = response.choices[0].message.content.strip()
            return jsonify({"generated_policy": policy_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
