import serial
from evdev import UInput, ecodes as e

ser = serial.Serial('/dev/serial0', 9600)
ui = UInput()

buttons = {
    'button_left_0': e.BTN_1,
    'button_left_1': e.BTN_2,
    'button_left_2': e.BTN_3,
    'button_left_3': e.BTN_4,
    'button_left_4': e.BTN_5,
    'button_left_5': e.BTN_6,
    'button_right_0': e.BTN_7,
    'button_right_1': e.BTN_8,
    'button_right_2': e.BTN_9,
    'button_right_3': e.BTN_10,
    'button_right_4': e.BTN_11,
    'button_right_5': e.BTN_12,
}

sticks = {
    'xStick1': e.ABS_X,
    'yStick1': e.ABS_Y,
    'xStick2': e.ABS_RX,
    'yStick2': e.ABS_RY,
}

while True:
    if ser.in_waiting > 0:
        data = ser.readline().decode().strip().split(',')
        print("data: ", data)
        if len(data) != 4:
            print(f"Fehler: Erwartete 16 Werte, aber empfangen: {len(data)}")
            continue

        xStick1 = int(data[0])
        yStick1 = int(data[1])
        xStick2 = int(data[2])
        yStick2 = int(data[3])

        ui.write(e.EV_ABS, sticks['xStick1'], xStick1)
        ui.write(e.EV_ABS, sticks['yStick1'], yStick1)
        ui.write(e.EV_ABS, sticks['xStick2'], xStick2)
        ui.write(e.EV_ABS, sticks['yStick2'], yStick2)

        ui.syn()
