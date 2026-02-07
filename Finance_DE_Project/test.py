import os
from dotenv import load_dotenv

load_dotenv()
print("API_KEY =", os.getenv("API_KEY"))
