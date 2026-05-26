from dotenv import load_dotenv
from flask import Flask, g, request

from src.funciones.auth import verificar_token
from src.root.auth import auth_bp

load_dotenv()

app = Flask(__name__)
app.register_blueprint(auth_bp)


@app.before_request
def _adjuntar_usuario_actual():
    token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    if not token:
        g.current_user = None
        return

    usuario, error = verificar_token(token)
    g.current_user = usuario if not error else None


if __name__ == "__main__":
    app.run(debug=True, port=5000)
