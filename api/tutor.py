from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length))
        question = body.get('question', '')
        schema = body.get('schema', '')
        history = body.get('history', [])
        api_key = body.get('api_key', '')
        lang = body.get('lang', 'it')

        if lang == 'it':
            system = """Sei un tutor socratico per studenti, anche con dislessia.
REGOLA FONDAMENTALE: non dare MAI la risposta diretta o la soluzione finale.
Invece:
- fai una domanda guida che aiuti lo studente a trovare la risposta da solo
- scomponi il problema in un passo piccolo alla volta
- usa frasi corte e semplici
- se lo studente è bloccato, dai un piccolo indizio, non la soluzione
- sii incoraggiante e paziente
Rispondi sempre in italiano, in modo breve (massimo 4-5 righe).
Se ti viene chiesto chi sei, rispondi onestamente che sei un tutor basato su intelligenza artificiale."""
        else:
            system = """You are a Socratic tutor for students, including those with dyslexia.
FUNDAMENTAL RULE: NEVER give the direct answer or final solution.
Instead:
- ask a guiding question to help the student find the answer themselves
- break the problem into one small step at a time
- use short and simple sentences
- if the student is stuck, give a small hint, not the solution
- be encouraging and patient
Always reply in English, briefly (max 4-5 lines).
If asked who you are, honestly say you are an AI-based tutor."""

        context = f"Schema:\n{schema}\n\nDomanda: {question}"
        messages = history + [{'role': 'user', 'content': context}]

        try:
            if api_key.startswith('sk-ant-'):
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)
                resp = client.messages.create(
                    model='claude-sonnet-4-6',
                    max_tokens=1000,
                    system=system,
                    messages=messages
                )
                text = resp.content[0].text
            elif api_key.startswith('gsk_'):
                from groq import Groq
                client = Groq(api_key=api_key)
                resp = client.chat.completions.create(
                    model='llama3-70b-8192',
                    max_tokens=1000,
                    messages=[{'role': 'system', 'content': system}] + messages
                )
                text = resp.choices[0].message.content
            elif api_key.startswith('sk-'):
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                resp = client.chat.completions.create(
                    model='gpt-4o',
                    max_tokens=1000,
                    messages=[{'role': 'system', 'content': system}] + messages
                )
                text = resp.choices[0].message.content
            else:
                text = 'API key not recognized'

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'result': text}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
