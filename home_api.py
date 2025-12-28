from flask import Flask, request, jsonify
import json
import logging
from functools import wraps
from PyP100 import PyP100
from config import API_KEY, ALLOWED_IPS, SSL_CERT, SSL_KEY, USE_HTTPS, SWITCHES, USER, PW


def create_app():
    app = Flask(__name__)
    
    # Configure file logging
    import os
    log_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(log_dir, 'logs\home_api.log')
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

    # Security decorator to check API key and IP whitelist
    def require_auth(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check IP whitelist if configured
            if ALLOWED_IPS and request.remote_addr not in ALLOWED_IPS:
                app.logger.warning(f"Blocked request from unauthorized IP: {request.remote_addr}")
                return jsonify({"error": "unauthorized IP"}), 403
            
            # Check API key
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                app.logger.warning("Missing or invalid Authorization header")
                return jsonify({"error": "missing Authorization header"}), 401
            
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            if token != API_KEY:
                app.logger.warning("Invalid API key")
                return jsonify({"error": "invalid API key"}), 401
            
            return f(*args, **kwargs)
        return decorated_function

    @app.route('/test', methods=['POST'])
    @require_auth
    def test():
        app.logger.info("INF: Received /test request")
        return jsonify({"status": "ok", "message": "Test endpoint working"}), 200

    @app.route('/print', methods=['POST'])
    @require_auth
    def print_message():
        # Debug: log headers and raw body to help diagnose parsing problems
        raw = request.get_data(as_text=True)
        request_info = {
            'headers': dict(request.headers),
            'raw_body': raw,
            'is_json': request.is_json,
        }
        app.logger.debug('Request info: %s', request_info)

        # Try several parsing strategies so clients that omit Content-Type still work
        data = {}
        if request.is_json:
            data = request.get_json(silent=True) or {}
        else:
            # Try to parse JSON from body even if header missing
            try:
                data = json.loads(raw) if raw else {}
            except Exception:
                data = request.form.to_dict() or request.values.to_dict() or {}

        message = data.get('message') or request.args.get('message')
        # If still not found, treat raw body as the message (useful for plain text clients)
        if message is None:
            if raw:
                # strip potential quotes
                message = raw.strip()
            else:
                return jsonify({"error": "missing 'message' parameter"}), 400

        # Print the message to stdout (visible in server logs)
        app.logger.info('Printing message: %s', message)
        print(message, flush=True)

        return jsonify({"status": "ok", "message": message}), 200

    # curl -X POST https://127.0.0.1:5000/switch   -H "Content-Type: application/json"   -H "Authorization: Bearer $API_KEY"   -d '{ "name": "office", "state": "on" }'   --insecure
    @app.route('/switch', methods=['POST'])
    @require_auth
    def switch():
        # Accept JSON body, form data, or query params
        data = {}
        if request.is_json:
            data = request.get_json() or {}
        else:
            data = request.form.to_dict() or request.values.to_dict() or {}

        name = data.get('switch') or data.get('name') or request.args.get('switch') or request.args.get('name')
        state = data.get('state') or data.get('on') or request.args.get('state') or request.args.get('on')
        if name is None or state is None:
            return jsonify({"error": "missing 'switch' or 'state' parameter"}), 400

        state_norm = str(state).lower()
        if state_norm in ('1', 'true', 'on', 'yes'):
            state_norm = 'on'
        elif state_norm in ('0', 'false', 'off', 'no'):
            state_norm = 'off'
        else:
            return jsonify({"error": "invalid 'state' value, expected on/off"}), 400

        msg = f"Switch '{name}' set to {state_norm}"
        app.logger.debug(msg)
        switch_controller(name, state_norm)

        return jsonify({"status": "ok", "switch": name, "state": state_norm}), 200

    def switch_controller(name, state):
        # Placeholder for actual switch control logic
        app.logger.info(f"Switching {name} to {state}")
        
        if SWITCHES.get(name, None) is not None:
            p100 = PyP100.P100(SWITCHES[name], USER, PW)
            if state == 'on':
                p100.turnOn()
            else:
                p100.turnOff()
            return True
        
        return False

    return app

if __name__ == '__main__':
    app = create_app()
    app.logger.setLevel(logging.INFO)
    if USE_HTTPS:
        app.run(host='0.0.0.0', port=5000, ssl_context=(SSL_CERT, SSL_KEY), debug=True)
    else:
        app.run(host='0.0.0.0', port=5000, debug=True)