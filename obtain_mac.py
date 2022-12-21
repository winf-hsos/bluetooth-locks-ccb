import asyncio
from bleak import BleakScanner

async def main():
    stop_event = asyncio.Event()

    def callback(device, advertising_data):
        print(device)

    async with BleakScanner(callback) as scanner:
        await stop_event.wait()

asyncio.run(main())