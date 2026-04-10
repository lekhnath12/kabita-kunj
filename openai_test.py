from openai import OpenAI
from dotenv import load_dotenv


poem_context = """
छापुच्छ्रे गिरिशिखरको पारमा मुक्तिक्षेत्र
बल्छन् बत्ती झलमल जहाँ भुलभुले मूलभित्र
तिम्रो जन्मस्थल छ पहिलो ज्योतिको दिव्य धाम
काली गङ्गा ! भनन कसरी 
"""

import os 
import json

from openai import OpenAI
from dotenv import load_dotenv

# Load the .env file from the current directory
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


VOC_PATH = r"C:\Users\lekhp\OneDrive\Desktop\clean_nepali_words.json" 
prim_voc = {}

if os.path.exists(VOC_PATH):
    with open(VOC_PATH, encoding="utf-8") as f:
        voc = json.load(f)
    
prompt = f"""
        Context (Poem so far): "{poem_context}"
        Task: You are a Nepali poet. Below is a list of Nepali words that fit the current rhythm. 
        Select the 20 most appropriate words as a next word the poem.
        CRITICAL: Arrange the words in DESCENDING order of relevance (best match first).
        Return ONLY the words separated by spaces.
        Candidate Words: {" ".join(voc[:100])}
        """

response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {"role": "system", "content": "You are an expert in Nepali literature and poetry."},
                {"role": "user", "content": prompt}
            ],
            temperature=1.0
        )

import pdb; pdb.set_trace()