from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from app.config import Config

OPENAI_API_KEY = Config.OPENAI_API_KEY

# Prompt template for shelter advice
prompt = ChatPromptTemplate.from_template(
    """
You are an emergency assistant. The user may provide their location and nearby shelters.
Answer clearly which shelter they should go to. If there are no shelters nearby, advise what to do.
Provide step-by-step safety instructions if needed.

User question: {question}
Nearby shelters: {shelters_list}
"""
)

chain = LLMChain(
    llm=ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7,
        openai_api_key=OPENAI_API_KEY
    ),
    prompt=prompt
)

def get_shelter_advice(question: str, shelters_list: list[dict]) -> str:
    """
    Generate advice about which shelter to go to.
    :param question: The user's question
    :param shelters_list: List of nearby shelters [{name, lat, lon}, ...]
    :return: String answer from the LLM
    """
    if shelters_list:
        shelters_str = "\n".join([f"{s['name']} ({s['lat']},{s['lon']})" for s in shelters_list])
    else:
        shelters_str = "No shelters found nearby."

    return chain.run(question=question, shelters_list=shelters_str)
