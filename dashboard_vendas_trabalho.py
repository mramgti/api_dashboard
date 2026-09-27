import os
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# Caminho absoluto para a base de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
caminho_excel = os.path.join(BASE_DIR, '1 - Base de Dados.xlsx')

# Carregar dados
df = pd.read_excel(caminho_excel)
df = df.drop("Unnamed: 0", axis=1, errors="ignore")
df['Data_Pedido'] = df['Data_Pedido'].dt.strftime('%B %Y')

# Inicializar o Dash
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# Expor o servidor Flask para o PythonAnywhere
server = app.server

estados_iniciais = [df['Estado_Cliente'].dropna().unique()[0]]
cidades_iniciais = df[df['Estado_Cliente'].isin(estados_iniciais)]['Cidade_Cliente'].dropna().unique().tolist()

app.layout = html.Div(style={'backgroundColor': 'black', 'color': 'white', 'padding': '20px'}, children=[
    html.H1("Relatório de Vendas - 2020", className='display-4 mb-4'),
    
    dcc.Graph(id='graph1'),
    dcc.Graph(id='graph2'),
    dcc.Graph(id='graph3'),
    
    html.Div(className='row justify-content-center', style={'marginTop': '30px'}, children=[
        html.Div(className='col-md-6', style={'marginBottom': '20px'}, children=[
            dcc.Graph(id='graph4'),
        ]),
        html.Div(className='col-md-6', style={'marginBottom': '20px'}, children=[
            dcc.Graph(id='graph5'),
        ]),
    ]),
    
    html.Label('Filtrar por Estado:', style={'color': 'gray', 'fontWeight': 'bold'}),
    dcc.Dropdown(
        id='estado-dropdown',
        options=[{'label': e, 'value': e} for e in sorted(df['Estado_Cliente'].dropna().unique())],
        value=estados_iniciais,
        multi=True,
        style={'color': 'black', 'marginBottom': '15px'}
    ),
    
    html.Label('Filtrar por Cidade:', style={'color': 'gray', 'fontWeight': 'bold'}),
    dcc.Dropdown(
        id='cidade-dropdown',
        options=[{'label': c, 'value': c} for c in sorted(cidades_iniciais)],
        value=[],
        multi=True,
        style={'color': 'black'}
    ),
])

@app.callback(
    Output('cidade-dropdown', 'options'),
    [Input('estado-dropdown', 'value')]
)
def update_cidades_options(selected_estados):
    if not selected_estados:
        return []
    if isinstance(selected_estados, str):
        selected_estados = [selected_estados]
    cidades = df[df['Estado_Cliente'].isin(selected_estados)]['Cidade_Cliente'].dropna().unique()
    return [{'label': c, 'value': c} for c in sorted(cidades)]

@app.callback(
    [Output('graph1', 'figure'),
     Output('graph2', 'figure'),
     Output('graph3', 'figure'),
     Output('graph4', 'figure'),
     Output('graph5', 'figure')],
    [Input('estado-dropdown', 'value'),
     Input('cidade-dropdown', 'value')]
)
def update_graphs(selected_estados, selected_cidades):
    if not selected_estados:
        dff = df.copy()
    else:
        if isinstance(selected_estados, str):
            selected_estados = [selected_estados]
        dff = df[df['Estado_Cliente'].isin(selected_estados)]

    if selected_cidades:
        if isinstance(selected_cidades, str):
            selected_cidades = [selected_cidades]
        dff = dff[dff['Cidade_Cliente'].isin(selected_cidades)]

    fig1 = px.histogram(dff, x='Data_Pedido', y='Valor_Total_Venda', title='Total de Vendas por Mês', 
                        color='Data_Pedido', labels={'Data_Pedido':'Meses', 'Valor_Total_Venda':'Total de Vendas'})
    fig2 = px.histogram(dff, x='Nome_Representante', y='Valor_Total_Venda', title='Total de Vendas por Representante', 
                        color='Nome_Representante', labels={'Nome_Representante':'Representantes', 'Valor_Total_Venda':'Total de Vendas'})
    fig3 = px.histogram(dff, x='Nome_Produto', y='Valor_Total_Venda', title='Total de Vendas por Produto', 
                        color='Nome_Produto', labels={'Nome_Produto':'Produtos', 'Valor_Total_Venda':'Total de Vendas'})
    fig4 = px.sunburst(dff, path=['Regional', 'Estado_Cliente'], values='Valor_Total_Venda', title='Total de Vendas por Região',
                       color='Estado_Cliente', labels={'Regional':'Região','Estado_Cliente':'Estado', 'Valor_Total_Venda':'Total de Vendas'})
    fig5 = px.histogram(dff, x='Estado_Cliente', y='Valor_Total_Venda', title='Total de Vendas por Estado',
                        color='Cidade_Cliente', labels={'Cidade_Cliente':'Cidade', 'Estado_Cliente':'Estado', 'Valor_Total_Venda':'Total de Vendas'})

    for fig in (fig1, fig2, fig3, fig4, fig5):
        fig.update_layout(template="plotly_dark")

    return fig1, fig2, fig3, fig4, fig5

if __name__ == '__main__':
    app.run_server(debug=True)
