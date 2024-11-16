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
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
# org.bluetooth.characteristic.temperature
_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)
# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_THERMOMETER = const(768)

# How frequently to send advertising beacons.
_ADV_INTERVAL_MS = 1000


# Register GATT server.
temp_service = aioble.Service(_ENV_SENSE_UUID)
temp_characteristic = aioble.Characteristic(
    temp_service, _ENV_SENSE_TEMP_UUID, read=True, notify=True
)
aioble.register_services(temp_service)

def debounce(pin):
    stable_time = 10  # Time in milliseconds to check for stable state
    current_value = pin.value()
    
    # Wait for the pin value to stabilize
    for _ in range(stable_time):
        if pin.value() != current_value:
            return False  # If the value changes during the debounce period, return False
        time.sleep_ms(1)
    
    return True  # If stable for the entire time, return True

# This would be periodically polling a hardware sensor.
async def sensor_task():
    button = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
    t = 0
    while True:
        if button.value() == 0:
            if debounce(button):
                t += 1
                print(f"new data to be sent: {t}")
                temp_characteristic.write(str(t), send_update=True)
        await asyncio.sleep(0.25)


# Serially wait for connections.
# Don't advertise while a central is connected.
async def server_task():
    while True:
        async with await aioble.advertise(
            _ADV_INTERVAL_MS,
            name="TEAM 1 CONTROLLER 1",
            services=[_ENV_SENSE_UUID],
            appearance=_ADV_APPEARANCE_GENERIC_THERMOMETER,
        ) as connection:
            print("Connection from", connection.device)
            await connection.disconnected(timeout_ms=None)
            print("DEVICE DISCONNECTED")


# blink led to confirm device is running
async def blink_task():
    led = machine.Pin("LED", machine.Pin.OUT)
    while True:
        led.high()
        await asyncio.sleep(1)
        led.low()
        await asyncio.sleep(1)


# Run tasks
async def main():
    t1 = asyncio.create_task(sensor_task())
    t2 = asyncio.create_task(server_task())
    t3 = asyncio.create_task(blink_task())
    await asyncio.gather(t1,t2,t3)


asyncio.run(main())
