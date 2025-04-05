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
                    value=df['uf'].unique()[:2],
                    options=[{'label': estado, 'value': estado} for estado in df['uf'].unique()] + [{'label': regiao, 'value': regiao} for regiao in df['regiao'].unique()]
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

])

@app.callback(
    Output('bar_plot_regiao_dia_semana', 'figure'),
    Input('regiao', 'value'),
)
def barPlotRegiaoDiaSemana(regiao):
    df_filtrado = df[df['uf'].isin(regiao) | df['regiao'].isin(regiao)]

    df_regiao_dia_semana = df_filtrado.groupby(['dia_semana', 'uf']).size().reset_index(name='quantidade')

    fig = px.bar(df_regiao_dia_semana,  
                 x='dia_semana',
                 y='quantidade',
                 color='uf',
                 barmode="group")
    return fig

    #ordem_dias = ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado', 'domingo']
    #df_regiao_horario[horario] = pd.Categorical(df_regiao_horario[horario], categories=ordem_dias, ordered=True)

#@app.callback(
   # Output('bar_plot_media_minutos', 'figure'),
   # Input('escolha_faixa_etaria2', 'value'),
#)
#def barPlotMediaMinutos(escolha_faixa_etaria):
  #  df_media = df[df['Age Group'].isin(escolha_faixa_etaria)].groupby('Age Group')['Minutes Streamed Per Day'].mean()


  #  fig = px.bar(df_media.reset_index(),
  #               x='Age Group',
   #              y='Minutes Streamed Per Day',
   #              color='Age Group')
   # return fig

if __name__ == '__main__':
    app.run(debug=True, port='8051')