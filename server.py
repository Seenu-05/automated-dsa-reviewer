from flask import Flask, request
import requests
from google import genai
from google.genai import types
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GITHUB_TOKEN or not GEMINI_API_KEY:
    raise ValueError("Missing API Keys! Check your .env file.")
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("Missing DATABASE_URL! Check your .env file.")

client = genai.Client(api_key=GEMINI_API_KEY)

def get_historical_context():
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        cursor.execute("SELECT timestamp, ai_feedback FROM code_review ORDER BY id DESC LIMIT 3")
        rows = cursor.fetchall()
        if not rows:
            return "No previous history found. This is the user's first attempt."
        context = "Here is the user's recent code optimization history:\n"
        for index, row in enumerate(rows, 1):
            context += f"\n--- Past Review #{index} ({row[0]}) ---\n{row[1]}\n"
        return context
    except psycopg2.Error as e:
        print(f"⚠️ Error fetching history: {e}")
        return "Could not retrieve history due to a database error."
    finally:
        if conn:
            conn.close()

def post_comment_to_github(repo_name, commit_id, comment_body):
    api_url = f"https://api.github.com/repos/{repo_name}/commits/{commit_id}/comments"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    payload = {
        "body": comment_body
    }

    print(f"DEBUG: Token starts with: {GITHUB_TOKEN[:8]}")
    print(f"DEBUG: Token total length: {len(GITHUB_TOKEN)}")

    response = requests.post(api_url, headers=headers, json=payload)

    if response.status_code == 201:
        print("✅ Successfully posted the AI review directly to GitHub!")
    else:
        print(f"❌ Failed to post comment to GitHub. Status: {response.status_code}")
        print(response.json())

@app.route('/webhook', methods=['POST']) 
def github_webhook():

    data = request.json
    event_type = request.headers.get('X-GitHub-Event')

    if event_type == 'push':
        
        print("\n---NEW PUSH DETECTED---")
        repo_name = data['repository']['full_name']
        commit_id = data['head_commit']['id']
        api_url = f"https://api.github.com/repos/{repo_name}/commits/{commit_id}"

        headers = {
            "Authorization" : f"token {GITHUB_TOKEN}",
            "Accept" : "application/vnd.github.v3+json"
        }
        response = requests.get(api_url, headers=headers)
        commit_data = response.json()

        if 'files' in commit_data:
            for file in commit_data['files']:
                if file['filename'].endswith('.cpp'):
                    print(f"\n[C++ File Found]: {file['filename']}")
                    patch = file.get('patch', '')
                    if patch:
                        print("---Sending to AI for DSA Analysis---")

                        history_data = get_historical_context()

                        system_instruction = f"""
                        You are an elite, highly disciplined Software Engineering Coach specializing in Data Structures and Algorithms (DSA). 
                        Your coaching philosophy is built on 'Eating That Frog'—forcing the developer to tackle the hardest, most computationally expensive logic first.

                        You have access to the user's past performance history below. Cross-reference their new code submission with this history.

                        {history_data}

                        CRITICAL RULES:
                        1. If the user's new code has a worse Time/Space complexity than their past entries, aggressively call out the regression.
                        2. If their previous attempt was an exponential or factorial nightmare (like O(2^N) or O(N!)) and they haven't optimized it, refuse to praise them. Force them to 'eat the frog' and address the core bottleneck.
                        3. Keep reviews brutally honest, high-energy, and deeply technical. Break down the Big-O comparison clearly.

                        REQUIRED OUTPUT FORMAT:
                        You MUST strictly adhere to this exact format:

                        SUMMARY: [1 sentence explaining what their new code does and if it improved from the history]
                        TIME COMPLEXITY: [Exact Big-O] - [1 sentence explanation]
                        SPACE COMPLEXITY: [Exact Big-O] - [1 sentence explanation]
                        THE COACH'S VERDICT: [Your brutal, gamified feedback based on the history comparison]
                        OPTIMIZATION TARGET: [1 single, actionable tip for the next commit]
                        """

                        ai_response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=patch,
                            config=types.GenerateContentConfig(
                                system_instruction=system_instruction
                            )
                        )

                        print("===AI CODE REVIEW===")
                        print(ai_response.text)
                        print("======================\n")

                        try:
                            conn = psycopg2.connect(DATABASE_URL)
                            cursor = conn.cursor()
                            insert_query = """
                            INSERT INTO code_review(commit_id, ai_feedback)
                            VALUES (%s, %s)
                            """
                            cursor.execute(insert_query, (commit_id, ai_response.text))
                            conn.commit()
                            print(f"💾 Successfully saved review for commit {commit_id[:7]} to database!\n")

                        except psycopg2.Error as e:
                            print(f"❌ Database error: {e}")
                        
                        finally:
                            if conn:
                                conn.close()

                        print("---Sending comment to GitHub---")
                        post_comment_to_github(repo_name, commit_id, ai_response.text)

                    else:
                        print("No logic changes found in this C++ file.")



    return {"status": "success"}, 200

if __name__ == '__main__':
    app.run(port=5000)

