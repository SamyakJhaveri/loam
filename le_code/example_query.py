"""
Minimal example: query Ask Sage API using .env file for credentials.

Usage:
    1. Put your API key and email in .env file (same directory):
        ASK_SAGE_API=your_api_key_here
        ASK_SAGE_EMAIL=your_email@anl.gov

    2. Run:
        python example_query.py
"""

import os
from dotenv import load_dotenv
from anl_asksage_client import ANLAskSageClient

# Load credentials from .env
load_dotenv()

api_key = os.getenv("ASK_SAGE_API")
email = os.getenv("ASK_SAGE_EMAIL")

if not api_key or not email:
    raise EnvironmentError("Missing ASK_SAGE_API or ASK_SAGE_EMAIL in .env file")

# Initialize client
client = ANLAskSageClient(
    email=email,
    api_key=api_key,
    path_to_CA_Bundle="asksage_anl_gov.pem",
)

# Query
result = client.query(
    message="What is Ask Sage?",
    model="gpt-4.1",
    temperature=0.7,
)

print(result.get("message"))
