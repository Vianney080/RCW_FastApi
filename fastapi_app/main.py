# ./fastapi_app/main.py
import sys
import os
from datetime import datetime
 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
 
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.templating import Jinja2Templates
import uvicorn
import requests
from dash_app.app import app as app_dash
 
# Configuration météo
CITY = 'Paris'
API_KEY = 'cec4b9a7d244be85582aa78b28423f2e'
 
def get_weather():
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
   
    try:
        response = requests.get(weather_url)
        data = response.json()
       
        weather = {
            'city': data['name'],
            'temperature': data['main']['temp'],
            'description': data['weather'][0]['description']
        }
    except Exception as e:
        print(e)
        weather = {
            'city': 'N/A',
            'temperature': 'N/A',
            'description': 'N/A'
        }
    return weather
 
# Créer l'objet FastAPI
app = FastAPI()
 
# Obtenir le chemin absolu vers le répertoire des templates
templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "templates"))
 
# Obtenir le chemin absolu vers le répertoire statique
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))
 
# Configurer Jinja2
templates = Jinja2Templates(directory=templates_dir)
 
# Créer le répertoire static s'il n'existe pas
os.makedirs(static_dir, exist_ok=True)
 
# Servir des fichiers statiques
app.mount("/static", StaticFiles(directory=static_dir), name="static")
 
# Monter l'application Dash
app.mount("/dashboard", WSGIMiddleware(app_dash.server))
 
# Base de données utilisateurs
users = {"admin": "123"}
 
@app.get("/")
async def root():
    return {"message": "FastAPI-Dash App is running!", "status": "OK"}
 
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
 
@app.get("/info")
async def get_info():
    current_datetime = datetime.now()
    formatted_date = current_datetime.strftime("%Y-%m-%d")
    formatted_time = current_datetime.strftime("%H:%M:%S")
 
    weather = get_weather()
   
    return {
        "date": formatted_date,
        "time": formatted_time,
        "weather": weather
    }
 
@app.get("/home")
async def home_page(request: Request):
    return templates.TemplateResponse('home.html', {"request": request})
 
@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse('login.html', {"request": request})
 
@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username in users and users[username] == password:
        response = RedirectResponse(url='/dashboard/', status_code=302)
        response.set_cookie(key="Authorization", value="Bearer Token", httponly=True)
        return response
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Invalid username and password"
    })
 
@app.get("/logout")
async def logout():
    response = RedirectResponse(url='/login')
    response.delete_cookie('Authorization')
    return response
 
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
 