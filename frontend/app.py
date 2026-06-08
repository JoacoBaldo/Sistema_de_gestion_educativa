import io
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
    jsonify
)

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")

from scripts.pdf_metricas import generar_pdf_metricas
from src.funciones.attendance import obtener_inasistencias_classroom
from src.funciones.auth import crear_token, validar_credenciales, verificar_token
from src.funciones.classroom import (
    crear_nueva_classroom,
    eliminar_usuario_classroom,
    obtener_alumnos_classroom,
    obtener_link_classroom,
    obtener_lista_classrooms,
    obtener_periodos_academicos,
    obtener_profesores_classroom,
)
from src.funciones.evaluaciones import (
    actualizar_evaluacion,
    crear_evaluacion,
    obtener_evaluaciones,
)
from src.funciones.metrics import obtener_metricas_classroom
from src.funciones.teams import obtener_equipos_classroom
from src.funciones.user import create_user, send_password_mail

from src.funciones.resources import listar_recursos, subir_contenido_classroom
from src.root.resources import resources_bp 

from src.root.teams import teams_bp

from src.db.students import obtener_o_crear_carrera, crear_student_profile, obtener_user_id_por_email
from src.db.classroom import agregar_usuario_classroom, usuario_en_classroom
from src.db.constantes import ESTUDIANTE
from src.funciones.students import cargar_estudiantes_csv

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "sge-dev-secret")

app.register_blueprint(teams_bp)
app.register_blueprint(resources_bp) 

TOKEN_SESSION_KEY = "token"
USER_SESSION_KEY = "user"

THEMES = [
    "theme-violet",
    "theme-aqua",
    "theme-emerald",
    "theme-coral",
    "theme-electric",
    "theme-orange",
]

DIAS_A_NUMERO = {
    "Lunes": 0,
    "Martes": 1,
    "Miércoles": 2,
    "Jueves": 3,
    "Viernes": 4,
    "Sábado": 5,
}

DIAS_NOMBRE = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

EVALUATION_TYPE_IDS = {
    "parcial": 1,
    "tp": 2,
    "recuperatorio": 3,
    "parcialito": 4,
}

ROLE_LABELS = {1: "Profesor", 2: "Ayudante", 7: "Administrador"}


def obtener_usuario_sesion():
    token = session.get(TOKEN_SESSION_KEY)
    if not token:
        return None
    usuario, error = verificar_token(token)
    if error:
        limpiar_sesion()
        return None
    return usuario


def guardar_sesion(usuario, token):
    session[TOKEN_SESSION_KEY] = token
    session[USER_SESSION_KEY] = {
        "id": usuario["id"],
        "username": usuario["username"],
        "email": usuario["email"],
    }


def limpiar_sesion():
    session.pop(TOKEN_SESSION_KEY, None)
    session.pop(USER_SESSION_KEY, None)


def requiere_login():
    usuario = obtener_usuario_sesion()
    if not usuario:
        return None, redirect(url_for("login"))
    return usuario, None


def iniciales_usuario(username):
    if not username:
        return "??"
    partes = str(username).strip().split()
    if len(partes) >= 2:
        return f"{partes[0][0]}{partes[1][0]}".upper()
    return str(username)[:2].upper()


def formatear_horarios_classroom(aula):
    filas = []
    horario = aula.get("schedule")
    if horario and horario.get("class_day") is not None:
        dia = DIAS_NOMBRE[horario["class_day"]] if horario["class_day"] < len(DIAS_NOMBRE) else str(
            horario["class_day"]
        )
        inicio = horario.get("class_start") or ""
        fin = horario.get("class_end") or ""
        if inicio or fin:
            filas.append(f"{dia} {inicio}-{fin}".strip())
    return filas


def enriquecer_aulas(aulas):
    resultado = []
    for indice, aula in enumerate(aulas):
        resultado.append(
            {
                **aula,
                "theme": THEMES[indice % len(THEMES)],
                "schedules": formatear_horarios_classroom(aula),
                "total_students": aula.get("total_students", 0),
            }
        )
    return resultado


def resolver_periodo_academico(fecha_inicio, fecha_fin, periodos):
    if not periodos:
        return None
    for periodo in periodos:
        inicio = str(periodo.get("start_date", ""))[:10]
        fin = str(periodo.get("end_date", ""))[:10]
        if fecha_inicio and fecha_fin and inicio <= fecha_inicio <= fin:
            return periodo["id"]
    return periodos[0]["id"]


def datos_vista_gestion(classroom_id, usuario, vista):
    datos = {
        "classroom_id": classroom_id,
        "user": session.get(USER_SESSION_KEY),
        "vista": vista,
        "flash_messages": [],
    }

    if vista == "students":
        alumnos, error = obtener_alumnos_classroom(classroom_id)
        if error:
            flash(error.get("error", "No se pudieron cargar los alumnos"), "error")
            datos["alumnos"] = []
        else:
            datos["alumnos"] = alumnos or []

    elif vista == "dashboard":
        metricas, error_m = obtener_metricas_classroom(classroom_id, usuario["id"])
        if error_m:
            flash(error_m.get("error", "No se pudieron cargar métricas"), "error")
            datos["metricas"] = None
        else:
            datos["metricas"] = metricas

        profesores, error_p = obtener_profesores_classroom(classroom_id, usuario["id"])
        if error_p:
            flash(error_p.get("error", "No se pudieron cargar colaboradores"), "error")
            datos["profesores"] = []
        else:
            datos["profesores"] = profesores or []

        alumnos, error_a = obtener_alumnos_classroom(classroom_id)
        datos["alumnos"] = alumnos or [] if not error_a else []

    elif vista == "asistance":
        asistencia, error = obtener_inasistencias_classroom(classroom_id, usuario["id"])
        if error:
            flash(error.get("error", "No se pudo cargar asistencia"), "error")
            datos["asistencia"] = None
        else:
            datos["asistencia"] = asistencia

    elif vista == "teams":
        equipos, error_t = obtener_equipos_classroom(classroom_id, usuario["id"])
        if error_t:
            flash(error_t.get("error", "No se pudieron cargar equipos"), "error")
            datos["equipos"] = []
        else:
            datos["equipos"] = equipos or []

        alumnos, error_a = obtener_alumnos_classroom(classroom_id)
        datos["alumnos"] = alumnos or [] if not error_a else []

    elif vista == "evaluations":
        evaluaciones, error_e = obtener_evaluaciones(classroom_id)
        if error_e:
            flash(error_e.get("error", "No se pudieron cargar evaluaciones"), "error")
            datos["evaluaciones"] = []
        else:
            datos["evaluaciones"] = evaluaciones or []

    # --- NUEVA VISTA: BIBLIOTECA DE RECURSOS ---
    elif vista == "library":
        recursos, error_r = listar_recursos(classroom_id, usuario["id"])
        if error_r:
            flash("No se pudieron cargar los recursos públicos de la biblioteca.", "error")
            datos["recursos"] = []
        else:
            datos["recursos"] = recursos or []

    return datos


@app.context_processor
def inyectar_globales():
    usuario = session.get(USER_SESSION_KEY)
    return {
        "user": usuario,
        "user_initials": iniciales_usuario(usuario.get("username") if usuario else ""),
        "role_labels": ROLE_LABELS,
        "token": session.get(TOKEN_SESSION_KEY, ""),
    }


@app.route("/auth", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if obtener_usuario_sesion():
            return redirect(url_for("classrooms"))
        return render_template("auth/login.html")

    accion = request.form.get("accion", "login")

    if accion == "register":
        username = (request.form.get("full_name") or "").strip()
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""
        resultado, error = create_user(
            {"username": username, "email": email, "password": password}
        )
        if error:
            flash(error.get("error", "No se pudo registrar la cuenta"), "error")
        else:
            flash(resultado.get("message", "Cuenta creada. Inicia sesión."), "success")
        return redirect(url_for("login"))

    if accion == "recover":
        email = (request.form.get("email") or "").strip()
        if not email:
            flash("El correo es obligatorio", "error")
            return redirect(url_for("login"))
        resultado, error = send_password_mail(email)
        if error:
            flash(error.get("error", "No se pudo enviar el correo"), "error")
        else:
            flash(resultado.get("message", "Revisa tu correo para el token."), "success")
        return redirect(url_for("login"))

    email = (request.form.get("email") or "").strip()
    password = request.form.get("password") or ""
    usuario, error = validar_credenciales(email, password)
    if error:
        flash(error.get("error", "Credenciales inválidas"), "error")
        return redirect(url_for("login"))

    token = crear_token(usuario)
    guardar_sesion(usuario, token)
    return redirect(url_for("classrooms"))


@app.route("/auth/logout")
def logout():
    limpiar_sesion()
    return redirect(url_for("login"))


@app.route("/")
def classrooms():
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    aulas, error = obtener_lista_classrooms(usuario["id"])
    if error:
        flash(error.get("error", "No se pudieron cargar las aulas"), "error")
        aulas = []

    periodos, _ = obtener_periodos_academicos()
    join_link = session.pop("join_link", None)

    return render_template(
        "main/classroomsGrid.html",
        classrooms=enriquecer_aulas(aulas or []),
        periodos=periodos or [],
        join_link=join_link,
    )


@app.route("/aulas/crear", methods=["POST"])
def crear_aula():
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    name = (request.form.get("nombre") or "").strip()
    department = (request.form.get("catedra") or "").strip()
    university = (request.form.get("universidad") or "").strip()
    fecha_inicio = request.form.get("fecha_inicio") or ""
    fecha_fin = request.form.get("fecha_fin") or ""

    dias = request.form.getlist("dia")
    inicios = request.form.getlist("h_inicio")
    fines = request.form.getlist("h_fin")

    if not name or not department or not university:
        flash("Completa nombre, cátedra y universidad.", "error")
        return redirect(url_for("classrooms"))

    if not dias or not inicios or not fines:
        flash("Agrega al menos un horario.", "error")
        return redirect(url_for("classrooms"))

    periodos, _ = obtener_periodos_academicos()
    academic_period_id = resolver_periodo_academico(fecha_inicio, fecha_fin, periodos or [])
    if not academic_period_id:
        flash("No hay períodos académicos configurados.", "error")
        return redirect(url_for("classrooms"))

    dia = dias[0]
    class_day = DIAS_A_NUMERO.get(dia, 0)
    class_start = inicios[0]
    class_end = fines[0]

    _, error = crear_nueva_classroom(
        name,
        department,
        university,
        usuario["id"],
        class_day,
        class_start,
        class_end,
        int(academic_period_id),
    )
    if error:
        flash(error.get("error", "No se pudo crear el aula"), "error")
    else:
        flash("Aula creada correctamente.", "success")

    return redirect(url_for("classrooms"))


@app.route("/clases/compartir", methods=["POST"])
def compartir_clase():
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    classroom_id = request.form.get("classId") or request.form.get("class_id")
    rol = request.form.get("rol") or "Editor"
    role_map = {"Lector": 2, "Editor": 1}
    role_id = role_map.get(rol, 1)

    try:
        classroom_id = int(classroom_id)
    except (TypeError, ValueError):
        flash("Selecciona un aula válida.", "error")
        return redirect(url_for("classrooms"))

    resultado, error = obtener_link_classroom(classroom_id, usuario["id"], role_id)
    if error:
        flash(error.get("error", "No se pudo generar el enlace"), "error")
    else:
        session["join_link"] = resultado.get("join_link", "")
        flash("Enlace de invitación generado.", "success")

    return redirect(url_for("classrooms"))


@app.route("/aulas/<int:classroom_id>/gestionar")
def classroom_manage(classroom_id):
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    vista = request.args.get("vista", "students")
    datos = datos_vista_gestion(classroom_id, usuario, vista)
    return render_template("classroom-manage/manageView.html", **datos)


@app.route("/aulas/<int:classroom_id>/gestionar/estudiantes")
def classroom_manage_students(classroom_id):
    return redirect(url_for("classroom_manage", classroom_id=classroom_id, vista="students"))


@app.route(
    "/aulas/<int:classroom_id>/gestionar/usuarios/<int:user_id>/eliminar",
    methods=["POST"],
)
def eliminar_usuario_aula(classroom_id, user_id):
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    _, error = eliminar_usuario_classroom(classroom_id, user_id, usuario["id"])
    if error:
        flash(error.get("error", "No se pudo quitar el acceso"), "error")
    else:
        flash("Acceso revocado.", "success")

    vista = request.form.get("vista", "dashboard")
    return redirect(url_for("classroom_manage", classroom_id=classroom_id, vista=vista))


@app.route("/aulas/<int:classroom_id>/gestionar/evaluaciones/crear", methods=["POST"])
def crear_evaluacion_aula(classroom_id):
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    nombre = (request.form.get("name") or "").strip()
    tipo_str = request.form.get("evaluation_type_id") or ""
    
    evaluation_type_id = EVALUATION_TYPE_IDS.get(tipo_str, None)
    individual = 1 if request.form.get("individual") else 0

    print(f"DEBUG FRONTEND -> nombre: '{nombre}', tipo: '{tipo_str}', tipo_id: {evaluation_type_id}")

    _, error = crear_evaluacion(
        classroom_id, nombre, evaluation_type_id, None, individual
    )
    
    if error:
        flash(error.get("error", "No se pudo crear la evaluación"), "error")
    else:
        flash("Evaluación creada correctamente.", "success")

    return redirect(url_for("classroom_manage", classroom_id=classroom_id, vista="evaluations"))


@app.route(
    "/aulas/<int:classroom_id>/gestionar/evaluaciones/<int:evaluation_id>/actualizar",
    methods=["POST"],
)
def actualizar_evaluacion_aula(classroom_id, evaluation_id):
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    nombre = (request.form.get("nombre") or "").strip() or None
    tipo = request.form.get("tipo") or ""
    evaluation_type_id = EVALUATION_TYPE_IDS.get(tipo) if tipo else None
    individual = 1 if request.form.get("individual") else 0

    _, error = actualizar_evaluacion(
        classroom_id,
        nombre,
        evaluation_type_id,
        None,
        individual,
        evaluation_id,
    )
    if error:
        flash(error.get("error", "No se pudo actualizar la evaluación"), "error")
    else:
        flash("Evaluación actualizada.", "success")

    return redirect(url_for("classroom_manage", classroom_id=classroom_id, vista="evaluations"))


@app.route("/aulas/<int:classroom_id>/gestionar/asistencia/registrar", methods=["POST"])
def registrar_asistencia_aula(classroom_id):
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    from src.funciones.asistencia import sumar_inasistencia

    resultado = sumar_inasistencia(classroom_id)
    if isinstance(resultado, tuple):
        body, codigo = resultado
        if codigo != 200 or (isinstance(body, dict) and body.get("error")):
            flash(body.get("error", "No se pudo registrar asistencia"), "error")
        else:
            flash("Evento de asistencia registrado.", "success")
    else:
        flash("Evento de asistencia registrado.", "success")

    return redirect(url_for("classroom_manage", classroom_id=classroom_id, vista="asistance"))


@app.route("/aulas/<int:classroom_id>/gestionar/metricas/pdf", methods=["POST"])
def descargar_metricas_pdf(classroom_id):
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    metricas, error = obtener_metricas_classroom(classroom_id, usuario["id"])
    if error:
        flash(error.get("error", "No se pudieron generar las métricas"), "error")
        return redirect(url_for("classroom_manage", classroom_id=classroom_id, vista="dashboard"))

    pdf_bytes, error_pdf = generar_pdf_metricas(
        classroom_id=classroom_id,
        usuario_id=usuario["id"],
        datos_metricas=metricas or {},
        filter=request.form.get("filter"),
    )
    if error_pdf:
        flash(error_pdf.get("error", "No se pudo generar el PDF"), "error")
        return redirect(url_for("classroom_manage", classroom_id=classroom_id, vista="dashboard"))

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"metricas_classroom_{classroom_id}.pdf",
    )


@app.route("/aulas/<int:classroom_id>/gestionar/estudiantes/crear", methods=["POST"])
def procesar_crear_estudiante(classroom_id):
    usuario, redireccion = requiere_login()
    if redireccion: return redireccion

    nombre = request.form.get("nombre")
    apellido = request.form.get("apellido")
    padron = request.form.get("padron")
    email = request.form.get("email")
    
    username = f"{nombre} {apellido}".strip()

    _, error = create_user({
        "username": username,
        "email": email,
        "password": padron, 
    })

    if error and error != "EMAIL_YA_EXISTE": 
        flash(f"Error al crear usuario: {error}", "error")
    else:
        try:
            user_id = obtener_user_id_por_email(email)
            career_id = obtener_o_crear_carrera("Ingeniería")
            
            crear_student_profile(user_id, padron, career_id)
            
            if not usuario_en_classroom(classroom_id, user_id):
                agregar_usuario_classroom(classroom_id, user_id, ESTUDIANTE)
                flash("Estudiante creado y asignado con éxito.", "success")
            else:
                flash("El estudiante ya estaba en el aula.", "warning")
        except Exception as e:
            flash(f"Error al vincular el estudiante: {str(e)}", "error")

    return redirect(url_for("classroom_manage", classroom_id=classroom_id, vista="students"))


@app.route("/aulas/<int:classroom_id>/gestionar/cargar-csv", methods=["POST"])
def cargar_csv_estudiantes(classroom_id):
    usuario, redireccion = requiere_login()
    if redireccion: return redireccion

    archivo = request.files.get("archivo") or request.files.get("csv_file")
    if not archivo or archivo.filename == "":
        flash("Selecciona un archivo CSV.", "error")
        return redirect(url_for("classroom_manage", classroom_id=classroom_id, vista="students"))

    resultado, error = cargar_estudiantes_csv(archivo, classroom_id)
    
    if error:
        flash(f"Error al procesar CSV: {error}", "error")
    else:
        flash(f"CSV procesado: {resultado['cantidad_creados']} creados, {resultado['cantidad_asociados']} asociados al aula.", "success")

    return redirect(url_for("classroom_manage", classroom_id=classroom_id, vista="students"))


@app.route("/aulas/<int:classroom_id>/gestionar/biblioteca/subir", methods=["POST"])
def subir_recurso_biblioteca(classroom_id):
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    titulo = request.form.get("titulo")
    url = request.form.get("url")
    tipo = request.form.get("tipo") or "link"  # Capturamos el tipo del select

    if not titulo or not url:
        flash("El título y el link del recurso son obligatorios.", "error")
        return redirect(url_for("classroom_manage", classroom_id=classroom_id, vista="library"))

    # Pasamos el tipo al backend
    _, error = subir_contenido_classroom(classroom_id, titulo, url, usuario["id"], tipo)
    
    if error:
        flash("No se pudo publicar el recurso en la base de datos.", "error")
    else:
        flash("Recurso publicado con éxito en la biblioteca.", "success")

    return redirect(url_for("classroom_manage", classroom_id=classroom_id, vista="library"))
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    titulo = request.form.get("titulo")
    url = request.form.get("url")

    if not titulo or not url:
        flash("El título y el link del recurso son obligatorios.", "error")
        return redirect(url_for("classroom_manage", classroom_id=classroom_id, vista="library"))

    _, error = subir_contenido_classroom(classroom_id, titulo, url, usuario["id"])
    
    if error:
        flash("No se pudo publicar el recurso en la base de datos.", "error")
    else:
        flash("Recurso publicado con éxito en la biblioteca.", "success")

    return redirect(url_for("classroom_manage", classroom_id=classroom_id, vista="library"))


if __name__ == "__main__":
    app.run(debug=True, port=5001)