from flask import Blueprint, request, jsonify
from services.processor import process_request
import logging

logger = logging.getLogger(__name__)
chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json(silent=True)
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON payload"}), 400

        message = data.get("message", "").strip()
        if not message:
            return jsonify({"error": "Field 'message' is required and cannot be empty."}), 400
        if len(message) > 1000:
            return jsonify({"error": "Text too long. Maximum 1000 characters allowed."}), 400

        result = process_request(message)
        return jsonify(result), 200

    except ValueError as e:
        logger.warning(f"VALIDATION_ERROR: {e}")
        return jsonify({"error": "Invalid request format"}), 400
    except Exception as e:
        logger.error(f"FALLBACK_TRIGGERED: {e}", exc_info=True)
        return jsonify({"error": "Service temporarily unavailable"}), 503