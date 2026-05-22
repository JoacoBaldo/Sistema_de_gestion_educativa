from flask import Flask, jsonify, request

from src.core.contracts.request.users.user_request import create_user_request
from src.core.usecase.users.users import execute as create_user_execute
from src.error import format_error_response, INVALID_JSON_BODY, INTERNAL_SERVER_ERROR

app = Flask(__name__)


@app.route("/users", methods=["POST"])
def create_user():
    try:
        data = request.get_json()
        if not data or not isinstance(data, dict):
            return jsonify(format_error_response(INVALID_JSON_BODY)), 400

        user_data = create_user_request(data)
        response = create_user_execute(user_data)
        status_code = response.pop("status_code", 200)
        return jsonify(response), status_code
    except Exception:
        return (
            jsonify(format_error_response(INTERNAL_SERVER_ERROR)),
            500,
        )
