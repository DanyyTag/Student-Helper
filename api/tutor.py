from groq import Groq
from anthropic import Anthropic
from openai import OpenAI
import json

def handler(request):
    if request.method == 'OPTIONS':
        from flask import Response
        return Response('', status=200, headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        })

    try:
        body = request.get_json()
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
            client = Anthropic(api_key=api_key)
            resp = client.messages.create(
                model='claude-sonnet-4-6',
                max_tokens=1000,
                system=system,
                messages=messages
            )
            text = resp.content[0].text
        elif api_key.startswith('gsk_'):
            client = Groq(api_key=api_key)
            resp = client.chat.completions.create(
                model='llama-3.1-8b-instant',
                max_tokens=1000,
                messages=[{'role': 'system', 'content': system}] + messages
            )
            text = resp.choices[0].message.content
        elif api_key.startswith('sk-'):
            client = OpenAI(api_key=api_key)
            resp = client.chat.completions.create(
                model='gpt-4o',
                max_tokens=1000,
                messages=[{'role': 'system', 'content': system}] + messages
            )
            text = resp.choices[0].message.content
        else:
            text = 'API key not recognized'

        from flask import Response as FlaskResponse
        return FlaskResponse(
            json.dumps({'result': text}),
            status=200,
            headers={'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
        )

    except Exception as e:
        from flask import Response as FlaskResponse
        return FlaskResponse(
            json.dumps({'error': str(e)}),
            status=500,
            headers={'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
        )
