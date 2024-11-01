import serial
import RPi.GPIO as GPIO
import time
from evdev import UInput, AbsInfo, ecodes as e
# GPIO und serielle Einstellungen
GPIO.setmode(GPIO.BCM)
button_pins = [17, 18, 27, 22, 23, 16, 19, 20, 26, 21, 5, 6, 24, 13]
buttons_state = [0] * len(button_pins)

# Die letzten beiden Pins als Schließer, die anderen als Öffner setzen
for i, pin in enumerate(button_pins):
    if i < len(button_pins) - 2:  # Öffner
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    else:  # Schließer
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

ser = serial.Serial("/dev/serial0", 9600)

# Definiere das virtuelle Gerät für 
ui = UInput({
    e.EV_ABS: [
        (e.ABS_X, AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=0, resolution=0)),
        (e.ABS_Y, AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=0, resolution=0)),
        (e.ABS_RX, AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=0, resolution=0)),
        (e.ABS_RY, AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=0, resolution=0))
    ],
    e.EV_KEY: [e.BTN_A, e.BTN_B, e.BTN_X, e.BTN_Y, e.BTN_TL, e.BTN_TR, e.BTN_SELECT, e.BTN_START, e.BTN_THUMBL, e.BTN_THUMBR]
})

try:
    while True:
        # Joystick-Daten abfragen
        if ser.in_waiting > 0:
            data = ser.readline().decode().strip().split(",")
            if len(data) == 4:
                xStick1, yStick1 = int(data[0]), int(data[1])
                xStick2, yStick2 = int(data[2]), int(data[3])
                
                # Werte für EmulationStation vorbereiten
                ui.write(e.EV_ABS, e.ABS_X, xStick1)
                ui.write(e.EV_ABS, e.ABS_Y, yStick1)
                ui.write(e.EV_ABS, e.ABS_RX, xStick2)
                ui.write(e.EV_ABS, e.ABS_RY, yStick2)
                ui.syn()
            else:
                print(f"Fehler: Erwartete 4 Werte, aber empfangen: {len(data)}")

        # Button-Zustände abfragen
        for i, pin in enumerate(button_pins):
            buttons_state[i] = GPIO.input(pin)
            
            # Tastenbehandlung für Öffner (0-9) und Schließer (letzte 2)
            if i < len(button_pins) - 2:  # Öffner: LOW wenn gedrückt
                if buttons_state[i] == GPIO.LOW:
                    ui.write(e.EV_KEY, e.BTN_A + i, 1)  # Taste drücken
                    print(f"Button {i+1} (Öffner) gedrückt")
                else:
                    ui.write(e.EV_KEY, e.BTN_A + i, 0)  # Taste loslassen
            else:  # Schließer: HIGH wenn gedrückt
                if buttons_state[i] == GPIO.HIGH:
                    ui.write(e.EV_KEY, e.BTN_A + i, 1)  # Taste drücken
                    print(f"Button {i+1} (Schließer) gedrückt")
                else:
                    ui.write(e.EV_KEY, e.BTN_A + i, 0)  # Taste loslassen
            
            ui.syn()  # Synchronisiert die Eingaben

        time.sleep(0.03)

except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
    ui.close()
