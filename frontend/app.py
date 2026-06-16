import csv
import io
import os
import logging
import requests
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
)

logging.basicConfig(level=logging.DEBUG)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "sge-dev-secret")

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:5000")

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

EVALUATION_TYPE_IDS = {"parcial": 1, "tp": 2, "recuperatorio": 3, "parcialito": 4}
ROLE_LABELS = {1: "Profesor", 2: "Ayudante", 7: "Administrador"}


@app.route("/debug")
def debug():
    return {
        "BACKEND_URL": BACKEND_URL,
        "SECRET_KEY_EXISTS": bool(os.environ.get("SECRET_KEY")),
    }


# -------------------------------------------------------------------
# COMUNICACIÓN CON LA API
# -------------------------------------------------------------------
def consumir_api(metodo, endpoint, json_data=None, data=None, files=None, params=None):
    url = f"{BACKEND_URL}{endpoint}"
    headers = {}

    token = session.get(TOKEN_SESSION_KEY)
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        if metodo.upper() == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif metodo.upper() == "POST":
            response = requests.post(
                url, headers=headers, json=json_data, data=data, files=files
            )
        elif metodo.upper() == "PUT":
            response = requests.put(url, headers=headers, json=json_data, data=data)
        elif metodo.upper() == "PATCH":
            response = requests.patch(url, headers=headers, json=json_data, data=data)
        elif metodo.upper() == "DELETE":
            response = requests.delete(url, headers=headers, json=json_data)
        else:
            return None, {"error": "Método HTTP no soportado"}

        if response.status_code == 401:
            limpiar_sesion()
            return None, {
                "error": "Sesión expirada. Por favor, inicia sesión nuevamente."
            }

        content_type = response.headers.get("Content-Type", "")
        if "application/pdf" in content_type:
            if response.ok:
                return response.content, None
            return None, {"error": "Error al generar el archivo en el backend."}

        try:
            data_json = response.json()
            if not response.ok:
                error_msg = data_json.get("error", f"Error HTTP {response.status_code}")
                return None, {"error": error_msg}
            return data_json, None

        except ValueError:
            return None, {
                "error": f"Error {response.status_code} del backend. Revisá la consola del puerto 5000."
            }

    except requests.exceptions.RequestException as e:
        return None, {"error": f"Error de conexión con el servidor: {str(e)}"}


# -------------------------------------------------------------------
# FUNCIONES AUXILIARES
# -------------------------------------------------------------------
def obtener_usuario_sesion():
    return session.get(USER_SESSION_KEY)


def guardar_sesion(usuario, token):
    session[TOKEN_SESSION_KEY] = token
    session[USER_SESSION_KEY] = {
        "id": usuario.get("id"),
        "username": usuario.get("username"),
        "email": usuario.get("email"),
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
        dia_idx = horario["class_day"]
        dia = DIAS_NOMBRE[dia_idx] if dia_idx < len(DIAS_NOMBRE) else str(dia_idx)
        inicio = horario.get("class_start", "")
        fin = horario.get("class_end", "")
        if inicio or fin:
            filas.append(f"{dia} {inicio}-{fin}".strip())
    return filas


def enriquecer_aulas(aulas):
    if not isinstance(aulas, list):
        return []
    resultado = []
    for indice, aula in enumerate(aulas):
        if isinstance(aula, dict):
            resultado.append(
                {
                    **aula,
                    "theme": THEMES[indice % len(THEMES)],
                    "schedules": formatear_horarios_classroom(aula),
                    "total_students": aula.get("total_students", 0),
                }
            )
    return resultado


def datos_vista_gestion(classroom_id, usuario, vista):
    datos = {
        "classroom_id": classroom_id,
        "user": session.get(USER_SESSION_KEY),
        "vista": vista,
        "flash_messages": [],
    }

    def extraer_lista(res, err):
        if err or not res:
            return []
        if isinstance(res, list):
            return res
        if isinstance(res, dict):
            if "error" in res:
                return []
            for val in res.values():
                if isinstance(val, list):
                    return val
        return []

    if vista == "students":
        res, err = consumir_api("GET", f"/api/v1/classrooms/{classroom_id}/alumnos")
        datos["alumnos"] = extraer_lista(res, err)
        if err:
            flash("No se pudieron cargar los alumnos", "error")

    elif vista == "dashboard":
        res_m, err_m = consumir_api("GET", f"/api/v1/metrics/{classroom_id}")
        datos["metricas"] = res_m if not err_m and isinstance(res_m, dict) else None

        res_p, err_p = consumir_api(
            "GET", f"/api/v1/classrooms/{classroom_id}/professors"
        )
        datos["profesores"] = extraer_lista(res_p, err_p)

        res_a, err_a = consumir_api("GET", f"/api/v1/classrooms/{classroom_id}/alumnos")
        datos["alumnos"] = extraer_lista(res_a, err_a)

    elif vista == "asistance":
        res, error = consumir_api("GET", f"/api/v1/attendance/{classroom_id}")

        if error or not res or not isinstance(res, dict):
            datos["asistencia"] = {
                "total_events": 0,
                "average_absences": 0.0,
                "attendance_percentage": 100.0,
                "students": [],
            }
        else:
            datos["asistencia"] = res

    elif vista == "teams":
        res_t, err_t = consumir_api("GET", f"/api/v1/teams?classroom_id={classroom_id}")
        if err_t or not res_t:
            # Fallback a métricas
            res_m, err_m = consumir_api("GET", f"/api/v1/metrics/{classroom_id}")
            if err_m:
                flash(
                    f"No se pudieron obtener los equipos desde métricas: {err_m.get('error')}",
                    "error",
                )
                datos["equipos"] = []
            else:
                datos["equipos"] = (
                    res_m.get("equipos", []) if isinstance(res_m, dict) else []
                )
        else:
            datos["equipos"] = extraer_lista(res_t, err_t)

        res_a, err_a = consumir_api("GET", f"/api/v1/classrooms/{classroom_id}/alumnos")
        datos["alumnos"] = extraer_lista(res_a, err_a)

        res_e, err_e = consumir_api(
            "GET", f"/api/v1/classroom/{classroom_id}/evaluaciones"
        )
        datos["evaluaciones"] = extraer_lista(res_e, err_e)

    elif vista == "evaluations":
        res, err = consumir_api("GET", f"/api/v1/classroom/{classroom_id}/evaluaciones")
        datos["evaluaciones"] = extraer_lista(res, err)

    elif vista == "library":
        res, err = consumir_api("GET", f"/api/v1/classrooms/{classroom_id}/resources")
        datos["recursos"] = extraer_lista(res, err)
        if err:
            flash("No se pudieron cargar los recursos", "error")

    return datos


@app.context_processor
def inyectar_globales():
    usuario = session.get(USER_SESSION_KEY)

    if usuario and isinstance(usuario, dict):
        if "role_id" not in usuario:
            classroom_id = (
                request.view_args.get("classroom_id") if request.view_args else None
            )

            if classroom_id:
                res, err = consumir_api(
                    "GET", f"/api/v1/classrooms/{classroom_id}/professors"
                )
                if not err and isinstance(res, list):
                    prof_match = next(
                        (p for p in res if p.get("id") == usuario.get("id")), None
                    )
                    usuario["role_id"] = (
                        prof_match.get("role_id", 1) if prof_match else 3
                    )
                else:
                    usuario["role_id"] = 3
            else:
                usuario["role_id"] = 3

    return {
        "user": usuario,
        "user_initials": iniciales_usuario(usuario.get("username") if usuario else ""),
        "role_labels": ROLE_LABELS,
        "token": session.get(TOKEN_SESSION_KEY, ""),
    }


# -------------------------------------------------------------------
# RUTAS DE LA APP
# -------------------------------------------------------------------
@app.route("/auth", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if obtener_usuario_sesion():
            return redirect(url_for("classrooms"))
        return render_template("auth/login.html")

    accion = request.form.get("accion", "login")

    if accion == "register":
        payload = {
            "username": (request.form.get("full_name") or "").strip(),
            "email": (request.form.get("email") or "").strip(),
            "password": request.form.get("password") or "",
        }
        res, error = consumir_api("POST", "/api/v1/register", json_data=payload)

        if error or (res and type(res) is dict and res.get("error")):
            flash(error.get("error") if error else res.get("error"), "error")
        else:
            flash("Cuenta creada. Inicia sesión.", "success")
        return redirect(url_for("login"))

    if accion == "recover":
        payload = {"email": (request.form.get("email") or "").strip()}
        if not payload["email"]:
            flash("El correo es obligatorio", "error")
            return redirect(url_for("login"))

        res, error = consumir_api("POST", "/api/v1/forgot-password", json_data=payload)
        if error or (res and type(res) is dict and res.get("error")):
            flash("No se pudo enviar el correo", "error")
        else:
            flash("Revisa tu correo para el token.", "success")
        return redirect(url_for("login"))

    if accion == "reset":
        payload = {
            "token": (request.form.get("token") or "").strip(),
            "password": request.form.get("password") or "",
        }
        res, error = consumir_api("PATCH", "/api/v1/users/password", json_data=payload)
        if error:
            flash(error.get("error", "No se pudo restablecer la contraseña"), "error")
        else:
            flash("Contraseña actualizada. Inicia sesión.", "success")
        return redirect(url_for("login"))

    payload = {
        "email": (request.form.get("email") or "").strip(),
        "password": request.form.get("password") or "",
    }
    res, error = consumir_api("POST", "/api/v1/users/login", json_data=payload)

    logging.debug(f"Login attempt - error={error}, res={res}")

    if error or not isinstance(res, dict) or not res.get("token"):
        flash(
            res.get("error", "Credenciales inválidas")
            if isinstance(res, dict)
            else "Error de servidor",
            "error",
        )
        return redirect(url_for("login"))

    guardar_sesion(res, res.get("token"))
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

    aulas_res, err_aulas = consumir_api("GET", f"/api/v1/classrooms/{usuario['id']}")
    periodos_res, err_periodos = consumir_api("GET", "/api/v1/academic-periods")
    roles_res, _ = consumir_api("GET", "/api/v1/role_types")

    aulas = aulas_res if not err_aulas and isinstance(aulas_res, list) else []
    periodos = (
        periodos_res if not err_periodos and isinstance(periodos_res, list) else []
    )
    role_types = roles_res if isinstance(roles_res, list) else []
    join_link = session.pop("join_link", None)

    return render_template(
        "main/classroomsGrid.html",
        classrooms=enriquecer_aulas(aulas),
        periodos=periodos,
        role_types=role_types,
        join_link=join_link,
    )


@app.route("/aulas/crear", methods=["POST"])
def crear_aula():
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    dias = request.form.getlist("dia")
    inicios = request.form.getlist("h_inicio")
    fines = request.form.getlist("h_fin")
    academic_period_id = request.form.get("academic_period_id")

    if not dias or not inicios or not fines:
        flash("Agrega al menos un horario.", "error")
        return redirect(url_for("classrooms"))

    if not academic_period_id:
        flash("Seleccioná un período académico.", "error")
        return redirect(url_for("classrooms"))

    payload = {
        "name": (request.form.get("nombre") or "").strip(),
        "department": (request.form.get("catedra") or "").strip(),
        "university": (request.form.get("universidad") or "").strip(),
        "class_day": DIAS_A_NUMERO.get(dias[0], 0),
        "class_start": inicios[0],
        "class_end": fines[0],
        "academic_period_id": int(academic_period_id),
    }

    res, error = consumir_api("POST", "/api/v1/classrooms", json_data=payload)
    if error or (res and type(res) is dict and res.get("error")):
        flash("No se pudo crear el aula", "error")
    else:
        flash("Aula creada correctamente.", "success")

    return redirect(url_for("classrooms"))


@app.route("/clases/compartir", methods=["POST"])
def compartir_clase():
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    classroom_id = request.form.get("classId") or request.form.get("class_id")
    role_id = request.form.get("role_id", 1)

    res, error = consumir_api(
        "GET", f"/api/v1/classrooms/{classroom_id}/link", params={"role_id": role_id}
    )

    if error or not isinstance(res, dict) or not res.get("join_link"):
        flash("No se pudo generar el enlace", "error")
    else:
        raw = res["join_link"]
        token = raw.split("token=")[-1]
        session["join_link"] = f"{request.host_url.rstrip('/')}/auth?token={token}"

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
    return redirect(
        url_for("classroom_manage", classroom_id=classroom_id, vista="students")
    )


@app.route(
    "/aulas/<int:classroom_id>/gestionar/usuarios/<int:user_id>/eliminar",
    methods=["POST"],
)
def eliminar_usuario_aula(classroom_id, user_id):
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    res, error = consumir_api(
        "DELETE", f"/api/v1/classrooms/{classroom_id}/user/{user_id}"
    )
    if error:
        flash("No se pudo quitar el acceso", "error")
    else:
        flash("Acceso revocado.", "success")

    vista = request.form.get("vista", "dashboard")
    return redirect(url_for("classroom_manage", classroom_id=classroom_id, vista=vista))


@app.route("/aulas/<int:classroom_id>/gestionar/evaluaciones/crear", methods=["POST"])
def crear_evaluacion_aula(classroom_id):
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    payload = {
        "name": (request.form.get("name") or "").strip(),
        "evaluation_type_id": EVALUATION_TYPE_IDS.get(
            request.form.get("evaluation_type_id")
        ),
        "individual": 1 if request.form.get("individual") else 0,
    }

    res, error = consumir_api(
        "POST", f"/api/v1/classroom/{classroom_id}/evaluaciones", json_data=payload
    )
    if error:
        flash("No se pudo crear la evaluación", "error")
    else:
        flash("Evaluación creada correctamente.", "success")

    return redirect(
        url_for("classroom_manage", classroom_id=classroom_id, vista="evaluations")
    )


@app.route(
    "/aulas/<int:classroom_id>/gestionar/evaluaciones/<int:evaluation_id>/actualizar",
    methods=["POST"],
)
def actualizar_evaluacion_aula(classroom_id, evaluation_id):
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    tipo = request.form.get("tipo")
    payload = {
        "name": (request.form.get("nombre") or "").strip() or None,
        "evaluation_type_id": EVALUATION_TYPE_IDS.get(tipo) if tipo else None,
        "individual": 1 if request.form.get("individual") else 0,
    }

    res, error = consumir_api(
        "PATCH", f"/api/v1/evaluaciones/{evaluation_id}", json_data=payload
    )
    if error:
        flash("No se pudo actualizar la evaluación", "error")
    else:
        flash("Evaluación actualizada.", "success")

    return redirect(
        url_for("classroom_manage", classroom_id=classroom_id, vista="evaluations")
    )


# Esto deberia ser un metodo DELETE pero al no poderse usar fetch, y los from solo envian post o get, se opto por esta solucion. El endpoint de la api si es DELETE


@app.route(
    "/aulas/<int:classroom_id>/gestionar/evaluaciones/<int:evaluation_id>/eliminar",
    methods=["POST"],
)
def eliminar_evaluacion_aula(classroom_id, evaluation_id):
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    res, error = consumir_api("DELETE", f"/api/v1/evaluaciones/{evaluation_id}")

    if error:
        error_msg = error.get("error", "No se pudo eliminar la evaluación.")
        flash(f"Error: {error_msg}", "error")
    else:
        flash("Evaluación eliminada correctamente.", "success")

    return redirect(
        url_for("classroom_manage", classroom_id=classroom_id, vista="evaluations")
    )


@app.route(
    "/aulas/<int:classroom_id>/gestionar/evaluaciones/<int:evaluation_id>/subir-notas",
    methods=["POST"],
)
def subir_notas_csv_aula(classroom_id, evaluation_id):
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    if "file_csv" not in request.files:
        flash("No se subió ningún archivo.", "error")
        return redirect(
            url_for("classroom_manage", classroom_id=classroom_id, vista="evaluations")
        )

    file = request.files["file_csv"]
    if file.filename == "":
        flash("El nombre de archivo está vacío.", "error")
        return redirect(
            url_for("classroom_manage", classroom_id=classroom_id, vista="evaluations")
        )

    if not file.filename.endswith(".csv"):
        flash("El archivo debe ser en formato CSV.", "error")
        return redirect(
            url_for("classroom_manage", classroom_id=classroom_id, vista="evaluations")
        )

    try:
        stream = io.StringIO(file.stream.read().decode("utf-8-sig"), newline=None)
        reader = csv.DictReader(
            stream, delimiter=";" if ";" in stream.getvalue() else ","
        )

        reader.fieldnames = (
            [f.strip().lower() for f in reader.fieldnames] if reader.fieldnames else []
        )

        tiene_identificador = (
            "documento" in reader.fieldnames or "email" in reader.fieldnames
        )
        if not tiene_identificador or "nota" not in reader.fieldnames:
            flash(
                "Estructura CSV inválida. Debe contener la columna 'nota' y al menos 'documento' o 'email'.",
                "error",
            )
            return redirect(
                url_for(
                    "classroom_manage", classroom_id=classroom_id, vista="evaluations"
                )
            )

        filas_procesadas = []
        # Validar estructura básica del CSV (Ahora soporta 'equipo')
        tiene_identificador = any(
            col in reader.fieldnames for col in ["documento", "email", "equipo"]
        )
        if not tiene_identificador or "nota" not in reader.fieldnames:
            flash(
                "Estructura CSV inválida. Debe contener la columna 'nota' y al menos 'documento', 'email' o 'equipo'.",
                "error",
            )
            return redirect(
                url_for(
                    "classroom_manage", classroom_id=classroom_id, vista="evaluations"
                )
            )

        if "equipo" in reader.fieldnames:
            tipo_id = "equipo"
        elif "documento" in reader.fieldnames:
            tipo_id = "documento"
        else:
            tipo_id = "email"

        filas_procesadas = []
        for fila in reader:
            identificador = fila.get(tipo_id, "").strip()
            nota_str = fila.get("nota", "").strip()

            if identificador and nota_str:
                filas_procesadas.append(
                    {
                        "identifier": identificador,
                        "score": float(nota_str.replace(",", ".")),
                        "type": tipo_id,  # Le pasamos a la DB qué tipo de dato es
                    }
                )

        payload = {
            "evaluation_id": evaluation_id,
            "classroom_id": classroom_id,
            "grades": filas_procesadas,
        }

        res, error = consumir_api(
            "POST",
            f"/api/v1/evaluations/{evaluation_id}/bulk-grades",
            json_data=payload,
        )

        if error:
            flash(
                f"Error al procesar notas: {error.get('error', 'Error desconocido')}",
                "error",
            )
        else:
            flash(
                f"¡Éxito! Se procesaron {res.get('inserted', 0)} notas correctamente.",
                "success",
            )

    except Exception as e:
        flash(f"Ocurrió un error al leer el archivo CSV: {str(e)}", "error")

    return redirect(
        url_for("classroom_manage", classroom_id=classroom_id, vista="evaluations")
    )


@app.route("/aulas/<int:classroom_id>/gestionar/asistencia/registrar", methods=["POST"])
def registrar_asistencia_aula(classroom_id):
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    payload = {"delta": 1}
    res, error = consumir_api(
        "POST", f"/api/v1/attendance/{classroom_id}", json_data=payload
    )

    if error or (res and type(res) is dict and res.get("error")):
        flash("No se pudo registrar asistencia", "error")
    else:
        flash("Evento de asistencia registrado con éxito.", "success")

    return redirect(
        url_for("classroom_manage", classroom_id=classroom_id, vista="asistance")
    )


@app.route("/aulas/<int:classroom_id>/gestionar/asistencia/enviar-qr", methods=["POST"])
def enviar_qr_asistencia(classroom_id):
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    code = request.form.get("code", "").strip()
    if not code:
        flash(
            "No se pudo obtener el código QR actual. Generá uno nuevo e intentá de nuevo.",
            "error",
        )
        return redirect(
            url_for("classroom_manage", classroom_id=classroom_id, vista="asistance")
        )

    res, error = consumir_api(
        "POST", f"/api/v1/attendance/{classroom_id}/qr", json_data={"code": code}
    )

    if error:
        flash(error.get("error", "No se pudieron enviar los QRs"), "error")
    else:
        enviados = res.get("enviados", 0)
        fallidos = res.get("fallidos", [])
        msg = f"QRs enviados a {enviados} estudiante{'s' if enviados != 1 else ''}."
        if fallidos:
            msg += f" No se pudo enviar a: {', '.join(fallidos)}."
        flash(msg, "success")

    return redirect(
        url_for("classroom_manage", classroom_id=classroom_id, vista="asistance")
    )


@app.route("/aulas/<int:classroom_id>/asistencia/validar", methods=["GET", "POST"])
def validar_asistencia_alumno(classroom_id):
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    if request.method == "POST":
        code = request.form.get("code")

        payload = {"code": code}
        res, error = consumir_api(
            "POST", f"/api/v1/attendance/{classroom_id}/validar", json_data=payload
        )

        if error:
            flash(
                f"Error al registrar asistencia: {error.get('error', 'Código inválido o expirado')}",
                "error",
            )
            return redirect(
                url_for(
                    "validar_asistencia_alumno", classroom_id=classroom_id, code=code
                )
            )
        else:
            flash("¡Asistencia registrada con éxito! Ya tenés tu presente.", "success")

            return redirect(url_for("classroom_manage", classroom_id=classroom_id))

    code = request.args.get("code", "")

    return render_template(
        "classroom-manage/asistance/validar_asistencia.html",
        classroom_id=classroom_id,
        code=code,
        usuario=usuario,
    )


@app.route("/aulas/<int:classroom_id>/gestionar/metricas/pdf", methods=["POST"])
def descargar_metricas_pdf(classroom_id):
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    payload = {"filter": request.form.get("filter")}
    res, error = consumir_api(
        "POST", f"/api/v1/metrics/{classroom_id}/pdf", data=payload
    )

    if error:
        flash("No se pudo generar el PDF", "error")
        return redirect(
            url_for("classroom_manage", classroom_id=classroom_id, vista="dashboard")
        )

    return send_file(
        io.BytesIO(res),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"metricas_classroom_{classroom_id}.pdf",
    )


@app.route("/aulas/<int:classroom_id>/gestionar/estudiantes/crear", methods=["POST"])
def procesar_crear_estudiante(classroom_id):
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    nombre = (request.form.get("nombre") or "").strip()
    apellido = (request.form.get("apellido") or "").strip()
    padron = (request.form.get("padron") or "").strip()
    email = (request.form.get("email") or "").strip()
    career = (request.form.get("career") or "").strip()

    payload = {
        "username": f"{nombre} {apellido}",
        "email": email,
        "document": padron,
        "career": career,
    }

    res, error = consumir_api(
        "POST", f"/api/v1/classrooms/{classroom_id}/student", json_data=payload
    )

    if error or (res and type(res) is dict and res.get("error")):
        error_msg = (
            error.get("error")
            if isinstance(error, dict)
            else (res.get("error") if isinstance(res, dict) else error)
        )
        flash(f"Error al vincular el estudiante: {error_msg}", "error")
    else:
        flash("Estudiante creado y asignado con éxito.", "success")

    return redirect(
        url_for("classroom_manage", classroom_id=classroom_id, vista="students")
    )


@app.route("/aulas/<int:classroom_id>/gestionar/estudiantes/editar", methods=["POST"])
def procesar_editar_estudiante(classroom_id):
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    nombre = (request.form.get("nombre") or "").strip()
    apellido = (request.form.get("apellido") or "").strip()
    padron = (request.form.get("padron") or "").strip()
    email = (request.form.get("email") or "").strip()
    career = (request.form.get("career") or "").strip()
    user_id = request.form.get("user_id")

    if not user_id:
        flash("Datos incompletos para editar el estudiante.", "error")
        return redirect(
            url_for("classroom_manage", classroom_id=classroom_id, vista="students")
        )

    payload = {
        "user_id": int(user_id),
        "username": f"{nombre} {apellido}",
        "email": email,
        "document": padron,
        "career": career,
    }

    res, error = consumir_api(
        "PUT", f"/api/v1/classrooms/{classroom_id}/student", json_data=payload
    )

    if error or (res and type(res) is dict and res.get("error")):
        error_msg = (
            error.get("error")
            if isinstance(error, dict)
            else (res.get("error") if isinstance(res, dict) else error)
        )
        flash(f"Error al editar el estudiante: {error_msg}", "error")
    else:
        flash("Estudiante actualizado con éxito.", "success")

    return redirect(
        url_for("classroom_manage", classroom_id=classroom_id, vista="students")
    )


@app.route("/aulas/<int:classroom_id>/gestionar/cargar-csv", methods=["POST"])
def cargar_csv_estudiantes(classroom_id):
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    archivo = request.files.get("archivo") or request.files.get("csv_file")
    if not archivo or archivo.filename == "":
        flash("Selecciona un archivo CSV.", "error")
        return redirect(
            url_for("classroom_manage", classroom_id=classroom_id, vista="students")
        )

    files = {"csv_file": (archivo.filename, archivo.stream, archivo.mimetype)}
    res, error = consumir_api(
        "POST", f"/api/v1/classrooms/{classroom_id}/students/import", files=files
    )

    if error or (res and type(res) is dict and res.get("error")):
        error_msg = (
            error.get("error")
            if isinstance(error, dict)
            else (res.get("error") if isinstance(res, dict) else error)
        )
        flash(f"Error al procesar CSV: {error_msg}", "error")
    else:
        flash("CSV procesado correctamente.", "success")

    return redirect(
        url_for("classroom_manage", classroom_id=classroom_id, vista="students")
    )


@app.route("/aulas/<int:classroom_id>/gestionar/biblioteca/subir", methods=["POST"])
def subir_recurso_biblioteca(classroom_id):
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    payload = {
        "titulo": request.form.get("titulo"),
        "url": request.form.get("url"),
        "tipo": request.form.get("tipo"),
        "user_id": usuario["id"],
    }

    print(
        f"DEBUG CREAR -> Titulo: {payload['titulo']}, URL: {payload['url']}, Tipo recibido: {payload['tipo']}"
    )

    if not payload["titulo"] or not payload["url"]:
        flash("El título y el link del recurso son obligatorios.", "error")
        return redirect(
            url_for("classroom_manage", classroom_id=classroom_id, vista="library")
        )

    res, error = consumir_api(
        "POST", f"/api/v1/classrooms/{classroom_id}/contenidos", json_data=payload
    )

    if error:
        flash("No se pudo publicar el recurso.", "error")
    else:
        flash("Recurso publicado con éxito en la biblioteca.", "success")

    return redirect(
        url_for("classroom_manage", classroom_id=classroom_id, vista="library")
    )


@app.route(
    "/aulas/<int:classroom_id>/gestionar/recursos/<int:resource_id>/actualizar",
    methods=["POST"],
)
def actualizar_recurso_biblioteca(classroom_id, resource_id):
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    payload = {
        "titulo": request.form.get("titulo"),
        "tipo": request.form.get("tipo"),
        "url": request.form.get("url"),
    }

    if not payload["titulo"] or not payload["url"] or not payload["tipo"]:
        flash("Todos los campos son obligatorios.", "error")
        return redirect(
            url_for("classroom_manage", classroom_id=classroom_id, vista="library")
        )

    res, error = consumir_api(
        "PUT",
        f"/api/v1/classrooms/{classroom_id}/contenidos/{resource_id}",
        json_data=payload,
    )

    if error:
        error_msg = error.get("error", "No se pudo modificar el recurso.")
        flash(error_msg, "error")
    else:
        flash("Recurso modificado exitosamente.", "success")

    return redirect(
        url_for("classroom_manage", classroom_id=classroom_id, vista="library")
    )


@app.route(
    "/aulas/<int:classroom_id>/gestionar/recursos/<int:resource_id>/eliminar",
    methods=["POST"],
)
def eliminar_recurso_biblioteca(classroom_id, resource_id):
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    res, error = consumir_api(
        "DELETE", f"/api/v1/classrooms/{classroom_id}/contenidos/{resource_id}"
    )

    if error:
        error_msg = error.get("error", "No se pudo eliminar el recurso.")
        flash(error_msg, "error")
    else:
        flash("El recurso ha sido eliminado correctamente.", "success")

    return redirect(
        url_for("classroom_manage", classroom_id=classroom_id, vista="library")
    )


# ===================================================================
# RUTAS DE EQUIPOS (TEAMS)
# ===================================================================


@app.route("/aulas/<int:classroom_id>/gestionar/equipos/crear", methods=["POST"])
def crear_equipo_aula(classroom_id):
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    evaluation_id_str = request.form.get("evaluation_id", "")
    payload = {
        "name": request.form.get("nombre_equipo", "").strip(),
        "classroom_id": classroom_id,
        "member_ids": request.form.getlist("miembros"),
        "evaluation_id": int(evaluation_id_str)
        if evaluation_id_str.isdigit()
        else None,
    }

    res, error = consumir_api("POST", "/api/v1/teams", json_data=payload)

    if error:
        flash(
            f"No se pudo crear el equipo: {error.get('error', 'Error desconocido')}",
            "error",
        )
    else:
        flash("Equipo creado con éxito.", "success")

    return redirect(
        url_for("classroom_manage", classroom_id=classroom_id, vista="teams")
    )


@app.route(
    "/aulas/<int:classroom_id>/gestionar/equipos/<int:team_id>/actualizar",
    methods=["POST"],
)
def actualizar_equipo_aula(classroom_id, team_id):
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    evaluation_id_str = request.form.get("evaluation_id", "")
    payload = {
        "name": request.form.get("nombre_equipo", "").strip(),
        "member_ids": request.form.getlist("miembros"),
    }
    if evaluation_id_str.isdigit():
        payload["evaluation_id"] = int(evaluation_id_str)

    res, error = consumir_api("PUT", f"/api/v1/teams/{team_id}", json_data=payload)

    if error:
        flash(
            f"No se pudo actualizar el equipo: {error.get('error', 'Error desconocido')}",
            "error",
        )
    else:
        flash("Equipo actualizado con éxito.", "success")

    return redirect(
        url_for("classroom_manage", classroom_id=classroom_id, vista="teams")
    )


@app.route(
    "/aulas/<int:classroom_id>/gestionar/equipos/<int:team_id>/eliminar",
    methods=["POST", "DELETE"],
)
def eliminar_equipo_aula(classroom_id, team_id):
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    res, error = consumir_api("DELETE", f"/api/v1/teams/{team_id}")

    if error:
        flash("No se pudo eliminar el equipo.", "error")
    else:
        flash("Equipo eliminado correctamente.", "success")

    return redirect(
        url_for("classroom_manage", classroom_id=classroom_id, vista="teams")
    )


@app.route("/aulas/<int:classroom_id>/gestionar/metricas/pdf")
def descargar_pdf_dashboard(classroom_id):
    usuario, redireccion = requiere_login()
    if redireccion:
        return redireccion

    filtro = request.args.get("filter", "students")
    res_m, err_m = consumir_api("GET", f"/api/v1/metrics/{classroom_id}")
    if err_m or not res_m:
        flash("No se pudieron obtener las métricas base para armar el PDF.", "error")
        return redirect(
            url_for("classroom_manage", classroom_id=classroom_id, vista="dashboard")
        )

    pdf_content, err_pdf = consumir_api(
        "POST", f"/api/v1/metrics/{classroom_id}/pdf?filter={filtro}", json_data=res_m
    )

    if err_pdf:
        flash(
            f"Error al generar el PDF: {err_pdf.get('error', 'Error desconocido')}",
            "error",
        )
        return redirect(
            url_for("classroom_manage", classroom_id=classroom_id, vista="dashboard")
        )

    return send_file(
        io.BytesIO(pdf_content),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"reporte_{filtro}_aula_{classroom_id}.pdf",
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)
