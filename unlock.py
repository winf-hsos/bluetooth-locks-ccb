import asyncio
from datetime import datetime

from bleak import BleakClient

async def unlock(mac_address):

    # Connect to client
    client = await connect(mac_address)

    print(f"Connected: { client.is_connected }")
    
    # Send date to speed up
    dateTimeObj = datetime.now()
    date = bytes([dateTimeObj.second, dateTimeObj.minute, dateTimeObj.hour, dateTimeObj.day, dateTimeObj.year % 100])

    print(f"Sending date")
    await client.write_gatt_char("4d4f4445-5343-4f2d-574f-524a45523033", data = date)

    # User code is in ASCII numbers
    # TODO: Replace with correct user code in ASCII numbers
    # See: https://www.asciitable.com/
    code = bytes([49, 51, 48, 57, 48, 48, 49])
    
    print(f"Unlocking")

    # Write data to characteristic
    await client.write_gatt_char("4d4f4445-5343-4f2d-574f-524a45523032", data = code)

async def connect(mac_address):
    
    # The max. timeout - connection can happen faster than that
    # TODO: Make robust - what if it takes longer (haven't observed, but can happen)?
    # TODO: Catch "bleak.exc.BleakError: Could not get GATT services: Unreachable" error
    timeout_sec = 120
    client = BleakClient(mac_address, timeout = timeout_sec)
    await client.connect(timeout = timeout_sec)
    return client


# TODO: Change MAC address
mac_address = "DE:44:38:02:AA:EA"
asyncio.run(unlock(mac_address))