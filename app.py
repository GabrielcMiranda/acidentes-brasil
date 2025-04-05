import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output
from dash_bootstrap_templates import ThemeSwitchAIO
import plotly.express as px
import pandas as pd
import seaborn as sns

app = dash.Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])
server = app.server

df = pd.read_csv('Dados_PRF_2022.csv', encoding = 'latin1', sep = ';')

# Tratamento
df = df.dropna(subset=['uop', 'br', 'km'])
df['delegacia'] = df['delegacia'].fillna(df['uop'].apply(lambda x: '-'.join(x.split('-')[1:])))

# Definindo regioes
norte = ['PA', 'AM', 'RR', 'RO', 'AC', 'AP', 'TO']
nordeste = ['MA', 'PI', 'BA', 'CE', 'RN', 'PB', 'PE', 'AL', 'SE']
centro_oeste = ['MT', 'MS', 'GO', 'DF']
sudeste = ['MG', 'ES', 'RJ', 'SP']
sul = ['PR', 'SC', 'RS']

def definir_regiao(estado):
    if estado in norte:
        return 'Norte'
    elif estado in nordeste:
        return 'Nordeste'
    elif estado in centro_oeste:
        return 'Centro Oeste'
    elif estado in sudeste:
        return 'Sudeste'
    else:
        return 'Sul'
    
df['regiao'] = df['uf'].apply(lambda x: definir_regiao(x))

# def barPlotAcidentesDiaSemana():
#     df_qtd_acidentes = df['dia_semana'].value_counts().reset_index()
#     df_qtd_acidentes.columns = ['dia_semana', 'quantidade']

#     fig = px.bar(df_qtd_acidentes,  
#                  x='dia_semana',
#                  y='quantidade',
#                  color='dia_semana',
#                  barmode="group")
#     return fig

app.layout = dbc.Container([

    # 1 LINHA
    dbc.Row([
        dbc.Col([
            html.H1(''),
            html.Hr(),
            html.H5('')
        ]),
    ]),

    # 2 LINHA
    dbc.Row([
        dbc.Col([
            html.Br(),
            html.Br(),
            html.H2(),
        ]),
    ]),

    # 3 LINHA
    dbc.Row([
        dbc.Col([
            html.Br(),
            html.Br(),
            dbc.Row([
                html.H4('Escolha a região ou estado que deseja analisar:')
            ]),
            dbc.Row([
                dcc.Dropdown(
                    id='regiao',
                    multi=True,
                    value=df['regiao'].unique()[:2],
                    options=[{'label': regiao, 'value': regiao} for regiao in df['regiao'].unique()]
                )
            ])
        ]),
        dbc.Col([
            dbc.Row([])
        ])
    ]),

    # 4 LINHA
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='bar_plot_regiao_dia_semana')
        ])
    ]),

    # 5 LINHA
    dbc.Row([
        dbc.Col([
            html.Br(),
            html.Br(),
            dbc.Row([
                html.H4('Escolha a região ou estado que deseja analisar:')
            ]),
            dbc.Row([
                dcc.Dropdown(
                    id='regiao2',
                    multi=True,
                    value=df['regiao'].unique()[:2],
                    options=[{'label': regiao, 'value': regiao} for regiao in df['regiao'].unique()]
                )
            ])
        ]),
        dbc.Col([
            dbc.Row([])
        ])
    ]),

    # 6 LINHA
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='bar_plot_morte_por_regiao')
        ])
    ]),

])

@app.callback(
    Output('bar_plot_regiao_dia_semana', 'figure'),
    Input('regiao', 'value'),
)
def barPlotRegiaoDiaSemana(regiao):
    df_filtrado = df[df['regiao'].isin(regiao)]

    df_regiao_dia_semana = df_filtrado.groupby(['dia_semana', 'regiao']).size().reset_index(name='quantidade')

    fig = px.bar(df_regiao_dia_semana,  
                 x='dia_semana',
                 y='quantidade',
                 color='regiao',
                 barmode="group")
    return fig

@app.callback(
    Output('bar_plot_morte_por_regiao', 'figure'),
    Input('regiao2', 'value'),
)
def barPlotMortePorRegiao(regiao):
    df_filtrado = df[(df['regiao'].isin(regiao)) & (df['mortos'] > 0)]

    df_mortes = df_filtrado.groupby('regiao')['mortos'].sum().reset_index()

    fig = px.bar(df_mortes,  
                 x='regiao',
                 y='mortos',
                 color='regiao',
                 barmode="group")
    return fig

if __name__ == '__main__':
    app.run(debug=True, port='8051')