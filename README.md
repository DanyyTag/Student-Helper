

<img width="259" height="226" alt="SchoolHelper-removebg-preview" src="https://github.com/user-attachments/assets/4978d376-a4b4-4e19-bfdd-7f69120532bb" />

---

# Student Helper

I'm dyslexic, and I made this web app for other dyslexic students (and anyone else who wants to use it).

Basically it won't give you the answer. You choose a topic, you get a short summary that's easy to read, and then you can ask questions. The tutor answers with hints and questions to make you think. Never the solution.

I kept the design simple on purpose: big text, short bullet points, nothing cluttered. Reading long walls of text is a pain for me, so I built it the way I'd want it.

---

## Try it online

https://student-helper-rouge-five.vercel.app/

Nothing to install. Open the link, make an account, done.

---

## Features

1. Structured topic summaries that are easy to read
2. A Socratic tutor that guides you and never gives the answer away
3. Login with Firebase, so you sign up once and your API key is saved securely
4. Password reset by email
5. Italian and English
6. Works with Anthropic, OpenAI and Groq APIs
7. Designed by a dyslexic for dyslexics

---

## Run it locally

1. Clone the repo
2. Install what you need:
```
pip install flask anthropic openai groq
```
3. Start it:
```
flask --app api/index.py run
```
4. Go to http://localhost:5000

---

## Bug reports

Found a bug? Open an issue from the Issues tab up there.

If you can, tell me:

1. What you were doing
2. What you thought would happen
3. What happened instead
4. Browser and OS, if you think it matters

The more you tell me, the quicker I can fix it. Even tiny bugs are fine, I want to know about them.

---

## Login problem

Sometimes you'll see "wrong email or password" even though they're right. Just click login again. The free database is slow to wake up the first time.

---

## IEP

Since the app only guides you and never solves things for you, it can be used as a compensatory or dispensatory tool. It depends on your country's laws, your school's rules and your IEP (Individualized Education Program, the personal plan students with learning disabilities like dyslexia get). You still do the thinking, the app just helps you get there.

---

## About

I'm a dyslexic student and I wanted a tool that actually fits how my brain works, so I made one.

Got ideas or feedback? Or just want to say hi? Open an issue. 
Thanks, bye❤️

