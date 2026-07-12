from flask import Blueprint, jsonify

ai_bp = Blueprint("ai", __name__)

@ai_bp.route("/status", methods=["GET"])
def status():
    return jsonify({
        "mode": "local",
        "version": "1.0.0",
        "tts": "browser_speech_synthesis",
        "stt": "browser_webkit_speech",
        "nlp": "spacy",
        "evaluator": "sentence_transformers",
        "question_gen": "template_local",
    }), 200
