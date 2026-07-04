Student Helper

Student Helper is a web app built by a dyslexic student, for dyslexic students and everyone else.

The idea is simple: instead of giving you the answer, it guides you to find it yourself. You pick a topic, get a clear and structured summary, then ask questions. The tutor responds with hints and guiding questions, never with direct solutions.

Designed with readability in mind, large text, short bullet points, clean layout, so it works well for everyone, especially students with dyslexia.

---

Try it online

https://student-hel-per.streamlit.app/

No installation needed, just open the link and create an account.

---

Features

1. Generates clear, structured topic summaries
2. Socratic tutor that guides your thinking and never gives the answer away
3. Firebase authentication so you sign up once and your API key is saved securely
4. Password reset via email
5. Available in Italian and English
6. Supports Anthropic, OpenAI and Groq APIs

---

Run it locally

1. Clone the repository
2. Install dependencies:
```
pip install streamlit anthropic openai groq pyrebase4
```
3. Run the app:
```
python -m streamlit run app_final2.py
```

---

Bug Reports

Found a bug? Open an issue on GitHub using the Issues tab at the top of this page.

When reporting a bug, try to include:

1. What you were doing when it happened
2. What you expected to happen
3. What actually happened
4. Your browser and operating system if relevant

The more detail you give, the faster it gets fixed. All reports are welcome, no bug is too small.

---

Note

If when logging in you get an error saying the email or password are wrong but you are sure they are correct, 
just click the login button one more time. 
The free database sometimes takes a moment to respond on the first attempt.

---

About

Built by a dyslexic student who wanted a tool that actually works the way dyslexic brains do.

If you have ideas, suggestions or just want to say hi, feel free to open an issue.
