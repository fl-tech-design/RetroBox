import time
import serial
import RPi.GPIO as GPIO
from evdev import UInput, ecodes as e, AbsInfo
import subprocess

# GPIO Setup
GPIO.setmode(GPIO.BCM)
button_pins = [19, 26, 20, 16, 21, 17, 18, 27, 22, 23, 24, 5]  # letzte zwei sind Select und Start
volume_up_pin = 9
volume_down_pin = 11
button_pins.extend([volume_up_pin, volume_down_pin])
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
    5: e.BTN_START       # Button 12 (Start)
}

# Volume Control Setup für USB Audio
def change_volume(direction):
    command = ["amixer", "sset", "PCM", "2%+" if direction == "up" else "2%-"]
    subprocess.run(command)

# Setup der Pins als Öffner oder Schließer
for pin in button_pins:
    if pin in [24, 5, volume_up_pin, volume_down_pin]:  # Letzte zwei als Schließer für Select und Start
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
    name="Controller RetroBox"
)

# Timing Setup
last_button_check = time.monotonic()
button_check_interval = 0.03  # 30 ms
volume_interval = 0.2  # Zeit zwischen Lautstärkeänderungen bei gehaltenem Button
last_volume_change = time.monotonic()

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
                
                # Lautstärkeregelung für Vol Up und Vol Down
                if pin == volume_up_pin and state == GPIO.LOW:
                    if current_time - last_volume_change > volume_interval:
                        change_volume("up")
                        last_volume_change = current_time
                elif pin == volume_down_pin and state == GPIO.LOW:
                    if current_time - last_volume_change > volume_interval:
                        change_volume("down")
                        last_volume_change = current_time

                # State basierend auf Öffner- oder Schließerlogik setzen
                elif pin in button_map:  # Andere Buttons
                    key_code = button_map[pin]
                    if pin in [24, 5]:  # Schließer (Select und Start)
                        ui.write(e.EV_KEY, key_code, 1 if state == GPIO.LOW else 0)
                    else:               # Öffner
                        ui.write(e.EV_KEY, key_code, 0 if state == GPIO.LOW else 1)
                    ui.syn()

except KeyboardInterrupt:
    pass
finally:
    ui.close()
    GPIO.cleanup()
