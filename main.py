import logging
import json
from flask import Flask, jsonify
from api.routes import chat_bp
from config.settings import get_config

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "ts": self.formatTime(record),
            "level": record.levelname,
            "msg": record.getMessage(),
            "module": record.module,
            "func": record.funcName
        }
        if record.exc_info and record.exc_info[0] is not None:
            log_obj["exc"] = self.formatException(record.exc_info)
        return json.dumps(log_obj, ensure_ascii=False)

def setup_logging():
    cfg = get_config()
    level = getattr(logging, cfg.get("LOG_LEVEL", "INFO").upper(), logging.INFO)
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()

    fmt = JSONFormatter()
    h_console = logging.StreamHandler()
    h_console.setFormatter(fmt)
    root.addHandler(h_console)

    h_file = logging.FileHandler("service.log", encoding="utf-8")
    h_file.setFormatter(fmt)
    root.addHandler(h_file)

def create_app():
    app = Flask(__name__)
    # Исправление кодировки для Flask 3.x
    app.json.ensure_ascii = False

    @app.after_request
    def set_utf8(response):
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response

    setup_logging()
    app.register_blueprint(chat_bp)

    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "message": "Service is running"})

    @app.errorhandler(500)
    def handle_500(error):
        logging.error(f"INTERNAL_SERVER_ERROR: {error}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        logging.error(f"UNHANDLED_EXCEPTION: {error}", exc_info=True)
        return jsonify({"error": "Service temporarily unavailable"}), 500

    return app

if __name__ == "__main__":
    app = create_app()
    print("=== Registered Routes ===")
    for rule in app.url_map.iter_rules():
        print(f"{list(rule.methods)} {rule.rule}")
    app.run(host="0.0.0.0", port=5000, debug=False)