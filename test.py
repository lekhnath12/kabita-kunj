from flask import Flask, request, jsonify, render_template
import json
import random
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load the .env file from the current directory
load_dotenv()




# Initialize OpenAI Client using the environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
print(f"OpenAI API Key Loaded: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")
