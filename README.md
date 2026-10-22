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
- **Algorithmic thinking**: how fast is the code? Can it be faster?
- **Algorithms**: classic problems such as searching and sorting.
- **Logic problems**: true/false puzzles and reasoning.

There are 302 questions in total.

## How it works

1. **Sign in** with GitHub or Google.
2. **Pick a language.** If you are new, you start with Fundamentals at level 1.
3. **Answer in your own words.** Say what the code does and why.
4. **Read your feedback.** You see what you got right, what you missed, and a model answer.

The app adapts to you. It gives you more questions on the skills you find hardest, and harder questions as you improve.
Once you have cleared Fundamentals, every topic opens up.
Turn on **Focus: Fundamentals** on the practice page if you only want the basics.

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
│   ├── app/content/    All the questions and their answer keys
│   ├── app/services/   Picks your next question and tracks your progress
│   ├── app/ai/         The graders (offline and AI model)
│   └── tests/          Automatic tests
├── frontend/           The website (Next.js)
│   └── src/app/        One folder per page: practice, progress, feedback, login
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
