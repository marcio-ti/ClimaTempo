from dash import Dash, html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import requests
import json


app = Dash(external_stylesheets=[dbc.themes.ZEPHYR])


api_key = 'c18c40053572110cfdb4e76a96fe91f9'
lat =-29.9713841
long = -51.168997



app.layout = html.Div([
    dcc.Dropdown(
        id='cidade_selecionada',
        options=['CANOAS'],
        value='CANOAS',
        placeholder='Selecione uma cidade'
    ),
    html.Div(id='dados')
])


@callback(
    Output('dados','children'),
    Input('cidade_selecionada','value')
)
def climaTempo(cidade):

    response = requests.get(f"api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={long}&appid={api_key}")

    return f"{response}"


if __name__ == '__main__':
    app.run(debug=True)