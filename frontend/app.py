from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def classrooms():
    return render_template("main/classroomsGrid.html")

@app.route("/aulas/crear")
def crear_aula():
    return render_template("main/forms/crear_aula.html")

@app.route("/clases/compartir")
def compartir_clase():
    return render_template("main/forms/compartir_clase.html")


@app.route("/auth")
def login():
    return render_template("auth/login.html")


if __name__ == "__main__":
    app.run(debug=True, port=5001)
