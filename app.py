from dotenv import load_dotenv
from flask import Flask

from src.root.classroom import classroom_bp
<<<<<<< HEAD
from src.root.teams import teams_bp
=======
from src.root.auth import auth_bp
>>>>>>> d175389 (Agrega funciones para actualizar la contrasenia de un usuario. Ademas añade auth.bp al main)

load_dotenv()

app = Flask(__name__)
app.register_blueprint(classroom_bp)
<<<<<<< HEAD
app.register_blueprint(teams_bp)
=======
app.register_blueprint(auth_bp)
>>>>>>> d175389 (Agrega funciones para actualizar la contrasenia de un usuario. Ademas añade auth.bp al main)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
