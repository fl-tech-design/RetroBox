import time
import serial
import RPi.GPIO as GPIO
from evdev import UInput, ecodes as e, AbsInfo
import subprocess  # Import für amixer

# GPIO Setup
GPIO.setmode(GPIO.BCM)
button_pins = [19, 26, 20, 16, 21, 17, 18, 27, 22, 23, 24, 5, 9, 11]  # letzte zwei sind Select, Start; neue Buttons 9 und 11 für Lautstärke
buttons_state = [0] * len(button_pins)

# Zuordnung der GPIO-Pins zu evdev-Key-Codes
button_map = {
    19: e.BTN_A,
    26: e.BTN_B,
    20: e.BTN_X,
    16: e.BTN_Y,
    21: e.BTN_TL,
    17: e.BTN_TR,
    18: e.BTN_THUMBL,
    27: e.BTN_THUMBR,
    22: e.BTN_TRIGGER_HAPPY1,
    23: e.BTN_TRIGGER_HAPPY2,
    24: e.BTN_SELECT,
    5: e.BTN_START
}

# Setup der Pins als Öffner oder Schließer
for pin in button_pins:
    if pin in [24, 5]:  # Letzte zwei als Schließer für Select und Start
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    else:               # Andere als Öffner
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Serial Setup für Joystick
ser = serial.Serial("/dev/serial0", 9600)

# UInput Setup für Gamepad
ui = UInput(
    {
        e.EV_ABS: [
            (e.ABS_X, AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=15, resolution=0)),
            (e.ABS_Y, AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=15, resolution=0)),
            (e.ABS_RX, AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=15, resolution=0)),
            (e.ABS_RY, AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=15, resolution=0)),
        ],
        e.EV_KEY: [
            e.BTN_A, e.BTN_B, e.BTN_X, e.BTN_Y,
            e.BTN_TL, e.BTN_TR, e.BTN_THUMBL, e.BTN_THUMBR,
            e.BTN_TRIGGER_HAPPY1, e.BTN_TRIGGER_HAPPY2,
            e.BTN_SELECT, e.BTN_START
        ],
    },
    name="Virtual Gamepad"
)

# Timing Setup
last_button_check = time.monotonic()
button_check_interval = 0.03  # 30 ms

# Funktion zur Lautstärkeregelung
def adjust_volume(direction: str):
    if direction == "up":
        subprocess.run(["amixer", "sset", "'Master'", "5%+"])
    elif direction == "down":
        subprocess.run(["amixer", "sset", "'Master'", "5%-"])

try:
    while True:
        # Joystick-Daten lesen
        if ser.in_waiting > 0:
            data = ser.readline().decode().strip().split(",")
            if len(data) == 4:
                xStick1, yStick1 = int(data[0]), int(data[1])
                xStick2, yStick2 = int(data[2]), int(data[3])

                # Joystick-Werte an den virtuellen Controller senden
                ui.write(e.EV_ABS, e.ABS_X, xStick1)
                ui.write(e.EV_ABS, e.ABS_Y, yStick1)
                ui.write(e.EV_ABS, e.ABS_RX, xStick2)
                ui.write(e.EV_ABS, e.ABS_RY, yStick2)
                ui.syn()

        # Button-Zustände alle 30 ms überprüfen
        current_time = time.monotonic()
        if current_time - last_button_check > button_check_interval:
            last_button_check = current_time
            for pin in button_pins:
                state = GPIO.input(pin)
                
                # Lautstärke erhöhen oder verringern
                if pin == 9 and state == GPIO.LOW:  # Lauter
                    adjust_volume("up")
                elif pin == 11 and state == GPIO.LOW:  # Leiser
                    adjust_volume("down")
                elif pin in button_map:  # Andere Buttons an evdev senden
                    key_code = button_map[pin]
                    
                    # State basierend auf Öffner- oder Schließerlogik setzen
                    if pin in [24, 5]:  # Schließer (Select und Start)
                        ui.write(e.EV_KEY, key_code, 1 if state == GPIO.LOW else 0)
                    else:               # Öffner
                        ui.write(e.EV_KEY, key_code, 0 if state == GPIO.LOW else 1)

                # Button-Status synchronisieren
                ui.syn()

except KeyboardInterrupt:
    pass
finally:
    ui.close()
    GPIO.cleanup()
