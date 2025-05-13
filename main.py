import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import sqlite3
from sqlite3 import connect
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from auth import show_login, process_login, logout

from linea.data_ingestion.data_ingestion_service import DataIngestionService

app = FastAPI()

# Montar archivos estáticos (CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="interface/static"), name="static")
templates = Jinja2Templates(directory="interface/templates")

@app.get("/assets-list")
def list_assets():
    assets_dir = os.path.join("interface", "static", "assets")
    try:
        files = os.listdir(assets_dir)
        pngs = [f"/static/assets/{f}" for f in files if f.lower().endswith(".png")]
        return JSONResponse(content=pngs)
    except FileNotFoundError:
        return JSONResponse(content=[], status_code=404)

# Ruta principal
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    username = request.cookies.get("username")
    name = request.cookies.get("name")
    role = request.cookies.get("role", "user")
    if not username:
        return RedirectResponse("/login")
    return templates.TemplateResponse("index.html", {
        "request": request,
        "username": username,
        "name": name,
        "role": role
    })

# Ruta de acción para los botones
@app.post("/navigate", response_class=HTMLResponse)
def navigate(request: Request, action: str = Form(...)):
    if action == "reportar":
        return RedirectResponse("/reportar", status_code=303)
    elif action == "modificar":
        return RedirectResponse("/modificar", status_code=303)
    elif action == "ver_todos":
        return RedirectResponse("/ver-todos", status_code=303)
    elif action == "admin_usuarios":
        return RedirectResponse("/admin-usuarios", status_code=303)
    elif action == "logout":
        return RedirectResponse("/logout", status_code=303)

# Vista para reportar parada
@app.get("/reportar", response_class=HTMLResponse)
def reportar(request: Request):
    username = request.cookies.get("username")
    name = request.cookies.get("name")
    if not username:
        return RedirectResponse("/login")
    return templates.TemplateResponse("reportar.html", {"request": request, "username": username, "name": name})

@app.get("/modificar", response_class=HTMLResponse)
def modificar(request: Request):
    username = request.cookies.get("username")
    name = request.cookies.get("name")
    if not username:
        return RedirectResponse("/login")

    db_path = os.path.join("data", "database", "events.db")
    with connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM events 
            WHERE Usuario = ?
            ORDER BY COALESCE(id_origen, id) DESC, id DESC
        """, (username,))
        all_reports = cursor.fetchall()

    # Group by id_origen (or id if null)
    grouped = {}
    for row in all_reports:
        origin = row["id_origen"] or row["id"]
        grouped.setdefault(origin, []).append(row)

    return templates.TemplateResponse("modificar.html", {
        "request": request,
        "username": username,
        "name": name,
        "reportes": grouped
    })

@app.get("/editar-reporte", response_class=HTMLResponse)
def editar_reporte(request: Request, reporte_id: int):
    username = request.cookies.get("username")
    if not username:
        return RedirectResponse("/login")

    # Fetch the report from DB
    service = DataIngestionService()
    db_path = service.db_saver.db_path

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {service.db_saver.table_name} WHERE id = ?", (reporte_id,))
        row = cursor.fetchone()

    if not row:
        return HTMLResponse("Reporte no encontrado", status_code=404)

    origin_id = row["id_origen"] if row["id_origen"] else row["id"]

    data = dict(row)
    data["id_origen"] = origin_id  # Make sure we carry original ID for further edits

    return templates.TemplateResponse("reportar.html", {
        "request": request,
        "username": username,
        "data": data
    })

# Vista solo para administradores
@app.get("/ver-todos", response_class=HTMLResponse)
def ver_todos(request: Request):
    username = request.cookies.get("username")
    name = request.cookies.get("name")
    role = request.cookies.get("role", "user")
    if not username or role != "admin":
        return RedirectResponse("/")

    db_path = os.path.join("data", "database", "events.db")
    with connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM events 
            ORDER BY COALESCE(id_origen, id) DESC, id DESC
        """)
        all_reports = cursor.fetchall()

    grouped = {}
    for row in all_reports:
        origin = row["id_origen"] or row["id"]
        grouped.setdefault(origin, []).append(row)

    return templates.TemplateResponse("ver_todos.html", {
        "request": request,
        "username": username,
        "name": name,
        "reportes": grouped
    })
@app.get("/admin-usuarios", response_class=HTMLResponse)
def admin_usuarios(request: Request):
    username = request.cookies.get("username")
    name = request.cookies.get("name")
    role = request.cookies.get("role", "user")
    if not username or role != "admin":
        return RedirectResponse("/")
    return templates.TemplateResponse("admin_usuarios.html", {"request": request, "username": username, "name": name})

# Rutas para login/logout
@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return await show_login(request)

@app.post("/login", response_class=HTMLResponse)
async def login_post(request: Request):
    form = await request.form()
    return await process_login(request, form.get("username"), form.get("password"))

@app.get("/logout", response_class=HTMLResponse)
async def logout_user():
    return await logout()

@app.post("/guardar-reporte")
async def guardar_reporte(
    request: Request,
    planta: str = Form(...),
    periodo: str = Form(...),
    fecha_inicio: str = Form(...),
    fecha_termino: str = Form(...),
    material: str = Form(...),
    descripcion: str = Form(...),
    batch: str = Form(...),
    vendedor: str = Form(...),
    complain_qty: str = Form(...),
    tiempo_parada: str = Form(...),
    consecuencia: str = Form(...),
    id_origen: str = Form(None)  # Optional
):
    username = request.cookies.get("username", "desconocido")

    # ensure id_origen keeps propagating from oldest version
    final_id_origen = id_origen
    if id_origen:
        with sqlite3.connect(os.path.join("data", "database", "events.db")) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id_origen FROM events WHERE id = ?", (id_origen,))
            existing = cursor.fetchone()
            if existing and existing["id_origen"]:
                final_id_origen = existing["id_origen"]

    event_data = {
        "Usuario": username,
        "Planta": planta,
        "Periodo": periodo,
        "Fecha_de_inicio": fecha_inicio,
        "Fecha_de_termino": fecha_termino,
        "Material": material,
        "Descripcion_del_material": descripcion,
        "Batch": batch,
        "Vendedor": vendedor,
        "Complain_Qty": complain_qty,
        "Tiempo_de_parada": tiempo_parada,
        "Consecuencia": consecuencia,
        "id_origen": final_id_origen
    }

    # Guardar en DB
    service = DataIngestionService()
    service.ingest_event(event_data)

    return RedirectResponse(url="/", status_code=303)
