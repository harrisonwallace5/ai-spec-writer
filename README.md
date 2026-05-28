# AI Spec Writer

AI Spec Writer is a Flask web app that turns a plain-language description of a product or engineering part into a structured technical specification using Claude. It is aimed at manufacturing, sourcing, prototyping, and engineering teams that need fast first-pass documentation for valves, brackets, enclosures, fittings, sensors, and similar components.

## What It Does

- Accepts a single part or product description from the browser
- Calls Anthropic Claude (`claude-3-5-sonnet-20241022`)
- Generates a specification with exactly six sections:
  - `OVERVIEW`
  - `DIMENSIONS AND TOLERANCES`
  - `MATERIALS`
  - `MANUFACTURING PROCESS`
  - `QUALITY REQUIREMENTS`
  - `STANDARDS AND COMPLIANCE`
- Renders each section in a clean card-based UI
- Stores the generated spec in memory and lets the user download it as `.txt`

## Project Structure

```text
ai_spec_writer/
├── app.py
├── templates/
│   ├── index.html
│   └── spec.html
├── static/
│   └── style.css
├── requirements.txt
├── README.md
└── .env.example
```

## How To Run Locally

1. Install dependencies:

```bash
pip3 install flask anthropic python-dotenv
```

2. Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY="your_api_key_here"
```

3. Optional: create a local `.env` file from the example:

```bash
cp .env.example .env
```

4. Start the app:

```bash
python3 app.py
```

5. Open:

```text
http://127.0.0.1:5050
```

## Deployment

### Railway

One-liner:

```bash
railway up
```

Set `ANTHROPIC_API_KEY` in the Railway dashboard and use a start command such as:

```bash
python3 -c "import os; from app import app; app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '5050')), debug=False)"
```

### Render

One-liner:

```bash
render deploy
```

Use:

- Build command: `pip3 install -r requirements.txt`
- Start command: `python3 -c "import os; from app import app; app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '5050')), debug=False)"`

### Fly.io

One-liner:

```bash
fly launch
```

After launch, set the secret and deploy:

```bash
fly secrets set ANTHROPIC_API_KEY=your_api_key_here
fly deploy
```

## How To Sell Or Monetize It

- Add Stripe subscriptions and charge per seat or per monthly document volume.
- Package it as a Gumroad or Lemon Squeezy download for small machine shops and industrial consultants.
- White-label it for manufacturing companies that want internal spec generation branded to their own process.
- Add admin reporting and usage tracking, then sell it as a lightweight internal engineering SaaS.

## How To Customize It

- Add more spec sections by editing `SECTION_HEADERS` and the Claude prompt in [app.py](/Users/awallace2023/jarvis_builds/ai_spec_writer/app.py).
- Change the Claude model by updating `CLAUDE_MODEL` in [app.py](/Users/awallace2023/jarvis_builds/ai_spec_writer/app.py).
- Add PDF export by rendering the spec into a print template and generating a PDF with a library such as WeasyPrint or ReportLab.
- Add persistence by replacing the in-memory `GENERATED_SPECS` dictionary with Redis, PostgreSQL, or another store.

## Notes

- The built-in Flask server is fine for local use and simple hosted deployments, but a production rollout should run behind a proper WSGI server or platform process manager.
- The in-memory download store resets on restart. That is intentional for this version and keeps the app simple.
- Claude output should be reviewed by a human before release in regulated or safety-critical environments.
