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


# Helper to encode the temperature characteristic encoding (sint16, hundredths of a degree).
def _encode_temperature(temp_deg_c):
    return struct.pack("<h", int(temp_deg_c))


# This would be periodically polling a hardware sensor.
async def sensor_task():
    t = 0
    while True:
        print(f"new data to be sent: {_encode_temperature(t)}")
        temp_characteristic.write(_encode_temperature(t), send_update=True)
        #temp_characteristic.write(t,send_update=True)
        #t += random.uniform(-0.5, 0.5)
        t += 1
        #time.sleep(1)
        await asyncio.sleep(1)


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