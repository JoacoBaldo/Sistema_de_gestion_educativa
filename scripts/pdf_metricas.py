import io
from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.db import classroom as db_classroom
from src.db import metrics as db_metrics
from src.db.constantes import ADMINISTRADOR, AYUDANTE, PROFESOR
from src.funciones.errores import (
    BODY_INVALIDO,
    CLASSROOM_NO_EXISTE,
    FILTRO_INVALIDO,
    NO_ES_ADMIN,
    SIN_ACCESO,
)

# ── Constantes ────────────────────────────────────────────────────────────────

FILTROS_VALIDOS = {"students", "students_passed", "teams", "colaborators"}

NOMBRE_ROL = {PROFESOR: "Profesor", AYUDANTE: "Ayudante", ADMINISTRADOR: "Administrador"}

COLOR_HEADER = colors.HexColor("#1a3557")
COLOR_FILA_PAR = colors.HexColor("#eaf0f8")
COLOR_BORDE = colors.HexColor("#a0b4cc")


# ── Punto de entrada público ──────────────────────────────────────────────────

def generar_pdf_metricas(
    classroom_id: int,
    usuario_id: int,
    datos_metricas: dict,
    filtro: str | None,
) -> tuple:
    if filtro is not None and filtro not in FILTROS_VALIDOS:
        return None, FILTRO_INVALIDO

    campos_requeridos = {
        "promedio_aprobados",
        "ingresos_por_año",
        "total_estudiantes",
        "total_activos",
        "total_abandonaron",
    }
    if not campos_requeridos.issubset(datos_metricas.keys()):
        return None, BODY_INVALIDO

    if not db_classroom.existe_classroom(classroom_id):
        return None, CLASSROOM_NO_EXISTE

    if not db_classroom.usuario_en_classroom(classroom_id, usuario_id):
        return None, SIN_ACCESO

    if not db_classroom.puede_administrar_classroom(classroom_id, usuario_id):
        return None, NO_ES_ADMIN

    tabla_extra, titulo_extra, columnas_extra = _obtener_datos_filtro(classroom_id, filtro)

    pdf_bytes = _construir_pdf(
        classroom_id=classroom_id,
        datos_metricas=datos_metricas,
        tabla_extra=tabla_extra,
        titulo_extra=titulo_extra,
        columnas_extra=columnas_extra,
    )
    return pdf_bytes, None


# ── Resolución de datos por filtro ────────────────────────────────────────────

def _obtener_datos_filtro(
    classroom_id: int,
    filtro: str | None,
) -> tuple[list | None, str | None, list | None]:
    if filtro is None:
        return None, None, None

    if filtro == "students":
        filas = db_metrics.obtener_alumnos_activos(classroom_id)
        return (
            [[f["id"], f["username"], f["email"], _fmt_fecha(f["created_at"])] for f in filas],
            "Alumnos Activos",
            ["ID", "Usuario", "Email", "Ingresó"],
        )

    if filtro == "students_passed":
        filas = db_metrics.obtener_alumnos_aprobados_activos(classroom_id)
        return (
            [[f["id"], f["username"], f["email"], _fmt_fecha(f["created_at"])] for f in filas],
            "Alumnos Activos y Aprobados",
            ["ID", "Usuario", "Email", "Ingresó"],
        )

    if filtro == "teams":
        filas = db_metrics.obtener_equipos(classroom_id)
        return (
            [
                [
                    f["id"],
                    f["name"],
                    f["classroom_id"],
                    _fmt_fecha(f["created_at"]),
                    _fmt_fecha(f["updated_at"]),
                ]
                for f in filas
            ],
            "Equipos",
            ["ID", "Nombre", "Classroom ID", "Creado", "Actualizado"],
        )

    if filtro == "colaborators":
        filas = db_metrics.obtener_colaboradores(classroom_id)
        return (
            [
                [
                    f["id"],
                    f["username"],
                    f["email"],
                    NOMBRE_ROL.get(f["role_id"], str(f["role_id"])),
                    _fmt_fecha(f["created_at"]),
                ]
                for f in filas
            ],
            "Colaboradores",
            ["ID", "Usuario", "Email", "Rol", "Ingresó"],
        )

    return None, None, None


# ── Builder PDF ───────────────────────────────────────────────────────────────

def _construir_pdf(
    classroom_id: int,
    datos_metricas: dict,
    tabla_extra: list | None,
    titulo_extra: str | None,
    columnas_extra: list | None,
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        "Titulo",
        parent=estilos["Title"],
        fontSize=20,
        textColor=COLOR_HEADER,
        spaceAfter=4,
        fontName="Helvetica-Bold",
    )
    estilo_subtitulo = ParagraphStyle(
        "Subtitulo",
        parent=estilos["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#555555"),
        spaceAfter=2,
        fontName="Helvetica",
    )
    estilo_seccion = ParagraphStyle(
        "Seccion",
        parent=estilos["Normal"],
        fontSize=13,
        textColor=COLOR_HEADER,
        spaceBefore=14,
        spaceAfter=6,
        fontName="Helvetica-Bold",
    )

    elementos = []

    # Encabezado
    elementos.append(Paragraph("Reporte de Métricas", estilo_titulo))
    elementos.append(Paragraph(f"Classroom ID: {classroom_id}", estilo_subtitulo))
    elementos.append(
        Paragraph(f"Fecha de generación: {date.today().strftime('%d/%m/%Y')}", estilo_subtitulo)
    )
    elementos.append(Spacer(1, 0.5 * cm))

    # Resumen general
    elementos.append(Paragraph("Resumen General", estilo_seccion))
    filas_resumen = [
        ["Métrica", "Valor"],
        ["Promedio de aprobados", f"{datos_metricas['promedio_aprobados']}%"],
        ["Total de estudiantes", str(datos_metricas["total_estudiantes"])],
        ["Estudiantes activos", str(datos_metricas["total_activos"])],
        ["Estudiantes que abandonaron", str(datos_metricas["total_abandonaron"])],
    ]
    elementos.append(_construir_tabla(filas_resumen, col_widths=[9 * cm, 7 * cm]))
    elementos.append(Spacer(1, 0.4 * cm))

    # Ingresos por año
    elementos.append(Paragraph("Ingresos por Año", estilo_seccion))
    ingresos = datos_metricas.get("ingresos_por_año", [])
    if ingresos:
        filas_ingresos = [["Año", "Total de estudiantes"]] + [
            [str(i["year"]), str(i["total"])] for i in ingresos
        ]
        elementos.append(_construir_tabla(filas_ingresos, col_widths=[8 * cm, 8 * cm]))
    else:
        elementos.append(Paragraph("Sin datos de ingresos registrados.", estilos["Normal"]))
    elementos.append(Spacer(1, 0.4 * cm))

    # Tabla filtrada (opcional)
    if tabla_extra is not None and columnas_extra is not None:
        elementos.append(Paragraph(titulo_extra, estilo_seccion))
        if tabla_extra:
            ancho_col = (17 * cm) / len(columnas_extra)
            filas_extra = [columnas_extra] + tabla_extra
            elementos.append(
                _construir_tabla(filas_extra, col_widths=[ancho_col] * len(columnas_extra))
            )
        else:
            elementos.append(Paragraph("No hay registros para mostrar.", estilos["Normal"]))

    doc.build(elementos)
    return buffer.getvalue()


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
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDE),
            ("BOX", (0, 0), (-1, -1), 1, COLOR_HEADER),
        ]
    )

    for i in range(2, n_filas, 2):
        estilo.add("BACKGROUND", (0, i), (-1, i), COLOR_FILA_PAR)

    tabla.setStyle(estilo)
    return tabla


def _fmt_fecha(valor) -> str:
    if valor is None:
        return "-"
    if isinstance(valor, date):
        return valor.strftime("%d/%m/%Y")
    return str(valor)
