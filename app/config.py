import os
from pathlib import Path

dotenv_path = Path(__file__).parent.parent / ".env"
if dotenv_path.exists():
    from dotenv import load_dotenv
    load_dotenv(dotenv_path)

class Config:   # <-- Uppercase
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    K_t   = 4.184e12          # 1 kt TNT in J
    RHO_I = 3300              # impactor density kg/m³
    RHO_T = 2700              # target density kg/m³
    G     = 6.674e-11
    PO    = 101325            # sea-level Pa
    CO    = 343               # sound speed m/s
