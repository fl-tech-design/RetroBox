import serial

ser = serial.Serial('/dev/serial0', 9600)



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
