from flask import Flask, jsonify, request

from src.core.contracts.request.users.user_request import create_user_request
from src.core.usecase.users.users import execute as create_user_execute

app = Flask(__name__)


@app.route("/users", methods=["POST"])
def create_user():
    try:
        data = request.get_json()
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON body", "status_code": 400}), 400

        user_data = create_user_request(data)
        response = create_user_execute(user_data)
        status_code = response.pop("status_code", 200)
        return jsonify(response), status_code
    except Exception:
        return (
            jsonify({"error": "Internal server error", "status_code": 500}),
            500,
        )
