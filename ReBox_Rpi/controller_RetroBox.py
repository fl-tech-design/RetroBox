import serial
import RPi.GPIO as GPIO
import time

# GPIO und serielle Einstellungen
GPIO.setmode(GPIO.BCM)
button_pins = [17, 18, 27, 22, 23, 16, 19, 20, 26, 21, 5, 6, 12, 13]
for pin in button_pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
ser = serial.Serial("/dev/serial0", 9600)

# Initiale Werte für den Button-Status und Timer
buttons_state = [0] * len(button_pins)
last_button_check = time.time()
button_check_interval = 0.03  # Interval für Buttonabfrage

try:
    while True:
        # Joystick-Daten ohne Pause abfragen
        if ser.in_waiting > 0:
            data = ser.readline().decode().strip().split(",")
            if len(data) == 4:
                xStick1, yStick1 = int(data[0]), int(data[1])
                xStick2, yStick2 = int(data[2]), int(data[3])
                print(f"Joystick: {xStick1}, {yStick1}, {xStick2}, {yStick2}")
            else:
                print(f"Fehler: Erwartete 4 Werte, aber empfangen: {len(data)}")

        # Button-Status alle 30ms abfragen
        if time.time() - last_button_check > button_check_interval:
            last_button_check = time.time()
            for i, pin in enumerate(button_pins):
                buttons_state[i] = GPIO.input(pin)
                if buttons_state[i] == GPIO.LOW:
                    print(f"Button {i+1} gedrückt")

except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
