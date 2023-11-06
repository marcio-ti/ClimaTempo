from datetime import datetime
import pandas as pd
import dash_bootstrap_components as dbc
import folium
from dash import Dash, html, dcc, callback, Input, Output
from dash import dash_table
from dash.exceptions import PreventUpdate
from meteostat import Point, Daily
import plotly.express as px
import plotly.graph_objects as go

# Data
lat = -29.9153435
lon = -51.2601959
start = datetime( 2023, 1, 1 )
end = datetime( 2023, 11, 6 )
location = Point( lat, lon )
data = Daily( location, start, end )

dados = data.fetch()
dados = dados[['tavg', 'tmin', 'tmax', 'prcp', 'wspd', 'pres', 'tsun']]
dados.rename( columns={
    'tavg': 'Temp. Média',
    'tmin': 'Temp. Min',
    'tmax': 'Temp. Max',
    'prcp': 'Precipitação',
    'wspd': 'Veloc. Vento',
    'pres': 'Pressão',
    'tsun': 'Tempo de Sol'
}, inplace=True )





app = Dash( external_stylesheets=[dbc.themes.ZEPHYR] )

app.layout = html.Div(
    className='p-5',
    children=[
        html.H4('Clima', className='mb-4'),
        dcc.Dropdown(
            id='cidade_selecionada',
            options=['Porto Alegre'],
            value='',
            placeholder='Selecione uma cidade',
            className='hover-blue'
        ),
        html.Div( id='dados', className='mt-4' ),
        html.Div( id='mapa', className='mt-4' ),

        dbc.Label("Variável escolhida"),
        dbc.RadioItems(
            options=[
                {"label": "Temperatura", "value": 'Temperatura'},
                {"label": "Vento", "value": 'Vento'},
                {"label": "Precipitação", "value": 'Precipitacao'},
            ],
            value=1,
            id="grafico_variavel",
        ),
        dcc.Graph( id='grafico' )
    ] )


@callback(
    Output( 'dados', 'children' ),
    Output( "mapa", "children" ),
    Input( 'cidade_selecionada', 'value' ),
    prevent_initial_call=True
)
def climaTempo(cidade):
    if cidade is None:
        raise PreventUpdate
    elif cidade == 'Porto Alegre':

        # Mapa
        map = folium.Map(
            location=[lat, lon], zoom_start=10
        )
        map.save( "mapa_cidade.html" )


        return (dash_table.DataTable(
            dados.to_dict( "records" ),
            style_cell={"textAlign": "center"},
            page_size=30,
            style_data_conditional=[
                {
                    "if": {"row_index": "odd"},
                    "backgroundColor": "rgb(220, 220, 220)",
                }
            ],

        ),
        html.Iframe(
            srcDoc=open( "mapa_cidade.html", "r" ).read(),
            style={"width": "100%", "height": "600px"},
            className="d-flex aligns-items-center justify-content-center rounded mx-auto p-4 ",
        )
        )


@callback(
Output( 'grafico', 'figure' ),
    Input( 'grafico_variavel', 'value' ),
    prevent_initial_call=True
)
def grafico(tipo_grafico):
    if tipo_grafico is None:
        raise PreventUpdate
    else:
        # Gráfico
        if tipo_grafico == 'Temperatura':
            fig = go.Figure(
                data=[
                    go.Scatter(
                        x=dados.index,
                        y=dados['Temp. Média'],
                        line=dict( color="blue", width=2 ),
                        name="Temperatura Média",
                    ),
                    go.Scatter(
                        x=dados.index,
                        y=dados['Temp. Max'],
                        line=dict( color="red", width=2 ),
                        name="Temperatura Máxima",
                    ),
                    go.Scatter(
                        x=dados.index,
                        y=dados['Temp. Min'],
                        line=dict( color="green", width=2 ),
                        name="Temperatura Mínima",
                    )
                ] )
            return fig
        elif tipo_grafico == 'Vento':
            fig = go.Figure(
                data=[
                    go.Scatter(
                        x=dados.index,
                        y=dados['Veloc. Vento'],
                        line=dict( color="blue", width=2 ),
                        name="Velocidade do Vento",
                    )
                ] )
            return fig
        elif tipo_grafico == 'Precipitacao':
            fig = px.bar(dados, x=dados.index, y=dados['Precipitação'])
            return fig



if __name__ == '__main__':
    # app.run( debug=True )
    app.run( host="0.0.0.0", port="8080" )
