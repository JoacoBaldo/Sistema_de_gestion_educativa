import json
from flask import g, request

from src.db.logs import guardar_log


def registrar_peticion(response):
    user_id = None
    if hasattr(g, "current_user") and g.current_user:
        user_id = g.current_user.get("id")

    request_body = None
    if request.is_json:
        body = request.get_json(silent=True)
        if body is not None:
            request_body = json.dumps(body, ensure_ascii=False)

    guardar_log(
        metodo=request.method,
        path=request.path,
        status_code=response.status_code,
        remote_addr=request.remote_addr,
        user_id=user_id,
        user_agent=request.headers.get("User-Agent"),
        request_body=request_body,
    )

    return response
