import time
import serial
import RPi.GPIO as GPIO
from evdev import UInput, ecodes as e, AbsInfo
import os  # Für die CPU-Temperatur

# GPIO Setup
GPIO.setmode(GPIO.BCM)
button_pins = [19, 26, 20, 16, 21, 17, 18, 27, 22, 23, 24, 5]  # Letzte zwei sind Select und Start
volume_up_pin, volume_down_pin = 9, 11
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

# Setup der Pins als Öffner oder Schließer
for pin in button_pins + [volume_up_pin, volume_down_pin]:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Serial Setup für Joystick und Lüftersteuerung
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
        e.EV_KEY: list(button_map.values()),
    },
    name="Virtual Gamepad"
)

# Timing Setup
last_button_check = time.monotonic()
button_check_interval = 0.03  # 30 ms

# CPU-Temperatur-Grenzwerte und Überwachungsintervall
temp_high_threshold = 55.0  # °C
temp_low_threshold = 49.0  # °C
fan_check_interval = 4.0  # Sekunde
last_temp_check = time.monotonic()
fan_state = 0  # Aktueller Zustand des Lüfters (0 = aus, 1 = an)

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
                key_code = button_map[pin]

                # State basierend auf Öffner- oder Schließerlogik setzen
                ui.write(e.EV_KEY, key_code, 1 if state == GPIO.LOW else 0)
                ui.syn()

            # Lautstärkeregler
            if GPIO.input(volume_up_pin) == GPIO.LOW:
                os.system("amixer set PCM 2%+")
            if GPIO.input(volume_down_pin) == GPIO.LOW:
                os.system("amixer set PCM 2%-")

        # CPU-Temperatur alle Sekunde überprüfen und Lüftersteuerung anpassen
        if current_time - last_temp_check > fan_check_interval:
            last_temp_check = current_time

            # CPU-Temperatur abrufen
            temp_str = os.popen("vcgencmd measure_temp").readline()
            print("temp_str: ", temp_str)
            cpu_temp = float(temp_str.replace("temp=", "").replace("'C\n", ""))

            # Lüftersteuerung basierend auf Temperatur
            if cpu_temp > temp_high_threshold and fan_state == 0:
                ser.write(b"1")  # Lüfter einschalten
                fan_state = 1
            elif cpu_temp < temp_low_threshold and fan_state == 1:
                ser.write(b"0")  # Lüfter ausschalten
                fan_state = 0

except KeyboardInterrupt:
    pass
finally:
    ui.close()
    GPIO.cleanup()
