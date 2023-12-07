import paho.mqtt.client as mqtt
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import time
import plotly.graph_objs as go
import pandas as pd
import plotly.express as px



# Configurações MQTT
mqtt_broker = "broker.emqx.io"
mqtt_port = 1883
mqtt_topic = "joao/pds/projetop3/prbs4"

# Configurações do gráfico
buffer_size = 100
data_buffer = []

# Inicializa o aplicativo Dash
app = dash.Dash(__name__)

# Layout do aplicativo
# Layout do aplicativo
app.layout = html.Div([
    # Div para o primeiro tópico - Sinal PRBS4
    html.Div([
        html.H2("Sinal PRBS4", style={'textAlign': 'center', 'color': '#black', 'font-family': 'Lobster'}),
        html.P("O Sinal PRBS4 (Pseudorandom Binary Sequence de Ordem 4) é uma sequência binária pseudoaleatória.",
               style={'textAlign': 'center', 'font-family': 'Arial'}),
        html.P("Essa sequência é gerada através de um processo lógico que envolve operações XOR entre bits anteriores.",
               style={'textAlign': 'center', 'font-family': 'Arial'}),
        dcc.Graph(id='live-update-graph'),
    ], style={'textAlign': 'center', 'margin': 'auto', 'width': '80%'}),

    # Div para o segundo tópico - FFT
    html.Div([
        html.H2("FFT do Sinal PRBS4", style={'textAlign': 'center', 'color': '#black', 'font-family': 'Lobster'}),
        html.P("A Transformada Rápida de Fourier (FFT) é uma técnica matemática utilizada para analisar sinais e decompor "
               "um sinal complexo em suas componentes de frequência.",
               style={'textAlign': 'center', 'font-family': 'Arial'}),
        html.P("O gráfico mostra a representação espectral do Sinal PRBS4 após a aplicação da FFT.",
               style={'textAlign': 'center', 'font-family': 'Arial'}),
        dcc.Graph(id='fft-graph'),
        dcc.Interval(
            id='interval-component',
            interval=1 * 1000,  # em milissegundos
            n_intervals=0
        ),
        dcc.Dropdown(
            id='graph-type-dropdown-fft',
            options=[
                {'label': 'Scatter', 'value': 'scatter'},
                {'label': 'Bar', 'value': 'bar'},
                # Adicione outros tipos de gráficos conforme necessário
            ],
            value='scatter',  # Valor padrão ao iniciar
            style={'width': '50%','textAlign': 'center', 'margin': 'auto'},
        ),
    ], style={'textAlign': 'center', 'margin': 'auto', 'width': '80%'}),

    # Div para o terceiro tópico - THD
    html.Div([
        html.H2("THD do Sinal PRBS4", style={'textAlign': 'center', 'color': '#black', 'font-family': 'Lobster'}),
        html.P("A Distorção Harmônica Total (THD) é uma métrica que quantifica a distorção introduzida em um sinal.",
               style={'textAlign': 'center', 'font-family': 'Arial'}),
        html.P("No contexto do Sinal PRBS4, o gráfico exibe a amplitude percentual das harmônicas em relação à fundamental.",
               style={'textAlign': 'center', 'font-family': 'Arial'}),
        dcc.Graph(id='dht-graph'),
        html.Div(id='thd-value-display'),
        dcc.Dropdown(
            id='graph-type-dropdown-dht',
            options=[
                {'label': 'Scatter', 'value': 'scatter'},
                {'label': 'Bar', 'value': 'bar'},
                # Adicione outros tipos de gráficos conforme necessário
            ],
            value='scatter',  # Valor padrão ao iniciar
            style={'width': '50%','textAlign': 'center', 'margin': 'auto'},
        ),
    ], style={'textAlign': 'center', 'margin': 'auto', 'width': '80%','textAlign': 'center', 'margin': 'auto'}),
])

# Função chamada quando o cliente se conecta ao broker MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado ao servidor MQTT!")
    else:
        print(f"Falha na conexão ao servidor MQTT. Código de retorno: {rc}")

# Função chamada quando uma nova mensagem é recebida
def on_message(client, userdata, msg):
#    value = int(msg.payload)
 #   data_buffer.append(value)

    values_list = msg.payload.decode('utf-8').split(',')
    #values_list =[1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0,1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0,1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0]
    # Converta cada valor para inteiro
    values_int = [int(value) for value in values_list]
    # Imprime os valores
    # with data_buffer_lock:
    data_buffer.extend(values_int)
    #     print(data_buffer)

    #     if len(data_buffer) > buffer_size:
    #         data_buffer.pop(0)
    #print(value)
    data_buffer.extend(values_int)
    if len(data_buffer) > buffer_size:
            data_buffer.pop(0)

    print(data_buffer)
    update_graph(0)
    update_fft_graph(0)
    update_dht_figure(0)

# Função para calcular a FFT
def calculate_fft(data):
    if len(data) > 0:
        fft_values = np.fft.fft(data)
        fft_freq = np.fft.fftfreq(len(data))
        df = pd.DataFrame({'Frequência': fft_freq, 'FFT': fft_values})

        # Exibindo o DataFrame
        # print(df)

        return fft_freq, fft_values
    else:
        return [], []

def calculate_dht(data):
    N = len(data)

    # Calcula a FFT do sinal
    fft_resultado = np.fft.fft(data)

    # Encontra o índice da componente fundamental
    fundamental_index = np.argmax(np.abs(fft_resultado))

    # Obtém a amplitude da componente fundamental
    fundamental_amplitude = np.abs(fft_resultado[fundamental_index])

    # Obtém as amplitudes das harmônicas (excluindo a componente DC)
    harmonic_amplitudes = np.abs(fft_resultado[1:])

    # Calcula o THD em percentagem
    thd = np.sqrt(np.sum(harmonic_amplitudes**2)) / fundamental_amplitude * 100

    # Calcula a amplitude percentual das harmônicas em relação à fundamental
    harmonic_amplitudes_percentual = harmonic_amplitudes / fundamental_amplitude * 100

    # Criação do DataFrame para o THD
    df_thd = pd.DataFrame({'Harmonica': np.arange(1, len(harmonic_amplitudes) + 1),
                           'Amplitude Percentual': harmonic_amplitudes_percentual})
    
    print

    return thd, df_thd
# Atualiza o gráfico
@app.callback(
    Output('live-update-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_graph(n_intervals):
    if data_buffer:
        trace = go.Scatter(y=data_buffer)
        fig = make_subplots(rows=1, cols=1, specs=[[{"type": "scatter"}]])
        fig.add_trace(trace)
        fig.update_layout(title="Sinal PRBS4 Recebido", xaxis_title="Amostras", yaxis_title="Valor")
        return fig
    else:
        # Se não houver dados, retorna um gráfico vazio
        return go.Figure()

# Atualiza o gráfico da FFT
@app.callback(
    Output('fft-graph', 'figure'),
    Input('interval-component', 'n_intervals'),
    Input('graph-type-dropdown-fft', 'value')
)
def update_fft_graph(n_intervals, graph_type='scatter'):
    if data_buffer:
        fft_freq, fft_values = calculate_fft(data_buffer)  
        frequencia = np.fft.fftfreq(len(data_buffer))
        fft_resultado = np.fft.fft(data_buffer)
        print    
        if graph_type == 'scatter':
            trace_fft = go.Scatter(x=frequencia, y= np.abs(fft_resultado), mode='lines')
            fig = make_subplots(rows=1, cols=1, specs=[[{"type": "scatter"}]])
            fig.add_trace(trace_fft)
            fig.update_layout(title="Sinal PRBS4 escala", xaxis_title="Amostras", yaxis_title="Amplitude")
            return fig
        elif graph_type == 'bar':
            trace_fft = go.Bar(x=frequencia, y= np.abs(fft_resultado))  # Ajuste a largura das barras aqui
            fig = make_subplots(rows=1, cols=1, specs=[[{"type": "bar"}]])
            fig.add_trace(trace_fft)
            fig.update_layout(xaxis_title="Amostras", yaxis_title="Amplitude", annotations=[
            dict(
                x=2,
                y=1.15,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=14),
            )
        ], bargap=0) 

            return fig
    else:
        # Se não houver dados suficientes, retorna um gráfico vazio
        return go.Figure()



@app.callback(
    [Output('dht-graph', 'figure'),
     Output('thd-value-display', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('graph-type-dropdown-dht', 'value')]
)
def update_dht_figure(n_intervals, graph_type='scatter'):
    if data_buffer:
        thd_value, df_thd = calculate_dht(data_buffer[:16])  # Pegando apenas os primeiros 16 valores do buffer

        # Lógica para criar o gráfico DHT com base no tipo selecionado
        if graph_type == 'scatter':
            trace_dht = go.Scatter(x=df_thd['Harmonica'], y=df_thd['Amplitude Percentual'],
                                  mode='markers+lines',
                                  line=dict(color='blue', width=2),
                                  marker=dict(color='black', size=8))
        elif graph_type == 'bar':
            trace_dht = go.Bar(x=df_thd['Harmonica'], y=df_thd['Amplitude Percentual'] ,width=0.5)

        # Criação da figura do gráfico DHT
        fig = go.Figure(trace_dht)

        # Adiciona o valor do DHT ao layout do gráfico
        fig.update_layout(annotations=[
            dict(
                x=0.5,
                y=1.15,
                xref="paper",
                yref="paper",
                text=f"DHT: {thd_value:.2f}",
                showarrow=False,
                font=dict(size=14),
            )
        ])

        # Retorna a figura do gráfico e o valor do THD
        return fig, f"THD: {thd_value:.2f}"
    else:
        # Se não houver dados suficientes, retorna valores vazios
        return go.Figure(), ""

 

# Conecta-se ao broker MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqtt_broker, mqtt_port, 60)
client.subscribe(mqtt_topic)
client.loop_start()
#on_message('','','')



# Mantém o aplicativo Dash em execução
if __name__ == '__main__':
    app.run_server(debug=False)
