import network
from umqtt.simple import MQTTClient
from machine import Pin, time_pulse_us
import time

# Configuración WiFi
WIFI_SSID = "celeste"
WIFI_PASSWORD = "12345678"

# Configuración MQTT
MQTT_BROKER = "192.168.137.191"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = ""
MQTT_TOPIC = "cerm/casa/distancia"
MQTT_PORT = 1883

TRIG_PIN = 15
ECHO_PIN = 4

trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

led_red = Pin(16, Pin.OUT)
led_green = Pin(5, Pin.OUT)
led_yellow = Pin(17,Pin.OUT)

# Función para conectar a WiFi
def conectar_wifi():
    print("Conectando a WiFi...", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    while not sta_if.isconnected():
        print(".", end="")
        time.sleep(0.3)
    print("\nWiFi Conectada!")

# Función para conectar al broker MQTT
def conectar_broker():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASSWORD)
    client.connect()
    print(f"Conectado a MQTT Broker: {MQTT_BROKER}, Topic: {MQTT_TOPIC}")
    return client

# Función para medir distancia con HC-SR04
def medir_distancia():
    trig.off()
    time.sleep_us(2)
    trig.on()
    time.sleep_us(10)
    trig.off()

    duracion = time_pulse_us(echo, 1, 30000)  # Máximo 30 ms de espera
    if duracion < 0:
        return -1  # Error en la medición
    
    distancia = (duracion * 0.0343) / 2  # Convertir a cm
    return distancia

conectar_wifi()
client = conectar_broker()

distancia_anterior = -1 

# Bucle principal
while True:
    distancia = medir_distancia()
    print(f"Distancia: {distancia} cm")

    # Cambiar el color del LED RGB según la distancia
    if distancia == -1:
        led_red.value(0)
        led_green.value(0)
        led_yellow.value(0)
    elif distancia > 20:
        led_red.value(0)
        led_green.value(1)
        led_yellow.value(0)
    elif distancia > 10:
        led_red.value(0)
        led_green.value(0)
        led_yellow.value(1)
    else:
        led_red.value(1)
        led_green.value(0)
        led_yellow.value(0)

    if distancia != distancia_anterior:
        client.publish(MQTT_TOPIC, str(distancia))
        distancia_anterior = distancia

    time.sleep(2)