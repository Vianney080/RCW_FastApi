import sys ,os
sys.path.append(os.path.abspath(os.path.dirname(__file__),'..'))

from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import WSGIMiddleware
import uvicorn
from dash_app import app as app_dash

# Create FastAPI app
app = FastAPI()

#obtenir le chemin absolu vers le repertoire des models
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))

#obtenu le chemin absolu vers le repertoire des static
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))

# Configure Jinja2 pour le rendu des fichiers HTML
templates = Jinja2Templates(directory=template_dir)

#servir des fichiers statiques
app.mount("static", StaticFiles(directory=static_dir))

#Montez l’application Dash sous le chemin /dashboard
app.mount("/dashboard", WSGIMiddleware(app_dash.server))

users = {"admin": "123"}

@app.get("/")
async def home_page(request: Request):
    return templates.TemplateResponse('home.html', {'request': request})

# recupere et affiche le formulaire  login.html
@app.get("/login")
async def login_page(request: Request):  # ⚠️ renommé ici
    return templates.TemplateResponse('login.html', {'request': request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username in users and users[username] == password:
        response = RedirectResponse(url="/dashboard", status_code=303)
        response.set_cookie(key="authorisation", value="bearer token", httponly=True)
        return response
    return templates.TemplateResponse('login.html', {'request': request, 'error': 'Invalid username or password'})


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="authoriastion")
    return response
