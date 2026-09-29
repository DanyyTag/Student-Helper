from flask import Flask, request, jsonify
from groq import Groq
from anthropic import Anthropic
from openai import OpenAI

app = Flask(__name__)

SCHEMA_IT = """Sei un tutor per studenti, anche con dislessia.
Crea uno SCHEMA chiaro e semplice sull'argomento:
- usa titoli brevi con emoji
- punti elenco corti (massimo 8-10 parole per punto)
- evita paragrafi lunghi
- struttura ad albero: concetto principale, poi sotto-punti
- alla fine 2-3 parole chiave da ricordare
Vai dritto al contenuto senza introduzioni."""

SCHEMA_EN = """You are a tutor for students, including those with dyslexia.
Create a clear and simple SUMMARY of the topic:
- use short titles with emoji
- short bullet points (max 8-10 words each)
- avoid long paragraphs
- tree structure: main concept, then sub-points
- at the end 2-3 key words to remember
Go straight to the content, no introductions."""

TUTOR_IT = """Sei un tutor socratico per studenti, anche con dislessia.
REGOLA: non dare MAI la risposta diretta.
- fai una domanda guida per aiutare lo studente a ragionare
- un passo piccolo alla volta
- frasi corte e semplici
- se bloccato, dai un piccolo indizio
- sii incoraggiante
Rispondi in italiano, massimo 4-5 righe."""

TUTOR_EN = """You are a Socratic tutor for students, including those with dyslexia.
RULE: NEVER give the direct answer.
- ask a guiding question to help the student think
- one small step at a time
- short and simple sentences
- if stuck, give a small hint
- be encouraging
Reply in English, max 4-5 lines."""

def cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

def call_ai(api_key, system, messages):
    if api_key.startswith('sk-ant-'):
        client = Anthropic(api_key=api_key)
        resp = client.messages.create(model='claude-sonnet-4-6', max_tokens=1000, system=system, messages=messages)
        return resp.content[0].text
    elif api_key.startswith('gsk_'):
        client = Groq(api_key=api_key)
        resp = client.chat.completions.create(model='openai/gpt-oss-20b', max_tokens=1000, messages=[{'role': 'system', 'content': system}] + messages)
        return resp.choices[0].message.content
    elif api_key.startswith('sk-'):
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(model='gpt-4o', max_tokens=1000, messages=[{'role': 'system', 'content': system}] + messages)
        return resp.choices[0].message.content
    else:
        raise ValueError('API key not recognized')

@app.route('/api/schema', methods=['POST', 'OPTIONS'])
def schema():
    if request.method == 'OPTIONS':
        return cors(jsonify({}))
    try:
        body = request.get_json()
        lang = body.get('lang', 'it')
        system = SCHEMA_IT if lang == 'it' else SCHEMA_EN
        text = call_ai(body['api_key'], system, [{'role': 'user', 'content': body['topic']}])
        return cors(jsonify({'result': text}))
    except Exception as e:
        return cors(jsonify({'error': str(e)})), 500

@app.route('/api/tutor', methods=['POST', 'OPTIONS'])
def tutor():
    if request.method == 'OPTIONS':
        return cors(jsonify({}))
    try:
        body = request.get_json()
        lang = body.get('lang', 'it')
        system = TUTOR_IT if lang == 'it' else TUTOR_EN
        context = f"Schema:\n{body['schema']}\n\nDomanda: {body['question']}"
        messages = body.get('history', []) + [{'role': 'user', 'content': context}]
        text = call_ai(body['api_key'], system, messages)
        return cors(jsonify({'result': text}))
    except Exception as e:
        return cors(jsonify({'error': str(e)})), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return app.send_static_file('index.html')
