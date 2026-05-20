from flask import Flask, jsonify, request

from src.core.contracts.request.users.user_request import create_user_request
from src.core.usecase.users.users import execute as create_user_execute

app = Flask(__name__)


@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    user_data = create_user_request(data)
    response = create_user_execute(user_data)
    status_code = response.pop("status_code", 200)
    return jsonify(response), status_code
