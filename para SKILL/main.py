import usocket as socket
import machine
import time
import json

# --- CONFIGURACIÓN DE PINES Y PARÁMETROS ---
RELE_PIN = 4
TRIG_PIN = 5
ECHO_PIN = 18

# Dimensiones del depósito (en centímetros)
DISTANCIA_VACIO = 100  # Distancia del sensor al fondo del tanque vacío
DISTANCIA_LLENO = 10   # Distancia del sensor al agua cuando esté lleno (margen mínimo)

# Configuración de Hardware
rele = machine.Pin(RELE_PIN, machine.Pin.OUT)
trigger = machine.Pin(TRIG_PIN, machine.Pin.OUT)
echo = machine.Pin(ECHO_PIN, machine.Pin.IN)

rele.value(0) # Bomba apagada al iniciar

# --- FUNCIÓN PARA MEDIR DISTANCIA ---
def medir_distancia():
    # Asegurar trigger en bajo
    trigger.value(0)
    time.sleep_us(5)
    
    # Enviar pulso de 10 microsegundos
    trigger.value(1)
    time.sleep_us(10)
    trigger.value(0)
    
    # Medir la duración del pulso de retorno
    duracion = machine.time_pulse_us(echo, 1, 30000) # Timeout de 30ms
    
    if duracion < 0:
        return -1 # Error de lectura
        
    # Calcular distancia en cm (Velocidad del sonido = 343 m/s)
    distancia = (duracion / 2) / 29.1
    return distancia

# --- LOGICA DE CONTROL Y API ---
def obtener_estado_deposito():
    distancia = medir_distancia()
    
    # Si hay error de lectura, devolvemos valores seguros
    if distancia <= 0:
        return {"bomba": "APAGADA", "porcentaje": 0, "estado": "ERROR SENSOR"}
    
    # Acotar la distancia dentro de los rangos del depósito
    distancia = max(DISTANCIA_LLENO, min(distancia, DISTANCIA_VACIO))
    
    # Calcular el porcentaje inverso (A menos distancia del sensor, más lleno está)
    rango_total = DISTANCIA_VACIO - DISTANCIA_LLENO
    distancia_medida = DISTANCIA_VACIO - distancia
    porcentaje = int((distancia_medida / rango_total) * 100)
    
    # --- SISTEMA DE SEGURIDAD AUTOMÁTICO ---
    if porcentaje >= 95 and rele.value() == 1:
        rele.value(0)
        print("¡ALERTA! Depósito al 95%. Bomba apagada automáticamente.")
        
    return {
        "bomba": "ENCENDIDA" if rele.value() == 1 else "APAGADA",
        "porcentaje": porcentaje,
        "distancia_cm": round(distancia, 1)
    }

# --- SERVIDOR WEB ---
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

print("Servidor Web con Ultrasonidos listo...")

while True:
    try:
        conn, addr = s.accept()
        request = conn.recv(1024).decode('utf-8')
        
        # Rutas de control manual
        if "GET /bomba/on" in request:
            # Solo permite encender si no está desbordando
            estado_actual = obtener_estado_deposito()
            if estado_actual["porcentaje"] < 95:
                rele.value(1)
        elif "GET /bomba/off" in request:
            rele.value(0)
            
        # Endpoint de la API que lee JavaScript
        if "GET /api/status" in request:
            respuesta = json.dumps(obtener_estado_deposito())
            conn.send('HTTP/1.1 200 OK\nContent-Type: application/json\n\n' + respuesta)
        else:
            # Servir interfaz web index.html
            with open('index.html', 'r') as f:
                html = f.read()
            conn.send('HTTP/1.1 200 OK\nContent-Type: text/html\n\n' + html)
            
        conn.close()
    except Exception as e:
        print("Error en el servidor:", e)
