import streamlit as st
import pyrebase
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

firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
auth = firebase.auth()
db = firebase.database()

st.set_page_config(page_title="Student Helper", page_icon="🧩", layout="centered")

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

ISTRUZIONI_SCHEMA = """Sei un tutor per studenti, anche con dislessia.
Quando ti viene dato un argomento, crea uno SCHEMA chiaro e semplice:
- usa titoli brevi con emoji
- punti elenco corti (massimo 8-10 parole per punto)
- evita paragrafi lunghi
- usa una struttura ad albero: concetto principale, poi sotto-punti
- alla fine aggiungi una riga con 2-3 parole chiave da ricordare
Non aggiungere introduzioni tipo "Ecco lo schema": vai dritto al contenuto.
Se ti viene chiesto chi sei o come funzioni, rispondi onestamente che sei un tutor basato su intelligenza artificiale."""

ISTRUZIONI_TUTOR = """Sei un tutor socratico per studenti, anche con dislessia.
REGOLA FONDAMENTALE: non dare MAI la risposta diretta o la soluzione finale.
Invece:
- fai una domanda guida che aiuti lo studente a trovare la risposta da solo
- scomponi il problema in un passo piccolo alla volta
- usa frasi corte e semplici
- se lo studente è bloccato, dai un piccolo indizio, non la soluzione
- sii incoraggiante e paziente
Rispondi sempre in italiano, in modo breve (massimo 4-5 righe).
Se ti viene chiesto chi sei o come funzioni, rispondi onestamente che sei un tutor basato su intelligenza artificiale."""

if st.session_state.utente is None:
    st.title("🧩 Student Helper")

    scheda = st.tabs(["Accedi", "Registrati", "Reset password"])

    with scheda[0]:
        st.subheader("Accedi")
        email_login = st.text_input("Email", key="email_login")
        pw_login = st.text_input("Password", type="password", key="pw_login")
        if st.button("Accedi", type="primary", key="btn_login"):
            try:
                utente = auth.sign_in_with_email_and_password(email_login, pw_login)
                st.session_state.utente = utente
                st.rerun()
            except:
                st.error("Email o password errati.")

    with scheda[1]:
        st.subheader("Crea account")
        email_reg = st.text_input("Email", key="email_reg")
        pw_reg = st.text_input("Password", type="password", key="pw_reg")
        api_key_reg = st.text_input("La tua chiave API", type="password", key="api_reg")
        if st.button("Registrati", type="primary", key="btn_reg"):
            if not email_reg or not pw_reg or not api_key_reg:
                st.warning("Compila tutti i campi.")
            elif rileva_provider(api_key_reg) is None:
                st.error("Formato chiave API non riconosciuto.")
            else:
                try:
                    utente = auth.create_user_with_email_and_password(email_reg, pw_reg)
                    uid = utente["localId"]
                    token = utente["idToken"]
                    db.child("utenti").child(uid).child("api_key").set(api_key_reg, token)
                    st.success("Account creato! Ora accedi.")
                except:
                    st.error("Errore durante la registrazione. Email già in uso?")

    with scheda[2]:
        st.subheader("Reset password")
        email_reset = st.text_input("Email", key="email_reset")
        if st.button("Invia email di reset", type="primary", key="btn_reset"):
            if not email_reset:
                st.warning("Inserisci la tua email.")
            else:
                try:
                    auth.send_password_reset_email(email_reset)
                    st.success("Email inviata! Controlla la tua casella.")
                except:
                    st.error("Email non trovata.")

else:
    utente = st.session_state.utente
    uid = utente["localId"]
    token = utente["idToken"]

    dati = db.child("utenti").child(uid).child("api_key").get(token)
    api_key = dati.val()

    if not api_key:
        st.error("Chiave API non trovata nel tuo account.")
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
        if st.button("Esci"):
            st.session_state.utente = None
            st.session_state.schema = None
            st.session_state.chat = []
            st.rerun()

    st.title("🧩 Student Helper")
    st.caption("Scegli un argomento, ottieni uno schema chiaro, poi fai domande: ti guido a ragionare, non ti do la soluzione pronta.")

    argomento = st.text_input("📚 Su quale argomento vuoi uno schema?", placeholder="Es: la fotosintesi, le frazioni, la Rivoluzione francese...")

    if st.button("Crea schema", type="primary") and argomento:
        with st.spinner("Sto preparando lo schema..."):
            testo_schema = chiedi(
                ISTRUZIONI_SCHEMA,
                [{"role": "user", "content": f"Argomento: {argomento}"}],
                provider, client, modello
            )
        st.session_state.schema = testo_schema
        st.session_state.chat = []

    if st.session_state.schema:
        st.markdown("### 🗂️ Il tuo schema")
        with st.container(border=True):
            st.markdown(st.session_state.schema)

        st.divider()
        st.markdown("### 💬 Hai domande? Ragioniamo insieme")

        for messaggio in st.session_state.chat:
            with st.chat_message(messaggio["role"]):
                st.markdown(messaggio["content"])

        domanda = st.chat_input("Scrivi qui la tua domanda...")

        if domanda:
            st.session_state.chat.append({"role": "user", "content": domanda})
            with st.chat_message("user"):
                st.markdown(domanda)

            contesto = f"Lo schema su cui sta studiando lo studente:\n{st.session_state.schema}\n\nDomanda dello studente: {domanda}"

            with st.chat_message("assistant"):
                with st.spinner("Sto pensando a come guidarti..."):
                    risposta = chiedi(
                        ISTRUZIONI_TUTOR,
                        st.session_state.chat[:-1] + [{"role": "user", "content": contesto}],
                        provider, client, modello
                    )
                    st.markdown(risposta)

            st.session_state.chat.append({"role": "assistant", "content": risposta})
