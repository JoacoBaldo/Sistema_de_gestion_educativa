from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def classrooms():
    return render_template("main/classroomsGrid.html")


@app.route("/auth")
def login():
    return render_template("auth/login.html")


@app.route("/aula/estudiantes")
def classroom_students():
    return render_template("classroom-manage/manageView.html")


if __name__ == "__main__":
    app.run(debug=True, port=5001)
