import sys
# ruff: noqa: E402
sys.path.append("")
from micropython import const
import asyncio
import aioble
import bluetooth
import random
import struct
import machine
import time


# org.bluetooth.service.environmental_sensing
ENV_SENSE_UUID = bluetooth.UUID(0x181A)
# org.bluetooth.characteristic.temperature
ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)
# org.bluetooth.characteristic.gap.appearance.xml
ADV_APPEARANCE_GENERIC_THERMOMETER = const(768)

# ADVERTISING FREQUENCY
ADV_INTERVAL_MS = 1000

# REGISTER GATT SERVER
temp_service = aioble.Service(ENV_SENSE_UUID)
temp_characteristic = aioble.Characteristic(
    temp_service, ENV_SENSE_TEMP_UUID, read=True, notify=True
)
aioble.register_services(temp_service)

# SENSORS/PINS
LED = machine.Pin("LED", machine.Pin.OUT)
DPAD_UP = machine.Pin(6, machine.Pin.IN, machine.Pin.PULL_UP)
DPAD_DOWN = machine.Pin(7, machine.Pin.IN, machine.Pin.PULL_UP)
DPAD_LEFT = machine.Pin(8, machine.Pin.IN, machine.Pin.PULL_UP)
DPAD_RIGHT = machine.Pin(9, machine.Pin.IN, machine.Pin.PULL_UP)
TRIGGER = machine.Pin(10, machine.Pin.IN, machine.Pin.PULL_UP)

# SENSOR VALUES
DPAD_UP_val,DPAD_DOWN_val,DPAD_LEFT_val,DPAD_RIGHT_val,TRIGGER_val = 1,1,1,1,1

# get most recent sensor values
def getSensorValues():
    return " ".join([str(val) for val in [DPAD_UP_val,DPAD_DOWN_val,DPAD_LEFT_val,DPAD_RIGHT_val,TRIGGER_val]])

# debounce DPAD_DOWN clicks
def debounce(pin):
    stable_time = 5  # Time in milliseconds to check for stable state
    current_value = pin.value()
    
    # Wait for the pin value to stabilize
    for _ in range(stable_time):
        if pin.value() != current_value:
            return False  # If the value changes during the debounce period, return False
        time.sleep_ms(1)
    
    return True  # If stable for the entire time, return True


# poll sensors
async def sensor_task():
    global DPAD_UP_val,DPAD_DOWN_val,DPAD_LEFT_val,DPAD_RIGHT_val,TRIGGER_val
    while True:
        # DPAD
        DPAD_UP_val,DPAD_DOWN_val,DPAD_LEFT_val,DPAD_RIGHT_val,TRIGGER_val = 1,1,1,1,1
        if DPAD_UP.value() == 0 and debounce(DPAD_UP): 
            DPAD_UP_val = DPAD_UP.value()
            temp_characteristic.write(getSensorValues(), send_update=True)
        if DPAD_DOWN.value() == 0 and debounce(DPAD_DOWN):
            DPAD_DOWN_val = DPAD_DOWN.value()
            temp_characteristic.write(getSensorValues(), send_update=True)
        if DPAD_LEFT.value() == 0 and debounce(DPAD_LEFT):
            DPAD_LEFT_val = DPAD_LEFT.value()
            temp_characteristic.write(getSensorValues(), send_update=True)
        if DPAD_RIGHT.value() == 0 and debounce(DPAD_RIGHT):
            DPAD_RIGHT_val = DPAD_RIGHT.value()
            temp_characteristic.write(getSensorValues(), send_update=True)
        print(f"DPAD_UP_val = {DPAD_UP_val}, DPAD_DOWN_val = {DPAD_DOWN_val}, DPAD_LEFT_val = {DPAD_LEFT_val}, DPAD_RIGHT_val = {DPAD_RIGHT_val}")

        # TRIGGER
        if TRIGGER.value() == 0 and debounce(TRIGGER):
            TRIGGER_val = TRIGGER.value()
            temp_characteristic.write(getSensorValues(), send_update=True)
        print(f"TRIGGER_val = {TRIGGER_val}")

        # write to characteristic
        temp_characteristic.write(getSensorValues(), send_update=True)
        await asyncio.sleep(0.1)


# serially wait for connections; no advertise while client connected
async def server_task():
    while True:
        async with await aioble.advertise(
            ADV_INTERVAL_MS,
            name="TEAM 1 LEFT CONTROLLER",
            services=[ENV_SENSE_UUID],
            appearance=ADV_APPEARANCE_GENERIC_THERMOMETER,
        ) as connection:
            print("Connection from", connection.device)
            await connection.disconnected(timeout_ms=None)
            print("DEVICE DISCONNECTED")


# blink led to confirm device is running
async def blink_task():
    while True:
        LED.high()
        await asyncio.sleep(1)
        LED.low()
        await asyncio.sleep(1)


# run tasks
async def main():
    t1 = asyncio.create_task(sensor_task())
    t2 = asyncio.create_task(server_task())
    t3 = asyncio.create_task(blink_task())
    await asyncio.gather(t1,t2,t3)


asyncio.run(main())
