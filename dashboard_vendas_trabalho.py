import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Carregar dados do arquivo XLSX
df = pd.read_excel('1 - Base de Dados.xlsx')
df = df.drop("Unnamed: 0", axis=1, errors="ignore")
df['Data_Pedido'] = df['Data_Pedido'].dt.strftime('%B %Y')

# Inicializar o aplicativo Dash
app = dash.Dash(__name__, external_stylesheets=['https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css'])

# Layout do Dashboard com estilo CSS para o fundo escuro
app.layout = html.Div(style={'backgroundColor': 'black', 'color': 'white', 'padding': '20px'}, children=[
    html.H1("Relatório de Vendas - 2020", className='display-4'),  # Título do painel com classe de Bootstrap
    
    dcc.Graph(
        id='graph1',
        figure=px.histogram(df, x='Data_Pedido', y='Valor_Total_Venda', title='Total de Vendas por Mês', color='Data_Pedido', labels={'Data_Pedido':'Meses', 'Valor_Total_Venda':'Total de Vendas'})
    ),
    
    dcc.Graph(
        id='graph2',
        figure=px.histogram(df, x='Nome_Representante', y='Valor_Total_Venda', title='Total de Vendas por Representante', color='Nome_Representante')
    ),
    
    dcc.Graph(
        id='graph3',
        figure=px.histogram(df, x='Nome_Produto', y='Valor_Total_Venda', title='Total de Vendas por Produto', color='Nome_Produto')
    ),
    
    html.Div(className='row justify-content-center', style={'margin-top': '30px'}, children=[  # Centralizar os gráficos
        html.Div(className='col-md-5', style={'margin-bottom': '20px'}, children=[  # Divisão de 5 colunas para os gráficos com margem inferior
            dcc.Graph(
                id='graph4',
                figure=px.sunburst(df, path=['Regional', 'Estado_Cliente'], values='Valor_Total_Venda', title='Total de Vendas por Região', color='Estado_Cliente')
            ),
        ]),
        html.Div(className='col-md-5', style={'margin-bottom': '20px'}, children=[  # Divisão de 5 colunas para os gráficos com margem inferior
            dcc.Graph(
                id='graph5',
                figure=px.histogram(df, x='Estado_Cliente', y='Valor_Total_Venda', title='Total de Vendas por Estado', color='Cidade_Cliente')
            ),
        ]),
    ]),
    
    html.Label('Selecione para filtrar Estados selecionados:', style={'color': 'gray'}),  # Definir cor do texto para cinza
    dcc.Dropdown(
        id='estado-dropdown',
        options=[{'label': estado, 'value': estado} for estado in df['Estado_Cliente'].unique()],
        value=df['Estado_Cliente'].unique()[0],
        multi=True,
        style={'color': 'black'}  # Definir cor do texto para preto
    ),
    
    html.Label('Selecione para filtrar Cidades selecionadas:', style={'color': 'gray'}),  # Definir cor do texto para cinza
    dcc.Dropdown(
        id='cidade-dropdown', multi=True,
        style={'color': 'black'}  # Definir cor do texto para preto
    ),
])

# Callback para atualizar as opções do dropdown de cidades com base no estado selecionado
@app.callback(
    Output('cidade-dropdown', 'options'),
    [Input('estado-dropdown', 'value')]
)
def update_cidades_options(selected_estados):
    if not selected_estados:
        return []
    cidades_options = [{'label': cidade, 'value': cidade} for estado in selected_estados for cidade in df[df['Estado_Cliente'] == estado]['Cidade_Cliente'].unique()]
    return cidades_options

# Callback para atualizar os gráficos com base nos filtros selecionados
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
        return {}, {}, {}, {}, {}

    if isinstance(selected_estados, str):
        selected_estados = [selected_estados]

    filtered_df = df[df['Estado_Cliente'].isin(selected_estados)]
    
    if selected_cidades:
        filtered_df = filtered_df[filtered_df['Cidade_Cliente'].isin(selected_cidades)]

    fig1 = px.histogram(filtered_df, x='Data_Pedido', y='Valor_Total_Venda', title='Total de Vendas por Mês', 
                        color= 'Data_Pedido', labels={'Data_Pedido':'Meses', 'Valor_Total_Venda':'Total de Vendas'})
    fig2 = px.histogram(filtered_df, x='Nome_Representante', y='Valor_Total_Venda', title='Total de Vendas por Representante', 
                        color='Nome_Representante',  labels={'Nome_Representante':'Representantes', 'Valor_Total_Venda':'Total de Vendas'})
    fig3 = px.histogram(filtered_df, x='Nome_Produto', y='Valor_Total_Venda', title='Total de Vendas por Produto', 
                        color='Nome_Produto',  labels={'Nome_Produto':'Produtos', 'Valor_Total_Venda':'Total de Vendas'})
    fig4 = px.sunburst(filtered_df, path=['Regional', 'Estado_Cliente'], values='Valor_Total_Venda', title='Total de Vendas por Região',
                  color='Estado_Cliente', labels={'Regional':'Região','Estado_Cliente':'Estado', 'Valor_Total_Venda':'Total de Vendas'})
    fig5 = px.histogram(filtered_df, x='Estado_Cliente', y='Valor_Total_Venda', title='Total de Vendas por Estado',
                        color='Cidade_Cliente', labels={'Cidade_Cliente':'Cidade', 'Estado_Cliente':'Estado', 'Valor_Total_Venda':'Total de Vendas'})

    return fig1, fig2, fig3, fig4, fig5

# Executar o aplicativo somente se este script for executado diretamente
if __name__ == '__main__':
    app.run_server(debug=True)
