from flask import Blueprint, render_template, request, jsonify
import requests as http_requests
from config import Config
from flask_login import login_required

chatbot_bp = Blueprint("chatbot", __name__, url_prefix="/chat")

# Docker Model Runner configuration
# LOCAL_MODEL_BASE_URL = getattr(Config, "LOCAL_MODEL_BASE_URL", "http://localhost:12434")
LOCAL_MODEL_BASE_URL = "http://localhost:12434"
LOCAL_MODEL_NAME = getattr(Config, "LOCAL_MODEL_NAME", "ai/gemma3-qat:latest")

# System prompt to give the model context
SYSTEM_PROMPT = (
    "You are a helpful AI assistant for a Smart Classroom platform. "
    "You help students and teachers with their questions about courses, "
    "assignments, study tips, and general academic queries. "
    "Keep your answers concise and helpful."
)


@chatbot_bp.route("/", methods=["GET"])
@login_required
def chat_interface():
    """Renders the main chatbot interface."""
    return render_template("chatbot/chat.html")


@chatbot_bp.route("/api/message", methods=["POST"])
@login_required
def send_message():
    """API endpoint to handle AJAX chat messages via local Docker Model Runner."""
    data = request.json
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "No message provided."}), 400

    try:
        # Build the chat history from the request (if provided)
        history = data.get("history", [])
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in history:
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        messages.append({"role": "user", "content": user_message})

        # Call the local model via OpenAI-compatible API
        api_url = f"{LOCAL_MODEL_BASE_URL}/engines/llama.cpp/v1/chat/completions"
        payload = {
            "model": LOCAL_MODEL_NAME,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024,
        }

        resp = http_requests.post(api_url, json=payload, timeout=120)
        resp.raise_for_status()

        result = resp.json()
        assistant_text = result["choices"][0]["message"]["content"]
        return jsonify({"text": assistant_text})

    except http_requests.exceptions.ConnectionError:
        return jsonify({"error": "Cannot connect to the local AI model. Is Docker Model Runner running on port 12434?"}), 503
    except http_requests.exceptions.Timeout:
        return jsonify({"error": "The AI model took too long to respond. Please try again."}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500
