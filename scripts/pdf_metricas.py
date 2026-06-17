import io
from datetime import date

from reportlab.lib import colors  # type: ignore[import-untyped]
from reportlab.lib.pagesizes import A4  # type: ignore[import-untyped]
from reportlab.lib.styles import (  # type: ignore[import-untyped]
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import cm  # type: ignore[import-untyped]
from reportlab.platypus import (  # type: ignore[import-untyped]
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.db import classroom as db_classroom
from src.db.conexion import obtener_conexion
from src.db.constantes import (
    ADMINISTRADOR,
    AYUDANTE,
    PROFESOR,
    STATUS_ACTIVO,
    ESTUDIANTE,
)
from src.funciones.errores import (
    BODY_INVALIDO,
    CLASSROOM_NO_EXISTE,
    FILTRO_INVALIDO,
    NO_ES_ADMIN,
    SIN_ACCESO,
)


FILTROS_VALIDOS = {"students", "students_passed", "teams", "colaborators"}

NOMBRE_ROL = {
    PROFESOR: "Profesor",
    AYUDANTE: "Ayudante",
    ADMINISTRADOR: "Administrador",
}

COLOR_PRIMARIO = colors.HexColor("#4F46E5")  # Indigo
COLOR_HEADER = colors.HexColor("#1F2937")  # Dark Charcoal
COLOR_TEXTO = colors.HexColor("#374151")  # Gray
COLOR_LINEA = colors.HexColor("#E5E7EB")  # Light Gray


def generar_pdf_metricas(
    classroom_id: int, usuario_id: int, datos_metricas: dict, filtro: str | None
) -> tuple[bytes | None, dict | None]:

    if not filtro or filtro not in FILTROS_VALIDOS:
        return None, FILTRO_INVALIDO

    if not db_classroom.existe_classroom(classroom_id):
        return None, CLASSROOM_NO_EXISTE

    if not db_classroom.usuario_en_classroom(classroom_id, usuario_id):
        return None, SIN_ACCESO

    if not db_classroom.puede_administrar_classroom(classroom_id, usuario_id):
        return None, NO_ES_ADMIN

    if not isinstance(datos_metricas, dict):
        return None, BODY_INVALIDO

    promedio_gpa = datos_metricas.get("promedio_aprobados", 0)
    total_estudiantes = datos_metricas.get("total_estudiantes", 0)
    total_activos = datos_metricas.get("total_activos", 0)
    total_abandonaron = datos_metricas.get("total_abandonaron", 0)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    estilos = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        "DocTitle",
        parent=estilos["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=24,
        textColor=COLOR_PRIMARIO,
        spaceAfter=6,
    )
    estilo_subtitulo = ParagraphStyle(
        "DocSubtitle",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=10,
        textColor=COLOR_TEXTO,
        spaceAfter=20,
    )
    estilo_h2 = ParagraphStyle(
        "SectionHeading",
        parent=estilos["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        textColor=COLOR_HEADER,
        spaceBefore=12,
        spaceAfter=10,
    )
    estilo_celda = ParagraphStyle(
        "GridCell",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=9,
        textColor=COLOR_TEXTO,
    )
    estilo_celda_bold = ParagraphStyle(
        "GridCellBold",
        parent=estilo_celda,
        fontName="Helvetica-Bold",
    )

    elementos = []

    elementos.append(Paragraph("Reporte de Métricas", estilo_titulo))
    fecha_actual = date.today().strftime("%d/%m/%Y")
    elementos.append(
        Paragraph(
            f"Classroom ID: {classroom_id} &nbsp;|&nbsp; Fecha: {fecha_actual}",
            estilo_subtitulo,
        )
    )

    resumen_datos = [
        [
            Paragraph("<b>Total Alumnos:</b>", estilo_celda),
            Paragraph(str(total_estudiantes), estilo_celda),
            Paragraph("<b>Alumnos Activos:</b>", estilo_celda),
            Paragraph(str(total_activos), estilo_celda),
        ],
        [
            Paragraph("<b>% Aprobación:</b>", estilo_celda),
            Paragraph(f"{promedio_gpa}%", estilo_celda),
            Paragraph("<b>Abandonos:</b>", estilo_celda),
            Paragraph(str(total_abandonaron), estilo_celda),
        ],
    ]
    tabla_resumen = Table(
        resumen_datos, colWidths=[3.5 * cm, 4.5 * cm, 3.5 * cm, 4.5 * cm]
    )
    tabla_resumen.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("LINEBELOW", (0, 0), (-1, -1), 0.5, COLOR_LINEA),
            ]
        )
    )
    elementos.append(tabla_resumen)
    elementos.append(Spacer(1, 15))

    engine = obtener_conexion()

    if filtro in {"students", "students_passed"}:
        with engine.connect() as conn:
            alumnos_db = conn.exec_driver_sql(
                """
                SELECT 
                    u.username, 
                    u.email, 
                    COALESCE(sp.document, '-') as document,
                    cu.status_type_id,
                    COALESCE((
                        SELECT SUM(att.absence)
                        FROM attendance att
                        JOIN attendance_events ae ON att.attendance_event_id = ae.id
                        WHERE att.student_id = u.id AND ae.classroom_id = cu.classroom_id
                    ), 0) as total_inasistencias,
                    COALESCE(AVG(g.score), 0) as promedio
                FROM classroom_users cu
                JOIN users u ON cu.user_id = u.id
                LEFT JOIN student_profiles sp ON u.id = sp.user_id
                LEFT JOIN grades g ON g.user_id = cu.user_id
                LEFT JOIN evaluations e ON e.id = g.evaluation_id AND e.classroom_id = cu.classroom_id
                WHERE cu.classroom_id = %s AND cu.role_id = %s
                GROUP BY u.id, u.username, u.email, sp.document, cu.status_type_id, cu.classroom_id
                ORDER BY u.username
                """,
                (classroom_id, ESTUDIANTE),
            ).fetchall()

        if filtro == "students_passed":
            tabla1_titulo = "Alumnos Aprobados (Promedio ≥ 4)"
            tabla2_titulo = "Alumnos Desaprobados (Promedio < 4)"
            grupo1 = [a for a in alumnos_db if float(a[5]) >= 4.0]
            grupo2 = [a for a in alumnos_db if float(a[5]) < 4.0]
        else:
            tabla1_titulo = "Alumnos Activos"
            tabla2_titulo = "Alumnos Inactivos / Abandonos"
            grupo1 = [a for a in alumnos_db if a[3] == STATUS_ACTIVO]
            grupo2 = [a for a in alumnos_db if a[3] != STATUS_ACTIVO]

        # Tabla 1
        elementos.append(Paragraph(tabla1_titulo, estilo_h2))
        if grupo1:
            filas = [
                [
                    Paragraph("Nombre", estilo_celda_bold),
                    Paragraph("Email", estilo_celda_bold),
                    Paragraph("Documento", estilo_celda_bold),
                    Paragraph("Promedio", estilo_celda_bold),
                    Paragraph("Inasistencias", estilo_celda_bold),
                ]
            ]
            for a in grupo1:
                filas.append(
                    [
                        Paragraph(a[0], estilo_celda),
                        Paragraph(a[1], estilo_celda),
                        Paragraph(a[2], estilo_celda),
                        Paragraph(str(round(float(a[5]), 2)), estilo_celda),
                        Paragraph(str(int(a[4])), estilo_celda),
                    ]
                )
            elementos.append(
                _construir_tabla(
                    filas, [4.5 * cm, 5.0 * cm, 3.5 * cm, 2.0 * cm, 3.0 * cm]
                )
            )
        else:
            elementos.append(
                Paragraph(
                    "No hay alumnos para listar en esta sección.", estilos["Normal"]
                )
            )

        elementos.append(Spacer(1, 15))

        # Tabla 2
        elementos.append(Paragraph(tabla2_titulo, estilo_h2))
        if grupo2:
            filas = [
                [
                    Paragraph("Nombre", estilo_celda_bold),
                    Paragraph("Email", estilo_celda_bold),
                    Paragraph("Documento", estilo_celda_bold),
                    Paragraph("Promedio", estilo_celda_bold),
                    Paragraph("Inasistencias", estilo_celda_bold),
                ]
            ]
            for a in grupo2:
                filas.append(
                    [
                        Paragraph(a[0], estilo_celda),
                        Paragraph(a[1], estilo_celda),
                        Paragraph(a[2], estilo_celda),
                        Paragraph(str(round(float(a[5]), 2)), estilo_celda),
                        Paragraph(str(int(a[4])), estilo_celda),
                    ]
                )
            elementos.append(
                _construir_tabla(
                    filas, [4.5 * cm, 5.0 * cm, 3.5 * cm, 2.0 * cm, 3.0 * cm]
                )
            )
        else:
            elementos.append(
                Paragraph(
                    "No hay alumnos para listar en esta sección.", estilos["Normal"]
                )
            )

    elif filtro == "teams":
        elementos.append(Paragraph("Desglose Analítico por Equipos", estilo_h2))

        with engine.connect() as conn:
            equipos_db = conn.exec_driver_sql(
                "SELECT id, name FROM teams WHERE classroom_id = %s ORDER BY name",
                (classroom_id,),
            ).fetchall()

        if equipos_db:
            for eq in equipos_db:
                equipo_id = eq[0]
                nombre_equipo = eq[1]

                elementos.append(Paragraph(f"Equipo: {nombre_equipo}", estilo_h2))

                with engine.connect() as conn:
                    miembros = conn.exec_driver_sql(
                        """
                        SELECT 
                            u.username, 
                            u.email, 
                            COALESCE(sp.document, '-') as document,
                            COALESCE((
                                SELECT SUM(att.absence)
                                FROM attendance att
                                JOIN attendance_events ae ON att.attendance_event_id = ae.id
                                WHERE att.student_id = u.id AND ae.classroom_id = %s
                            ), 0) as total_inasistencias,
                            COALESCE(AVG(g.score), 0) as promedio
                        FROM team_members tm
                        JOIN users u ON tm.user_id = u.id
                        JOIN classroom_users cu ON cu.user_id = u.id AND cu.classroom_id = %s
                        LEFT JOIN student_profiles sp ON u.id = sp.user_id
                        LEFT JOIN grades g ON g.user_id = u.id
                        LEFT JOIN evaluations e ON e.id = g.evaluation_id AND e.classroom_id = %s
                        WHERE tm.team_id = %s
                        GROUP BY u.id, u.username, u.email, sp.document, cu.classroom_id
                        """,
                        (classroom_id, classroom_id, classroom_id, equipo_id),
                    ).fetchall()

                if miembros:
                    filas = [
                        [
                            Paragraph("Integrante", estilo_celda_bold),
                            Paragraph("Email", estilo_celda_bold),
                            Paragraph("Documento", estilo_celda_bold),
                            Paragraph("Promedio", estilo_celda_bold),
                            Paragraph("Inasistencias", estilo_celda_bold),
                        ]
                    ]
                    for m in miembros:
                        filas.append(
                            [
                                Paragraph(m[0], estilo_celda),
                                Paragraph(m[1], estilo_celda),
                                Paragraph(m[2], estilo_celda),
                                Paragraph(str(round(float(m[4]), 2)), estilo_celda),
                                Paragraph(str(int(m[3])), estilo_celda),
                            ]
                        )
                    elementos.append(
                        _construir_tabla(
                            filas, [4.5 * cm, 5.0 * cm, 3.5 * cm, 2.0 * cm, 3.0 * cm]
                        )
                    )
                else:
                    elementos.append(
                        Paragraph(
                            "Este equipo no registra miembros actualmente.",
                            estilos["Normal"],
                        )
                    )

                elementos.append(Spacer(1, 15))
        else:
            elementos.append(
                Paragraph(
                    "No se encontraron equipos estructurados en esta aula.",
                    estilos["Normal"],
                )
            )

    elif filtro == "colaborators":
        elementos.append(Paragraph("Cuerpo de Colaboradores del Aula", estilo_h2))

        with engine.connect() as conn:
            colaboradores = conn.exec_driver_sql(
                """
                SELECT u.username, u.email, cu.role_id
                FROM classroom_users cu
                JOIN users u ON cu.user_id = u.id
                WHERE cu.classroom_id = %s AND cu.role_id IN (1, 2, 3)
                ORDER BY cu.role_id, u.username
                """,
                (classroom_id,),
            ).fetchall()

        if colaboradores:
            filas = [
                [
                    Paragraph("Nombre del Colaborador", estilo_celda_bold),
                    Paragraph("Email de Contacto", estilo_celda_bold),
                    Paragraph("Rol Asignado", estilo_celda_bold),
                ]
            ]
            for c in colaboradores:
                rol_txt = NOMBRE_ROL.get(c[2], "Asistente")
                filas.append(
                    [
                        Paragraph(c[0], estilo_celda),
                        Paragraph(c[1], estilo_celda),
                        Paragraph(rol_txt, estilo_celda),
                    ]
                )
            elementos.append(_construir_tabla(filas, [6.5 * cm, 7.5 * cm, 4.0 * cm]))
        else:
            elementos.append(
                Paragraph(
                    "No hay colaboradores vinculados a este espacio.", estilos["Normal"]
                )
            )

    doc.build(elementos)
    return buffer.getvalue(), None


def _construir_tabla(filas: list, col_widths: list) -> Table:
    tabla = Table(filas, colWidths=col_widths)
    n_filas = len(filas)

    estilo = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), COLOR_HEADER),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("TOPPADDING", (0, 0), (-1, 0), 8),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("ALIGN", (0, 1), (-1, -1), "LEFT"),
            ("TOPPADDING", (0, 1), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]
    )

    for i in range(1, n_filas):
        bg_color = colors.white if i % 2 != 0 else colors.HexColor("#F9FAFB")
        estilo.add("BACKGROUND", (0, i), (-1, i), bg_color)
        estilo.add("LINEBELOW", (0, i), (-1, i), 0.5, COLOR_LINEA)

    tabla.setStyle(estilo)
    return tabla
