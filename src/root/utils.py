from flask import jsonify, request


def extraer_token():
    return request.headers.get("Authorization", "").removeprefix("Bearer ").strip()


def responder_error(error):
    return jsonify({"error": error["error"]}), error["status"]
