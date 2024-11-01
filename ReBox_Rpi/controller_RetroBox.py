import time
import serial
import RPi.GPIO as GPIO
from evdev import UInput, ecodes as e, AbsInfo

# GPIO Setup
GPIO.setmode(GPIO.BCM)
button_pins = [17, 18, 27, 22, 23, 16, 19, 20, 26, 21, 5, 6, 24, 13]
buttons_state = [0] * len(button_pins)

# Set up the pins as openers and closers
for i, pin in enumerate(button_pins):
    if i < len(button_pins) - 2:  # Opener
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    else:  # Closer
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Serial setup
ser = serial.Serial("/dev/serial0", 9600)

# UInput setup
ui = UInput({
    e.EV_ABS: [
        (e.ABS_X, AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=0, resolution=0)),
        (e.ABS_Y, AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=0, resolution=0)),
        (e.ABS_RX, AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=0, resolution=0)),
        (e.ABS_RY, AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=0, resolution=0))
    ],
    e.EV_KEY: [e.BTN_A, e.BTN_B, e.BTN_X, e.BTN_Y, e.BTN_TL, e.BTN_TR, e.BTN_SELECT, e.BTN_START, e.BTN_THUMBL, e.BTN_THUMBR]
})

# Timing setup
last_button_check = time.monotonic()
button_check_interval = 0.03  # 30 ms

try:
    while True:
        # Read joystick data
        if ser.in_waiting > 0:
            data = ser.readline().decode().strip().split(",")
            if len(data) == 4:
                xStick1, yStick1 = int(data[0]), int(data[1])
                xStick2, yStick2 = int(data[2]), int(data[3])

                # Debugging: Print joystick values
                #print(f"Joystick: {xStick1}, {yStick1}, {xStick2}, {yStick2}")

                # Send joystick values to the virtual controller
                ui.write(e.EV_ABS, e.ABS_X, xStick1)
                ui.write(e.EV_ABS, e.ABS_Y, yStick1)
                ui.write(e.EV_ABS, e.ABS_RX, xStick2)
                ui.write(e.EV_ABS, e.ABS_RY, yStick2)
                ui.syn()

        # Check button states every 30 ms
        current_time = time.monotonic()
        if current_time - last_button_check > button_check_interval:
            last_button_check = current_time
            for i, pin in enumerate(button_pins):
                buttons_state[i] = GPIO.input(pin)
                
                if i < len(button_pins) - 2:  # Opener
                    if buttons_state[i] == GPIO.LOW:
                        ui.write(e.EV_KEY, e.BTN_A + i, 0)
                    else:
                        ui.write(e.EV_KEY, e.BTN_A + i, 1)
                        print(f"Button {i+1} (Öffner) gedrückt")
                else:  # Closer
                    if buttons_state[i] == GPIO.HIGH:
                        ui.write(e.EV_KEY, e.BTN_A + i, 1)
                    else:
                        ui.write(e.EV_KEY, e.BTN_A + i, 0)
                        print(f"Button {i+1} (Schließer) gedrückt")
                
                # Synchronize the button state updates
                ui.syn()

except KeyboardInterrupt:
    pass
finally:
    ui.close()
    GPIO.cleanup()
