import math, requests, datetime as dt, random, json, os, base64
import plotly.graph_objs as go
from flask import Blueprint, render_template, jsonify, request
from dotenv import load_dotenv

# ✅ new LangChain imports
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from app.neo import bp

# ✅ OpenAI SDK v1+
from openai import OpenAI

load_dotenv()   # load .env variables

API_KEY = "i4qSfG0QQG1E05NrJ8NEr3RyMkmAD7dB83edeElz"   # NASA API key
BROWSE  = "https://api.nasa.gov/neo/rest/v1/neo/browse?page=0&size=30"

 


# --------------------------------------------------
# --------------  orbital mechanics ----------------
# --------------------------------------------------
def kepler_to_xyz(a, e, i, Omega, omega, M):
    a, e, i, Omega, omega, M = map(float, (a, e, i, Omega, omega, M))
    i, Omega, omega, M = map(math.radians, [i, Omega, omega, M])
    a *= 149597870.7          # AU → km
    E = M if e < 0.8 else math.pi
    for _ in range(20):
        E = M + e * math.sin(E)
    nu = 2 * math.atan2(
        math.sqrt(1 + e) * math.sin(E / 2),
        math.sqrt(1 - e) * math.cos(E / 2)
    )
    r = a * (1 - e * math.cos(E))
    cosO, sinO = math.cos(Omega), math.sin(Omega)
    cosw, sinw = math.cos(omega), math.sin(omega)
    cosi, sini = math.cos(i), math.sin(i)
    xp = r * math.cos(nu)
    yp = r * math.sin(nu)
    x = (cosO * cosw - sinO * sinw * cosi) * xp + (-cosO * sinw - sinO * cosw * cosi) * yp
    y = (sinO * cosw + cosO * sinw * cosi) * xp + (-sinO * sinw + cosO * cosw * cosi) * yp
    z = (sinw * sini) * xp + (cosw * sini) * yp
    return x, y, z


def orbit_trace(el, n=120):
    a   = el.get("semi_major_axis")
    e   = el.get("eccentricity")
    i   = el.get("inclination")
    Omega = el.get("ascending_node_longitude")
    omega = el.get("perihelion_argument")
    if None in (a, e, i, Omega, omega):
        return [], [], []
    xs, ys, zs = [], [], []
    for k in range(n + 1):
        M = 2 * math.pi * k / n
        x, y, z = kepler_to_xyz(a, e, i, Omega, omega, M)
        xs.append(x); ys.append(y); zs.append(z)
    return xs, ys, zs


# --------------------------------------------------
# --------------  /data route ----------------------
# --------------------------------------------------
@bp.route("/data")
def data():
    resp = requests.get(BROWSE, params={"api_key": API_KEY}, timeout=15)
    resp.raise_for_status()
    neos = resp.json()["near_earth_objects"]

    traces = []

    # Starfield
    def stars():
        return [random.randint(-3, 3) * 1e9 for _ in range(300)]

    traces.append(go.Scatter3d(
        x=stars(), y=stars(), z=stars(),
        mode="markers", marker=dict(size=1, color="white"),
        hoverinfo="skip", name="Stars"
    ))

    # Sun
    traces.append(go.Scatter3d(
        x=[0], y=[0], z=[0], mode="markers",
        marker=dict(size=18, color="#ffd166", line=dict(width=2, color="white")),
        name="Sun", hovertemplate="Sun<extra></extra>"
    ))

    # Earth
    earth_M = 2 * math.pi * (dt.datetime.utcnow().timetuple().tm_yday / 365.25)
    ex, ey, ez = kepler_to_xyz(1.0, 0.0167, 0, 0, 0, earth_M)
    traces.append(go.Scatter3d(
        x=[ex], y=[ey], z=[ez], mode="markers",
        marker=dict(size=12, color="#3a86ff", line=dict(width=2, color="white")),
        name="Earth", hovertemplate="Earth<extra></extra>"
    ))

    # NEOs
    for obj in neos:
        el = obj["orbital_data"]
        xs, ys, zs = orbit_trace(el)
        if not xs:
            continue
        pha = obj["is_potentially_hazardous_asteroid"]
        color = "#ff006e" if pha else "#8338ec"
        traces.append(go.Scatter3d(
            x=xs, y=ys, z=zs, mode="lines",
            line=dict(width=4, color=color), hoverinfo="skip",
            name=obj["name"][:30], showlegend=False
        ))
        traces.append(go.Scatter3d(
            x=[xs[0]], y=[ys[0]], z=[zs[0]], mode="markers",
            marker=dict(size=5, color=color, line=dict(width=1, color="white")),
            hovertemplate=f"<b>{obj['name']}</b><br>PHA: {'Yes' if pha else 'No'}<extra></extra>",
            showlegend=False
        ))

    return jsonify({"traces": [t.to_plotly_json() for t in traces]})


# --------------------------------------------------
# --------------  CHATBOT --------------------------
# --------------------------------------------------
_KNOWLEDGE = ""


def _build_knowledge():
    """Fetch NEO facts once at startup for chatbot context."""
    global _KNOWLEDGE
    try:
        resp = requests.get(BROWSE, params={"api_key": API_KEY}, timeout=15)
        resp.raise_for_status()
        neos = resp.json()["near_earth_objects"]
        lines = []
        for obj in neos:
            name = obj["name"]
            dia = (obj["estimated_diameter"]["kilometers"]["estimated_diameter_max"] +
                   obj["estimated_diameter"]["kilometers"]["estimated_diameter_min"]) / 2
            pha = obj["is_potentially_hazardous_asteroid"]
            miss = (min([float(close["miss_distance"]["kilometers"])
                        for close in obj["close_approach_data"]])
                    if obj["close_approach_data"] else None)
            if miss:
                lines.append(f"- {name}: diameter ≈ {dia:.2f} km, "
                             f"PHA: {'YES' if pha else 'no'}, "
                             f"closest pass ≈ {miss/1e6:.1f} M km")
            else:
                lines.append(f"- {name}: diameter ≈ {dia:.2f} km, "
                             f"PHA: {'YES' if pha else 'no'}, "
                             "no close-approach data")
        _KNOWLEDGE = "NEO facts:\n" + "\n".join(lines)
    except Exception:
        _KNOWLEDGE = "NEO facts: (temporarily unavailable)"


_build_knowledge()

# ✅ LangChain LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

SYSTEM_PROMPT = (
    "You are a friendly space expert. Use only the provided NEO facts to answer. "
    "If a question is outside the data, say so. Keep answers short and clear.\n\n"
    f"{_KNOWLEDGE}"
)


def ask_neo_chat(human_text: str) -> str:
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=human_text)
    ]
    return llm(messages).content


@bp.route("/chat", methods=["POST"])
def chat():
    """
    Expects JSON: {"message": "string", "want_audio": bool}
    Returns JSON: {"reply": "string", "reply_audio": base64|None}
    """
    data = request.get_json(force=True)
    question = data.get("message", "").strip()
    if not question:
        return jsonify({"reply": "No question received."}), 400

    answer = ask_neo_chat(question)

    audio_b64 = None
    if data.get("want_audio"):
        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.audio.speech.create(
                model="gpt-4o-mini-tts",
                voice="alloy",
                input=answer
            )
            audio_bytes = response.read()
            audio_b64 = base64.b64encode(audio_bytes).decode()
        except Exception:
            pass  # fallback to browser TTS

    return jsonify({"reply": answer, "reply_audio": audio_b64})


# --------------------------------------------------
# --------------  PAGE ROUTE -----------------------
# --------------------------------------------------
@bp.route("/")
def index():
    return render_template("neo.html")

@bp.route("/page1")
def page1():
    return render_template("page1.html")

@bp.route("/page2")
def page2():
    return render_template("page2.html")

@bp.route("/page2A")
def page2A():
    return render_template("page2A.html")
