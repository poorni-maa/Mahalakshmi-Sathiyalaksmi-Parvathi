import json
import os
from typing import Any

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from google import genai
from google.genai import types


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.8-flash"
)


# Create Gemini client only when API key exists
client = None

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def check_gemini():
    """
    Make sure the Gemini API is configured.
    """

    if client is None:
        raise RuntimeError(
            "Gemini API key is missing. "
            "Please add GEMINI_API_KEY to your .env file."
        )


def generate_response(
    prompt: str,
    temperature: float = 0.7,
    max_output_tokens: int = 1500
) -> str:
    """
    Send a prompt to Gemini and return the generated text.
    """

    check_gemini()

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        ),
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return response.text.strip()


# ============================================================
# ASK QUESTION
# ============================================================

def ask_edugenie(question: str) -> str:

    prompt = f"""
You are EduGenie, an intelligent and friendly AI learning assistant.

A student has asked the following question:

{question}

Answer the question clearly.

Requirements:

1. Use simple student-friendly language.
2. Explain the concept instead of only giving a one-line answer.
3. Use examples when useful.
4. Break difficult concepts into smaller parts.
5. Do not make up facts.
6. If the question is academic, make the explanation educational.
7. Keep the response reasonably concise.

Student question:
{question}
"""

    return generate_response(prompt)


# ============================================================
# EXPLAIN TOPIC
# ============================================================

def explain_topic(topic: str) -> str:

    prompt = f"""
You are EduGenie, a personal AI tutor.

Explain the following topic to a student:

{topic}

Use the following structure:

Definition:
Give a simple definition.

Main Explanation:
Explain the concept in simple language.

Important Points:
Give the most important points as bullet points.

Example:
Give one simple example.

Quick Recap:
Give a short recap at the end.

Topic:
{topic}
"""

    return generate_response(prompt)


# ============================================================
# SUMMARIZE TEXT
# ============================================================

def summarize_text(text: str) -> str:

    prompt = f"""
You are EduGenie, an AI study assistant.

Summarize the following study material.

Requirements:

1. Keep the important information.
2. Remove unnecessary repetition.
3. Use simple student-friendly language.
4. Use bullet points where useful.
5. Do not add information that is not present in the original text.
6. Make the summary useful for exam preparation.

Study material:

{text}
"""

    return generate_response(prompt)


# ============================================================
# GENERATE QUIZ
# ============================================================

def generate_quiz(topic: str) -> list[dict[str, Any]]:

    prompt = f"""
You are EduGenie, an educational quiz generator.

Create exactly 5 multiple-choice questions about:

{topic}

Each question must contain:

- question
- options
- answer

Return ONLY valid JSON.

Use exactly this structure:

[
    {{
        "question": "Question here",
        "options": [
            "Option A",
            "Option B",
            "Option C",
            "Option D"
        ],
        "answer": "Option A"
    }}
]

Important rules:

1. Create exactly 5 questions.
2. Every question must have exactly 4 options.
3. The answer must exactly match one of the options.
4. Do not use Markdown.
5. Do not add explanations outside the JSON.
6. Questions should be educational and related to the requested topic.

Topic:

{topic}
"""

    raw_response = generate_response(
        prompt,
        temperature=0.4,
        max_output_tokens=2500
    )

    # Remove accidental Markdown code fences
    raw_response = raw_response.strip()

    if raw_response.startswith("```json"):
        raw_response = raw_response[7:]

    elif raw_response.startswith("```"):
        raw_response = raw_response[3:]

    if raw_response.endswith("```"):
        raw_response = raw_response[:-3]

    raw_response = raw_response.strip()

    quiz_data = json.loads(raw_response)

    if not isinstance(quiz_data, list):
        raise ValueError(
            "Gemini did not return a valid quiz."
        )

    valid_questions = []

    for question in quiz_data:

        if not isinstance(question, dict):
            continue

        question_text = str(
            question.get("question", "")
        ).strip()

        options = question.get("options", [])

        answer = str(
            question.get("answer", "")
        ).strip()

        if not question_text:
            continue

        if not isinstance(options, list):
            continue

        if len(options) != 4:
            continue

        options = [
            str(option).strip()
            for option in options
        ]

        if answer not in options:
            continue

        valid_questions.append(
            {
                "question": question_text,
                "options": options,
                "answer": answer,
            }
        )

    if len(valid_questions) < 5:
        raise ValueError(
            "Gemini did not return five valid questions. "
            "Please try again."
        )

    return valid_questions[:5]


# ============================================================
# LEARNING RECOMMENDATIONS
# ============================================================

def get_learning_recommendations(topic: str) -> str:

    prompt = f"""
You are EduGenie, a personal learning assistant.

Create a practical learning plan for:

{topic}

Include:

1. What the student should learn first.
2. Important subtopics.
3. A logical order for learning.
4. Practice activities.
5. Common mistakes to avoid.
6. Suggested resource types such as:
   - textbooks
   - documentation
   - videos
   - practice questions
   - projects

Do not invent specific URLs.

Keep the recommendations simple and useful for a student.

Topic:
{topic}
"""

    return generate_response(prompt)


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ============================================================
# ASK API
# ============================================================

@app.route(
    "/api/ask",
    methods=["POST"]
)
def api_ask():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        question = str(
            data.get("question", "")
        ).strip()

        if not question:

            return jsonify(
                {
                    "error":
                    "Please enter a question."
                }
            ), 400

        answer = ask_edugenie(
            question
        )

        return jsonify(
            {
                "answer": answer
            }
        )

    except Exception as error:

        return jsonify(
            {
                "error": str(error)
            }
        ), 500


# ============================================================
# EXPLAIN API
# ============================================================

@app.route(
    "/api/explain",
    methods=["POST"]
)
def api_explain():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        topic = str(
            data.get("topic", "")
        ).strip()

        if not topic:

            return jsonify(
                {
                    "error":
                    "Please enter a topic."
                }
            ), 400

        explanation = explain_topic(
            topic
        )

        return jsonify(
            {
                "explanation":
                explanation
            }
        )

    except Exception as error:

        return jsonify(
            {
                "error": str(error)
            }
        ), 500


# ============================================================
# SUMMARY API
# ============================================================

@app.route(
    "/api/summarize",
    methods=["POST"]
)
def api_summarize():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        text = str(
            data.get("text", "")
        ).strip()

        if not text:

            return jsonify(
                {
                    "error":
                    "Please paste some text."
                }
            ), 400

        summary = summarize_text(
            text
        )

        return jsonify(
            {
                "summary":
                summary
            }
        )

    except Exception as error:

        return jsonify(
            {
                "error": str(error)
            }
        ), 500


# ============================================================
# QUIZ API
# ============================================================

@app.route(
    "/api/quiz",
    methods=["POST"]
)
def api_quiz():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        topic = str(
            data.get("topic", "")
        ).strip()

        if not topic:

            return jsonify(
                {
                    "error":
                    "Please enter a quiz topic."
                }
            ), 400

        quiz = generate_quiz(
            topic
        )

        return jsonify(
            {
                "quiz": quiz
            }
        )

    except json.JSONDecodeError:

        return jsonify(
            {
                "error":
                "Gemini returned invalid quiz data. "
                "Please try again."
            }
        ), 500

    except Exception as error:

        return jsonify(
            {
                "error": str(error)
            }
        ), 500


# ============================================================
# RECOMMENDATIONS API
# ============================================================

@app.route(
    "/api/recommendations",
    methods=["POST"]
)
def api_recommendations():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        topic = str(
            data.get("topic", "")
        ).strip()

        if not topic:

            return jsonify(
                {
                    "error":
                    "Please enter a topic."
                }
            ), 400

        recommendations = (
            get_learning_recommendations(
                topic
            )
        )

        return jsonify(
            {
                "recommendations":
                recommendations
            }
        )

    except Exception as error:

        return jsonify(
            {
                "error": str(error)
            }
        ), 500


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route(
    "/api/health",
    methods=["GET"]
)
def health():

    return jsonify(
        {
            "status": "running",
            "gemini_configured":
                client is not None,
            "model":
                GEMINI_MODEL
        }
    )


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("EduGenie AI Learning Assistant")
    print("=" * 60)
    print()

    if client is None:
        print(
            "WARNING: GEMINI_API_KEY is not configured."
        )
        print(
            "Add your API key to the .env file."
        )
        print()

    print(
        "Open this URL in your browser:"
    )

    print(
        "http://127.0.0.1:5000"
    )

    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )