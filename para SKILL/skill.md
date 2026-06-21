---
name: control-bomba-ultrasonidos-esp32
description: Skill para gestionar el servidor web de control de una bomba de agua y sensor ultrasónico HC-SR04 en ESP32 con MicroPython.
version: 1.1.0
---

# Instrucciones para Claude

Eres un experto en IoT con ESP32 y MicroPython. Al modificar este proyecto debes asegurar:
1. **Pines**: Usa Pin 4 (Relé), Pin 5 (Trigger ultrasonidos) y Pin 18 (Echo ultrasonidos).
2. **Dimensiones del Depósito**: 
   * Distancia máxima (Depósito Vacío): 100 cm (ajustable por el usuario).
   * Distancia mínima (Depósito Lleno): 10 cm (distancia de seguridad para el sensor).
3. * La bomba de agua irá alojada en la parte de arriba del depósito en un orificio practicado en la tapadera.
4. * La bomba junto con el circuito iran alojados en una carcasa de petg que se habrá diseñado en fusiom360 e impreso en una bambulab A1.
3. **Seguridad**: Si el nivel supera el 95% de su capacidad, apaga la bomba de forma automática en el bucle principal.
