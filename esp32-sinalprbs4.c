#include <WiFi.h>
#include <PubSubClient.h>

// Configurações do Wi-Fi
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// Configurações do MQTT
const char* mqtt_server = "broker.emqx.io";
const char* mqtt_topic = "prbs4";

WiFiClient espClient;
PubSubClient client(espClient);

/*
  Classe PRBS4Generator
  Esta classe implementa um gerador de sequência pseudoaleatória de bit de acordo com o padrão PRBS4.
  O padrão PRBS4 é gerado usando um registrador de deslocamento de 4 bits com feedback exclusivo-OU
  nos bits 4 e 2, conforme descrito pelo polinômio x^4 + x^3 + 1.
  A classe mantém um estado interno de 4 bits para gerar os bits seguintes da sequência.
*/

class PRBS4Generator {
  public:
    /*
      Construtor
      Inicializa o estado interno do gerador com o valor 0x0F, que é um padrão conhecido.
    */
    PRBS4Generator() : state(0x0F) {}

    /*
      Função generateBit()
      Gera o próximo bit na sequência PRBS4.
      Retorna:
      - Um inteiro representando o próximo bit (0 ou 1) na sequência PRBS4.
    */
    int generateBit() {
      // Calcula o feedback usando uma operação de exclusivo-OU
      int feedback = ((state & 0x08) >> 3) ^ ((state & 0x04) >> 2);
      // Obtém o bit mais à direita (bit 0) do estado atual
      int newBit = state & 0x01;
      // Atualiza o estado, deslocando para a esquerda e aplicando o feedback
      state = ((state << 1) | feedback) & 0x0F;
      // Retorna o novo bit gerado
      return newBit;
    }

  private:
    // Estado interno do gerador de PRBS4 (registrador de deslocamento de 4 bits)
    uint8_t state;
};

PRBS4Generator prbs4Generator;

void setup() {
  Serial.begin(115200);

  // Inicia a conexão Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi conectado!");

  // Inicia o cliente MQTT
  client.setServer(mqtt_server, 1883);
  while (!client.connected()) {
    if (client.connect("ESP32Client")) {
      Serial.println("Conectado ao servidor MQTT!");
    } else {
      Serial.print("Falha na conexão ao servidor MQTT. Tentando novamente em 5 segundos...");
      delay(5000);
    }
  }
}

void loop() {
    // Gera um bit PRBS4
    int prbs4Bit = prbs4Generator.generateBit();

    // Envia o bit via MQTT
    char message[2];
    sprintf(message, "%d", prbs4Bit);

    // Publica a mensagem e aguarda confirmação
    bool mensagemRecebida = false;
    while (!mensagemRecebida) {
        client.publish(mqtt_topic, message);

        // Espera por um curto período para a confirmação
        delay(1000);

        // Verifica se a confirmação foi recebida
        if (confirmaRecebimento()) {
            Serial.println("Enviado e confirmado: " + String(prbs4Bit));
            mensagemRecebida = true;
        } else {
            Serial.println("Enviado, aguardando confirmação: " + String(prbs4Bit));
        }
    }

    // Aguarda 1 segundo entre as transmissões
    delay(4000);
}

