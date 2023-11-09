"""
    Aplicativo de pesquisa do histórico de dados climáticos dos municípios
"""

from datetime import datetime

import dash_bootstrap_components as dbc
import folium
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, callback, Input, Output
from dash import dash_table
from dash.exceptions import PreventUpdate
from meteostat import Point, Daily

"""
    Dados coletados via API -> Meteostat
    * Latitude -> lat
    * Longitude -> lon
    * Start -> Data inicial da Consulta
    * End -> Data Final da Consulta
    * Location -> tupla contendo os pontos geográficos para consulta na API
    * data -> Descreve a periodicidade dos dados, neste caso, foi selecioado diário
    ! data.fetch() -> Transforma os dados em um DataFrame apto a ser manupulado
"""
lat = -29.9153435
lon = -51.2601959
start = datetime(2023, 1, 1)
end = datetime(2023, 11, 6)
location = Point(lat, lon)
data = Daily(location, start, end)
dados = data.fetch()

"""
    ? Manipulação dos dados do DataFrame
"""
# ? Cria a coluna Data atrabvés da cópia do index do DataFramme
dados['data'] = dados.index

# ? Seleciona apenas as colunas que serão utilizadas
dados = dados[['data', 'tavg', 'tmin', 'tmax', 'prcp', 'wspd', 'pres', 'tsun']]

# ? Renomeia as colunas
dados.rename(columns={
    'data': 'Data',
    'tavg': 'Temp. Média',
    'tmin': 'Temp. Min',
    'tmax': 'Temp. Max',
    'prcp': 'Precipitação',
    'wspd': 'Veloc. Vento',
    'pres': 'Pressão',
    'tsun': 'Tempo de Sol'
}, inplace=True)

# --------------------------------------------------------------------------------------------------------
"""
    ! Aplicação
"""

#  Criando a Aplicação
app = Dash(external_stylesheets=[dbc.themes.ZEPHYR])

# LAYOUT
app.layout = html.Div(
    className='p-5',
    children=[
        html.H4('Clima', className='mb-4'),
        dcc.Dropdown(
            id='cidade_selecionada',
            options=['Porto Alegre'],
            value='',
            placeholder='Selecione uma cidade',
        ),
        html.Div(id='dados', className='mt-4'),
        html.Div(id='mapa', className='mt-4'),

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
        dcc.Graph(id='grafico')
    ])


# -------------------------------------------------------------------------------------------------------
# Funções da Aplicação
@callback(
    Output('dados', 'children'),
    Output("mapa", "children"),
    Input('cidade_selecionada', 'value'),
    prevent_initial_call=True
)
def clima_tempo(cidade):
    """
    Esta função gera um mapa e uma tabela de dados para a cidade selecionada.

    :param cidade: A cidade selecionada no Dropdown. Se a cidade for None, a função irá parar a atualização.
    :return: Retorna um DataTable e um Iframe. O DataTable contém os dados da cidade selecionada,
            ordenados por data em ordem decrescente. O Iframe contém um mapa da cidade selecionada.
    Exceções:
        PreventUpdate: Se tipo_grafico for None, a função irá lançar uma exceção PreventUpdate.
    """

    # Verifica primeiramente se o valor passado não é "None"
    if cidade is None:
        raise PreventUpdate
    elif cidade == 'Porto Alegre':

        # Cria o mapa centralizando a cidade escolhida no centro
        mapa = folium.Map(
            location=[lat, lon], zoom_start=10, tiles="cartodb positron"
        )
        # Salva o Mapa no formato html
        mapa.save("mapa_cidade.html")

        # Faz uma cópia do DataFrame para manipulação dos dados
        dados_tabela = dados.copy()
        # Ordena a tabela com base nos valores do tipo Data de maneira decrescente
        dados_tabela = dados_tabela.sort_values(by=['Data'], ascending=False)
        # Retira os valores referentes ao tempo, transformando a Data em uma String
        dados_tabela['Data'] = dados_tabela['Data'].dt.strftime('%d-%m-%Y')

        # Retorno da Função
        return (dash_table.DataTable(
            dados_tabela.to_dict("records"),
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
                    srcDoc=open("mapa_cidade.html", "r").read(),
                    style={"width": "100%", "height": "600px"},
                    className="d-flex aligns-items-center justify-content-center rounded mx-auto p-4 ",
                )
        )


@callback(
    Output('grafico', 'figure'),
    Input('grafico_variavel', 'value'),
    prevent_initial_call=True
)
def grafico(tipo_grafico):
    """
    Esta função gera um gráfico com base no tipo de gráfico especificado.

    Parâmetros:
    tipo_grafico (str): O tipo de gráfico a ser gerado. Pode ser 'Temperatura', 'Vento' ou 'Precipitacao'.

    Retorna:
    fig: Um objeto de figura Plotly que representa o gráfico especificado.

    Exceções:
    PreventUpdate: Se tipo_grafico for None, a função irá lançar uma exceção PreventUpdate.
    """
    if tipo_grafico is None:
        raise PreventUpdate
    else:
        # Gráfico
        if tipo_grafico == 'Temperatura':
            fig = go.Figure(
                data=[
                    go.Scatter(
                        x=dados['Data'],
                        y=dados['Temp. Média'],
                        line=dict(color="blue", width=2),
                        name="Temperatura Média",
                    ),
                    go.Scatter(
                        x=dados['Data'],
                        y=dados['Temp. Max'],
                        line=dict(color="red", width=2),
                        name="Temperatura Máxima",
                    ),
                    go.Scatter(
                        x=dados['Data'],
                        y=dados['Temp. Min'],
                        line=dict(color="green", width=2),
                        name="Temperatura Mínima",
                    )
                ])
            return fig
        elif tipo_grafico == 'Vento':
            fig = go.Figure(
                data=[
                    go.Scatter(
                        x=dados['Data'],
                        y=dados['Veloc. Vento'],
                        line=dict(color="blue", width=2),
                        name="Velocidade do Vento",
                    )
                ])
            return fig
        elif tipo_grafico == 'Precipitacao':
            fig = px.bar(dados, x=dados['Data'], y=dados['Precipitação'])
            return fig


# ----------------------------------------------------------------------------------------------------------
# SERVIDOR
if __name__ == '__main__':
    # app.run( debug=True )
    app.run(host="0.0.0.0", port="8080")
