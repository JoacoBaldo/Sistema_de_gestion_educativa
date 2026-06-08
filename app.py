from dotenv import load_dotenv
from flask import Flask

from src.root.attendance import attendance_bp
from src.root.auth import auth_bp
from src.root.classroom import classroom_bp
from src.root.evaluaciones import evaluacion_bp
from src.root.metrics import metrics_bp
from src.root.teams import teams_bp
from src.root.students import students_bp
from src.root.user import user_bp

load_dotenv()

app = Flask(__name__)
app.register_blueprint(auth_bp)
app.register_blueprint(classroom_bp)
app.register_blueprint(evaluacion_bp)
app.register_blueprint(teams_bp)
app.register_blueprint(students_bp)
app.register_blueprint(user_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(metrics_bp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
