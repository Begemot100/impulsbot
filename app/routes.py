from flask import Blueprint, request, session, jsonify, render_template_string, redirect
from .chat_ui import CHAT_HTML
from .assistant import ImpulsAssistant

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return redirect("/chat")

@main.route("/chat", methods=["GET"])
def chat():
    session.clear()
    return render_template_string(CHAT_HTML)

@main.route("/chat-message", methods=["POST"])
def chat_message():
    user_msg = request.json.get("message", "")
    assistant = ImpulsAssistant()
    reply = assistant.process_message(user_msg)
    return jsonify({"response": reply})