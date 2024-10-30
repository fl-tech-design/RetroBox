import serial

ser = serial.Serial('/dev/serial0', 9600)



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

        print(f"{xStick1}, {yStick1}, {xStick2}, {yStick2}")