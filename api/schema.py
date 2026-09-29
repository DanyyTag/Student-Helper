from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length))
        topic = body.get('topic', '')
        api_key = body.get('api_key', '')
        lang = body.get('lang', 'it')

        if lang == 'it':
            system = """Sei un tutor per studenti, anche con dislessia.
Quando ti viene dato un argomento, crea uno SCHEMA chiaro e semplice:
- usa titoli brevi con emoji
- punti elenco corti (massimo 8-10 parole per punto)
- evita paragrafi lunghi
- usa una struttura ad albero: concetto principale, poi sotto-punti
- alla fine aggiungi una riga con 2-3 parole chiave da ricordare
Non aggiungere introduzioni: vai dritto al contenuto.
Se ti viene chiesto chi sei, rispondi onestamente che sei un tutor basato su intelligenza artificiale."""
        else:
            system = """You are a tutor for students, including those with dyslexia.
When given a topic, create a clear and simple SUMMARY:
- use short titles with emoji
- short bullet points (max 8-10 words each)
- avoid long paragraphs
- use a tree structure: main concept, then sub-points
- at the end add 2-3 key words to remember
Do not add introductions: go straight to the content.
If asked who you are, honestly say you are an AI-based tutor."""

        try:
            if api_key.startswith('sk-ant-'):
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)
                resp = client.messages.create(
                    model='claude-sonnet-4-6',
                    max_tokens=1000,
                    system=system,
                    messages=[{'role': 'user', 'content': topic}]
                )
                text = resp.content[0].text
            elif api_key.startswith('gsk_'):
                from groq import Groq
                client = Groq(api_key=api_key)
                resp = client.chat.completions.create(
                    model='llama-3.3-70b-versatile',
                    max_tokens=1000,
                    messages=[{'role': 'system', 'content': system}, {'role': 'user', 'content': topic}]
                )
                text = resp.choices[0].message.content
            elif api_key.startswith('sk-'):
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                resp = client.chat.completions.create(
                    model='gpt-4o',
                    max_tokens=1000,
                    messages=[{'role': 'system', 'content': system}, {'role': 'user', 'content': topic}]
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
