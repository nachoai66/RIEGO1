import network
import urequests
import ntptime
import time
from machine import Pin
from machine import WDT
# =====================================
# PERRO GUARDIAN
# ===
wdt = WDT(timeout=60000)

# =====================================
# CONFIGURACIÓN
# =====================================

SSID = "MiFibra-0CB0"
PASSWORD = "--------------"

TOKEN = "----------------"
CHAT_ID = "7195902508"

# =====================================
# GPIO
# =====================================

PIN_SENSOR = 4
PIN_BOMBA = 5

sensor = Pin(PIN_SENSOR, Pin.IN, Pin.PULL_UP)

bomba = Pin(PIN_BOMBA, Pin.OUT)

bomba.value(0)

# =====================================
# WIFI
# =====================================

def conectar_wifi():

    wlan = network.WLAN(network.STA_IF)

    wlan.active(True)

    if not wlan.isconnected():

        print("Conectando WiFi...")

        wlan.connect(SSID, PASSWORD)

        timeout = 20

        while timeout > 0:

            if wlan.isconnected():

                print("WiFi conectado")
                print(wlan.ifconfig())

                return wlan

            timeout -= 1

            time.sleep(1)

    return wlan

# =====================================
# NTP
# =====================================

def sincronizar_hora():

    try:

        ntptime.settime()

        print("Hora sincronizada")

    except Exception as e:

        print("Error NTP")
        print(e)

# =====================================
# TELEGRAM SEND
# =====================================

def enviar_telegram(mensaje):

    mensaje = mensaje.replace(" ", "%20")

    url = (
        "https://api.telegram.org/bot"
        + TOKEN
        + "/sendMessage?chat_id="
        + CHAT_ID
        + "&text="
        + mensaje
    )

    try:

        r = urequests.get(url)

        print(r.text)

        r.close()

    except Exception as e:

        print("ERROR TELEGRAM")
        print(e)

# =====================================
# TELEGRAM GET
# =====================================

ultimo_update = 0

def leer_comandos():

    global ultimo_update

    url = (
        "https://api.telegram.org/bot"
        + TOKEN
        + "/getUpdates?offset="
        + str(ultimo_update + 1)
    )

    try:

        r = urequests.get(url)

        respuesta = r.text

        r.close()

        # =====================================
        # EXTRAER SOLO JSON
        # =====================================

        inicio = respuesta.find("{")

        if inicio < 0:

            print("JSON no encontrado")

            return

        respuesta_json = respuesta[inicio:]

        # =====================================
        # PARSE JSON
        # =====================================

        import json

        datos = json.loads(respuesta_json)

        # =====================================
        # VALIDAR
        # =====================================

        if not datos["ok"]:

            print("Error Telegram")

            return

        # =====================================
        # RECORRER MENSAJES
        # =====================================

        for item in datos["result"]:

            ultimo_update = item["update_id"]

            if "message" not in item:
                continue

            message = item["message"]

            if "text" not in message:
                continue

            chat_id = str(message["chat"]["id"])

            if chat_id != CHAT_ID:

                print("Usuario no autorizado")

                continue

            comando = message["text"].strip()

            print("Comando recibido:")
            print(comando)

            procesar_comando(comando)

    except Exception as e:

        print("ERROR LEYENDO COMANDOS")
        print(e)

# =====================================
# COMANDOS
# =====================================

def procesar_comando(cmd):

    print("Comando:", cmd)

    # =========================
    # ESTADO
    # =========================

    if cmd == "/estado":

        agua = "SI" if sensor.value() == 0 else "NO"

        mensaje = (
            "📊 Estado sistema\n\n"
            f"💧 Agua depósito: {agua}"
        )

        enviar_telegram(mensaje)

    # =========================
    # REGAR
    # =========================

    elif cmd == "/regar":

        if sensor.value() == 0:

            enviar_telegram("💧 Activando bomba")

            bomba.value(1)

            time.sleep(10)

            bomba.value(0)

            enviar_telegram("✅ Riego completado")

        else:

            enviar_telegram(⚠️ Depósito vacío")

    # =========================
    # PING
    # =========================

    elif cmd == "/ping":

        enviar_telegram("🏓 ESP32 online")

    # =========================
    # HELP
    # =========================

    elif cmd == "/help":

        mensaje = (
            "Comandos disponibles:\n\n"
            "/estado\n"
            "/regar\n"
            "/ping\n"
            "/help"
        )

        enviar_telegram(mensaje)

# =====================================
# MAIN
# =====================================

print("========================")
print(" RIEGO SOLAR ESP32 ")
print("========================")

wifi = conectar_wifi()

if wifi.isconnected():

    sincronizar_hora()

    enviar_telegram("✅ Sistema iniciado")

    while True:
        
        wdt.feed()

        leer_comandos()

        time.sleep(5)

else:

    print("No se pudo conectar WiFi")