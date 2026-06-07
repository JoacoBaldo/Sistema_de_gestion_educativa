import os
from urllib.parse import quote

import requests
from flask import Flask, Response, render_template, request, redirect

app = Flask(__name__)

API_BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:5000").rstrip("/")


def _proxy_to_api(path: str):
    target = f"{API_BASE_URL}/{path.lstrip('/')}"
    headers = {}
    auth = request.headers.get("Authorization")
    if auth:
        headers["Authorization"] = auth
    content_type = request.headers.get("Content-Type")
    if content_type:
        headers["Content-Type"] = content_type

    upstream = requests.request(
        method=request.method,
        url=target,
        params=request.args,
        data=request.get_data(),
        headers=headers,
        timeout=60,
    )
    excluded = {"content-encoding", "content-length", "transfer-encoding", "connection"}
    response_headers = [
        (key, value)
        for key, value in upstream.headers.items()
        if key.lower() not in excluded
    ]
    return Response(
        upstream.content, status=upstream.status_code, headers=response_headers
    )


@app.route(
    "/api/<path:api_path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
)
def api_proxy(api_path):
    if request.method == "OPTIONS":
        return "", 204
    return _proxy_to_api(f"api/{api_path}")


@app.route("/recuperar-password", methods=["POST", "OPTIONS"])
def recover_proxy():
    if request.method == "OPTIONS":
        return "", 204
    return _proxy_to_api("recuperar-password")


@app.route("/")
def classrooms():
    return render_template("main/classroomsGrid.html")


@app.route("/aulas/crear")
def crear_aula():
    return redirect("/?accion=crear")


@app.route("/clases/compartir")
def compartir_clase():
    class_id = request.args.get("id", "")
    nombre = request.args.get("nombre", "")
    return redirect(f"/?accion=compartir&id={class_id}&nombre={quote(nombre)}")


@app.route("/auth")
def login():
    return render_template("auth/login.html")


@app.route("/aulas/<int:classroom_id>/gestionar")
def classroom_manage(classroom_id):
    return render_template(
        "classroom-manage/manageView.html",
        classroom_id=classroom_id,
    )


@app.route("/aulas/<int:classroom_id>/gestionar/estudiantes")
def classroom_manage_students(classroom_id):
    return render_template(
        "classroom-manage/students/studentsview.html",
        classroom_id=classroom_id,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)
