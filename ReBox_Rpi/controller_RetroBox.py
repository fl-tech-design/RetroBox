import time
import serial
import RPi.GPIO as GPIO
from evdev import UInput, ecodes as e, AbsInfo

# GPIO Setup
GPIO.setmode(GPIO.BCM)
button_pins = [19, 26, 20, 16, 21, 17, 18, 27, 22, 23, 24, 5]
buttons_state = [0] * len(button_pins)

# Set up the pins as openers and closers
for i, pin in enumerate(button_pins):
    if i < len(button_pins) - 2:  # Opener
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    else:  # Closer
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Serial setup
ser = serial.Serial("/dev/serial0", 9600)

# UInput setup for a Gamepad
ui = UInput(
    {
        e.EV_ABS: [
            (e.ABS_X, AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=15, resolution=0)),
            (e.ABS_Y, AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=15, resolution=0)),
            (e.ABS_RX, AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=15, resolution=0)),
            (e.ABS_RY, AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=15, resolution=0)),
        ],
        e.EV_KEY: [
            e.BTN_A,  # Button 1
            e.BTN_B,  # Button 2
            e.BTN_X,  # Button 3
            e.BTN_Y,  # Button 4
            e.BTN_TL,  # Button 5
            e.BTN_TR,  # Button 6
            e.BTN_SELECT,  # Button 7
            e.BTN_START,  # Button 8
            e.BTN_THUMBL,  # Button 9
            e.BTN_THUMBR,  # Button 10
        ],
    },
    name="Virtual Gamepad"  # Name für EmulationStation, damit es als Gamepad erkannt wird
)

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
                        ui.write(e.EV_KEY, e.BTN_A + i, 1)
                    else:
                        ui.write(e.EV_KEY, e.BTN_A + i, 0)
                else:  # Closer
                    if buttons_state[i] == GPIO.LOW:
                        ui.write(e.EV_KEY, e.BTN_A + i, 1)
                    else:
                        ui.write(e.EV_KEY, e.BTN_A + i, 0)

                # Synchronize the button state updates
                ui.syn()

except KeyboardInterrupt:
    pass
finally:
    ui.close()
    GPIO.cleanup()
