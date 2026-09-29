from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            question = body.get('question', '')
            schema = body.get('schema', '')
            history = body.get('history', [])
            api_key = body.get('api_key', '')
            lang = body.get('lang', 'it')

            if lang == 'it':
                system = """Sei un tutor socratico per studenti, anche con dislessia.
REGOLA: non dare MAI la risposta diretta.
- fai una domanda guida per aiutare lo studente a ragionare
- un passo piccolo alla volta
- frasi corte e semplici
- se bloccato, dai un piccolo indizio
- sii incoraggiante
Rispondi in italiano, massimo 4-5 righe."""
            else:
                system = """You are a Socratic tutor for students, including those with dyslexia.
RULE: NEVER give the direct answer.
- ask a guiding question to help the student think
- one small step at a time
- short and simple sentences
- if stuck, give a small hint
- be encouraging
Reply in English, max 4-5 lines."""

            context = f"Schema:\n{schema}\n\nDomanda: {question}"
            messages = history + [{'role': 'user', 'content': context}]

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
                    model='llama-3.1-8b-instant',
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
                raise ValueError('API key format not recognized')

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
