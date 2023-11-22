import paho.mqtt.client as mqtt
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import time

# Configurações MQTT
mqtt_broker = "broker.emqx.io"
mqtt_port = 1883
mqtt_topic = "prbs4"

# Configurações do gráfico
buffer_size = 100
data_buffer = []

# Inicializa o aplicativo Dash
app = dash.Dash(__name__)

# Layout do aplicativo
app.layout = html.Div([
    html.H1("Trabalho PDS - PRBS4", style={'textAlign': 'center', 'color': '#7FDBFF'}),
    dcc.Graph(id='live-update-graph'),
    dcc.Graph(id='fft-graph'),
    dcc.Interval(
        id='interval-component',
        interval=1 * 1000,  # em milissegundos
        n_intervals=0
    ),
    #  dcc.Dropdown(
    #     id='graph-type-dropdown',
    #     options=[
    #         {'label': 'Scatter', 'value': 'scatter'},
    #         {'label': 'histogram', 'value': 'histogram'},
    #         {'label': 'Bar', 'value': 'bar'},
    #         # Adicione outros tipos de gráficos conforme necessário
    #     ],
    #     value='scatter',  # Valor padrão ao iniciar
    #     style={'width': '50%', 'textAlign': 'center', 'color': '#7FDBFF', 'left': '50%'},
    # ),
     dcc.Graph(id='dht-graph'),
])

# Função chamada quando o cliente se conecta ao broker MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado ao servidor MQTT!")
    else:
        print(f"Falha na conexão ao servidor MQTT. Código de retorno: {rc}")

# Função chamada quando uma nova mensagem é recebida
def on_message(client, userdata, msg):
    value = int(msg.payload)
    print(value)
    data_buffer.append(value)
    update_graph(0)
    update_fft_graph(0)
    update_dht_graph(0)

# Função para calcular a FFT
def calculate_fft(data):
    if len(data) > 0:
        fft_values = np.fft.fft(data)
        fft_freq = np.fft.fftfreq(len(data))
        return fft_freq, fft_values
    else:
        # Retornar algum valor padrão ou tratar de outra forma quando não há dados suficientes
        return [], []
def calculate_dht(data):
        N = len(data)
        dht_values = np.zeros(N)
        for k in range(N):
            cos_sum = np.sum(data * np.cos(2 * np.pi / N * k * np.arange(N)))
            sin_sum = np.sum(data * np.sin(2 * np.pi / N * k * np.arange(N)))
            dht_values[k] = cos_sum + sin_sum

        return dht_values

# Conecta-se ao broker MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqtt_broker, mqtt_port, 60)
client.subscribe(mqtt_topic)
client.loop_start()

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
    Input('interval-component', 'n_intervals')
)
def update_fft_graph(n_intervals):
    if  buffer_size:
        fft_freq, fft_values = calculate_fft(data_buffer)
        trace_fft = go.Bar(x=fft_freq, y=np.abs(fft_values))
        fig = make_subplots(rows=1, cols=1, specs=[[{"type": "bar"}]])
        fig.add_trace(trace_fft)
        fig.update_layout(title="Cálculo da FFT", xaxis_title="Frequência", yaxis_title="Amplitude")
        return fig
    else:
        # Se não houver dados suficientes, retorna um gráfico vazio
        return go.Figure()

def update_dht_graph(n_intervals):
        if buffer_size:
            dht_values = calculate_dht(data_buffer)
            trace_dht = go.Scatter(x=np.arange(len(dht_values)), y=dht_values)
            fig = make_subplots(rows=1, cols=1, specs=[[{"type": "scatter"}]])
            fig.add_trace(trace_dht)
            fig.update_layout(title="Cálculo da DHT", xaxis_title="Amostras", yaxis_title="Amplitude")
            return fig
        else:
            # Se não houver dados suficientes, retorna um gráfico vazio
            return go.Figure()


# Mantém o aplicativo Dash em execução
if __name__ == '__main__':
    app.run_server(debug=True)
