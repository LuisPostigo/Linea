import bcrypt
from fastapi import Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os

# Apuntar correctamente a /interface/templates
BASE_DIR = os.path.dirname(__file__)
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "interface", "templates"))

# Usuarios hardcoded con nombre, email y rol
USERS = {
    "luispostigo": {
        "password": bcrypt.hashpw("abcd".encode(), bcrypt.gensalt()),
        "name": "Luis Postigo",
        "email": "luis@example.com",
        "role": "user"
    },
    "danipostigo": {
        "password": bcrypt.hashpw("1234".encode(), bcrypt.gensalt()),
        "name": "Daniela Postigo",
        "email": "dani@example.com",
        "role": "admin"
    }
}

# Mostrar pantalla de login
async def show_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": False})

# Procesar login
async def process_login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = USERS.get(username)
    if user and bcrypt.checkpw(password.encode(), user["password"]):
        response = RedirectResponse("/", status_code=303)
        response.set_cookie("username", username)
        response.set_cookie("name", user["name"])
        response.set_cookie("email", user["email"])
        response.set_cookie("role", user["role"])
        return response
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": True})

# Procesar logout
async def logout():
    response = RedirectResponse("/login", status_code=303)
    for cookie in ["username", "name", "email", "role"]:
        response.delete_cookie(cookie)
    return response
