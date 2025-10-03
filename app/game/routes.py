# app/game.py
from flask import Blueprint, render_template, request, jsonify
from app.config import Config

# Import LangChain components with error handling
try:
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from app.game import bp 

def get_advisor_chain():
    if not LANGCHAIN_AVAILABLE:
        return None
        
    openai_api_key = Config.OPENAI_API_KEY
    if not openai_api_key:
        return None
    
    try:
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=openai_api_key
        )
        
        advisor_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are Dr. Astra, the Chief Scientific Advisor to the Global Asteroid Defense Initiative (GADI). 
            Your role is to provide strategic recommendations to the Director based on the current game state.
            
            Analyze the situation and provide:
            1. A concise assessment of the current threat level
            2. Specific budget allocation recommendations (percentages for each category)
            3. Technology research priorities
            4. Diplomatic actions to take
            5. Public communication strategy
            
            Keep your response professional, data-driven, and focused on saving Earth. 
            Be direct but not alarmist. Use bullet points for clarity.
            
            Current game state:"""),
            ("human", "{game_state}")
        ])
        
        return advisor_prompt | llm | StrOutputParser()
    except Exception as e:
        print(f"Error initializing AI advisor: {e}")
        return None

@bp.route("/")
def index():
    return render_template("game.html")

@bp.route("/front")
def indexW():
    return render_template("front.html")


@bp.route("/game2")
def index2():
    return render_template("game2.html")

@bp.route("/get_advice", methods=["POST"])
def get_advice():
    if not LANGCHAIN_AVAILABLE:
        return jsonify({
            "advice": "⚠️ **AI Advisor Unavailable**\n\nRequired packages not installed. Run:\n\npip install langchain langchain-openai"
        })
    
    try:
        advisor_chain = get_advisor_chain()
        
        if not advisor_chain:
            return jsonify({
                "advice": "⚠️ **AI Advisor Unavailable**\n\nPlease configure your `.env` file with:\n\n`OPENAI_API_KEY=your_api_key_here`"
            })
        
        game_state = request.json.get("game_state", {})
        formatted_state = format_game_state(game_state)
        advice = advisor_chain.invoke({"game_state": formatted_state})
        
        return jsonify({"advice": advice})
    
    except Exception as e:
        print(f"AI Advisor Error: {str(e)}")
        return jsonify({
            "advice": f"⚠️ **Technical Difficulties**\n\nError: {str(e)}"
        })

def format_game_state(game_state):
    year = game_state.get("year", "Unknown")
    budget = game_state.get("budget", 0)
    approval = game_state.get("approval", 0)
    threats = game_state.get("threats", [])
    technologies = game_state.get("technologies", {})

    threat_info = []
    for threat in threats:
        size_str = threat['size']
        if '50m' in size_str:
            diameter = 50
        elif '200m' in size_str:
            diameter = 200
        elif '500m' in size_str:
            diameter = 500
        elif '1km+' in size_str:
            diameter = 1000
        else:
            diameter = 100
        
        volume = (4/3) * 3.14159 * (diameter/2)**3
        mass = volume * Config.RHO_I
        ke_joules = 0.5 * mass * (20000)**2
        kt_tnt = ke_joules / Config.K_t
        
        threat_info.append(
            f"- {threat['name']}: {threat['size']}, {threat['yearsUntilImpact']}y, "
            f"Risk {threat['risk']}/4, Est. Energy: {kt_tnt:.1f} kt TNT"
        )

    researched_tech = [t["name"] for t in technologies.values() if t.get("researched", False)]
    unresearched_tech = [f"{t['name']} (${t['cost']/1000:.1f}B)" for t in technologies.values() if not t.get("researched", False)]

    formatted = f"""
    Current Year: {year}
    Budget: ${budget/1000:.1f}B
    Public Approval: {approval}%

    Active Threats ({len(threats)}):
    {chr(10).join(threat_info) if threat_info else "None"}

    Researched Technologies:
    {', '.join(researched_tech) if researched_tech else "None"}

    Available Technologies for Research:
    {', '.join(unresearched_tech) if unresearched_tech else "All researched"}
    """
    return formatted

# Keep your test route for debugging
@bp.route("/test-api")
def test_api():
    return jsonify({
        "status": "API is working!",
        "config_loaded": bool(Config.OPENAI_API_KEY),
        "langchain_available": LANGCHAIN_AVAILABLE
    })