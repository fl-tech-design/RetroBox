import serial
from evdev import UInput, ecodes as e

# Serielle Schnittstelle öffnen
ser = serial.Serial('/dev/serial0', 9600)

# Virtuelles Eingabegerät erstellen
ui = UInput()

# Button- und Stick-Events definieren
buttons = {
    'button_left_0': e.BTN_A,  # Linke Buttons
    'button_left_1': e.BTN_B,
    'button_left_2': e.BTN_C,
    'button_left_3': e.BTN_X,
    'button_left_4': e.BTN_Y,
    'button_left_5': e.BTN_Z,
    'button_right_0': e.BTN_TL,  # Rechte Buttons
    'button_right_1': e.BTN_TR,
    'button_right_2': e.BTN_SELECT,
    'button_right_3': e.BTN_START,
    'button_right_4': e.BTN_MODE,
    'button_right_5': e.BTN_THUMBL,
}

# Analog-Stick-Events definieren
sticks = {
    'xStick1': e.ABS_X,
    'yStick1': e.ABS_Y,
    'xStick2': e.ABS_RX,
    'yStick2': e.ABS_RY,
}

while True:
    if ser.in_waiting > 0:
        # Seriell empfangene Daten einlesen und in Werte umwandeln
        data = ser.readline().decode().strip().split(',')

        # Annahme: Die empfangenen Daten sind in der Reihenfolge: 
        # 6 linke Buttons, 6 rechte Buttons, xStick1, yStick1, xStick2, yStick2
        button_left = [int(data[i]) for i in range(6)]
        button_right = [int(data[i + 6]) for i in range(6)]
        xStick1 = int(data[12])
        yStick1 = int(data[13])
        xStick2 = int(data[14])
        yStick2 = int(data[15])

        # Buttons links senden
        for i in range(6):
            ui.write(e.EV_KEY, buttons[f'button_left_{i}'], button_left[i])

        # Buttons rechts senden
        for i in range(6):
            ui.write(e.EV_KEY, buttons[f'button_right_{i}'], button_right[i])

        # Analog-Sticks senden
        ui.write(e.EV_ABS, sticks['xStick1'], xStick1)
        ui.write(e.EV_ABS, sticks['yStick1'], yStick1)
        ui.write(e.EV_ABS, sticks['xStick2'], xStick2)
        ui.write(e.EV_ABS, sticks['yStick2'], yStick2)

        # Änderungen übernehmen
        ui.syn()