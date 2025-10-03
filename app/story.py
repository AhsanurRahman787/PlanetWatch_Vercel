# ----------  story.py  ----------
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from app.config import Config

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, openai_api_key=Config.OPENAI_API_KEY)

zone_prompts = {
    "crater":  "Explain in a few short sentences what happens inside the {c:.1f} km crater. make it bulletpoint based",
    "shock":   "Explain in a few short sentences what the gold shock-wave ring ({s:.1f} seismic) does to buildings.make it bulletpoint based",
    "quake":   "Explain in a few short sentences the orange quake circle effects at {s:.1f} km.make it bulletpoint based. find out if similar earthquack happend in the past",
    "tsunami": "Explain in a few short sentences the blue tsunami circle ({ts:.1f} m) for coastal areas. make it bulletpoint based"
}

def generate_zone_story(zone, c, s, op, w, th, ts):
    template = zone_prompts[zone]
    prompt = ChatPromptTemplate.from_template(template)
    chain  = LLMChain(llm=llm, prompt=prompt)
    return chain.run(c=c, s=s, op=op, w=w, th=th, ts=ts)