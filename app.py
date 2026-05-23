from dotenv import load_dotenv
from flask import Flask

from src.app.router import classroom_bp

load_dotenv()

app = Flask(__name__)
app.register_blueprint(classroom_bp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
