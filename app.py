import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output
from dash_bootstrap_templates import ThemeSwitchAIO
from wordcloud import WordCloud, STOPWORDS
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

app = dash.Dash(__name__, external_stylesheets = [dbc.themes.LUX])
server = app.server

df = pd.read_csv('Dados_PRF_2022.csv', encoding = 'latin1', sep = ';')

# Tratamento
df = df.dropna(subset=['uop', 'br', 'km'])
df['delegacia'] = df['delegacia'].fillna(df['uop'].apply(lambda x: '-'.join(x.split('-')[1:])))
df['horario'] = pd.to_datetime(df['horario'], format='%H:%M:%S')
df['hora'] = df['horario'].dt.hour


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


# funcao nuvem de palavras
def plotNuvemCausaAcidente():

    excluir = ['de','na','dos','da']
    stopwords = STOPWORDS.union(excluir)
    palavras_nuvem = " ".join(df['causa_acidente'])  
    nuvem = WordCloud(width=1000, height=500, background_color='white', stopwords=stopwords).generate(palavras_nuvem)

    fig = px.imshow(nuvem.to_array(), height=1000)
    return fig.update_layout(
                  xaxis=dict(showticklabels=False),
                  yaxis=dict(showticklabels=False))

app.layout = dbc.Container([

    # NOME DO SITE
    dbc.Row([
        dbc.Col([
            html.H1('incidentes de trânsito no Brasil'),
            html.Hr(),
            html.H5('Este dashboard tem como objetivo comparar os perfis de incidentes de trânsito entre diferentes regiões do Brasil.')
        ]),
    ]),

# QUANTIDADE DE ACIDENTES POR DIA DA SEMANA ===========================================================
    #titulo
    dbc.Row([
        dbc.Col([
            html.Br(),
            html.Br(),
            html.H2('Quantidade de acidentes por dia da semana:'),
        ]),
    ]),
    #select box
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
    #grafico
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='bar_plot_regiao_dia_semana')
        ])
    ]),

# FREQUENCIA DOS TIPOS DE ACIDENTE POR REGIAO ==============================================
    #titulo
     dbc.Row([
        dbc.Col([
            html.Br(),
            html.Br(),
            html.H2('Quantidade de mortes por tipo de acidente:'),
        ]),
    ]),
    #select box
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
    #grafico
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='bar_plot_tipo_acidente_regiao')
        ])
    ]),

# NUVEM DE PALAVRAS =================================================================
     dbc.Row([
        dbc.Col([
            html.Br(),
            html.Br(),
            html.H2('Nuvem de palavras das causas de acidente:'),
        ]),
    ]),
    #grafico
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='nuvem_palavras', figure=plotNuvemCausaAcidente())
        ])
    ]),

# RELACAO HORARIO ACIDENTE =============================================================

    #titulo
    dbc.Row([
        dbc.Col([
            html.Br(),
            html.Br(),
            html.H2('Relação entre horário e acidentes:'),
        ]),
        #select box
        dbc.Row([
            dbc.Col([
                html.Br(),
                html.Br(),
                dbc.Row([
                    html.H4('Escolha a região que deseja analisar:')
                ]),
                dbc.Row([
                    dcc.Dropdown(
                    id='regiao3',
                    multi=True,
                    value=df['regiao'].unique()[:2],
                    options=[{'label': regiao, 'value': regiao} for regiao in df['regiao'].unique()]
                )
                ]),
            ]),
            dbc.Col([
                html.Br(),
                html.Br(),
                dbc.Row([
                    html.H4('Escolha a relação de acidente:')
                ]),
                dbc.Row([
                    dcc.Dropdown(
                    id='tipo_acidente1',
                    multi=False,
                    value='causa_acidente',
                    options=[{'label': 'Causa do Acidente', 'value': 'causa_acidente'},
                            {'label': 'Tipo de Acidente', 'value': 'tipo_acidente'}]
                )
                ]),
            ])
        ]),
        #grafico
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='scatterplot_horario_acidente')
            ])
        ])
    ]),

# RELACAO FERIDOS ACIDENTE =====================================================================

    #titulo
    dbc.Row([
        dbc.Col([
            html.Br(),
            html.Br(),
            html.H2('Relação entre número de feridos graves e acidentes:'),
        ]),
        #select box
        dbc.Row([
            dbc.Col([
                html.Br(),
                html.Br(),
                dbc.Row([
                    html.H4('Escolha a região que deseja analisar:')
                ]),
                dbc.Row([
                    dcc.Dropdown(
                    id='regiao4',
                    multi=True,
                    value=df['regiao'].unique()[:2],
                    options=[{'label': regiao, 'value': regiao} for regiao in df['regiao'].unique()]
                )
                ])
            ]),
            dbc.Col([
                html.Br(),
                html.Br(),
                dbc.Row([
                    html.H4('Escolha a relação de acidente:')
                ]),
                dbc.Row([
                    dcc.Dropdown(
                    id='tipo_acidente2',
                    multi=False,
                    value='causa_acidente',
                    options=[{'label': 'Causa do Acidente', 'value': 'causa_acidente'},
                            {'label': 'Tipo de Acidente', 'value': 'tipo_acidente'}]
                )
                ]),
            ])
        ]),
        #grafico
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='scatterplot_feridos_acidente')
            ])
        ])
    ]),

#RELACAO CONDICAO METEREOLOGICA ACIDENTE ==========================================================
    #titulo
    dbc.Row([
        dbc.Col([
            html.Br(),
            html.Br(),
            html.H2('Relação entre condição metereológica e acidentes:'),
        ]),
        #selectbox
        dbc.Row([
            dbc.Col([
                html.Br(),
                html.Br(),
                dbc.Row([
                    html.H4('Escolha a região que deseja analisar:')
                ]),
                dbc.Row([
                    dcc.Dropdown(
                    id='regiao5',
                    multi=True,
                    value=df['regiao'].unique()[:2],
                    options=[{'label': regiao, 'value': regiao} for regiao in df['regiao'].unique()]
                )
                ]),
            ]),
            dbc.Col([
                html.Br(),
                html.Br(),
                dbc.Row([
                    html.H4('Escolha a relação de acidente:')
                ]),
                dbc.Row([
                    dcc.Dropdown(
                    id='tipo_acidente3',
                    multi=False,
                    value='causa_acidente',
                    options=[{'label': 'Causa do Acidente', 'value': 'causa_acidente'},
                            {'label': 'Tipo de Acidente', 'value': 'tipo_acidente'}]
                    )
                ]),
            ])
        ]),
        #grafico
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='scatterplot_condicao_metereologica')
            ])
        ])
    ]),

])


# funcao quantidade de acidentes por dia da semana

@app.callback(
    Output('bar_plot_regiao_dia_semana', 'figure'),
    Input('regiao', 'value'),
)
def barPlotRegiaoDiaSemana(regiao):
    df_filtrado = df[df['regiao'].isin(regiao)]

    semana = ['segunda-feira','terça-feira','quarta-feira','quinta-feira','sexta-feira','sábado','domingo']
    df_regiao_dia_semana = df_filtrado.groupby(['dia_semana', 'regiao']).size().reset_index(name='quantidade')

    fig = px.bar(df_regiao_dia_semana,  
                 x='dia_semana',
                 y='quantidade',
                 color='regiao',
                 barmode="group")
    return fig

# funcao frequencia de morte dos tipos de acidente por regiao

@app.callback(
    Output('bar_plot_tipo_acidente_regiao', 'figure'),
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

# funcao da relacao horario acidente

@app.callback(
    Output('scatterplot_horario_acidente', 'figure'),
    Input('regiao3', 'value'),
    Input('tipo_acidente1','value')
)
def HorarioAcidente(regiao, acidente):

    df_filtrado = df[df['regiao'].isin(regiao)]

    top_acidentes = (df_filtrado[acidente].value_counts().nlargest(10).index)

    df_filtrado_top = df_filtrado[df_filtrado[acidente].isin(top_acidentes)]

    df_causa_horario = df_filtrado_top.groupby([acidente, 'regiao'])['horario'].value_counts().sort_values(ascending=True).reset_index(name='count')


    fig = px.scatter(
        df_causa_horario,
        height=700,
        width=1350,
        x="horario",
        y=acidente,
        size="count",
        color="count",
        labels={"horario": "faixa de hora do acidetnte", "causa_acidente": "motivo do acidente"},
    )
    
    fig.update_traces(marker=dict(opacity=0.8, line=dict(width=1, color='DarkSlateGrey')))
    fig.update_layout(xaxis_tickangle=-45)

    return fig

# funcao da relacao feridos acidente

@app.callback(
    Output('scatterplot_feridos_acidente', 'figure'),
    Input('regiao4', 'value'),
    Input('tipo_acidente2','value')
)
def feridosGraves(regiao, acidente):

    df_filtrado = df[(df['regiao'].isin(regiao)) & (df['feridos_graves'] > 0)]

    top_acidentes = (df_filtrado[acidente].value_counts().nlargest(10).index)

    df_filtrado_top = df_filtrado[df_filtrado[acidente].isin(top_acidentes)]

    df_feridos = df_filtrado_top.groupby([acidente, 'regiao'])['feridos_graves'].value_counts().sort_values(ascending=False).reset_index()

    df_feridos['feridos_graves'] = [df_feridos['feridos_graves'][i] * df_feridos['count'][i] for i in range(0,len(df_feridos))]

    df_feridos = df_feridos.groupby([acidente, 'regiao'])['feridos_graves'].sum().sort_values(ascending=False).reset_index()

    fig = px.scatter(
        df_feridos,
        height=500,
        x="feridos_graves",
        y=acidente,
        size="feridos_graves",
        color="regiao",
        labels={"feridos_graves": "Total de Feridos Graves", "tipo_acidente": "Tipo de Acidente"},
    )
    
    fig.update_traces(marker=dict(opacity=0.8, line=dict(width=1, color='DarkSlateGrey')))
    fig.update_layout(xaxis_tickangle=-45)

    return fig

#funcao da relacao condicao metereologica acidente 

@app.callback(
    Output('scatterplot_condicao_metereologica', 'figure'),
    Input('regiao5', 'value'),
    Input('tipo_acidente3', 'value')
)
def condicaoMetereologica(regiao, acidente):

    df_filtrado = df[df['regiao'].isin(regiao)]

    top_acidentes = (df_filtrado[acidente].value_counts().nlargest(10).index)

    df_filtrado_top = df_filtrado[df_filtrado[acidente].isin(top_acidentes)]

    df_causa_horario = df_filtrado_top.groupby([acidente, 'regiao'])['condicao_metereologica'].value_counts().sort_values(ascending=True).reset_index(name='count')


    fig = px.scatter(
        df_causa_horario,
        height=700,
        x=acidente,
        y="condicao_metereologica",
        size="count",
        color="count",
        labels={"horario": "faixa de hora do acidetnte", "causa_acidente": "motivo do acidente"},
    )
    
    fig.update_traces(marker=dict(opacity=0.8, line=dict(width=1, color='DarkSlateGrey')))
    fig.update_layout(xaxis_tickangle=-45)

    return fig

#funcao main

if __name__ == '__main__':
    app.run(debug=True, port='8051')