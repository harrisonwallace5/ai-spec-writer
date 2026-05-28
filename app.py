import os
import re
import uuid

import anthropic
from dotenv import load_dotenv
from flask import Flask, Response, abort, render_template, request


load_dotenv()

app = Flask(__name__)

CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
SECTION_HEADERS = [
    "OVERVIEW",
    "DIMENSIONS AND TOLERANCES",
    "MATERIALS",
    "MANUFACTURING PROCESS",
    "QUALITY REQUIREMENTS",
    "STANDARDS AND COMPLIANCE",
]
SYSTEM_PROMPT = (
    "You are a senior mechanical/manufacturing engineer. Generate a complete "
    "technical specification for the following part. Your response must include "
    "exactly these 6 sections with these exact headers on their own lines: "
    "OVERVIEW, DIMENSIONS AND TOLERANCES, MATERIALS, MANUFACTURING PROCESS, "
    "QUALITY REQUIREMENTS, STANDARDS AND COMPLIANCE. Be specific with numbers, "
    "tolerances, material grades, and standards (ISO, ASTM, ASME, DIN, etc.)"
)
GENERATED_SPECS = {}


def api_key_error_message():
    return (
        "ANTHROPIC_API_KEY is not set. Add it to your environment or .env file "
        "before generating a specification."
    )


def normalize_header(line):
    cleaned = re.sub(r"^[#>*\-\s]+", "", line.strip())
    cleaned = re.sub(r"^\d+\s*[\.\)]\s*", "", cleaned)
    return cleaned.rstrip(":").strip().upper()


def extract_message_text(message):
    parts = []
    for block in getattr(message, "content", []):
        if getattr(block, "type", "") != "text":
            continue
        text = getattr(block, "text", "").strip()
        if text:
            parts.append(text)
    return "\n\n".join(parts).strip()


def parse_spec_sections(spec_text):
    section_map = {header: [] for header in SECTION_HEADERS}
    current_header = None

    for raw_line in spec_text.splitlines():
        normalized = normalize_header(raw_line)
        if normalized in section_map:
            current_header = normalized
            continue
        if current_header:
            section_map[current_header].append(raw_line.rstrip())

    if not any(section_map.values()):
        return [{"header": "GENERATED SPECIFICATION", "content": spec_text.strip()}]

    return [
        {
            "header": header,
            "content": "\n".join(section_map[header]).strip()
            or "No content generated for this section.",
        }
        for header in SECTION_HEADERS
    ]


def build_user_prompt(description):
    return (
        "Part description:\n"
        f"{description}\n\n"
        "Generate a full technical specification in plain text. Use exactly the "
        "six required headers, each on its own line, and do not add any extra "
        "sections, title, introduction, or conclusion."
    )


def generate_specification(description):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(api_key_error_message())

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=2200,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_prompt(description)}],
    )
    spec_text = extract_message_text(message)
    if not spec_text:
        raise RuntimeError("Claude returned an empty response. Please try again.")
    return spec_text


def render_index(description="", error=None, status_code=200):
    warning = None
    if not os.environ.get("ANTHROPIC_API_KEY"):
        warning = api_key_error_message()
        if warning == error:
            warning = None

    return (
        render_template(
            "index.html",
            description=description,
            error=error,
            api_key_warning=warning,
        ),
        status_code,
    )


@app.get("/")
def index():
    return render_index(status_code=200)


@app.post("/generate")
def generate():
    description = request.form.get("description", "").strip()
    if not description:
        return render_index(
            description=description,
            error="Please describe the part or product you want specified.",
            status_code=400,
        )

    try:
        spec_text = generate_specification(description)
    except RuntimeError as exc:
        return render_index(description=description, error=str(exc), status_code=500)
    except Exception as exc:
        app.logger.exception("Claude API request failed.")
        return render_index(
            description=description,
            error=f"Unable to generate the specification right now: {exc}",
            status_code=502,
        )

    spec_id = str(uuid.uuid4())
    GENERATED_SPECS[spec_id] = spec_text

    return render_template(
        "spec.html",
        spec_id=spec_id,
        spec_text=spec_text,
        sections=parse_spec_sections(spec_text),
    )


@app.get("/download/<spec_id>")
def download(spec_id):
    spec_text = GENERATED_SPECS.get(spec_id)
    if spec_text is None:
        abort(404, description="Specification not found.")

    response = Response(spec_text, mimetype="text/plain; charset=utf-8")
    response.headers["Content-Disposition"] = (
        f'attachment; filename="technical-specification-{spec_id}.txt"'
    )
    return response


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5050"))
    print(f"Running on http://127.0.0.1:{port}", flush=True)
    app.run(host="127.0.0.1", port=port, debug=False)
