# ./dash_app/app.py
import dash
from dash import html, dcc, callback, Input, Output
from datetime import datetime
import requests
 
# Initialiser l'application Dash
app = dash.Dash(__name__, requests_pathname_prefix='/dashboard/')
 
# Configuration API - Utiliser votre API Azure déployée
AZURE_API_URL = 'https://meteo-casablanca-api-hsd2hrhzemfvh3as.canadaeast-01.azurewebsites.net'
 
def get_weather():
    """
    Récupère les données météo depuis votre API Azure
    """
    try:
        # Appel à votre endpoint /info sur Azure
        response = requests.get(f"{AZURE_API_URL}/info", timeout=10)
        response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP
       
        data = response.json()
       
        # Extraire les données météo de la réponse
        weather = {
            'city': data['weather']['city'],
            'temperature': data['weather']['temperature'],
            'description': data['weather']['description'],
            'date': data['date'],
            'time': data['time']
        }
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'appel à l'API Azure: {e}")
        weather = {
            'city': 'N/A',
            'temperature': 'N/A',
            'description': 'N/A',
            'date': 'N/A',
            'time': 'N/A'
        }
    except KeyError as e:
        print(f"Erreur dans la structure des données reçues: {e}")
        weather = {
            'city': 'N/A',
            'temperature': 'N/A',
            'description': 'N/A',
            'date': 'N/A',
            'time': 'N/A'
        }
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        weather = {
            'city': 'N/A',
            'temperature': 'N/A',
            'description': 'N/A',
            'date': 'N/A',
            'time': 'N/A'
        }
   
    return weather
 
# Layout de l'application
app.layout = html.Div(children=[
    html.Div([
        html.A('Accueil', href='/'),
        " | ",
        html.A("Logout", href="/logout")
    ], style={'marginTop': 25}),
   
    html.H1(children="Dashboard Météo - Données depuis Azure API"),
   
    # Section météo avec données depuis Azure
    html.H2("*** Météo Casablanca (via Azure API) ***"),
    html.Div([
        html.P(f"API Source: {AZURE_API_URL}", style={'fontSize': '12px', 'color': 'gray'}),
        html.Div(id="weather-info"),
        html.Button('Actualiser', id='refresh-button', style={'margin': '10px'})
    ], style={'border': '1px solid #ccc', 'padding': '10px', 'margin': '10px'}),
   
    html.H2("*** Bar Graph ***"),
    dcc.Graph(
        id="exm1",
        figure={
            "data": [
                {"x": [5, 7, 12], "y": [10, 16, 11], "type": "bar", "name": "exemple1"},
                {"x": [8, 18, 22], "y": [5, 8, 3], "type": "bar", "name": "exemple2"}
            ],
            "layout": {"title": "Exemple de graphique en barres"}
        }
    ),
   
    html.H2("*** Line Graph ***"),
    dcc.Graph(
        id="exm2",
        figure={
            "data": [
                {"x": [1, 3, 5], "y": [10, 12, 14], "type": "line", "name": "exemple3"},
                {"x": [2, 4, 6], "y": [13, 15, 17], "type": "line", "name": "exemple4"}
            ],
            "layout": {"title": "Exemple de graphique linéaire"}
        }
    ),
   
    html.H2("*** Scatter Plot Graph ***"),
    dcc.Graph(
        id="exm3",
        figure={
            "data": [
                {"x": [1, 3, 5, 7], "y": [10, 12, 14, 16], "type": "scatter", "mode": "markers", "name": "scatter exemple1"},
                {"x": [2, 4, 6, 8], "y": [13, 15, 17, 19], "type": "scatter", "mode": "markers", "name": "scatter exemple2"}
            ],
            "layout": {"title": "Exemple de graphique de dispersion"}
        }
    ),
   
    html.H2("*** Pie Chart Graph ***"),
    dcc.Graph(
        id="exm4",
        figure={
            "data": [
                {"labels": ["A", "B", "C"], "values": [10, 12, 14], "type": "pie", "name": "pie chart exemple1"},
            ],
            "layout": {"title": "Exemple de graphique circulaire"}
        }
    ),
   
    # Interval pour mise à jour automatique
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # Mise à jour toutes les minutes
        n_intervals=0
    )
])
 
# Callback pour mettre à jour les informations météo
@callback(
    Output('weather-info', 'children'),
    [Input('refresh-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')]
)
def update_weather_info(n_clicks, n_intervals):
    weather = get_weather()
    current_time = datetime.now().strftime("%H:%M:%S")
   
    return html.Div([
        html.H4("Données depuis Azure API:", style={'color': 'blue'}),
        html.P(f"🌍 Ville: {weather['city']}"),
        html.P(f"🌡️ Température: {weather['temperature']}°C"),
        html.P(f"☁️ Description: {weather['description']}"),
        html.P(f"📅 Date API: {weather.get('date', 'N/A')}"),
        html.P(f"⏰ Heure API: {weather.get('time', 'N/A')}"),
        html.P(f"🔄 Mise à jour Dashboard: {current_time}"),
        html.Hr(),
        html.P("✅ Connecté à l'API Azure" if weather['city'] != 'N/A' else "❌ Erreur de connexion à l'API",
               style={'color': 'green' if weather['city'] != 'N/A' else 'red'})
    ], style={'backgroundColor': '#f0f0f0', 'padding': '10px', 'borderRadius': '5px'})
 
server = app.server