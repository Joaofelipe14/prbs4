# Dashboard para Análise de Sinal PRBS4 com MQTT

Este projeto consiste em um dashboard interativo usando a biblioteca Dash para Python, que permite a análise em tempo real de um sinal PRBS4 recebido via MQTT. O sinal PRBS4 é visualizado em um gráfico de linha em tempo real, e são fornecidas análises adicionais na forma de uma representação de frequência (FFT) e da Transformada Discreta de Hankel (DHT).

## Configuração

### Requisitos

Certifique-se de ter o Python e o pip instalados em seu ambiente.

### Instalação de Dependências

Execute o seguinte comando para instalar as bibliotecas necessárias:

```bash
pip install paho-mqtt dash plotly numpy
```

### Configuração do Broker MQTT

Este projeto assume o uso de um broker MQTT para enviar o sinal PRBS4. Certifique-se de ter acesso a um broker MQTT e ajuste as configurações no código conforme necessário:

```python
mqtt_broker = "broker.emqx.io"  # Altere para o endereço do seu broker MQTT
mqtt_port = 1883
mqtt_topic = "prbs4"
```

### Execução do Projeto

Após a configuração, execute o script Python fornecido. O dashboard estará acessível em [http://127.0.0.1:8050/](http://127.0.0.1:8050/) no seu navegador.

```bash
python main.py
```

## Uso do Dashboard

O dashboard exibirá três gráficos principais:

1. **Sinal PRBS4 em Tempo Real:** Este gráfico mostra o sinal PRBS4 conforme ele é recebido em tempo real.

2. **Análise de Frequência (FFT):** Exibe a representação de frequência do sinal usando a Transformada Rápida de Fourier (FFT).

3. **Transformada Discreta de Hankel (DHT):** Fornece uma análise adicional usando a DHT para avaliar as características do sinal.

## Personalização

Você pode personalizar ainda mais o projeto, como adicionar diferentes tipos de gráficos, ajustar o tamanho do buffer, ou modificar as representações de frequência. Sinta-se à vontade para explorar e ajustar o código conforme necessário.