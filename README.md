<p align="center">
  <img src="frontend/public/logo.svg" width="72" height="72" alt="Vexalith logo" />
</p>

<h1 align="center">Vexalith</h1>
<p align="center"><strong>Build Logic. Break Limits.</strong></p>

Vexalith is a free practice app for learning to think like a programmer.
You read a short piece of code, explain what it does, and get feedback on your answer.
It checks two things: whether your answer is right, and whether your reasoning makes sense.

**Live demo:** <https://vexalith-app.vercel.app>

![A beginner question on the practice page](docs/screenshots/practice-fundamentals-desktop.png)

## What you can practice

**Languages**

- Python
- JavaScript
- PHP
- C++ (modern C++17: from your first `cout` to pointers, classes, the STL and smart pointers)
- Java (modern Java 17: from your first `System.out.println` to `String` vs `.equals()`, collections, exceptions and OOP)
- HTML
- CSS
- General (no code needed: logic puzzles, binary numbers, step-by-step problem solving)

**Topics** (each has 3 levels: beginner, intermediate, advanced)

- **Fundamentals**: the basics, from your very first variable. New learners start here.
- **Code tracing**: predict what the code prints.
- **Debugging**: find the mistake and fix it.
- **Edge cases and testing**: find the input that breaks the code.
- **Code review**: suggest how to make the code better.
- **Data structures**: pick the right container (list, dictionary, set and more).
- **Object-Oriented Programming (OOP)**: classes, constructors, encapsulation (`private`/`public`, getters/setters), inheritance (`super`/`extends`), polymorphism, abstract classes vs interfaces, `static` vs instance members, and composition vs inheritance.
- **Algorithmic thinking**: how fast is the code? Can it be faster?
- **Algorithms**: classic problems such as searching and sorting.
- **Logic problems**: true/false puzzles and reasoning.

**Two kinds of questions**

- **Explain it**: read the code and say what it does and why (most questions).
- **Fill in the missing code**: part of the code is hidden behind a highlighted **?** slot. Type the line, expression, tag or property that belongs there. Equivalent answers count (spacing, quote style and a trailing `;` don't matter), so `i<3;` is as good as `i < 3`.

There are also plenty of **loop** drills in every language: `for`, `while`, `do-while`, nested loops, `break` and `continue`, "what does this print?" and off-by-one bugs.

There are 536 questions in total across 8 language tracks and 10 skill domains, including 67 for Java, 79 for C++, 58 Object-Oriented Programming questions, 56 fill-in-the-missing-code questions and 33 loop drills.

## How it works

1. **Sign in** with GitHub or Google.
2. **Pick a language and a level.** If you are new, you start with Fundamentals at level 1.
   The **Level** switch under the languages has four choices:
   - **Adaptive** (the default): the app picks the level from your results.
   - **Beginner**, **Intermediate** or **Advanced**: you only get questions at that level.
   You can also filter by **Topic** (such as **OOP**, **Fundamentals**, **Debugging** or **Data Structures**) using the Topic row under the level selector. Your choices are remembered as you skip or advance.
3. **Answer in your own words.** Say what the code does and why.
   Every question is written in plain words and ends with a **Your task** line that says exactly what to do
   (for example *"write the exact output first, then say why, pointing at the lines that cause it"*). Above the
   answer box, the small **How to answer** box adds only what the task line doesn't: what to look for in the code
   and, for fill-in-the-missing-code questions, what counts as a right answer. You can fold it away.
   Write the way you talk. The grader understands casual answers: contractions (*doesn't*, *didnt*), everyday
   words (*"it spits out five"*, *"cuz"*, *"the loop never ends"*), number words and small typos (*"varible"*).
   A casual answer with the right ideas scores about the same as a polished one; an answer that is off topic still fails.
   You can write in **English, Filipino (Tagalog) or Taglish** (a mix of both), for example:
   *"Nagpi-print siya ng 5 kasi copy lang ng value ang nakuha ng y."*
   The grader checks your ideas, not your language, so the same explanation gets about the same score in any of the three.
   Keep code (like `i < 5` or `acc.append(x)`) as you would type it.
   Stuck? Press **Show hint**. Every question has 3 hints, shown one at a time: first a way to approach it, then the key idea, then the point your answer must make. Each hint takes 10% off that answer's score (30% at most).
4. **Read your feedback.** It is written like a friendly tutor talking to you ("You're on the right track. You got 1 of the 3 key points..."). Right or wrong, you get an explanation: the key concept, one checklist of everything a full answer covers (ticked where you got it, open where something is still missing), any common mistake you made and why it's wrong, and the model answer. Points already shown in the checklist aren't repeated in the other notes. For fill-in-the-missing-code questions you also see the correct code.
   If you answered in Filipino or Taglish, the feedback says so ("Tinanggap ang sagot mo sa Filipino") and its headings switch to Filipino. Use the **English / Filipino** switch on the feedback to choose; your browser remembers it. The rubric points and the model answer stay in English.

The app adapts to you. It gives you more questions on the skills you find hardest, and harder questions as you improve.
Once you have cleared Fundamentals, every topic opens up.
Turn on **Focus: Fundamentals** on the practice page if you only want the basics.

**Daily challenge.** Open **Daily** in the menu. There is one question a day, the same for everyone. It changes at midnight Manila time (Asia/Manila, UTC+8), and the language changes every day. Answer it to complete the day. Do it on consecutive days to build a **streak**; your current and best streak appear on the Daily and Progress pages.

**Your progress page** shows:
- how many questions you solved, your accuracy and your average score;
- a chart of your score over the last 30 days, with how much you improved;
- your mastery per skill (with how many attempts) and per language;
- your recent answers;
- your daily streak, plus how many questions you skipped and how many hints you used.

**Recommended for you.** Your progress page (and the home page, once you are signed in) suggests what to do next:
- your 3 weakest skills, each with a **Practise** button that opens questions on just that topic;
- a few questions you haven't seen yet, at a level that suits you;
- any language where your average score is below your overall average.

## Write and run code

Open **Code** in the menu to write real code and test it. There are 57 small exercises:
12 in Python, 12 in JavaScript and 11 each in C++, Java and PHP. They go from
beginner (add up a list, reverse a word, FizzBuzz) to advanced (binary search, flatten nested lists).
Topics: loops, strings, conditions, lists and sets, dictionaries/maps, hash maps, math, recursion and searching.

1. Pick a language with the tabs at the top (your choice is remembered).
2. Open an exercise. **Your task** says what the function must do; the example tests show inputs and the right answers.
3. Write the function in the editor. Your draft is saved in your browser, and **Reset** brings back the starter code.
4. Press **Run examples** (or Ctrl + Enter) to try the example tests. Anything you print shows up under each test.
5. Press **Submit** to also run the hidden tests. Pass them all and the exercise is marked solved on your progress.

When a test fails you see what was expected, what your code returned and a short tip. A compile error is shown once, with the line number.

**Stuck? Use "How to solve it"** (under the example tests; on a phone it sits above the editor):

- **Hints**: up to 3, shown one at a time. The first is a nudge, the second the key idea, the third the technique to use.
  Exercises aren't scored, so hints are free.
- **Explanation**: opens by itself when you pass every test. It explains the problem in general terms, not line by line:
  *the idea* behind it, *the approach* in a few steps, *what to watch out for* (common mistakes and edge cases) and
  *the pattern* you can reuse on similar problems, plus a short reference solution to compare with yours.
- **Show solution**: opens the explanation and reference solution early. After you've run your code it opens straight away;
  before your first try it asks *"Are you sure?"* first. If you see the solution before passing, the exercise shows as
  **Solved with help**.

**Your code runs in your own browser, never on our server.** It's free for everyone: no paid services and no keys.
Each language's engine is downloaded from a public CDN only when you first pick that language, and your browser keeps it for next time:

| Language | Engine | Download the first time | License |
|---|---|---|---|
| JavaScript | your browser, in a locked-down Web Worker | nothing | – |
| Python | [Pyodide](https://pyodide.org) 0.29 (CPython in WebAssembly) | about 5 MB | MPL-2.0 |
| PHP | [php-wasm](https://github.com/seanmorris/php-wasm) 0.2 (PHP 8.4 in WebAssembly) | about 3 MB | Apache-2.0 (or GPL-2.0) |
| C++ | [YoWASP Clang](https://yowasp.org) (Clang/LLVM compiled to WebAssembly), C++17 | about 23 MB | ISC; LLVM is Apache-2.0 with LLVM exception |
| Java | [CheerpJ](https://cheerpj.com) 4.3 running OpenJDK's `javac` | about 20 MB | CheerpJ Community License (free for personal and open-source use, with credit); OpenJDK tools are GPL-2.0 with Classpath Exception |

How it stays safe and fast:

- JavaScript, Python and PHP run in a **Web Worker** (a background thread) with network access switched off
  (`fetch`, `XMLHttpRequest`, `WebSocket`, `importScripts` and similar are removed before your code starts).
- C++ is compiled to WebAssembly and run in its own worker. The program can only print; it gets no files or network.
- Java runs through CheerpJ in a hidden frame. Every loop gets a tiny time check, so an endless loop stops cleanly.
- **Each test has a time limit** (4 seconds, 6 for Java). If your code takes longer, it's stopped
  ("Is there a loop that never ends?") and the remaining tests are skipped.
- **Hidden tests stay secret.** Your browser only gets their inputs. It sends your outputs to the server,
  which compares them with the right answers it keeps to itself. `3.0` and `3` count as the same answer.

CheerpJ is made by [Leaning Technologies](https://leaningtech.com) and used here under its free
[Community License](https://cheerpj.com/docs/licensing). If you run a copy of Vexalith for a company, check that license first.

## Run it on your computer

### What you need

- [Python 3.11 or newer](https://www.python.org/downloads/): runs the backend (the server that stores questions and grades answers).
- [Node.js 18 or newer](https://nodejs.org/) (20 recommended): runs the frontend (the website you click around in).
- [Git](https://git-scm.com/downloads): downloads the code.

You do **not** need any API keys. Without one, answers are graded by a built-in offline grader.

### 1. Download the code

Copy the project to your computer:

```bash
git clone <repository-url> vexalith
```

Go into the project folder:

```bash
cd vexalith
```

### 2. Start the backend

Go into the backend folder:

```bash
cd backend
```

Create a virtual environment (a private folder for this project's Python packages):

```bash
python3 -m venv .venv
```

Turn it on (on Windows use `.venv\Scripts\activate` instead):

```bash
source .venv/bin/activate
```

Install the packages the backend needs:

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

Create a settings file with a random secret (the frontend uses the same secret to talk to the backend):

```bash
echo "BACKEND_JWT_SECRET=$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')" > .env
```

Start the server. It runs at <http://localhost:8000> and creates a small local database on first start:

```bash
uvicorn app.main:app --reload
```

Leave this window open.

### 3. Start the frontend

Open a **second** terminal window in the project folder, then go into the frontend folder:

```bash
cd frontend
```

Install the packages the website needs:

```bash
npm install
```

Create the website's settings file. It copies the backend's secret and adds a new one for sign-in:

```bash
grep BACKEND_JWT_SECRET ../backend/.env > .env.local
echo "AUTH_SECRET=$(node -e "console.log(require('crypto').randomBytes(48).toString('base64'))")" >> .env.local
echo "BACKEND_URL=http://localhost:8000" >> .env.local
echo "AUTH_URL=http://localhost:3000" >> .env.local
```

Start the website:

```bash
npm run dev
```

Open <http://localhost:3000> in your browser.

### 4. Turn on sign-in

You need to sign in to practice. To make sign-in work on your computer, create a free GitHub OAuth app. This is the "Sign in with GitHub" button setup:

1. Go to <https://github.com/settings/developers> and click **New OAuth App**.
2. Set **Homepage URL** to `http://localhost:3000`.
3. Set **Authorization callback URL** to `http://localhost:3000/api/auth/callback/github`.
4. Create the app, then generate a client secret.
5. Add both values to `frontend/.env.local`:

```bash
AUTH_GITHUB_ID=your-client-id
AUTH_GITHUB_SECRET=your-client-secret
```

Restart `npm run dev`. The login page now shows **Continue with GitHub**.

### Optional: smarter feedback with an AI model

Vexalith can use an AI model (xAI Grok) to write more detailed feedback. Add your key to `backend/.env` and restart the backend:

```bash
XAI_API_KEY=your-xai-key
```

If the key is missing or the model has a problem, the offline grader takes over automatically.

### Run the tests

In the backend folder, with the virtual environment turned on:

```bash
pytest -q
```

## Project folders

```
vexalith/
├── backend/            The server (Python, FastAPI)
│   ├── app/content/    All the questions and their answer keys, the coding exercises and their hints/explanations
│   ├── app/services/   Picks your next question and tracks your progress
│   ├── app/ai/         The graders (offline and AI model)
│   └── tests/          Automatic tests
├── frontend/           The website (Next.js)
│   ├── src/app/        One folder per page: practice, code, daily, progress, feedback, login
│   ├── src/lib/runner* The in-browser code runners (one file per language)
│   └── public/runners/ The page that hosts the Java runner
├── docs/               Screenshots and advanced documentation
└── scripts/            Small helper scripts
```

## Tech used

- **Python + FastAPI**: the backend web server.
- **SQLAlchemy**: saves data to the database (SQLite on your computer, Postgres online).
- **Next.js + React**: the website.
- **TypeScript**: JavaScript with type checking, used for the website code.
- **Tailwind CSS**: styling for the website.
- **Auth.js**: "Sign in with GitHub/Google".
- **pytest**: runs the backend tests.
- **Vercel + Neon**: hosting for the live demo (Neon provides the Postgres database).

## Common problems

**"Address already in use" or "port 3000/8000 is in use"**
Another program is using that port. Close it, or use a different port:
`uvicorn app.main:app --reload --port 8001` (then set `BACKEND_URL=http://localhost:8001` in `frontend/.env.local`),
or `npm run dev -- -p 3001` (then set `AUTH_URL=http://localhost:3001` and update your GitHub OAuth app URLs).

**`npm install` fails**
Check your Node.js version with `node -v`. It must be 18 or newer. Then delete the `node_modules` folder and run `npm install` again.

**The login page says sign-in isn't configured**
You haven't added the GitHub values yet. Follow [step 4](#4-turn-on-sign-in), then restart `npm run dev`.

**"Could not load question" or a 401 error after signing in**
`BACKEND_JWT_SECRET` must be exactly the same in `backend/.env` and `frontend/.env.local`. Restart both after changing it.

**A Code exercise says "Downloading…" for a long time**
The C++ and Java engines are about 20 MB each. The first download can take a minute on a slow connection; after that your browser keeps them.
If it never finishes, check that your network allows `cdn.jsdelivr.net`, `unpkg.com` and `cjrtnc.leaningtech.com`, then reload.

**`python3` or `pip` not found**
On Windows try `py` instead of `python3`. Make sure you turned on the virtual environment first.

## Contributing

1. Fork this repository (make your own copy on GitHub).
2. Create a branch for your change: `git checkout -b my-change`.
3. Make your change, then run the tests (`pytest -q`) and `npm run build`.
4. Push your branch and open a pull request that explains what you changed and why.

Ideas are welcome too: use the **Feedback** page in the app.

More technical details (architecture, API, deployment, settings): [docs/ADVANCED.md](docs/ADVANCED.md).

## License

[MIT](LICENSE): free to use, change and share.
