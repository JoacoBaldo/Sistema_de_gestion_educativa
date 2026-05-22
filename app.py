from dotenv import load_dotenv

load_dotenv()

from flask import Flask

from src.entrypoints.classroom.classroom import list_classroom_professors

app = Flask(__name__)

app.add_url_rule(
    "/classrooms/<int:classroom_id>/professors",
    view_func=list_classroom_professors,
    methods=["GET"],
)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
