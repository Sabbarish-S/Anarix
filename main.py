from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
import google.generativeai as genai
import os
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Check API key
if not api_key:
    raise Exception("❌ GOOGLE_API_KEY not found in .env file.")

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")  # or "models/gemini-1.5-pro"

# Initialize FastAPI app
app = FastAPI()

# Request body model
class Question(BaseModel):
    user_question: str

# Function to query SQLite database
def query_database(sql_query):
    # Resolve the correct database path
    project_root = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(project_root, "database", "ecommerce.db")

    # Check if the database file exists
    if not os.path.exists(db_path):
        return f"❌ Database file not found at: {db_path}"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        result = cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        return f"❌ SQL Execution Error: {str(e)}"

# API endpoint to ask a question
@app.post("/ask")
async def ask_question(q: Question):
    prompt = f"""You are a helpful SQL assistant. Convert the question to a single SQL query.
Use only these tables: eligibility, ad_sales, total_sales.
For questions like "What is my total sales?", return a SUM on the appropriate column.
Return ONLY the SQL query. No explanation or formatting.

Question: {q.user_question}
"""

    # Gemini generates SQL
    response = model.generate_content(prompt)
    sql_raw = response.text

    # Clean markdown/code block formatting
    sql_query = re.sub(r"```sql|```", "", sql_raw).strip()
    sql_query = sql_query.split(";")[0].strip() + ";"

    # Query DB
    result = query_database(sql_query)

    # Format the result if it's a single value
    try:
        if isinstance(result, list) and len(result) == 1 and len(result[0]) == 1:
            answer = f"✅ {q.user_question.strip().capitalize()} is ₹{result[0][0]:,.2f}"
        else:
            answer = "✅ Query executed successfully. See result."
    except:
        answer = "⚠️ Unable to interpret the result."

    return {
        "user_question": q.user_question,
        "sql_query": sql_query,
        "result": result,
        "answer": answer
    }