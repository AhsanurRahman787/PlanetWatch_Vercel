import os
import requests
from flask import Flask, request, jsonify, redirect
from flask_caching import Cache
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser

cache = Cache()

# ---------- NASA / impact data helpers ----------
neo_cache = Cache(config={'CACHE_TYPE': 'simple'})

@neo_cache.cached(timeout=3600, key_prefix='nasa_summary')
def nasa_summary():
    try:
        key = os.getenv("NASA_API_KEY", "DEMO_KEY")
        resp = requests.get(
            "https://api.nasa.gov/neo/rest/v1/neo/browse",
            params={"api_key": key, "size": 20},
            timeout=10,
        )
        resp.raise_for_status()
        neos = resp.json()["near_earth_objects"]
        lines = []
        for n in neos:
            el = n["orbital_data"]
            lines.append(
                f"{n['name']}: a={float(el.get('semi_major_axis', 0)):.2f} AU, "
                f"e={float(el.get('eccentricity', 0)):.2f}, "
                f"PHA={'Yes' if n['is_potentially_hazardous_asteroid'] else 'No'}"
            )
        return "\n".join(lines)
    except Exception:
        return "NASA data temporarily unavailable."

def impact_summary(lat, lon, E):
    from app.physics import overpressure
    rings = [2, 5, 10, 20, 50]
    lines = [f"Impact energy: {E:.2e} J"]
    for r in rings:
        op = overpressure(E, r) / 1000
        lines.append(f"{r} km → {op:.1f} kPa over-pressure")
    return "\n".join(lines)

# ---------- Flask factory ----------
def create_app():
    app = Flask(__name__, static_folder="../static", template_folder="templates")
    app.config.from_object("app.config.Config")
    cache.init_app(app, config={"CACHE_TYPE": "simple"})
    neo_cache.init_app(app)

    # register blueprints
    from app.neo import bp as neo_bp
    from app.quiz import bp as quiz_bp
    from app.game import bp as game_bp
    from app.impact import bp as impact_bp
    from app.shelters import bp as shelters_bp

    app.register_blueprint(neo_bp, url_prefix="/neo")
    app.register_blueprint(quiz_bp, url_prefix="/quiz")
    app.register_blueprint(game_bp, url_prefix="/game")
    app.register_blueprint(impact_bp, url_prefix="/impact")
    app.register_blueprint(shelters_bp, url_prefix="/shelters")

    @app.route("/")
    def index():
        return redirect("/game/front")

    # ---------- AI chat ----------
    llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")

    @app.post("/chat")
    def chat():
        data = request.get_json(force=True)
        user_msg = data.get("message", "")
        page = data.get("page", "neo")

        persona = {
            "/neo": "You are a helpful planetary-defence scientist. Use concise language.",
            "/quiz": "You are a friendly tutor. Explain why answers are right or wrong.",
            "/game": "You are a game strategist. Give concise arcade tips.",
            "/impact": "You are a crisis assistant. Interpret impact physics for humans.",
        }.get(page, "You are a survival advisor. Give practical shelter advice.")

        context = ""
        if page.startswith("/neo"):
            context = "Current NEO orbital data:\n" + nasa_summary()
        elif page.startswith("/impact"):
            lat = request.args.get("lat", 0, float)
            lon = request.args.get("lon", 0, float)
            E = request.args.get("E", 5e15, float)
            context = impact_summary(lat, lon, E)

        prompt = ChatPromptTemplate.from_messages([
            ("system", persona + "\n\n{context}"),
            ("human", "{question}")
        ])
        chain = prompt | llm | StrOutputParser()
        reply = chain.invoke({"context": context, "question": user_msg})
        return jsonify({"reply": reply})

    return app