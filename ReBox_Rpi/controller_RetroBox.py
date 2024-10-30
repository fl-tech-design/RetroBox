import serial
import RPi.GPIO as GPIO
import time

# Setze die GPIO-Modus
GPIO.setmode(GPIO.BCM)

# Definiere die GPIO-Pins für die Buttons
button_pins = [2, 3, 4, 17, 27, 22, 10, 9, 11, 5]  # Beispiel-Pins
buttons_state = [0] * len(button_pins)  # Array zur Speicherung des Button-Zustands

# Setze die Pins als Eingänge mit Pull-Up-Widerständen
for pin in button_pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Serielle Verbindung zum Arduino
ser = serial.Serial("/dev/serial0", 9600)

try:
    while True:
        # Überprüfe, ob Daten vom Arduino empfangen werden
        if ser.in_waiting > 0:
            data = ser.readline().decode().strip().split(",")
            print("data: ", data)

            if len(data) != 4:
                print(f"Fehler: Erwartete 4 Werte, aber empfangen: {len(data)}")
                continue

            # Auslesen der Joystick-Werte
            xStick1 = int(data[0])
            yStick1 = int(data[1])
            xStick2 = int(data[2])
            yStick2 = int(data[3])

            print(f"Joystick: {xStick1}, {yStick1}, {xStick2}, {yStick2}")

        # Überprüfe die Zustände der Buttons
        for i, pin in enumerate(button_pins):
            buttons_state[i] = GPIO.input(pin)
            # Wenn der Button gedrückt ist (LOW), drucke den Zustand
            if buttons_state[i] == GPIO.LOW:
                print(f"Button {i+1} gedrückt")

        time.sleep(0.1)  # Kurze Pause zur Entlastung der CPU

except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()  # Bereinige die GPIOs beim Beenden
