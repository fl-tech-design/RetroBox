import serial
import RPi.GPIO as GPIO
import time

# GPIO und serielle Einstellungen
GPIO.setmode(GPIO.BCM)
button_pins = [17, 18, 27, 22, 23, 16, 19, 20, 26, 21, 5, 6, 24, 13]
buttons_state = [0] * len(button_pins)

# Die letzten beiden Pins als Schließer, die anderen als Öffner setzen
for i, pin in enumerate(button_pins):
    if i < len(button_pins) - 2:  # Öffner mit Pull-Up-Widerstand
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    else:  # Schließer mit Pull-Down-Widerstand
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Serielle Verbindung zum Arduino
ser = serial.Serial("/dev/serial0", 9600)

# Timer-Werte für Button-Abfrage
last_button_check = time.time()
button_check_interval = 0.03

try:
    while True:
        # Joystick-Daten abfragen
        if ser.in_waiting > 0:
            data = ser.readline().decode().strip().split(",")
            if len(data) == 4:
                xStick1, yStick1 = int(data[0]), int(data[1])
                xStick2, yStick2 = int(data[2]), int(data[3])
                print(f"Joystick: {xStick1}, {yStick1}, {xStick2}, {yStick2}")
            else:
                print(f"Fehler: Erwartete 4 Werte, aber empfangen: {len(data)}")

        # Button-Zustände abfragen
        if time.time() - last_button_check > button_check_interval:
            last_button_check = time.time()
            for i, pin in enumerate(button_pins):
                buttons_state[i] = GPIO.input(pin)
                
                # Zustandsprüfung entsprechend der Pin-Typen
                if i < len(button_pins) - 2:  # Öffner: LOW = gedrückt
                    if buttons_state[i] == GPIO.LOW:
                        print(f"Button {i+1} (Öffner) gedrückt")
                else:  # Schließer: HIGH = gedrückt
                    if buttons_state[i] == GPIO.HIGH:
                        print(f"Button {i+1} (Schließer) gedrückt")

except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
