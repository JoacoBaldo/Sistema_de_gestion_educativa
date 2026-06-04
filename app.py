from dotenv import load_dotenv
from flask import Flask

from src.root.auth import auth_bp
from src.root.classroom import classroom_bp
from src.root.evaluaciones import evaluacion_bp
from src.root.teams import teams_bp
from src.root.user import user_bp

load_dotenv()

app = Flask(__name__)
app.register_blueprint(auth_bp)
app.register_blueprint(classroom_bp)
app.register_blueprint(evaluacion_bp)
app.register_blueprint(teams_bp)
app.register_blueprint(evaluacion_bp)
app.register_blueprint(user_bp)


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response


@app.route("/api/<path:_path>", methods=["OPTIONS"])
@app.route("/recuperar-password", methods=["OPTIONS"])
def cors_preflight(**_kwargs):
    return "", 204

if __name__ == "__main__":
    app.run(debug=True, port=5000)
