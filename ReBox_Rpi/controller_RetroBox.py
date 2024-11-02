import time
import serial
import RPi.GPIO as GPIO
from evdev import UInput, ecodes as e, AbsInfo

# GPIO Setup
GPIO.setmode(GPIO.BCM)
button_pins = [19, 26, 20, 16, 21, 17, 18, 27, 22, 23, 24, 5, 9, 11]  # 12 reguläre Buttons + 2 Lautstärke-Buttons
buttons_state = [0] * len(button_pins)

# Zuordnung der GPIO-Pins zu evdev-Key-Codes
button_map = {
    19: e.BTN_A,         # Button 1
    26: e.BTN_B,         # Button 2
    20: e.BTN_X,         # Button 3
    16: e.BTN_Y,         # Button 4
    21: e.BTN_TL,        # Button 5
    17: e.BTN_TR,        # Button 6
    18: e.BTN_THUMBL,    # Button 7
    27: e.BTN_THUMBR,    # Button 8
    22: e.BTN_TRIGGER_HAPPY1,  # Button 9
    23: e.BTN_TRIGGER_HAPPY2,  # Button 10
    24: e.BTN_SELECT,    # Button 11 (Select)
    5: e.BTN_START,      # Button 12 (Start)
    9: "VOLUME_UP",      # Lautstärke erhöhen
    11: "VOLUME_DOWN"    # Lautstärke verringern
}

# Setup der Pins als Öffner oder Schließer
for pin in button_pins:
    if pin in [24, 5, 9, 11]:  # Schließer für Select, Start und Lautstärke
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    else:                      # Andere als Öffner
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Serial Setup für Joystick
ser = serial.Serial("/dev/serial0", 9600)

# UInput Setup für Gamepad und Lautstärke
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
        e.EV_SND: [
            e.SND_VOLUME  # Volume control support
        ]
    },
    name="Virtual Gamepad"
)

# Timing Setup
last_button_check = time.monotonic()
button_check_interval = 0.03  # 30 ms
volume_level = 50  # Beispiel Lautstärke-Startwert

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
                if pin in [9, 11]:  # Lautstärke erhöhen oder verringern
                    if state == GPIO.LOW:
                        if pin == 9:  # Lautstärke erhöhen
                            volume_level = min(100, volume_level + 5)
                        elif pin == 11:  # Lautstärke verringern
                            volume_level = max(0, volume_level - 5)
                        ui.write(e.EV_SND, e.SND_VOLUME, volume_level)

                else:
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
