import streamlit as st
import pyrebase
import time
from anthropic import Anthropic
from openai import OpenAI
from groq import Groq

FIREBASE_CONFIG = {
    "apiKey": "AIzaSyCxFM0jRILM3KgAUxPA8G5O8M5vpege8AY",
    "authDomain": "student-helper-2026.firebaseapp.com",
    "databaseURL": "https://student-helper-2026-default-rtdb.europe-west1.firebasedatabase.app",
    "projectId": "student-helper-2026",
    "storageBucket": "student-helper-2026.firebasestorage.app",
    "messagingSenderId": "517915471668",
    "appId": "1:517915471668:web:c788362c4b9a2c6fe57f61",
    "measurementId": "G-GRZCC8DM5J"
}

TESTI = {
    "it": {
        "titolo": "🎓 Student Helper",
        "caption": "Scegli un argomento, ottieni uno schema chiaro, poi fai domande: ti guido a ragionare, non ti do la soluzione pronta.",
        "accedi": "Accedi",
        "registrati": "Registrati",
        "reset": "Reset password",
        "email": "Email",
        "password": "Password",
        "chiave_api": "La tua chiave API",
        "btn_accedi": "Accedi",
        "btn_registrati": "Registrati",
        "btn_reset": "Invia email di reset",
        "reset_ok": "Email inviata! Controlla la tua casella.",
        "reset_err": "Email non trovata.",
        "reset_vuota": "Inserisci la tua email.",
        "login_err": "Email o password errati.",
        "reg_vuota": "Compila tutti i campi.",
        "reg_chiave_err": "Formato chiave API non riconosciuto.",
        "reg_ok": "Account creato! Ora accedi.",
        "reg_err": "Errore durante la registrazione. Email già in uso?",
        "chiave_mancante": "Chiave API non trovata nel tuo account.",
        "esci": "Esci",
        "argomento": "📚 Su quale argomento vuoi uno schema?",
        "placeholder": "Es: la fotosintesi, le frazioni, la Rivoluzione francese...",
        "crea_schema": "Crea schema",
        "spinner_schema": "Sto preparando lo schema...",
        "schema_titolo": "### 🗂️ Il tuo schema",
        "chat_titolo": "### 💬 Hai domande? Ragioniamo insieme",
        "chat_input": "Scrivi qui la tua domanda...",
        "spinner_chat": "Sto pensando a come guidarti...",
    },
    "en": {
        "titolo": "🎓 Student Helper",
        "caption": "Choose a topic, get a clear summary, then ask questions: I'll guide your thinking, not give you the answer.",
        "accedi": "Login",
        "registrati": "Sign up",
        "reset": "Reset password",
        "email": "Email",
        "password": "Password",
        "chiave_api": "Your API key",
        "btn_accedi": "Login",
        "btn_registrati": "Sign up",
        "btn_reset": "Send reset email",
        "reset_ok": "Email sent! Check your inbox.",
        "reset_err": "Email not found.",
        "reset_vuota": "Please enter your email.",
        "login_err": "Wrong email or password.",
        "reg_vuota": "Please fill in all fields.",
        "reg_chiave_err": "Unrecognized API key format.",
        "reg_ok": "Account created! Now log in.",
        "reg_err": "Registration error. Email already in use?",
        "chiave_mancante": "API key not found in your account.",
        "esci": "Logout",
        "argomento": "📚 What topic do you want a summary for?",
        "placeholder": "E.g.: photosynthesis, fractions, the French Revolution...",
        "crea_schema": "Create summary",
        "spinner_schema": "Preparing your summary...",
        "schema_titolo": "### 🗂️ Your summary",
        "chat_titolo": "### 💬 Got questions? Let's think together",
        "chat_input": "Type your question here...",
        "spinner_chat": "Thinking about how to guide you...",
    }
}

ISTRUZIONI_SCHEMA = {
    "it": """Sei un tutor per studenti, anche con dislessia.
Quando ti viene dato un argomento, crea uno SCHEMA chiaro e semplice:
- usa titoli brevi con emoji
- punti elenco corti (massimo 8-10 parole per punto)
- evita paragrafi lunghi
- usa una struttura ad albero: concetto principale, poi sotto-punti
- alla fine aggiungi una riga con 2-3 parole chiave da ricordare
Non aggiungere introduzioni: vai dritto al contenuto.
Se ti viene chiesto chi sei, rispondi onestamente che sei un tutor basato su intelligenza artificiale.""",
    "en": """You are a tutor for students, including those with dyslexia.
When given a topic, create a clear and simple SUMMARY:
- use short titles with emoji
- short bullet points (max 8-10 words each)
- avoid long paragraphs
- use a tree structure: main concept, then sub-points
- at the end add 2-3 key words to remember
Do not add introductions: go straight to the content.
If asked who you are, honestly say you are an AI-based tutor."""
}

ISTRUZIONI_TUTOR = {
    "it": """Sei un tutor socratico per studenti, anche con dislessia.
REGOLA FONDAMENTALE: non dare MAI la risposta diretta o la soluzione finale.
Invece:
- fai una domanda guida che aiuti lo studente a trovare la risposta da solo
- scomponi il problema in un passo piccolo alla volta
- usa frasi corte e semplici
- se lo studente è bloccato, dai un piccolo indizio, non la soluzione
- sii incoraggiante e paziente
Rispondi sempre in italiano, in modo breve (massimo 4-5 righe).
Se ti viene chiesto chi sei, rispondi onestamente che sei un tutor basato su intelligenza artificiale.""",
    "en": """You are a Socratic tutor for students, including those with dyslexia.
FUNDAMENTAL RULE: NEVER give the direct answer or final solution.
Instead:
- ask a guiding question to help the student find the answer themselves
- break the problem into one small step at a time
- use short and simple sentences
- if the student is stuck, give a small hint, not the solution
- be encouraging and patient
Always reply in English, briefly (max 4-5 lines).
If asked who you are, honestly say you are an AI-based tutor."""
}

firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
auth_fb = firebase.auth()
db = firebase.database()

st.set_page_config(page_title="Student Helper", page_icon="🎓", layout="centered")

st.markdown("""
<style>
html, body, [class*="css"] {
    font-size: 19px;
    line-height: 1.7;
    font-family: 'Atkinson Hyperlegible', 'Verdana', sans-serif;
    letter-spacing: 0.3px;
}
.stChatMessage { border-radius: 14px; }
</style>
""", unsafe_allow_html=True)

if "utente" not in st.session_state:
    st.session_state.utente = None
if "schema" not in st.session_state:
    st.session_state.schema = None
if "chat" not in st.session_state:
    st.session_state.chat = []
if "lingua" not in st.session_state:
    st.session_state.lingua = "it"

with st.sidebar:
    scelta = st.radio("🌍 Lingua / Language", ["Italiano", "English"], horizontal=True)
    st.session_state.lingua = "it" if scelta == "Italiano" else "en"

T = TESTI[st.session_state.lingua]
lingua = st.session_state.lingua

def rileva_provider(chiave):
    if chiave.startswith("sk-ant-"):
        return "anthropic"
    if chiave.startswith("gsk_"):
        return "groq"
    if chiave.startswith("sk-"):
        return "openai"
    return None

def chiedi(istruzioni_sistema, messaggi, provider, client, modello):
    if provider == "anthropic":
        risposta = client.messages.create(
            model=modello,
            max_tokens=1000,
            system=istruzioni_sistema,
            messages=messaggi,
        )
        return risposta.content[0].text
    else:
        risposta = client.chat.completions.create(
            model=modello,
            max_tokens=1000,
            messages=[{"role": "system", "content": istruzioni_sistema}] + messaggi,
        )
        return risposta.choices[0].message.content

if st.session_state.utente is None:
    st.title(T["titolo"])
    schede = st.tabs([T["accedi"], T["registrati"], T["reset"]])

    with schede[0]:
        email_login = st.text_input(T["email"], key="email_login")
        pw_login = st.text_input(T["password"], type="password", key="pw_login")
        if st.button(T["btn_accedi"], type="primary", key="btn_login"):
            try:
                utente = auth_fb.sign_in_with_email_and_password(email_login, pw_login)
                if utente and "idToken" in utente:
                    st.session_state.utente = utente
                    st.rerun()
                else:
                    time.sleep(2)
                    st.error(T["login_err"])
            except Exception as e:
                msg = str(e)
                if "INVALID_LOGIN_CREDENTIALS" not in msg:
                    try:
                        time.sleep(2)
                        utente = auth_fb.sign_in_with_email_and_password(email_login, pw_login)
                        st.session_state.utente = utente
                        st.rerun()
                    except:
                        st.error(T["login_err"])
                else:
                    time.sleep(2)
                    st.error(T["login_err"])

    with schede[1]:
        email_reg = st.text_input(T["email"], key="email_reg")
        pw_reg = st.text_input(T["password"], type="password", key="pw_reg")
        api_key_reg = st.text_input(T["chiave_api"], type="password", key="api_reg")
        if st.button(T["btn_registrati"], type="primary", key="btn_reg"):
            if not email_reg or not pw_reg or not api_key_reg:
                st.warning(T["reg_vuota"])
            elif rileva_provider(api_key_reg) is None:
                st.error(T["reg_chiave_err"])
            else:
                try:
                    utente = auth_fb.create_user_with_email_and_password(email_reg, pw_reg)
                    uid = utente["localId"]
                    token = utente["idToken"]
                    db.child("utenti").child(uid).child("api_key").set(api_key_reg, token)
                    st.success(T["reg_ok"])
                except:
                    st.error(T["reg_err"])

    with schede[2]:
        email_reset = st.text_input(T["email"], key="email_reset")
        if st.button(T["btn_reset"], type="primary", key="btn_reset"):
            if not email_reset:
                st.warning(T["reset_vuota"])
            else:
                try:
                    auth_fb.send_password_reset_email(email_reset)
                    st.success(T["reset_ok"])
                except:
                    st.error(T["reset_err"])

else:
    utente = st.session_state.utente
    uid = utente["localId"]
    token = utente["idToken"]

    dati = db.child("utenti").child(uid).child("api_key").get(token)
    api_key = dati.val()

    if not api_key:
        st.error(T["chiave_mancante"])
        st.stop()

    provider = rileva_provider(api_key)

    if provider == "anthropic":
        client = Anthropic(api_key=api_key)
        modello = "claude-sonnet-4-6"
    elif provider == "groq":
        client = Groq(api_key=api_key)
        modello = "llama-3.3-70b-versatile"
    else:
        client = OpenAI(api_key=api_key)
        modello = "gpt-4o"

    with st.sidebar:
        st.markdown(f"👤 {utente['email']}")
        if st.button(T["esci"]):
            st.session_state.utente = None
            st.session_state.schema = None
            st.session_state.chat = []
            st.rerun()

    st.title(T["titolo"])
    st.caption(T["caption"])

    argomento = st.text_input(T["argomento"], placeholder=T["placeholder"])

    if st.button(T["crea_schema"], type="primary") and argomento:
        with st.spinner(T["spinner_schema"]):
            testo_schema = chiedi(
                ISTRUZIONI_SCHEMA[lingua],
                [{"role": "user", "content": argomento}],
                provider, client, modello
            )
        st.session_state.schema = testo_schema
        st.session_state.chat = []

    if st.session_state.schema:
        st.markdown(T["schema_titolo"])
        with st.container(border=True):
            st.markdown(st.session_state.schema)

        st.divider()
        st.markdown(T["chat_titolo"])

        for messaggio in st.session_state.chat:
            with st.chat_message(messaggio["role"]):
                st.markdown(messaggio["content"])

        domanda = st.chat_input(T["chat_input"])

        if domanda:
            st.session_state.chat.append({"role": "user", "content": domanda})
            with st.chat_message("user"):
                st.markdown(domanda)

            contesto = f"Schema:\n{st.session_state.schema}\n\nDomanda: {domanda}"

            with st.chat_message("assistant"):
                with st.spinner(T["spinner_chat"]):
                    risposta = chiedi(
                        ISTRUZIONI_TUTOR[lingua],
                        st.session_state.chat[:-1] + [{"role": "user", "content": contesto}],
                        provider, client, modello
                    )
                    st.markdown(risposta)

            st.session_state.chat.append({"role": "assistant", "content": risposta})
