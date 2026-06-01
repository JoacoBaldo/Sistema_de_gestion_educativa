from flask import Flask, render_template, request, redirect

app = Flask(__name__)

CLASSES = []
SHARES = []


@app.route("/")
def classrooms():
    return render_template("main/classroomsGrid.html")

@app.route("/aulas/crear")
def crear_aula():
    return render_template("main/forms/crear_aula.html")

@app.route("/clases/compartir")
def compartir_clase():
    return render_template("main/forms/compartir_clase.html")

@app.route("/clases", methods=["POST"])
def clases_post():
    data = {
        "nombre": request.form.get("nombre", "").strip(),
        "catedra": request.form.get("catedra", "").strip(),
        "universidad": request.form.get("universidad", "").strip(),
        "fecha_inicio": request.form.get("fecha_inicio", "").strip(),
        "fecha_fin": request.form.get("fecha_fin", "").strip(),
        "dia": request.form.get("dia", "").strip(),
        "h_inicio": request.form.get("h_inicio", "").strip(),
        "h_fin": request.form.get("h_fin", "").strip(),
    }
    CLASSES.append(data)
    return redirect("/")

@app.route("/clases/compartir", methods=["POST"])
def compartir_post():
    data = {
        "classId": request.form.get("classId", "").strip(),
        "email": request.form.get("email", "").strip(),
        "rol": request.form.get("rol", "").strip(),
    }
    SHARES.append(data)
    return redirect("/")


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
