from groq import Groq
from anthropic import Anthropic
from openai import OpenAI
import json

def allow_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

def handler(request):
    from http import HTTPStatus
    
    if request.method == 'OPTIONS':
        return Response('', status=200, headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        })

    try:
        body = request.json()
        topic = body.get('topic', '')
        api_key = body.get('api_key', '')
        lang = body.get('lang', 'it')

        if lang == 'it':
            system = """Sei un tutor per studenti, anche con dislessia.
Crea uno SCHEMA chiaro e semplice sull'argomento:
- usa titoli brevi con emoji
- punti elenco corti (massimo 8-10 parole per punto)
- evita paragrafi lunghi
- struttura ad albero: concetto principale, poi sotto-punti
- alla fine 2-3 parole chiave da ricordare
Vai dritto al contenuto senza introduzioni."""
        else:
            system = """You are a tutor for students, including those with dyslexia.
Create a clear and simple SUMMARY of the topic:
- use short titles with emoji
- short bullet points (max 8-10 words each)
- avoid long paragraphs
- tree structure: main concept, then sub-points
- at the end 2-3 key words to remember
Go straight to the content, no introductions."""

        if api_key.startswith('sk-ant-'):
            client = Anthropic(api_key=api_key)
            resp = client.messages.create(
                model='claude-sonnet-4-6',
                max_tokens=1000,
                system=system,
                messages=[{'role': 'user', 'content': topic}]
            )
            text = resp.content[0].text
        elif api_key.startswith('gsk_'):
            client = Groq(api_key=api_key)
            resp = client.chat.completions.create(
                model='llama-3.1-8b-instant',
                max_tokens=1000,
                messages=[
                    {'role': 'system', 'content': system},
                    {'role': 'user', 'content': topic}
                ]
            )
            text = resp.choices[0].message.content
        elif api_key.startswith('sk-'):
            client = OpenAI(api_key=api_key)
            resp = client.chat.completions.create(
                model='gpt-4o',
                max_tokens=1000,
                messages=[
                    {'role': 'system', 'content': system},
                    {'role': 'user', 'content': topic}
                ]
            )
            text = resp.choices[0].message.content
        else:
            return Response(json.dumps({'error': 'API key not recognized'}), status=400, headers={'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'})

        return Response(json.dumps({'result': text}), status=200, headers={'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'})

    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=500, headers={'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'})
