import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output
from dash_bootstrap_templates import ThemeSwitchAIO
from wordcloud import WordCloud, STOPWORDS
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
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

df['horario'] = pd.to_datetime(df['horario'], format='%H:%M:%S')
df['hora'] = df['horario'].dt.hour

def plotNuvemCausaAcidente():

    excluir = ['de','na','dos','da']
    stopwords = STOPWORDS.union(excluir)
    palavras_nuvem = " ".join(df['causa_acidente'])  
    nuvem = WordCloud(width=1000, height=500, background_color='white', stopwords=stopwords).generate(palavras_nuvem)

    fig = px.imshow(nuvem.to_array(), height=1000)
    return fig.update_layout(title='Nuvem de Palavras - Tipo de Acidente',
                  xaxis=dict(showticklabels=False),
                  yaxis=dict(showticklabels=False))

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
                html.H4('Escolha a região que deseja analisar:')
            ]),
            dbc.Row([
                dcc.Dropdown(
                    id='regiao',
                    multi=True,
                    value=df['regiao'].unique()[0:],
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
                html.H4('Escolha a região que deseja analisar:')
            ]),
            dbc.Row([
                dcc.Dropdown(
                    id='regiao2',
                    multi=False,
                    value=df['regiao'].unique()[0],
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

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='nuvem_palavras', figure=plotNuvemCausaAcidente())
        ])
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='scatterplot')
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
    df_filtrado = df[(df['regiao']==regiao) & (df['mortos'] > 0)]

    df_mortes = df_filtrado.groupby(['tipo_acidente', 'regiao'])['mortos'].value_counts().sort_values(ascending=False).reset_index()

    df_mortes['mortos'] = [df_mortes['mortos'][i] * df_mortes['count'][i] for i in range(0,len(df_mortes))]

    df_mortes = df_mortes.groupby(['tipo_acidente', 'regiao'])['mortos'].sum().sort_values(ascending=False).reset_index()

    fig = px.bar(df_mortes,  
                 x='mortos',
                 y='tipo_acidente',
                 color='tipo_acidente',
                 barmode="overlay")
    return fig.update_layout(bargap=0.0, bargroupgap=0.05)

@app.callback(
    Output('scatterplot', 'figure'),
    Input('regiao', 'value'),
)
def scatterFeridosPorTipo(regiao):

    # FERIDOS GRAVES ===================================================================

    #df_filtrado = df[(df['regiao'].isin(regiao)) & (df['feridos_graves'] > 0)]

    #df_feridos = df_filtrado.groupby(['tipo_acidente', 'regiao'])['feridos_graves'].value_counts().sort_values(ascending=False).reset_index()

    #df_feridos['feridos_graves'] = [df_feridos['feridos_graves'][i] * df_feridos['count'][i] for i in range(0,len(df_feridos))]

    #df_feridos = df_feridos.groupby(['tipo_acidente', 'regiao'])['feridos_graves'].sum().sort_values(ascending=False).reset_index()

    #fig = px.scatter(
        #df_feridos,
        #x="tipo_acidente",
        #y="feridos_graves",
        #size="feridos_graves",
        #color="regiao",
        #title=f"Feridos Graves por Tipo de Acidente - Região {regiao}",
        #labels={"feridos_graves": "Total de Feridos Graves", "tipo_acidente": "Tipo de Acidente"},
    #)
    
    #fig.update_traces(marker=dict(opacity=0.8, line=dict(width=1, color='DarkSlateGrey')))
    #fig.update_layout(xaxis_tickangle=-45)

    #return fig
    
    # CONDICAO METEREOLOGICA ======================================================

    #df_filtrado = df[df['regiao'].isin(regiao)]

    #df_causa_horario = df_filtrado.groupby(['causa_acidente', 'regiao'])['condicao_metereologica'].value_counts().sort_values(ascending=True).reset_index(name='count')


    #fig = px.scatter(
        #df_causa_horario,
        #height=700,
        #x="causa_acidente",
        #y="condicao_metereologica",
        #size="count",
        #color="count",
        #title=f"frequencia de horario por causa de acidente - Região {regiao}",
        #labels={"horario": "faixa de hora do acidetnte", "causa_acidente": "motivo do acidente"},
    #)
    
    #fig.update_traces(marker=dict(opacity=0.8, line=dict(width=1, color='DarkSlateGrey')))
    #fig.update_layout(xaxis_tickangle=-45)

    #return fig


# HORARIO ============================================================

    df_filtrado = df[df['regiao'].isin(regiao)]

    df_causa_horario = df_filtrado.groupby(['causa_acidente', 'regiao'])['horario'].value_counts().sort_values(ascending=True).reset_index(name='count')


    fig = px.scatter(
        df_causa_horario,
        height=1000,
        width=1500,
        x="horario",
        y="causa_acidente",
        size="count",
        color="count",
        title=f"frequencia de horario por causa de acidente - Região {regiao}",
        labels={"horario": "faixa de hora do acidetnte", "causa_acidente": "motivo do acidente"},
    )
    
    fig.update_traces(marker=dict(opacity=0.8, line=dict(width=1, color='DarkSlateGrey')))
    fig.update_layout(xaxis_tickangle=-45)

    return fig


if __name__ == '__main__':
    app.run(debug=True, port='8051')